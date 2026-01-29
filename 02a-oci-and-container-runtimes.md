# OCI Standards and Container Runtimes

Understanding the standards that power modern containerization.

---

## Table of Contents

1. [Introduction](#introduction)
2. [What is OCI?](#what-is-oci)
3. [OCI Image Specification](#oci-image-specification)
4. [OCI Runtime Specification](#oci-runtime-specification)
5. [Container Runtime Hierarchy](#container-runtime-hierarchy)
6. [What is containerd?](#what-is-containerd)
7. [Docker vs containerd Architecture](#docker-vs-containerd-architecture)
8. [Why Kubernetes Uses containerd](#why-kubernetes-uses-containerd)
9. [Practical Demo with containerd](#practical-demo-with-containerd)

---

## Introduction

When Docker became popular, it was the only major player. But what happens if Docker disappears? How do we ensure containers work everywhere?

**Answer: Standards**

Just like HTML is a standard (not owned by any single browser), **OCI creates standards** for containers so any tool can work with any container.

---

## What is OCI?

**OCI = Open Container Initiative**

Founded in 2015 by Docker, CoreOS, Google, and others to create open industry standards.

```
┌──────────────────────────────────────────────────────────────────┐
│                  OPEN CONTAINER INITIATIVE (OCI)                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Goal: Define open standards for containers                      │
│                                                                  │
│  Two Main Specifications:                                        │
│  ┌────────────────────────────────────────────────┐             │
│  │  1. IMAGE SPEC                                 │             │
│  │     How to package containers?                 │             │
│  │     Format of container images                 │             │
│  └────────────────────────────────────────────────┘             │
│                                                                  │
│  ┌────────────────────────────────────────────────┐             │
│  │  2. RUNTIME SPEC                               │             │
│  │     How to run containers?                     │             │
│  │     Standardized container lifecycle           │             │
│  └────────────────────────────────────────────────┘             │
│                                                                  │
│  Why It Matters:                                                 │
│  • Any OCI-compliant tool can run any OCI image                  │
│  • Docker images work in Podman, containerd, CRI-O               │
│  • No vendor lock-in                                             │
│  • Innovation without breaking compatibility                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```


```
OCI ensures:
• Any container image works with any OCI runtime
• Build once, run anywhere (truly!)
```

---

## OCI Image Specification

### What is a Container Image?

A container image is a **packaged bundle** containing everything needed to run an application.

### OCI Image Format

```
┌──────────────────────────────────────────────────────────────────┐
│                    OCI IMAGE STRUCTURE                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Container Image = Layers + Configuration + Manifest             │
│                                                                  │
│  ┌────────────────────────────────────────────────┐             │
│  │  1. IMAGE LAYERS (Filesystem content)          │             │
│  │  ┌──────────────────────────────────────────┐  │             │
│  │  │  Layer 1: Base OS files (tar.gz)         │  │             │
│  │  │  • /bin/bash, /usr/lib/, etc.            │  │             │
│  │  ├──────────────────────────────────────────┤  │             │
│  │  │  Layer 2: Python runtime                 │  │             │
│  │  │  • /usr/bin/python3.10                   │  │             │
│  │  ├──────────────────────────────────────────┤  │             │
│  │  │  Layer 3: Application dependencies       │  │             │
│  │  │  • /usr/local/lib/python3.10/            │  │             │
│  │  ├──────────────────────────────────────────┤  │             │
│  │  │  Layer 4: Application code               │  │             │
│  │  │  • /app/server.py                        │  │             │
│  │  └──────────────────────────────────────────┘  │             │
│  └────────────────────────────────────────────────┘             │
│                                                                  │
│  ┌────────────────────────────────────────────────┐             │
│  │  2. IMAGE CONFIGURATION (JSON)                 │             │
│  │  {                                             │             │
│  │    "architecture": "amd64",                    │             │
│  │    "os": "linux",                              │             │
│  │    "config": {                                 │             │
│  │      "Cmd": ["python", "server.py"],           │             │
│  │      "Env": ["PATH=/usr/bin"],                 │             │
│  │      "WorkingDir": "/app"                      │             │
│  │    }                                           │             │
│  │  }                                             │             │
│  └────────────────────────────────────────────────┘             │
│                                                                  │
│  ┌────────────────────────────────────────────────┐             │
│  │  3. MANIFEST (Image Metadata)                  │             │
│  │  {                                             │             │
│  │    "mediaType": "application/vnd.oci.image...",│             │
│  │    "config": {                                 │             │
│  │      "digest": "sha256:abc123...",             │             │
│  │       "size": 1234                             │             │
│  │    },                                          │             │
│  │    "layers": [                                 │             │
│  │      {"digest": "sha256:def456..."},           │             │
│  │      {"digest": "sha256:ghi789..."}            │             │
│  │    ]                                           │             │
│  │  }                                             │             │
│  └────────────────────────────────────────────────┘             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Key Points

- **Layers are immutable**: Never changes, identified by SHA256 hash
- **Layers are reusable**: Same layer used across multiple images
- **Content-addressed**: Each layer has unique cryptographic hash
- **Portable**: Works across different container runtimes

---

## OCI Runtime Specification

Defines HOW to run a container from an image.

### Container Lifecycle

```
┌──────────────────────────────────────────────────────────────────┐
│                  OCI RUNTIME SPECIFICATION                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Standard Container Lifecycle:                                   │
│                                                                  │
│  1. CREATE                                                       │
│     ├─ Unpack image layers                                      │
│     ├─ Setup filesystem (overlayFS)                             │
│     ├─ Create namespaces (PID, network, mount, etc.)            │
│     ├─ Configure cgroups (CPU, memory limits)                   │
│     └─ Prepare container environment                            │
│                                                                  │
│  2. START                                                        │
│     ├─ Execute container process                                │
│     └─ Container is now RUNNING                                 │
│                                                                  │
│  3. RUNNING                                                      │
│     ├─ Process executes inside container                        │
│     ├─ Monitored by runtime                                     │
│     └─ Resource usage tracked                                    │
│                                                                  │
│  4. STOP                                                         │
│     ├─ Send SIGTERM to process                                  │
│     ├─ Wait for graceful shutdown                               │
│     └─ Send SIGKILL if timeout                                  │
│                                                                  │
│  5. DELETE                                                       │
│     ├─ Cleanup namespaces                                       │
│     ├─ Remove cgroups                                           │
│     └─ Delete container filesystem                              │
│                                                                  │
│  Any OCI-compliant runtime follows this standard lifecycle       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Runtime Configuration

OCI runtime spec defines a `config.json` file:

```json
{
  " ociVersion": "1.0.2",
  "process": {
    "terminal": false,
    "user": { "uid": 0, "gid": 0 },
    "args": ["python", "server.py"],
    "env": ["PATH=/usr/bin", "LANG=en_US.UTF-8"],
    "cwd": "/app"
  },
  "root": {
    "path": "rootfs",
    "readonly": false
  },
  "hostname": "container-1",
  "mounts": [
    {
      "destination": "/data",
      "source": "/host/data",
      "options": ["rbind", "rw"]
    }
  ],
  "linux": {
    "namespaces": [
      { "type": "pid" },
      { "type": "network" },
      { "type": "mount" }
    ],
    "resources": {
      "memory": { "limit": 536870912 },
      "cpu": { "quota": 100000, "period": 100000 }
    }
  }
}
```

**This standardized format ensures any OCI runtime can create the same container.**

---

## Container Runtime Hierarchy

Not all runtimes are created equal. There's a hierarchy.

```
┌──────────────────────────────────────────────────────────────────┐
│              CONTAINER RUNTIME HIERARCHY                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────┐             │
│  │  HIGH-LEVEL RUNTIME                            │             │
│  │  (User-friendly, feature-rich)                 │             │
│  │                                                 │             │
│  │  • Docker                                       │             │
│  │  • Podman                                       │             │
│  │  • containerd                                   │             │
│  │  • CRI-O                                        │             │
│  │                                                 │             │
│  │  Features:                                      │             │
│  │  ├─ Image building                             │             │
│  │  ├─ Image pulling from registry                │             │
│  │  ├─ Networking setup                           │             │
│  │  ├─ Volume management                          │             │
│  │  └─ Image management                           │             │
│  └────────────────────────────────────────────────┘             │
│                       │                                          │
│                       │ Calls                                    │
│                       ▼                                          │
│  ┌────────────────────────────────────────────────┐             │
│  │  LOW-LEVEL RUNTIME (OCI Runtime)               │             │
│  │  (Just runs containers)                        │             │
│  │                                                 │             │
│  │  • runc (reference implementation)              │             │
│  │  • crun (C implementation, faster)              │             │
│  │  • kata-runtime (VM-based containers)           │             │
│  │  • gVisor runsc (sandboxed containers)          │             │
│  │                                                 │             │
│  │  Responsibilities:                              │             │
│  │  ├─ Create namespaces                          │             │
│  │  ├─ Setup cgroups                              │             │
│  │  ├─ Mount filesystem                           │             │
│  │  ├─ Execute container process                  │             │
│  │  └─ Follow OCI runtime spec                    │             │
│  └────────────────────────────────────────────────┘             │
│                       │                                          │
│                       │ Uses                                     │
│                       ▼                                          │
│  ┌────────────────────────────────────────────────┐             │
│  │  LINUX KERNEL                                  │             │
│  │  • Namespaces                                  │             │
│  │  • Cgroups                                     │             │
│  │  • OverlayFS                                   │             │
│  └────────────────────────────────────────────────┘             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Example Flow

```
User runs: docker run nginx

1. Docker (high-level runtime):
   ├─ Pulls nginx image from Docker Hub
   ├─ Unpacks image layers
   ├─ Sets up networking
   ├─ Creates volume mounts
   └─ Calls containerd

2. containerd (high-level runtime):
   ├─ Prepares image for execution
   ├─ Generates OCI config.json
   └─ Calls runc

3. runc (low-level OCI runtime):
   ├─ Reads config.json
   ├─ Creates Linux namespaces
   ├─ Sets up cgroups
   ├─ Mounts filesystem
   └─ Executes nginx process

4. Container is now running!
```

---

## What is containerd?

**containerd** = Industry-standard core container runtime.

```
┌──────────────────────────────────────────────────────────────────┐
│                        CONTAINERD                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Originally:  Part of Docker                                     │
│  Since 2017:  Independent project (CNCF graduated)               │
│                                                                  │
│  What it does:                                                   │
│  ┌────────────────────────────────────────────────┐             │
│  │  containerd Core Functions:                    │             │
│  │                                                 │             │
│  │  1. Image Management                           │             │
│  │     ├─ Pull images from registries             │             │
│  │     ├─ Store images locally                    │             │
│  │     └─ Push images to registries               │             │
│  │                                                 │             │
│  │  2. Container Lifecycle                        │             │
│  │     ├─ Create containers                       │             │
│  │     ├─ Start/Stop containers                   │             │
│  │     └─ Delete containers                       │             │
│  │                                                 │             │
│  │  3. Snapshot Management                        │             │
│  │     ├─ Manage filesystem layers                │             │
│  │     └─ Use overlay filesystem                  │             │
│  │                                                 │             │
│  │  4. Network Namespace Management               │             │
│  │     └─ Setup container networking               │             │
│  │                                                 │             │
│  │  5. OCI Runtime Integration                    │             │
│  │     └─ Calls runc to execute containers        │             │
│  └────────────────────────────────────────────────┘             │
│                                                                  │
│  What it DOESN'T do:                                             │
│  • No image building (use BuildKit or docker build)              │
│  • No user-friendly CLI (use nerdctl or Docker)                  │
│  • No Docker Compose equivalent built-in                         │
│                                                                  │
│  Who uses it:                                                     │
│  • Docker (uses containerd internally)                           │
│  • Kubernetes (directly uses containerd)                         │
│  • AWS Fargate                                                   │
│  • Google Cloud Run                                              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Docker vs containerd Architecture

### Docker Architecture (Full Stack)

```
┌──────────────────────────────────────────────────────────────────┐
│                      DOCKER ARCHITECTURE                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User                                                             │
│   │                                                              │
│   │ docker run nginx                                             │
│   ▼                                                              │
│  ┌────────────────────────────────────────────────┐             │
│  │  Docker CLI                                    │             │
│  │  • User-friendly interface                     │             │
│  │  • docker build, run, pull, push, etc.         │             │
│  └───────────────────┬────────────────────────────┘             │
│                      │ REST API                                  │
│                      ▼                                           │
│  ┌────────────────────────────────────────────────┐             │
│  │  Docker Daemon (dockerd)                       │             │
│  │  • Image building                              │             │
│  │  • Volume management                           │             │
│  │  • Network management                          │             │
│  │  • Docker Compose                              │             │
│  │  • Swarm orchestration                         │             │
│  └───────────────────┬────────────────────────────┘             │
│                      │ gRPC                                      │
│                      ▼                                           │
│  ┌────────────────────────────────────────────────┐             │
│  │  containerd                                    │             │
│  │  • Container lifecycle                         │             │
│  │  • Image management                            │             │
│  │  • Snapshot management                         │             │
│  └───────────────────┬────────────────────────────┘             │
│                      │                                           │
│                      ▼                                           │
│  ┌────────────────────────────────────────────────┐             │
│  │  runc (OCI Runtime)                            │             │
│  │  • Creates namespaces                          │             │
│  │  • Sets up cgroups                             │             │
│  │  • Executes container process                  │             │
│  └────────────────────────────────────────────────┘             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Kubernetes with containerd (Simplified) 

```
┌──────────────────────────────────────────────────────────────────┐
│              KUBERNETES + CONTAINERD (No Docker)                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User                                                             │
│   │                                                              │
│   │ kubectl create deployment nginx                              │
│   ▼                                                              │
│  ┌────────────────────────────────────────────────┐             │
│  │  Kubernetes API Server                         │             │
│  │  • Receives deployment request                 │             │
│  │  • Stores desired state in etcd                │             │
│  └───────────────────┬────────────────────────────┘             │
│                      │                                           │
│                      ▼                                           │
│  ┌────────────────────────────────────────────────┐             │
│  │  kubelet (on worker node)                      │             │
│  │  • Monitors API server                         │             │
│  │  • Creates pods as requested                   │             │
│  └───────────────────┬────────────────────────────┘             │
│                      │ CRI (Container Runtime Interface)         │
│                      ▼                                           │
│  ┌────────────────────────────────────────────────┐             │
│  │  containerd                                    │             │
│  │  • Pull image                                  │             │
│  │  • Create container                            │             │
│  │  • Start container                             │             │
│  └───────────────────┬────────────────────────────┘             │
│                      │                                           │
│                      ▼                                           │
│  ┌────────────────────────────────────────────────┐             │
│  │  runc (OCI Runtime)                            │             │
│  │  • Execute container                           │             │
│  └────────────────────────────────────────────────┘             │
│                                                                  │
│  NOTICE: Docker completely removed!                              │
│          Kubernetes talks to containerd directly                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Key Differences

| Aspect            | Docker                            | Kubernetes + containerd     |
| ----------------- | --------------------------------- | --------------------------- |
| **Layers**        | CLI → dockerd → containerd → runc | kubelet → containerd → runc |
| **Image Build**   | docker build                      | BuildKit, Kaniko, or CI/CD  |
| **CLI**           | docker                            | kubectl + ctr/nerdctl       |
| **Networking**    | Docker networks                   | Kubernetes CNI              |
| **Volumes**       | Docker volumes                    | Kubernetes PVs/PVCs         |
| **Orchestration** | Docker Swarm                      | Kubernetes                  |

---

## Why Kubernetes Uses containerd

###  Docker Deprecation 

```
┌──────────────────────────────────────────────────────────────────┐
│         KUBERNETES REMOVES DOCKER SUPPORT (2020-2022)            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Timeline:                                                        │
│                                                                  │
│  Before 2016:                                                     │
│    Kubernetes → Docker (only option)                             │
│                                                                  │
│  2016:                                                            │
│    Kubernetes introduces CRI (Container Runtime Interface)       │
│    Goal: Support multiple runtimes, not just Docker              │
│                                                                  │
│  2016-2020:                                                       │
│    Multiple runtimes supported:                                  │
│    ├─ Docker (via dockershim - compatibility layer)              │
│    ├─ containerd (direct CRI support)                            │
│    └─ CRI-O (direct CRI support)                                 │
│                                                                  │
│  December 2020:                                                   │
│    Kubernetes announces:                                         │
│    "dockershim is deprecated, will be removed in v1.24"          │
│                                                                  │
│  May 2022:                                                        │
│    Kubernetes v1.24 released                                     │
│    ├─ dockershim removed                                         │
│    └─ Direct Docker support gone                                 │
│                                                                  │
│  Current (2024+):                                                 │
│    Kubernetes uses:                                              │
│    ├─ containerd (most popular)                                  │
│    ├─ CRI-O                                                      │
│    └─ Other CRI-compliant runtimes                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Why Remove Docker?

```
┌──────────────────────────────────────────────────────────────────┐
│            WHY KUBERNETES MOVED AWAY FROM DOCKER                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Problem with Docker in Kubernetes:                              │
│                                                                  │
│  ┌────────────────────────────────────────────────┐             │
│  │  kubelet                                       │             │
│  │   ↓                                            │             │
│  │  dockershim (compatibility layer)  ← Extra!    │             │
│  │   ↓                                            │             │
│  │  Docker Engine                     ← Extra!    │             │
│  │   ↓                                            │             │
│  │  containerd                                    │             │
│  │   ↓                                            │             │
│  │  runc                                           │             │
│  └────────────────────────────────────────────────┘             │
│                                                                  │
│  Issues:                                                         │
│  • Too many layers (complexity)                                  │
│  • Docker includes features K8s doesn't need                     │
│  • Slower than direct containerd                                 │
│  • Additional maintenance burden                                 │
│                                                                  │
│  ┌────────────────────────────────────────────────┐             │
│  │  Solution: Use containerd directly              │             │
│  │                                                 │             │
│  │  kubelet                                        │             │
│  │   ↓ CRI                                        │             │
│  │  containerd                                    │             │
│  │   ↓                                            │             │
│  │  runc                                           │             │
│  └────────────────────────────────────────────────┘             │
│                                                                  │
│  Benefits:                                                        │
│  • Simpler architecture                                          │
│  • Faster container operations                                   │
│  • Less memory usage                                             │
│  • Kubernetes-specific optimizations                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### What This Means for You

**Q: Can I still use Docker images?**  
**A: YES!** Docker images are OCI-compliant. They work with containerd, Podman, CRI-O, etc.

**Q: Can I still use `docker build`?**  
**A: YES!** For local development, Docker is still great. Just know that in production Kubernetes, containerd runs those images.

**Q: Do I need to learn containerd?**  
**A: Not really.** For daily work, kubectl is enough. Understanding the architecture helps.

```
Developer Workflow (unchanged):
├─ Write Dockerfile
├─ docker build -t myapp:v1 .
├─ docker push myapp:v1
└─ kubectl apply -f deployment.yaml

Kubernetes (behind the scenes):
└─ Uses containerd to pull and run myapp:v1
```

---

## Practical Demo with containerd

### Install containerd (Linux)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y containerd

# Start containerd
sudo systemctl start containerd
sudo systemctl enable containerd
```

### Using containerd directly

containerd doesn't have a user-friendly CLI like Docker. Use `ctr` (basic) or `nerdctl` (Docker-like).

#### With ctr (basic CLI)

```bash
# Pull an image
sudo ctr image pull docker.io/library/nginx:latest

# List images
sudo ctr image ls

# Run a container (basic, foreground)
sudo ctr run --rm docker.io/library/nginx:latest my-nginx

# This is very basic - missing many Docker features!
```

####  With nerdctl (Docker-compatible CLI)

```bash
# Install nerdctl
# Download from: https://github.com/containerd/nerdctl/releases

# Pull image
nerdctl pull nginx:latest

# Run container (same as Docker!)
nerdctl run -d -p 8080:80 --name web nginx:latest

# List containers
nerdctl ps

# Stop container
nerdctl stop web

# Remove container
nerdctl rm web
```

### Inspect containerd Architecture

```bash
# Check containerd is running
sudo systemctl status containerd

# View containerd config
sudo cat /etc/containerd/config.toml

# See containerd process
ps aux | grep containerd

# When you run a container, you'll also see:
ps aux | grep runc
# runc is the actual process executor
```

### Compare: Docker vs nerdctl + containerd

```bash
# Docker command:
docker run -d -p 8080:80 nginx

# Equivalent nerdctl command:
nerdctl run -d -p 8080:80 nginx

# Behind the scenes:
# Docker: docker CLI → dockerd → containerd → runc
# nerdctl: nerdctl → containerd → runc
```

---

## Summary

### Key Takeaways

**OCI (Open Container Initiative)**:
- Creates open standards for containers
- Image Spec: How to package containers
- Runtime Spec: How to run containers
- Ensures portability and interoperability

**Container Runtime Hierarchy**:
1. **High-level**: Docker, Podman, containerd (feature-rich)
2. **Low-level**: runc (OCI runtime, just executes)
3. **Kernel**: Namespaces + cgroups (isolation)

**containerd**:
- Core container runtime
- Used by Docker internally
- Used directly by Kubernetes
- Industry standard (CNCF project)

**Why Kubernetes Dropped Docker**:
- Too many layers (dockerd was extra)
- containerd is enough
- Faster, simpler, more efficient
- **But** Docker images still work!

### The Big Picture

```
You (developer):
├─ Write Dockerfile
├─ docker build (local dev)
└─ Push to registry

Production (Kubernetes):
├─ Pulls OCI-compliant image
├─ Uses containerd to run it
└─ runc creates actual container

Result:
Your Docker image runs perfectly in Kubernetes,
even though Kubernetes doesn't use Docker!
```

