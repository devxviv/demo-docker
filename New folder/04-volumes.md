# Part 4: Volumes and Data Persistence

## 4.1 The Problem: Containers Are Ephemeral

Containers are **temporary**. When you remove a container, all data inside is **lost**.

```
┌─────────────────────────────────────────────────────────┐
│  Container Running                                       │
│  ┌─────────────────────────────┐                        │
│  │  /data/database.db          │  ← Data here          │
│  └─────────────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼  docker rm container
┌─────────────────────────────────────────────────────────┐
│  Container Removed                                       │
│                                                          │
│  DATA IS GONE! 💀                                        │
└─────────────────────────────────────────────────────────┘
```

**Solution:** Use **Volumes** to store data outside the container.

---

## 4.2 Types of Data Storage

| Type            | Description             | Use Case                   |
| --------------- | ----------------------- | -------------------------- |
| **Volumes**     | Managed by Docker       | Databases, persistent data |
| **Bind Mounts** | Maps host path directly | Development, config files  |
| **tmpfs**       | Stored in memory only   | Sensitive data, temp files |

```
┌─────────────────────────────────────────────────────────────┐
│  HOST MACHINE                                                │
│                                                              │
│  /var/lib/docker/volumes/   ← Docker Volumes (managed)      │
│  /home/user/project/        ← Bind Mounts (your folders)    │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │ Container A  │   │ Container B  │   │ Container C  │    │
│  │              │   │              │   │              │    │
│  │ /data ──────────▶│ volume1     │   │ /app ────────────▶│
│  │              │   │              │   │ /home/user/code  │
│  └──────────────┘   └──────────────┘   └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 4.3 Docker Volumes (Recommended)

### Create and Use Volumes
```bash
# Create a named volume
docker volume create mydata

# List volumes
docker volume ls

# Use volume in container
docker run -d \
  -v mydata:/var/lib/postgresql/data \
  postgres:15

# Inspect volume
docker volume inspect mydata

# Remove volume
docker volume rm mydata

# Remove all unused volumes
docker volume prune
```

### Volume Commands Explained
```bash
docker run -v <volume-name>:<container-path>

# Example: PostgreSQL
docker run -d \
  -v pgdata:/var/lib/postgresql/data \  # Volume mount
  -e POSTGRES_PASSWORD=secret \
  postgres:15
```

---

## 4.4 Bind Mounts (Development)

Maps a **host folder** directly into the container.

```bash
# Syntax
docker run -v /host/path:/container/path

# Development example: Live reload
docker run -d \
  -v $(pwd)/src:/app/src \    # Mount current directory
  -p 3000:3000 \
  node:18 npm run dev
```

### When to Use Bind Mounts
- **Development:** Edit code on host, see changes in container
- **Config files:** Mount nginx.conf, .env files
- **NOT for production databases**

---

## 4.5 PostgreSQL Examples

### Development (Bind Mount for Data)
```bash
# Create data directory
mkdir -p ./postgres-data

# Run PostgreSQL
docker run -d \
  --name postgres-dev \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=myapp \
  -v $(pwd)/postgres-data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15

# Connect
psql -h localhost -U admin -d myapp
```

### Production (Named Volume)
```bash
# Create volume
docker volume create postgres-prod-data

# Run PostgreSQL
docker run -d \
  --name postgres-prod \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=supersecret \
  -e POSTGRES_DB=production \
  -v postgres-prod-data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15

# Backup the volume
docker run --rm \
  -v postgres-prod-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz /data
```

---

## 4.6 Read-Only Mounts

For security, mount config files as read-only:

```bash
docker run -d \
  -v ./nginx.conf:/etc/nginx/nginx.conf:ro \  # :ro = read-only
  nginx
```

---

## 4.7 Volume Lifecycle

```
┌────────────────────────────────────────────────────────────┐
│                    VOLUME LIFECYCLE                         │
│                                                             │
│  1. Create Volume                                           │
│     docker volume create mydata                             │
│                      │                                      │
│                      ▼                                      │
│  2. Use in Container                                        │
│     docker run -v mydata:/app/data myapp                    │
│                      │                                      │
│                      ▼                                      │
│  3. Container Removed (Volume Persists!)                    │
│     docker rm container                                     │
│                      │                                      │
│                      ▼                                      │
│  4. New Container Uses Same Volume                          │
│     docker run -v mydata:/app/data newapp                   │
│                      │                                      │
│                      ▼                                      │
│  5. Delete Volume (When Done)                               │
│     docker volume rm mydata                                 │
└────────────────────────────────────────────────────────────┘
```

---

**Next:** [Part 5: Docker Compose](./05-docker-compose.md)
