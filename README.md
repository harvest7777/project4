# P2P Decentralized Storage Network

A peer-to-peer distributed storage system built with Flask and Docker. Each node supports file upload/download, a key-value store, DHT-based routing, and automatic peer health monitoring.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Build

```bash
docker compose build
```

## Run

```bash
docker compose up
```

This starts 3 nodes:

| Node  | Host Port | Storage Volume        |
|-------|-----------|-----------------------|
| node1 | 5001      | `./storage/node1/`    |
| node2 | 5002      | `./storage/node2/`    |
| node3 | 5003      | `./storage/node3/`    |

All nodes discover each other automatically via the `PEERS` environment variable.

## Testing

### File Upload

```bash
# Using the helper script
./upload.sh myfile.txt

# Or directly with curl
curl -F 'file=@myfile.txt' http://localhost:5001/upload
```

### File Download

```bash
# Using the helper script
./download.sh myfile.txt

# Or directly with curl
curl -O http://localhost:5001/download/myfile.txt
```

### Key-Value Store (DHT-Routed)

Keys are distributed across nodes using SHA-1 hashing. Any node will automatically forward requests to the responsible node.

```bash
# Store a key-value pair
curl -X POST http://localhost:5001/kv \
  -H "Content-Type: application/json" \
  -d '{"key": "color", "value": "blue"}'

# Retrieve a value by key
curl http://localhost:5001/kv/color
```

You can target any node (5001, 5002, or 5003) — routing is handled automatically.

### Health Check

Nodes ping each other every 10 seconds and update their active peer lists automatically. To manually check a node:

```bash
curl http://localhost:5001/ping
```

## Stop

```bash
docker compose down
```
