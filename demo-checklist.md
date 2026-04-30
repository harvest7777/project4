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
  docker logs node1
  ```
  Logs should show `Forwarding PUT key='color' to http://node2:5000`

- [ ] Send `dht-test=hello` to node1, confirm it routes to node3
  ```
  curl -X POST http://localhost:5001/kv -H "Content-Type: application/json" -d '{"key": "dht-test", "value": "hello"}'
  docker logs node1
  ```
  Logs should show `Forwarding PUT key='dht-test' to http://node3:5000`

- [ ] Get `color` from node1, confirm it routes to node2
  ```
  curl http://localhost:5001/kv/color
  docker logs node1
  ```
  Logs should show `Forwarding GET key='color' to http://node2:5000`

- [ ] Get `dht-test` from node1, confirm it routes to node3
  ```
  curl http://localhost:5001/kv/dht-test
  docker logs node1
  ```
  Logs should show `Forwarding GET key='dht-test' to http://node3:5000`

---

## Peer Health Monitoring

- [ ] Kill node2 and confirm node1 detects it as unreachable
  ```
  docker stop node2
  ```
  Wait ~10 seconds, then:
  ```
  docker logs node1
  ```
  Logs should show `http://node2:5000 is unreachable, removed from peer list`

- [ ] Bring node2 back and confirm node1 detects it as online
  ```
  docker start node2
  ```
  Wait ~10 seconds, then:
  ```
  docker logs node1
  ```
  Logs should show `http://node2:5000 is back online, added to peer list`

---

## Failure Handling

- [ ] With node2 still down, store `color=red` via node1 — should reroute to node3 instead of failing
  ```
  curl -X POST http://localhost:5001/kv -H "Content-Type: application/json" -d '{"key": "color", "value": "red"}'
  docker logs node1
  ```
  Logs should show `Forwarding PUT key='color' to http://node3:5000`

- [ ] Retrieve `color` via node1 — should still resolve from node3
  ```
  curl http://localhost:5001/kv/color
  docker logs node1
  ```
  Logs should show `Forwarding GET key='color' to http://node3:5000`

---

## Re-join

- [ ] With node2 back online, store `color=blue` via node1 — should route back to node2
  ```
  curl -X POST http://localhost:5001/kv -H "Content-Type: application/json" -d '{"key": "color", "value": "blue"}'
  docker logs node1
  ```
  Logs should show `Forwarding PUT key='color' to http://node2:5000`

- [ ] Retrieve `color` via node1 — should resolve from node2 again
  ```
  curl http://localhost:5001/kv/color
  docker logs node1
  ```
  Logs should show `Forwarding GET key='color' to http://node2:5000`
