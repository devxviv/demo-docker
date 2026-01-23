# Part 4b: Docker Networking

## 4b.1 Docker Network Types

Docker provides several network drivers for different use cases:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCKER NETWORK TYPES                         │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐  │
│  │   bridge   │  │    host    │  │    none    │  │  overlay  │  │
│  │  (default) │  │ (no isol.) │  │ (no net)   │  │ (swarm)   │  │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

| Network Type | Isolation              | Use Case                         |
| ------------ | ---------------------- | -------------------------------- |
| **bridge**   | Yes - own subnet       | Default, most containers         |
| **host**     | No - uses host network | High performance, port conflicts |
| **none**     | Complete - no network  | Security, isolated processing    |
| **macvlan**  | Yes - own MAC address  | Legacy apps needing real IPs     |

---

## 4b.2 Bridge Network (Default)

Containers on the same bridge network can communicate.

```
┌──────────────────────────────────────────────────────────────┐
│  HOST (172.17.0.1)                                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  DOCKER BRIDGE NETWORK (172.17.0.0/16)                 │  │
│  │                                                        │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│  │  │ Container A │  │ Container B │  │ Container C │     │  │
│  │  │ 172.17.0.2  │  │ 172.17.0.3  │  │ 172.17.0.4  │     │  │
│  │  │ nginx:80    │  │ backend:8000│  │   db:5432   │     │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│  │         │                 │                │           │  │
│  │         └─────────────────┼────────────────┘           │  │
│  │                           │                            │  │
│  └───────────────────────────┼────────────────────────────┘  │
│                              │                               │
│                              ▼ (Port mapping -p 8080:80)     │
└──────────────────────────────┼───────────────────────────────┘
                               │
                          External: localhost:8080
```

### Commands
```bash
# List networks
docker network ls

# Inspect default bridge
docker network inspect bridge

# Create custom bridge
docker network create mynetwork

# Run container on custom network
docker run -d --network mynetwork --name web nginx

# Container on same network can use name
docker run -d --network mynetwork --name api myapp
# api can reach: http://web:80
```

---

## 4b.3 Container Communication

### Same Network - DNS Resolution
```bash
# Create network
docker network create app-network

# Run database
docker run -d \
  --network app-network \
  --name postgres \
  -e POSTGRES_PASSWORD=secret \
  postgres:15

# Run backend (connects to postgres by name)
docker run -d \
  --network app-network \
  --name backend \
  -e DATABASE_URL=postgresql://user:pass@postgres:5432/db \
  mybackend:v1
```

### Different Networks - No Communication
```bash
# Network A
docker network create network-a
docker run -d --network network-a --name app1 nginx

# Network B
docker network create network-b
docker run -d --network network-b --name app2 nginx

# app1 CANNOT reach app2 (isolated)
```

### Connect Container to Multiple Networks
```bash
# Container can be on multiple networks
docker network connect network-b app1

# Now app1 is on both network-a and network-b
```

---

## 4b.4 Port Mapping

```
┌────────────────────────────────────────────────────────────────┐
│  PORT MAPPING (-p flag)                                        │
│                                                                │
│  External          Host          Container                     │
│  ┌──────┐         ┌──────┐         ┌──────┐                    │
│  │ :8080├────────▶│ :8080├────────▶│  :80 │                    │
│  └──────┘         └──────┘         └──────┘                    │
│  Internet         Docker          nginx                        │
│                   Host                                         │
└────────────────────────────────────────────────────────────────┘
```

### Port Mapping Syntax
```bash
# Format: -p HOST_PORT:CONTAINER_PORT

# Map port 8080 on host to 80 in container
docker run -d -p 8080:80 nginx

# Map to specific host IP
docker run -d -p 127.0.0.1:8080:80 nginx

# Random host port (ephemeral)
docker run -d -p 80 nginx

# Multiple ports
docker run -d -p 8080:80 -p 8443:443 nginx

# Check port mappings
docker port <container>
```

