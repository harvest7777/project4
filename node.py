import hashlib
import logging
import os
import threading
import time

import requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

STORAGE_DIR = "/app/storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

store = {}

ALL_PEERS = os.environ["PEERS"].split(",")
MY_URL = os.environ["MY_URL"]

active_peers = [p for p in ALL_PEERS if p != MY_URL]
peers_lock = threading.Lock()


def responsible_node(key):
    with peers_lock:
        alive = set(active_peers) | {MY_URL}
    pool = [p for p in ALL_PEERS if p in alive]
    index = int(hashlib.sha1(key.encode()).hexdigest(), 16) % len(pool)
    return pool[index]


def health_check():
    while True:
        time.sleep(10)
        for peer in ALL_PEERS:
            if peer == MY_URL:
                continue
            try:
                requests.get(f"{peer}/ping", timeout=2)
                with peers_lock:
                    if peer not in active_peers:
                        active_peers.append(peer)
                        app.logger.info(f"{peer} is back online, added to peer list")
            except requests.exceptions.RequestException:
                with peers_lock:
                    if peer in active_peers:
                        active_peers.remove(peer)
                        app.logger.info(f"{peer} is unreachable, removed from peer list")


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"})


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(f"{STORAGE_DIR}/{file.filename}")
    return jsonify({"status": "uploaded", "filename": file.filename})


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(STORAGE_DIR, filename)


@app.route('/kv', methods=['POST'])
def put_kv():
    data = request.json
    owner = responsible_node(data['key'])
    if owner != MY_URL:
        app.logger.info(f"Forwarding PUT key='{data['key']}' to {owner}")
        return requests.post(f"{owner}/kv", json=data).json()
    store[data['key']] = data['value']
    return jsonify({"status": "stored", "key": data['key']})


@app.route('/kv/<key>', methods=['GET'])
def get_kv(key):
    owner = responsible_node(key)
    if owner != MY_URL:
        app.logger.info(f"Forwarding GET key='{key}' to {owner}")
        return requests.get(f"{owner}/kv/{key}").json()
    value = store.get(key)
    if value is None:
        return jsonify({"error": "key not found"}), 404
    return jsonify({"key": key, "value": value})


if __name__ == "__main__":
    threading.Thread(target=health_check, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
