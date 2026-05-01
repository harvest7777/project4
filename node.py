import hashlib
import logging
import os
import threading
import time

import requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# directory where uploaded files are stored
STORAGE_DIR = "/app/storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

# in-memory key-value store for this node
store = {}

# full peer list from env; MY_URL identifies this node
ALL_PEERS = os.environ["PEERS"].split(",")
MY_URL = os.environ["MY_URL"]

# tracks which peers are currently reachable
active_peers = [p for p in ALL_PEERS if p != MY_URL]
peers_lock = threading.Lock()


# SHA-1 hash the key to determine which node owns it
def responsible_node(key):
    with peers_lock:
        alive = set(active_peers) | {MY_URL}
    pool = [p for p in ALL_PEERS if p in alive]
    index = int(hashlib.sha1(key.encode()).hexdigest(), 16) % len(pool)
    return pool[index]


# background thread: ping all peers every 10s, update active_peers accordingly
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


# health check endpoint used by peers to verify this node is alive
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"})


# save uploaded file to local storage
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(f"{STORAGE_DIR}/{file.filename}")
    return jsonify({"status": "uploaded", "filename": file.filename})


# serve a file from local storage by filename
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(STORAGE_DIR, filename)


# store a key-value pair; forward to responsible node if it's not this one
@app.route('/kv', methods=['POST'])
def put_kv():
    data = request.json
    owner = responsible_node(data['key'])
    if owner != MY_URL:
        app.logger.info(f"Forwarding PUT key='{data['key']}' to {owner}")
        return requests.post(f"{owner}/kv", json=data).json()
    store[data['key']] = data['value']
    return jsonify({"status": "stored", "key": data['key']})


# retrieve a value by key; forward to responsible node if it's not this one
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
    # start health monitor in background before serving requests
    threading.Thread(target=health_check, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
