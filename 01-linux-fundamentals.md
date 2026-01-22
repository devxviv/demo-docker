# Part 1: Linux Fundamentals for Docker

## 1.1 What is Linux?

Linux is an **Operating System Kernel** - the core program that manages hardware and allows software to run.

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR APPLICATIONS                     │
│            (Chrome, VS Code, Python, Java)              │
├─────────────────────────────────────────────────────────┤
│                    LINUX KERNEL                          │
│     (Process management, Memory, Filesystems, I/O)      │
├─────────────────────────────────────────────────────────┤
│                      HARDWARE                            │
│              (CPU, RAM, Disk, Network)                  │
└─────────────────────────────────────────────────────────┘
```

---

## 1.2 Key Linux Concepts Docker Uses

### 1.2.1 Processes

Every running program is a **process** with a unique ID (PID).

```bash
# List all processes
ps aux

# Find a specific process
ps aux | grep python

# Kill a process
kill <PID>
kill -9 <PID>  # Force kill
```

### 1.2.2 Namespaces (Isolation)

Namespaces create **isolated views** of system resources. Docker uses these to isolate containers.

| Namespace | What It Isolates                                    |
| --------- | --------------------------------------------------- |
| **PID**   | Process IDs - container sees only its own processes |
| **NET**   | Network interfaces - container gets its own IP      |
| **MNT**   | Filesystem mounts - container has its own file tree |
| **UTS**   | Hostname - container can have its own hostname      |
| **IPC**   | Inter-process communication                         |
| **USER**  | User/Group IDs                                      |

```
┌──────────────────────────────────────────────────────┐
│                    HOST LINUX                         │
│                                                       │
│   ┌──────────────┐  ┌──────────────┐                │
│   │ Namespace 1  │  │ Namespace 2  │                │
│   │ (Container A)│  │ (Container B)│                │
│   │              │  │              │                │
│   │ PID 1: nginx │  │ PID 1: python│  ← Same PID,  │
│   │ IP: 172.17.2 │  │ IP: 172.17.3 │    different  │
│   │ Files: /app  │  │ Files: /app  │    namespaces │
│   └──────────────┘  └──────────────┘                │
└──────────────────────────────────────────────────────┘
```

### 1.2.3 Control Groups (cgroups) - Resource Limits

Cgroups **limit** how much CPU, memory, disk I/O a process can use.

```bash
# Check cgroup usage
cat /sys/fs/cgroup/memory/memory.usage_in_bytes

# Docker uses cgroups automatically:
docker run --memory=512m --cpus=1 nginx
```

### 1.2.4 Union Filesystems (Layers)

Docker images are built in **layers**. Each layer is read-only, stacked on top of each other.

```
┌─────────────────────────────────────┐
│  Layer 4: Your app code (10 MB)    │  ← Changes only this layer
├─────────────────────────────────────┤
│  Layer 3: pip install (200 MB)     │  ← Cached, reused
├─────────────────────────────────────┤
│  Layer 2: Python 3.11 (50 MB)      │  ← Cached, reused
├─────────────────────────────────────┤
│  Layer 1: Ubuntu base (70 MB)      │  ← Cached, reused
└─────────────────────────────────────┘
```

---

## 1.3 Essential Linux Commands

### File Operations
```bash
# Navigate
cd /path/to/dir     # Change directory
pwd                 # Print current directory
ls -la              # List files with details

# File operations
cp source dest      # Copy
mv source dest      # Move/rename
rm file             # Delete file
rm -rf dir          # Delete directory (CAREFUL!)

# View files
cat file            # Print entire file
head -20 file       # First 20 lines
tail -20 file       # Last 20 lines
tail -f file        # Follow file (live updates)
```

### Permissions
```bash
# Format: rwxrwxrwx (user/group/others)
chmod 755 script.sh  # rwx r-x r-x (execute for all)
chmod 644 file.txt   # rw- r-- r-- (read for all)
chown user:group file
```

### Networking
```bash
# Check ports
netstat -tulpn      # List listening ports
ss -tulpn           # Modern alternative

# Network info
ip addr             # Show IP addresses
curl http://url     # HTTP request
wget http://url     # Download file
```

### Process Management
```bash
# View processes
ps aux              # All processes
top                 # Live process monitor
htop                # Better live monitor

# Background jobs
command &           # Run in background
nohup command &     # Run even after logout
```

---

## 1.4 Why Docker is a "Linux Concept"

Docker is NOT magic. It uses **existing Linux features**:

| Docker Feature      | Linux Technology             |
| ------------------- | ---------------------------- |
| Container isolation | Namespaces                   |
| Resource limits     | cgroups                      |
| Image layers        | Union filesystem (OverlayFS) |
| Networking          | iptables, bridges            |

**On Windows/Mac:** Docker runs a hidden Linux VM because these features only exist in Linux!

```
WINDOWS/MAC:
┌─────────────────────────────┐
│  Docker Desktop             │
│  ┌───────────────────────┐ │
│  │  Hidden Linux VM      │ │
│  │  ┌─────────────────┐  │ │
│  │  │  Containers     │  │ │
│  │  └─────────────────┘  │ │
│  └───────────────────────┘ │
└─────────────────────────────┘

LINUX:
┌─────────────────────────────┐
│  Linux Host                 │
│  ┌─────────────────┐        │
│  │  Containers     │        │  ← No VM needed!
│  └─────────────────┘        │
└─────────────────────────────┘
```

---

## 1.5 Hands-On Exercise

```bash
# 1. Create a namespace manually (advanced)
sudo unshare --pid --fork /bin/bash
# Now you're in a new PID namespace!
ps aux  # Only shows bash

# 2. View namespaces of a running container
docker run -d --name test nginx
ls -la /proc/$(docker inspect test --format '{{.State.Pid}}')/ns/

# 3. Check cgroups
cat /sys/fs/cgroup/memory/docker/*/memory.limit_in_bytes
```

---

**Next:** [Part 2: Docker Fundamentals](./02-docker-fundamentals.md)
