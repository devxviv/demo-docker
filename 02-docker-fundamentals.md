# Part 2: Docker Fundamentals

## 2.1 What is Docker?

Docker is a tool that **packages applications with their dependencies** into isolated units called **containers**.

```
WITHOUT DOCKER:
┌─────────────────────────────────────────────────┐
│  Developer's Laptop          Production Server  │
│  Python 3.11                  Python 3.8 ❌     │
│  OpenSSL 1.1.1                OpenSSL 1.0.2 ❌  │
│  "Works on my machine!"       "It's broken!"    │
└─────────────────────────────────────────────────┘

WITH DOCKER:
┌─────────────────────────────────────────────────┐
│  Same Container Runs Everywhere                 │
│  ┌─────────────────────────────────────────┐   │
│  │  Your App + Python 3.11 + OpenSSL 1.1.1 │   │
│  │  (All bundled together)                 │   │
│  └─────────────────────────────────────────┘   │
│  Dev Laptop ✓   Staging ✓   Production ✓       │
└─────────────────────────────────────────────────┘
```

---

## 2.2 Docker Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        DOCKER CLIENT                          │
│                    (docker CLI commands)                      │
│         docker build | docker run | docker push              │
└────────────────────────────┬─────────────────────────────────┘
                             │ REST API
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                      DOCKER DAEMON (dockerd)                  │
│                                                               │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│   │   Images    │  │ Containers  │  │  Networks   │         │
│   │   Manager   │  │   Runtime   │  │   Manager   │         │
│   └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                    CONTAINER RUNTIME                          │
│                (containerd + runc)                            │
│                                                               │
│   Uses Linux: Namespaces | cgroups | UnionFS                 │
└──────────────────────────────────────────────────────────────┘
```

### Key Components

| Component         | What It Does                                                |
| ----------------- | ----------------------------------------------------------- |
| **Docker Client** | CLI tool you type commands into                             |
| **Docker Daemon** | Background service that manages everything                  |
| **containerd**    | Industry-standard container runtime                         |
| **runc**          | Low-level tool that creates containers using Linux features |

---

## 2.3 Image vs Container

| Image                           | Container               |
| ------------------------------- | ----------------------- |
| Blueprint/Template              | Running instance        |
| Read-only                       | Read-write layer on top |
| Like a **Class** in programming | Like an **Object**      |
| Stored on disk                  | Running in memory       |

```bash
# Image = Recipe
# Container = The cooked dish

docker images        # List images (recipes)
docker ps            # List containers (dishes being served)
```

---

## 2.4 OCI Standards

**OCI = Open Container Initiative** - Industry standards so containers work everywhere.

| Standard              | What It Defines             |
| --------------------- | --------------------------- |
| **Image Spec**        | Format for container images |
| **Runtime Spec**      | How to run containers       |
| **Distribution Spec** | How to push/pull images     |

**Why it matters:** Images built with Docker work with Podman, containerd, CRI-O, etc.

```
OCI-COMPLIANT IMAGES WORK EVERYWHERE:
┌─────────────────────────────────────────────────┐
│  Build with Docker → Run with Podman ✓         │
│  Build with Buildah → Run in Kubernetes ✓      │
│  Push to Docker Hub → Pull on any runtime ✓    │
└─────────────────────────────────────────────────┘
```

---

## 2.5 Docker is Not Always Necessary!

You can build OCI images **without Docker**:

| Tool         | Description                                        |
| ------------ | -------------------------------------------------- |
| **Podman**   | Drop-in Docker replacement, daemonless             |
| **Buildah**  | Build images without running daemon                |
| **kaniko**   | Build in Kubernetes (no Docker socket)             |
| **Buildkit** | Next-gen image builder (used by Docker internally) |

```bash
# Podman works exactly like Docker
podman build -t myapp .
podman run myapp

# Buildah for scriptable builds
buildah from ubuntu
buildah run ubuntu-working-container pip install flask
buildah commit ubuntu-working-container myflask
```

---

## 2.6 Essential Docker Commands

### Getting Help
```bash
docker --help                 # All commands
docker <command> --help       # Specific command help
docker run --help             # Example: run command options
```

### Image Commands
```bash
# List images
docker images
docker image ls

# Pull from registry
docker pull nginx:latest
docker pull python:3.11-slim

# Build image
docker build -t myapp:v1 .
docker build -t myapp:v1 -f Dockerfile.prod .

# Remove image
docker rmi myapp:v1
docker image prune           # Remove unused images

# Tag and push
docker tag myapp:v1 registry.com/myapp:v1
docker push registry.com/myapp:v1
```

### Container Commands
```bash
# Run container
docker run nginx                    # Foreground
docker run -d nginx                 # Background (detached)
docker run -d -p 8080:80 nginx      # Port mapping
docker run -d --name web nginx      # With name

# List containers
docker ps                           # Running only
docker ps -a                        # All (including stopped)

# Stop/Start/Restart
docker stop <container>
docker start <container>
docker restart <container>

# Remove
docker rm <container>
docker rm -f <container>            # Force remove running

# Logs
docker logs <container>
docker logs -f <container>          # Follow (live)
docker logs --tail 100 <container>  # Last 100 lines

# Execute command inside
docker exec -it <container> bash
docker exec <container> ls /app
```

### Inspection Commands
```bash
docker inspect <container>          # Full JSON details
docker stats                        # Live resource usage
docker top <container>              # Processes in container
docker port <container>             # Port mappings
```

---

## 2.7 Hands-On Examples

### Example 1: Run NGINX
```bash
# Pull and run
docker run -d -p 8080:80 --name myweb nginx

# Test
curl http://localhost:8080

# View logs
docker logs myweb

# Stop and remove
docker stop myweb
docker rm myweb
```

### Example 2: Interactive Python
```bash
# Run Python interactively
docker run -it python:3.11 python

# Inside Python shell:
>>> print("Hello from container!")
>>> exit()
```

### Example 3: Run with Environment Variables
```bash
docker run -d \
  -e DATABASE_URL=postgres://db:5432 \
  -e DEBUG=true \
  --name myapp \
  myapp:v1
```

---

**Next:** [Part 3: Writing Dockerfiles](./03-dockerfiles.md)
