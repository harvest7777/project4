import hashlib
import logging
import os

import requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

STORAGE_DIR = "/app/storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

store = {}

PEERS = os.environ["PEERS"].split(",")
MY_URL = os.environ["MY_URL"]


def responsible_node(key):
    index = int(hashlib.sha1(key.encode()).hexdigest(), 16) % len(PEERS)
    return PEERS[index]


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
    app.run(host="0.0.0.0", port=5000)
