# Demo Checklist

## File Upload & Download

- [ ] Upload a file to node1
  ```
  curl -F "file=@test_file.txt" http://localhost:5001/upload
  ```
- [ ] Show file exists inside node1's container
  ```
  docker exec node1 ls /app/storage
  ```
- [ ] Download the file
  ```
  curl -O http://localhost:5001/download/test_file.txt
  ```
- [ ] Show file saved locally
  ```
  ls test_file.txt
  ```

---

## KV Store & DHT Routing

- [ ] Send `color=blue` to node1, confirm it routes to node2
  ```
  curl -X POST http://localhost:5001/kv -H "Content-Type: application/json" -d '{"key": "color", "value": "blue"}'
  ```
  Response should show `"node": "http://node2:5000"`

- [ ] Send `dht-test=hello` to node1, confirm it routes to node3
  ```
  curl -X POST http://localhost:5001/kv -H "Content-Type: application/json" -d '{"key": "dht-test", "value": "hello"}'
  ```
  Response should show `"node": "http://node3:5000"`
