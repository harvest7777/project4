import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

STORAGE_DIR = "./storage"
os.makedirs(STORAGE_DIR, exist_ok=True)


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(f"{STORAGE_DIR}/{file.filename}")
    return jsonify({"status": "uploaded", "filename": file.filename})


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(STORAGE_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
