#!/bin/bash
set -e

HOST="http://localhost:5001"
TEST_FILE="/tmp/test_upload.txt"
FILENAME="test_upload.txt"

echo "test content from upload script" > "$TEST_FILE"

echo "Uploading $FILENAME..."
UPLOAD_RESPONSE=$(curl -sf -F "file=@$TEST_FILE" "$HOST/upload")
echo "Upload response: $UPLOAD_RESPONSE"

echo "Downloading $FILENAME..."
DOWNLOAD_RESPONSE=$(curl -sf "$HOST/download/$FILENAME")

if [ "$DOWNLOAD_RESPONSE" = "$(cat $TEST_FILE)" ]; then
    echo "PASS: downloaded content matches uploaded content"
else
    echo "FAIL: content mismatch"
    echo "  expected: $(cat $TEST_FILE)"
    echo "  got:      $DOWNLOAD_RESPONSE"
    exit 1
fi