---

## 4b.5 Host Network Mode

Container uses host's network directly (no isolation).

```
┌──────────────────────────────────────────────────────────────┐
│  HOST NETWORK MODE                                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  HOST (192.168.1.100)                                  │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │  Container (--network host)                     │   │  │
│  │  │  - Uses 192.168.1.100 directly                  │   │  │
│  │  │  - nginx listens on host's port 80              │   │  │
│  │  │  - No port mapping needed                       │   │  │
│  │  │  - No network isolation                         │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

```bash
# Use host network
docker run -d --network host nginx

# Access directly at host IP (no -p needed)
curl http://localhost:80
```

**Use Cases:**
- High performance (no NAT overhead)
- Network monitoring tools
- Kubernetes pods (similar concept)

**Drawbacks:**
- Port conflicts with host
- Less portable
- Security concerns

---

## 4b.6 Network Troubleshooting

### Inspect Network
```bash
# View network details
docker network inspect bridge

# See which containers are connected
docker network inspect mynetwork | grep -A 5 Containers
```

### Test Connectivity
```bash
# Run busybox for debugging
docker run --rm -it --network mynetwork busybox sh

# Inside busybox:
ping postgres
wget -qO- http://backend:8000/healthz
nslookup postgres
```

### Check DNS Resolution
```bash
# DNS lookup from container
docker exec <container> nslookup backend

# Should return container IP
```

### Common Issues

| Problem               | Cause              | Solution                   |
| --------------------- | ------------------ | -------------------------- |
| Cannot ping container | Different networks | Connect to same network    |
| DNS not working       | Default bridge     | Use custom bridge network  |
| Port already in use   | Host port conflict | Use different host port    |
| Cannot reach internet | Network driver     | Check DNS/gateway settings |

---

## 4b.7 Docker Compose Networking

Compose automatically creates a network for all services.

```yaml
version: "3.8"
services:
  frontend:
    image: nginx
    # Can reach backend at http://backend:8000
  
  backend:
    image: myapp
    # Can reach db at postgresql://db:5432
  
  db:
    image: postgres:15

# All on same network: <project>_default
```

### Custom Networks in Compose
```yaml
version: "3.8"
services:
  web:
    networks:
      - frontend
  
  api:
    networks:
      - frontend
      - backend
  
  db:
    networks:
      - backend

networks:
  frontend:
  backend:
```

```
┌──────────────────────────────────────────────────────────┐
│  DOCKER COMPOSE MULTI-NETWORK                            │
│                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────┐  │
│  │     web      │────▶│     api      │────▶│    db    │  │
│  │   (nginx)    │     │  (backend)   │     │(postgres)│  │
│  └──────────────┘     └──────────────┘     └──────────┘  │
│         │                     │                   │      │
│    ┌────┴────┐           ┌────┴────┐         ┌────┴────┐ │
│    │frontend │           │frontend │         │ backend │ │
│    │ network │           │ backend │         │ network │ │
│    └─────────┘           │ networks│         └─────────┘ │
│                          └─────────┘                     │
└──────────────────────────────────────────────────────────┘
```

---

## 4b.8 Practical Example: Full Stack

```bash
# Create network
docker network create fullstack

# Database
docker run -d \
  --network fullstack \
  --name db \
  -e POSTGRES_PASSWORD=secret \
  postgres:15

# Backend API
docker run -d \
  --network fullstack \
  --name api \
  -e DATABASE_URL=postgresql://postgres:secret@db:5432/myapp \
  myapi:v1

# Frontend
docker run -d \
  --network fullstack \
  --name web \
  -p 3000:80 \
  -e API_URL=http://api:8000 \
  myfrontend:v1

# Test from outside
curl http://localhost:3000

# Test internally
docker exec web curl http://api:8000/healthz
```

---

**Next:** [Part 5: Docker Compose](./05-docker-compose.md)
