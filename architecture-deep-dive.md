# Docker & Kubernetes Architecture Deep Dive

Complete guide to understanding Docker and Kubernetes architecture, component interactions, and workflows.

---

## Table of Contents

1. [Docker Architecture](#docker-architecture)
   - [Linux Architecture](#docker-on-linux)
   - [Windows Architecture](#docker-on-windows)
   - [Complete Docker Flow](#complete-docker-flow)
2. [Kubernetes Architecture](#kubernetes-architecture)
   - [Control Plane Components](#control-plane-components)
   - [Worker Node Components](#worker-node-components)
   - [Complete K8s Flow](#complete-kubernetes-flow)
3. [Real-World Examples](#real-world-examples)

---

## Docker Architecture

### Docker on Linux

#### Complete Component Stack

```
┌─────────────────────────────────────────────────────────────┐
│                 DOCKER ON LINUX - FULL STACK                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: USER INTERACTION                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │ $ docker run -p 8080:80 nginx                      │    │
│  │ $ docker build -t myapp .                          │    │
│  │ $ docker ps                                        │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Layer 2: DOCKER CLIENT (CLI)                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │ /usr/bin/docker                                    │    │
│  │ • Parses commands                                  │    │
│  │ • Validates syntax                                 │    │
│  │ • Sends REST API calls                             │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│                    REST API (HTTP)                          │
│              unix:///var/run/docker.sock                    │
│                          ↓                                  │
│  Layer 3: DOCKER DAEMON (dockerd)                           │
│  ┌────────────────────────────────────────────────────┐    │
│  │ /usr/bin/dockerd                                   │    │
│  │ • API Server                                       │    │
│  │ • Image management                                 │    │
│  │ • Network management                               │    │
│  │ • Volume management                                │    │
│  │ • Authentication                                   │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│                     gRPC calls                              │
│                          ↓                                  │
│  Layer 4: CONTAINERD                                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ /usr/bin/containerd                                │    │
│  │ • Container lifecycle management                   │    │
│  │ • Image pull/push                                  │    │
│  │ • Container storage                                │    │
│  │ • Snapshots                                        │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│                   Creates shims                             │
│                          ↓                                  │
│  Layer 5: CONTAINERD-SHIM                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │ /usr/bin/containerd-shim-runc-v2                   │    │
│  │ • One per container                                │    │
│  │ • Keeps STDIO open                                 │    │
│  │ • Reports exit status                              │    │
│  │ • Daemonless containers                            │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│                     Executes                                │
│                          ↓                                  │
│  Layer 6: RUNC (OCI Runtime)                                │
│  ┌────────────────────────────────────────────────────┐    │
│  │ /usr/bin/runc                                      │    │
│  │ • Creates namespaces                               │    │
│  │ • Configures cgroups                               │    │
│  │ • Sets up rootfs                                   │    │
│  │ • Executes container process                       │    │
│  │ • Exits after start                                │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Layer 7: LINUX KERNEL                                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Namespaces:                                        │    │
│  │ ├── PID namespace (process isolation)             │    │
│  │ ├── NET namespace (network isolation)             │    │
│  │ ├── MNT namespace (filesystem isolation)          │    │
│  │ ├── UTS namespace (hostname isolation)            │    │
│  │ ├── IPC namespace (IPC isolation)                 │    │
│  │ └── USER namespace (user isolation)               │    │
│  │                                                    │    │
│  │ Cgroups:                                           │    │
│  │ ├── CPU limits                                     │    │
│  │ ├── Memory limits                                  │    │
│  │ ├── Block I/O limits                               │    │
│  │ └── Network I/O limits                             │    │
│  │                                                    │    │
│  │ Union Filesystem (OverlayFS):                      │    │
│  │ ├── Lower layers (image layers - read-only)       │    │
│  │ └── Upper layer (container layer - writable)      │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Layer 8: RUNNING CONTAINER                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │ nginx process (PID 1 in container)                 │    │
│  │ • Isolated process tree                           │    │
│  │ • Isolated network                                │    │
│  │ • Isolated filesystem                             │    │
│  │ • Resource limited                                │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Docker on Windows

#### Complete Component Stack

```
┌─────────────────────────────────────────────────────────────┐
│               DOCKER ON WINDOWS - FULL STACK                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TWO MODES: Linux Containers & Windows Containers           │
│                                                             │
│  ═══════════════════════════════════════════════════════    │
│  MODE 1: LINUX CONTAINERS (Default, Most Common)            │
│  ═══════════════════════════════════════════════════════    │
│                                                             │
│  Layer 1: USER INTERACTION                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │ PS> docker run -p 8080:80 nginx                    │    │
│  │ (PowerShell or CMD)                                │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Layer 2: DOCKER CLIENT (Windows binary)                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ C:\Program Files\Docker\docker.exe                 │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│               Named Pipe or TCP                             │
│         \\.\pipe\docker_engine                              │
│                          ↓                                  │
│  Layer 3: DOCKER DESKTOP (Windows Service)                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Docker Desktop                                     │    │
│  │ • Manages WSL 2 / Hyper-V                          │    │
│  │ • Runs Docker daemon inside VM                     │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Layer 4: WSL 2 (Windows Subsystem for Linux)               │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Lightweight VM running Linux kernel                │    │
│  │ ┌────────────────────────────────────────────────┐ │    │
│  │ │  LINUX ENVIRONMENT                             │ │    │
│  │ │  ├── dockerd                                   │ │    │
│  │ │  ├── containerd                                │ │    │
│  │ │  ├── runc                                      │ │    │
│  │ │  └── Linux kernel (Microsoft's custom)        │ │    │
│  │ │                                                │ │    │
│  │ │  Container runs exactly like on Linux!         │ │    │
│  │ └────────────────────────────────────────────────┘ │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  ═══════════════════════════════════════════════════════    │
│  MODE 2: WINDOWS CONTAINERS (Less Common)                   │
│  ═══════════════════════════════════════════════════════    │
│                                                             │
│  Layer 1-3: Same as above                                   │
│                          ↓                                  │
│  Layer 4: WINDOWS KERNEL (No VM needed!)                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Windows Server Core / Nano Server                  │    │
│  │                                                    │    │
│  │ Windows Isolation Features:                        │    │
│  │ ├── Job Objects (process isolation)               │    │
│  │ ├── Object Namespace (filesystem isolation)       │    │
│  │ ├── Network Compartments (network isolation)      │    │
│  │ └── Silo (resource isolation)                     │    │
│  │                                                    │    │
│  │ Note: Can only run Windows-based images!           │    │
│  │ (e.g., mcr.microsoft.com/windows/servercore)       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Complete Docker Flow: docker run nginx

#### Step-by-Step Execution

```
┌─────────────────────────────────────────────────────────────┐
│         COMPLETE FLOW: docker run -p 8080:80 nginx          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: User Command                                       │
│  $ docker run -p 8080:80 nginx                              │
│         ↓                                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Docker CLI validates:                              │    │
│  │ ✓ Syntax correct                                   │    │
│  │ ✓ Flags valid (-p 8080:80)                         │    │
│  │ ✓ Image name valid (nginx)                         │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 2: Send API Request                                   │
│  POST /containers/create                                    │
│  {                                                          │
│    "Image": "nginx",                                        │
│    "HostConfig": {                                          │
│      "PortBindings": {"80/tcp": [{"HostPort": "8080"}]}    │
│    }                                                        │
│  }                                                          │
│         ↓                                                   │
│  STEP 3: Docker Daemon Processes                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │ dockerd receives request                           │    │
│  │                                                    │    │
│  │ 3a. Check if image exists locally                  │    │
│  │     ├─ Search: /var/lib/docker/overlay2/           │    │
│  │     └─ Not found!                                  │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 4: Pull Image (if not local)                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │ dockerd → containerd: "Pull nginx:latest"          │    │
│  │                                                    │    │
│  │ containerd contacts Docker Hub:                    │    │
│  │ ├─ GET https://registry-1.docker.io/v2/           │    │
│  │ ├─ GET /library/nginx/manifests/latest            │    │
│  │ ├─ Download layer 1 (sha256:a1b2c3...)            │    │
│  │ ├─ Download layer 2 (sha256:d4e5f6...)            │    │
│  │ ├─ Download layer 3 (sha256:g7h8i9...)            │    │
│  │ └─ Extract to: /var/lib/containerd/               │    │
│  │                                                    │    │
│  │ Image stored as OCI format                         │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 5: Create Container Filesystem                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ containerd creates OverlayFS mount:                │    │
│  │                                                    │    │
│  │ Lower (read-only layers):                          │    │
│  │ ├─ Layer 1: Base Ubuntu filesystem                │    │
│  │ ├─ Layer 2: nginx installation                    │    │
│  │ └─ Layer 3: nginx config                          │    │
│  │                                                    │    │
│  │ Upper (writable layer):                            │    │
│  │ └─ /var/lib/docker/overlay2/<container-id>/       │    │
│  │                                                    │    │
│  │ Merged view mounted at:                            │    │
│  │ /var/lib/docker/overlay2/<container-id>/merged    │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 6: containerd Creates Container Config                │
│  ┌────────────────────────────────────────────────────┐    │
│  │ OCI Runtime Spec (config.json):                    │    │
│  │ {                                                  │    │
│  │   "process": {                                     │    │
│  │     "args": ["nginx", "-g", "daemon off;"]        │    │
│  │   },                                               │    │
│  │   "root": {                                        │    │
│  │     "path": "/overlay2/.../merged"                │    │
│  │   },                                               │    │
│  │   "linux": {                                       │    │
│  │     "namespaces": [                                │    │
│  │       {"type": "pid"},                             │    │
│  │       {"type": "network"},                         │    │
│  │       {"type": "mount"}                            │    │
│  │     ],                                             │    │
│  │     "resources": {                                 │    │
│  │       "memory": {"limit": -1},                     │    │
│  │       "cpu": {"shares": 1024}                      │    │
│  │     }                                              │    │
│  │   }                                                │    │
│  │ }                                                  │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 7: containerd-shim Spawned                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │ containerd spawns shim process:                    │    │
│  │ $ containerd-shim-runc-v2 \                        │    │
│  │     -namespace moby \                               │    │
│  │     -id abc123 \                                    │    │
│  │     -address /run/containerd/containerd.sock       │    │
│  │                                                    │    │
│  │ Shim responsibilities:                             │    │
│  │ ├─ Call runc to start container                   │    │
│  │ ├─ Keep STDIO streams open                         │    │
│  │ ├─ Report container status                         │    │
│  │ └─ Allow containerd to restart without killing    │    │
│  │    containers                                      │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 8: runc Creates Namespaces & Cgroups                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │ runc system calls:                                 │    │
│  │                                                    │    │
│  │ 1. Create PID namespace:                           │    │
│  │    unshare(CLONE_NEWPID)                           │    │
│  │                                                    │    │
│  │ 2. Create Network namespace:                       │    │
│  │    unshare(CLONE_NEWNET)                           │    │
│  │    ├─ Create veth pair                             │    │
│  │    ├─ Attach one end to docker0 bridge            │    │
│  │    └─ Give container IP: 172.17.0.2               │    │
│  │                                                    │    │
│  │ 3. Create Mount namespace:                         │    │
│  │    unshare(CLONE_NEWNS)                            │    │
│  │    ├─ Mount overlayfs as /                        │    │
│  │    └─ Mount proc, sys, dev                        │    │
│  │                                                    │    │
│  │ 4. Create Cgroups:                                 │    │
│  │    /sys/fs/cgroup/memory/docker/abc123/           │    │
│  │    /sys/fs/cgroup/cpu/docker/abc123/              │    │
│  │                                                    │    │
│  │ 5. Port mapping (iptables):                        │    │
│  │    iptables -t nat -A DOCKER \                     │    │
│  │      -p tcp --dport 8080 \                         │    │
│  │      -j DNAT --to 172.17.0.2:80                    │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 9: Execute Container Process                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │ runc executes:                                     │    │
│  │ $ nginx -g "daemon off;"                           │    │
│  │                                                    │    │
│  │ Inside container:                                  │    │
│  │ ├─ PID 1: nginx master                            │    │
│  │ └─ PID 6: nginx worker                            │    │
│  │                                                    │    │
│  │ From host perspective:                             │    │
│  │ ├─ PID 12345: nginx master (in namespace)         │    │
│  │ └─ PID 12346: nginx worker (in namespace)         │    │
│  │                                                    │    │
│  │ runc exits (job done)                              │    │
│  │ shim remains, monitoring the process               │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 10: Container Running                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │ $ docker ps                                        │    │
│  │ CONTAINER ID   IMAGE   COMMAND        PORTS        │    │
│  │ abc123         nginx   "nginx -g..."  8080->80     │    │
│  │                                                    │    │
│  │ Container accessible at:                           │    │
│  │ http://localhost:8080                              │    │
│  │                                                    │    │
│  │ Host:8080 → iptables → Container:80 → nginx       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Kubernetes Architecture

### Complete Cluster Components

```
┌─────────────────────────────────────────────────────────────┐
│            KUBERNETES CLUSTER ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  CONTROL PLANE (Master Node)         │  │
│  │                                                      │  │
│  │  ┌───────────────────────────────────────────────┐  │  │
│  │  │ kube-apiserver                                │  │  │
│  │  │ • RESTful API (HTTPS, port 6443)              │  │  │
│  │  │ • Authentication & Authorization              │  │  │
│  │  │ • Validates requests                          │  │  │
│  │  │ • Only component that talks to etcd           │  │  │
│  │  │ • Stateless (can have multiple instances)     │  │  │
│  │  └───────────────────────────────────────────────┘  │  │
│  │         ↕                  ↕                         │  │
│  │  ┌──────────────┐   ┌──────────────────────────┐   │  │
│  │  │ etcd         │   │ kube-scheduler           │   │  │
│  │  │              │   │                          │   │  │
│  │  │ • Key-value  │   │ • Watches for new pods   │   │  │
│  │  │   database   │   │ • Finds best node        │   │  │
│  │  │ • Cluster    │   │ • Considers:             │   │  │
│  │  │   state      │   │   - Resources            │   │  │
│  │  │ • Config     │   │   - Affinity             │   │  │
│  │  │ • Secrets    │   │   - Constraints          │   │  │
│  │  │ • Port 2379  │   │ • Assigns pod to node    │   │  │
│  │  └──────────────┘   └──────────────────────────┘   │  │
│  │         ↕                                            │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │ kube-controller-manager                      │   │  │
│  │  │                                              │   │  │
│  │  │ Runs controllers:                            │   │  │
│  │  │ ├─ Node Controller (monitors nodes)          │   │  │
│  │  │ ├─ Replication Controller (maintain replicas)│   │  │
│  │  │ ├─ Endpoints Controller (populates endpoints)│   │  │
│  │  │ ├─ Service Account Controller (create SA)    │   │  │
│  │  │ └─ Job Controller (run jobs to completion)   │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  │         ↕                                            │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │ cloud-controller-manager (optional)          │   │  │
│  │  │ • Cloud-specific control logic               │   │  │
│  │  │ • Node lifecycle                             │   │  │
│  │  │ • LoadBalancer provisioning                  │   │  │
│  │  │ • Volume creation (cloud disks)              │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│                    HTTPS / kubectl                          │
│                          ↕                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               WORKER NODES (Multiple)                │  │
│  │                                                      │  │
│  │  Node 1                  Node 2                      │  │
│  │  ┌──────────────────┐   ┌──────────────────┐        │  │
│  │  │ kubelet          │   │ kubelet          │        │  │
│  │  │ • Pod lifecycle  │   │ • Pod lifecycle  │        │  │
│  │  │ • Talks to       │   │ • Talks to       │        │  │
│  │  │   apiserver      │   │   apiserver      │        │  │
│  │  │ • Uses CRI to    │   │ • Uses CRI to    │        │  │
│  │  │   manage pods    │   │   manage pods    │        │  │
│  │  │ • Port 10250     │   │ • Port 10250     │        │  │
│  │  └────────┬─────────┘   └────────┬─────────┘        │  │
│  │           ↕                      ↕                   │  │
│  │  ┌────────────────────┐ ┌────────────────────┐      │  │
│  │  │ Container Runtime  │ │ Container Runtime  │      │  │
│  │  │ (containerd/CRI-O) │ │ (containerd/CRI-O) │      │  │
│  │  │                    │ │                    │      │  │
│  │  │ ├─ Pod 1           │ │ ├─ Pod 3           │      │  │
│  │  │ │  └─ Container A  │ │ │  └─ Container E  │      │  │
│  │  │ │  └─ Container B  │ │ │  └─ Container F  │      │  │
│  │  │ └─ Pod 2           │ │ └─ Pod 4           │      │  │
│  │  │    └─ Container C  │ │    └─ Container G  │      │  │
│  │  │    └─ Container D  │ │    └─ Container H  │      │  │
│  │  └────────────────────┘ └────────────────────┘      │  │
│  │           ↕                      ↕                   │  │
│  │  ┌────────────────────┐ ┌────────────────────┐      │  │
│  │  │ kube-proxy         │ │ kube-proxy         │      │  │
│  │  │ • Maintains        │ │ • Maintains        │      │  │
│  │  │   network rules    │ │   network rules    │      │  │
│  │  │ • Service          │ │ • Service          │      │  │
│  │  │   load balancing   │ │   load balancing   │      │  │
│  │  │ • Uses iptables    │ │ • Uses iptables    │      │  │
│  │  │   or IPVS          │ │   or IPVS          │      │  │
│  │  └────────────────────┘ └────────────────────┘      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Complete Kubernetes Flow: Create Deployment

```
┌─────────────────────────────────────────────────────────────┐
│      COMPLETE FLOW: kubectl create deployment nginx         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: User Command                                       │
│  $ kubectl create deployment nginx --image=nginx --replicas=3│
│         ↓                                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │ kubectl CLI:                                       │    │
│  │ 1. Reads ~/.kube/config                            │    │
│  │ 2. Finds cluster API server URL                    │    │
│  │ 3. Loads authentication cert                       │    │
│  │ 4. Constructs API request                          │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 2: API Request to Control Plane                       │
│  POST https://master:6443/apis/apps/v1/namespaces/default/deployments│
│  Authorization: Bearer <token>                              │
│  {                                                          │
│    "metadata": {"name": "nginx"},                           │
│    "spec": {                                                │
│      "replicas": 3,                                         │
│      "selector": {"matchLabels": {"app": "nginx"}},         │
│      "template": {                                          │
│        "metadata": {"labels": {"app": "nginx"}},            │
│        "spec": {                                            │
│          "containers": [{                                   │
│            "name": "nginx",                                 │
│            "image": "nginx"                                 │
│          }]                                                 │
│        }                                                    │
│      }                                                      │
│    }                                                        │
│  }                                                          │
│         ↓                                                   │
│  STEP 3: API Server Processes                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │ kube-apiserver:                                    │    │
│  │                                                    │    │
│  │ 1. Authentication:                                 │    │
│  │    ✓ Verify client certificate                    │    │
│  │    ✓ Check token validity                         │    │
│  │                                                    │    │
│  │ 2. Authorization (RBAC):                           │    │
│  │    ✓ Can user create deployments?                 │    │
│  │    ✓ Check ClusterRole/Role bindings              │    │
│  │    ✓ Authorized!                                   │    │
│  │                                                    │    │
│  │ 3. Admission Control:                              │    │
│  │    ✓ MutatingAdmissionWebhook                      │    │
│  │    ✓ ValidatingAdmissionWebhook                    │    │
│  │    ✓ ResourceQuota check                           │    │
│  │    ✓ LimitRanger                                   │    │
│  │                                                    │    │
│  │ 4. Schema Validation:                              │    │
│  │    ✓ Is this valid YAML/JSON?                      │    │
│  │    ✓ All required fields present?                  │    │
│  │                                                    │    │
│  │ 5. Write to etcd:                                  │    │
│  │    Key: /registry/deployments/default/nginx        │    │
│  │    Value: <deployment JSON>                        │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 4: Deployment Controller Watches                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │ kube-controller-manager:                           │    │
│  │                                                    │    │
│  │ Deployment Controller:                             │    │
│  │ • Watches apiserver for new deployments            │    │
│  │ • Sees: New deployment "nginx" with replicas=3     │    │
│  │                                                    │    │
│  │ Controller logic:                                  │    │
│  │ ├─ Current state: 0 ReplicaSets                   │    │
│  │ ├─ Desired state: 1 ReplicaSet with 3 replicas    │    │
│  │ └─ Action: Create ReplicaSet                       │    │
│  │                                                    │    │
│  │ Creates ReplicaSet via API call:                   │    │
│  │ POST /apis/apps/v1/namespaces/default/replicasets  │    │
│  │ {                                                  │    │
│  │   "metadata": {"name": "nginx-abc123"},            │    │
│  │   "spec": {                                        │    │
│  │     "replicas": 3,                                 │    │
│  │     "selector": {"matchLabels": {"app": "nginx"}}, │    │
│  │     "template": <pod template>                     │    │
│  │   }                                                │    │
│  │ }                                                  │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 5: ReplicaSet Controller Watches                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ReplicaSet Controller:                             │    │
│  │ • Sees new ReplicaSet "nginx-abc123"               │    │
│  │ • Current pods: 0                                  │    │
│  │ • Desired pods: 3                                  │    │
│  │                                                    │    │
│  │ Creates 3 Pod objects via API:                     │    │
│  │ POST /api/v1/namespaces/default/pods (x3)          │    │
│  │ {                                                  │    │
│  │   "metadata": {                                    │    │
│  │     "name": "nginx-abc123-xyz01",                  │    │
│  │     "labels": {"app": "nginx"}                     │    │
│  │   },                                               │    │
│  │   "spec": {                                        │    │
│  │     "containers": [{                               │    │
│  │       "name": "nginx",                             │    │
│  │       "image": "nginx"                             │    │
│  │     }]                                             │    │
│  │   }                                                │    │
│  │ }                                                  │    │
│  │                                                    │    │
│  │ Pods written to etcd with status: Pending          │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 6: Scheduler Assigns Nodes                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │ kube-scheduler:                                    │    │
│  │                                                    │    │
│  │ For each pod "nginx-abc123-xyz01":                 │    │
│  │                                                    │    │
│  │ Phase 1: Filtering (find feasible nodes)          │    │
│  │ ├─ Node1: 2 CPU available, 4GB RAM ✓              │    │
│  │ ├─ Node2: 4 CPU available, 8GB RAM ✓              │    │
│  │ └─ Node3: 0 CPU available (busy) ✗                │    │
│  │                                                    │    │
│  │ Phase 2: Scoring (rank nodes)                      │    │
│  │ ├─ Node1: Score 75 (moderate resources)           │    │
│  │ └─ Node2: Score 95 (lots of resources)            │    │
│  │                                                    │    │
│  │ Decision: Assign pod to Node2                      │    │
│  │                                                    │    │
│  │ Updates Pod via API:                               │    │
│  │ PATCH /api/v1/namespaces/default/pods/nginx-xyz01  │    │
│  │ {"spec": {"nodeName": "node2"}}                    │    │
│  │                                                    │    │
│  │ Pod status: Pending → Assigned to node2            │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 7: kubelet on Node2 Takes Over                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ kubelet (on node2):                                │    │
│  │                                                    │    │
│  │ • Watches API for pods assigned to "node2"         │    │
│  │ • Sees new pod: "nginx-abc123-xyz01"               │    │
│  │                                                    │    │
│  │ 7a. Pull image (if not cached):                    │    │
│  │     Talks to containerd → pulls nginx from         │    │
│  │     Docker Hub                                     │    │
│  │                                                    │    │
│  │ 7b. Create pod sandbox:                            │    │
│  │     CRI call: RunPodSandbox                        │    │
│  │     ├─ Create pause container (infra container)   │    │
│  │     ├─ Setup network namespace                     │    │
│  │     ├─ Allocate IP: 10.244.2.5                     │    │
│  │     └─ Setup cgroup                                │    │
│  │                                                    │    │
│  │ 7c. Start containers:                              │    │
│  │     CRI call: CreateContainer                      │    │
│  │     CRI call: StartContainer                       │    │
│  │     ├─ containerd creates container                │    │
│  │     └─ Shares network namespace with pause         │    │
│  │                                                    │    │
│  │ 7d. Update pod status:                             │    │
│  │     PATCH /api/v1/.../pods/nginx-xyz01/status      │    │
│  │     {"status": {"phase": "Running"}}               │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 8: Networking Setup (CNI)                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Container Network Interface (e.g., Calico):        │    │
│  │                                                    │    │
│  │ • Creates veth pair                                │    │
│  │ • One end in pod namespace (eth0)                  │    │
│  │ • Other end on node                                │    │
│  │ • Configures routes across nodes                   │    │
│  │ • Pod can now communicate cluster-wide             │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 9: All 3 Pods Running                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Final State:                                       │    │
│  │                                                    │    │
│  │ Node1: nginx-abc123-xyz01 (10.244.1.5)            │    │
│  │ Node2: nginx-abc123-xyz02 (10.244.2.5)            │    │
│  │ Node2: nginx-abc123-xyz03 (10.244.2.6)            │    │
│  │                                                    │    │
│  │ All pods: status=Running                           │    │
│  │                                                    │    │
│  │ $ kubectl get pods                                 │    │
│  │ NAME                    READY   STATUS    IP          │    │
│  │ nginx-abc123-xyz01      1/1     Running   10.244.1.5 │    │
│  │ nginx-abc123-xyz02      1/1     Running   10.244.2.5 │    │
│  │ nginx-abc123-xyz03      1/1     Running   10.244.2.6 │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Service Creation and Traffic Flow

```
┌─────────────────────────────────────────────────────────────┐
│      COMPLETE FLOW: kubectl expose deployment nginx         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: Create Service                                     │
│  $ kubectl expose deployment nginx --port=80 --type=ClusterIP│
│         ↓                                                   │
│  STEP 2: API Server Creates Service Object                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Service written to etcd:                           │    │
│  │ {                                                  │    │
│  │   "metadata": {"name": "nginx"},                   │    │
│  │   "spec": {                                        │    │
│  │     "selector": {"app": "nginx"},                  │    │
│  │     "ports": [{"port": 80, "targetPort": 80}],     │    │
│  │     "type": "ClusterIP"                            │    │
│  │   },                                               │    │
│  │   "status": {                                      │    │
│  │     "clusterIP": "10.96.100.50"  // Auto-assigned  │    │
│  │   }                                                │    │
│  │ }                                                  │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 3: Endpoints Controller Creates Endpoints             │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Endpoints Controller:                              │    │
│  │ • Finds all pods matching selector "app=nginx"     │    │
│  │ • Creates Endpoints object:                        │    │
│  │   {                                                │    │
│  │     "subsets": [{                                  │    │
│  │       "addresses": [                               │    │
│  │         {"ip": "10.244.1.5", "nodeName": "node1"}, │    │
│  │         {"ip": "10.244.2.5", "nodeName": "node2"}, │    │
│  │         {"ip": "10.244.2.6", "nodeName": "node2"}  │    │
│  │       ],                                           │    │
│  │       "ports": [{"port": 80}]                      │    │
│  │     }]                                             │    │
│  │   }                                                │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 4: kube-proxy Updates iptables (on all nodes)         │
│  ┌────────────────────────────────────────────────────┐    │
│  │ kube-proxy on each node:                           │    │
│  │                                                    │    │
│  │ Creates iptables rules:                            │    │
│  │                                                    │    │
│  │ # Intercept traffic to ClusterIP                   │    │
│  │ iptables -t nat -A KUBE-SERVICES \                 │    │
│  │   -d 10.96.100.50 -p tcp --dport 80 \              │    │
│  │   -j KUBE-SVC-NGINX                                │    │
│  │                                                    │    │
│  │ # Load balance to 3 pod IPs (33% each)             │    │
│  │ iptables -t nat -A KUBE-SVC-NGINX \                │    │
│  │   -m statistic --mode random --probability 0.33 \   │    │
│  │   -j DNAT --to 10.244.1.5:80                       │    │
│  │                                                    │    │
│  │ iptables -t nat -A KUBE-SVC-NGINX \                │    │
│  │   -m statistic --mode random --probability 0.50 \   │    │
│  │   -j DNAT --to 10.244.2.5:80                       │    │
│  │                                                    │    │
│  │ iptables -t nat -A KUBE-SVC-NGINX \                │    │
│  │   -j DNAT --to 10.244.2.6:80                       │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 5: Traffic Flow                                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Client Pod wants to access nginx:                  │    │
│  │                                                    │    │
│  │ $ curl http://nginx:80                             │    │
│  │        ↓                                           │    │
│  │ DNS (CoreDNS) resolves:                            │    │
│  │   nginx → 10.96.100.50 (ClusterIP)                 │    │
│  │        ↓                                           │    │
│  │ Packet sent to: 10.96.100.50:80                    │    │
│  │        ↓                                           │    │
│  │ iptables intercepts (on source node):              │    │
│  │   Destination: 10.96.100.50:80                     │    │
│  │   Matches: KUBE-SVC-NGINX                          │    │
│  │   Random selection: 10.244.2.5:80 (chosen)         │    │
│  │        ↓                                           │    │
│  │ DNAT applied:                                      │    │
│  │   From: src-ip → 10.96.100.50:80                   │    │
│  │   To: src-ip → 10.244.2.5:80                       │    │
│  │        ↓                                           │    │
│  │ CNI Routes packet to node2                         │    │
│  │        ↓                                           │    │
│  │ Pod receives request on 10.244.2.5:80              │    │
│  │        ↓                                           │    │
│  │ nginx process handles request                      │    │
│  │        ↓                                           │    │
│  │ Response flows back (reverse DNAT)                 │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Complete Flow on Kubernetes

```
┌─────────────────────────────────────────────────────────────┐
│        YOUR SOFTHSM APP ON KUBERNETES - COMPLETE FLOW       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: User Access                                        │
│  User browser: http://10.10.11.185/auth/login              │
│         ↓                                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Worker Node (10.10.11.185) - eth0:80              │    │
│  │ (because hostNetwork: true)                        │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 2: Ingress Controller                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │ nginx-ingress-controller Pod                       │    │
│  │                                                    │    │
│  │ Reads Ingress rules:                               │    │
│  │ • Path /auth/.* → backend:8001                     │    │
│  │                                                    │    │
│  │ Decision: Forward to backend service               │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 3: Service Discovery                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Service: backend (ClusterIP: 10.96.x.x)            │    │
│  │                                                    │    │
│  │ Endpoints:                                         │    │
│  │ ├─ 192.168.31.84:8001 (pod 1)                      │    │
│  │ └─ 192.168.31.87:8001 (pod 2)                      │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 4: kube-proxy iptables                                │
│  ┌────────────────────────────────────────────────────┐    │
│  │ iptables selects one pod randomly                  │    │
│  │ Selected: 192.168.31.84:8001                       │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 5: Backend Pod Processes                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Backend Pod (FastAPI)                              │    │
│  │ IP: 192.168.31.84                                  │    │
│  │                                                    │    │
│  │ FastAPI receives: POST /auth/login                 │    │
│  │ {                                                  │    │
│  │   "username": "admin",                             │    │
│  │   "password": "***"                                │    │
│  │ }                                                  │    │
│  │                                                    │    │
│  │ 1. Validate credentials                            │    │
│  │ 2. Query MongoDB (database:27017)                  │    │
│  │    ├─ DNS: database → 10.96.y.y                    │    │
│  │    ├─ iptables → 192.168.31.90:27017              │    │
│  │    └─ Connect to MongoDB pod                       │    │
│  │ 3. Generate JWT token                              │    │
│  │ 4. Return response                                 │    │
│  └────────────────────────────────────────────────────┘    │
│         ↓                                                   │
│  STEP 6: Response Returns                                   │
│  Backend → Service → Ingress → Node:80 → User Browser      │
│                                                             │
│  Complete journey:                                          │
│  User (browser)                                             │
│    → 10.10.11.185:80 (node eth0)                            │
│    → nginx-ingress pod                                      │
│    → backend ClusterIP (10.96.x.x)                          │
│    → iptables DNAT                                          │
│    → backend pod (192.168.31.84:8001)                       │
│    → (pod connects to MongoDB)                              │
│    → response flows back                                    │
│    → User receives JWT token                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary Diagrams

### Docker: The Stack

```
USER COMMAND (docker run)
    ↓
DOCKER CLI (parses command)
    ↓
DOCKER DAEMON (API server, orchestrator)
    ↓
CONTAINERD (container lifecycle)
    ↓
CONTAINERD-SHIM (per-container process)
    ↓
RUNC (creates namespaces/cgroups, starts process)
    ↓
LINUX KERNEL (enforces isolation)
    ↓
RUNNING CONTAINER (isolated process)
```

### Kubernetes: The Stack

```
USER COMMAND (kubectl create)
    ↓
KUBECTL CLI (API client)
    ↓
KUBE-APISERVER (validates, authenticates)
    ↓
ETCD (stores desired state)
    ↓
CONTROLLERS (reconcile desired vs actual state)
    ↓
SCHEDULER (assigns pods to nodes)
    ↓
KUBELET (manages pod lifecycle on node)
    ↓
CONTAINER RUNTIME (containerd/CRI-O)
    ↓
LINUX KERNEL (runs container)
    ↓
RUNNING POD (one or more containers)
```

---


