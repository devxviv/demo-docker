# Docker & Kubernetes Training Documentation

## Overview

Comprehensive training guide covering containerization and orchestration from absolute fundamentals to production deployment. Designed for beginners with hands-on demos, ASCII diagrams, and real-world examples.

---

## Prerequisites

- Basic command line knowledge (Linux/Mac/Windows)
- Text editor (VS Code recommended)
- Docker Desktop installed
- Enthusiasm to learn!

---

## Table of Contents

### Foundation: The Big Picture

| Part    | Topic                                                                 | Description                                                 |
| ------- | --------------------------------------------------------------------- | ----------------------------------------------------------- |
| **00**  | [Big Picture Overview](./00-overview-big-picture.md)                  | Complete architecture: Frontend+Backend+DB+Docker+K8s+CI/CD |
| **01a** | [Virtualization vs Containers](./01a-virtualization-vs-containers.md) | Evolution story, VMs vs Containers, Linux concepts          |
| **02a** | [OCI & Container Runtimes](./02a-oci-and-container-runtimes.md)       | Standards, containerd, why K8s dropped Docker               |

### Docker Fundamentals

| Part    | Topic                                              | Description                                  |
| ------- | -------------------------------------------------- | -------------------------------------------- |
| **01**  | [Linux Fundamentals](./01-linux-fundamentals.md)   | Namespaces, cgroups, essential commands      |
| **02**  | [Docker Fundamentals](./02-docker-fundamentals.md) | Architecture, images, containers, registries |
| **03**  | [Dockerfiles](./03-dockerfiles.md)                 | Writing Dockerfiles, multi-stage builds      |
| **04**  | [Volumes](./04-volumes.md)                         | Data persistence, bind mounts, volumes       |
| **04b** | [Docker Networking](./04b-docker-networking.md)    | Bridge, host, overlay networks, port mapping |
| **05**  | [Docker Compose](./05-docker-compose.md)           | Multi-container applications                 |

### Kubernetes Fundamentals

| Part    | Topic                                              | Description                                       |
| ------- | -------------------------------------------------- | ------------------------------------------------- |
| **07**  | [Kubernetes Basics](./07-kubernetes.md)            | Architecture, pods, deployments, services         |
| **07b** | [K8s Components](./07b-kubernetes-components.md)   | API Server, Scheduler, etcd, kubelet, kube-proxy  |
| **07c** | [K8s Objects](./07c-kubernetes-objects.md)         | Pods, Deployments, StatefulSets, Jobs, DaemonSets |
| **07d** | [K8s Networking](./07d-kubernetes-networking.md)   | Services, DNS, Endpoints, Network Policies, CNI   |
| **07e** | [K8s RBAC](./07e-kubernetes-rbac.md)               | ServiceAccounts, Roles, RoleBindings, security    |
| **07f** | [K8s Storage & Scale](./07f-kubernetes-storage.md) | PVs, PVCs, StorageClasses, HPA, VPA               |
| **07g** | [Cloud vs On-Premise](./07g-onpremise-vs-cloud.md) | EKS/GKE vs kubeadm, considerations                |

### Production & Specialized Topics

| Part   | Topic                                           | Description                                  |
| ------ | ----------------------------------------------- | -------------------------------------------- |
| **08** | [K8s Production](./08-kubernetes-production.md) | Secrets, ConfigMaps, Ingress, best practices |
| **06** | [Embedded Systems](./06-embedded.md)            | FPGA, RPi, Smart Cards, TPM (specialized)    |
| **09** | [Sample Files](./09-sample-files.md)            | Complete working examples                    |
| **10** | [Quick Reference](./10-quick-reference.md)      | Command cheat sheet                          |

### Live Demos

- [Live Demo Scripts](./LIVE_DEMO_SCRIPTS.md) - Step-by-step demonstration guides

---

## Recommended Learning Path

### Module 1: Understanding the Big Picture

**Goal**: Understand what Docker and Kubernetes solve and why they exist.

1. [Big Picture Overview](./00-overview-big-picture.md)
   - See the complete modern application stack
   - Understand where Docker, Kubernetes, and CI/CD fit
   - Grasp the benefits of the entire ecosystem

2. [Virtualization vs Containers](./01a-virtualization-vs-containers.md)
   - Learn the evolution: Physical → VMs → Containers
   - Understand VMs vs Containers deeply
   - See Linux concepts (namespaces, cgroups) in action
   - Practical demos proving isolation

3. [OCI & Container Runtimes](./02a-oci-and-container-runtimes.md)
   - Understand container standards
   - Learn about containerd and the runtime stack
   - Understand why Kubernetes dropped Docker (but images still work!)

**Time**: 3-4 hours  
**Outcome**: Solid mental model of containerization ecosystem

---

### Module 2: Docker Hands-On

**Goal**: Build, run, and manage Docker containers confidently.

4. [Linux Fundamentals](./01-linux-fundamentals.md)
   - Essential Linux commands
   - Understand filesystem, processes, networking

5. [Docker Fundamentals](./02-docker-fundamentals.md)
   - Images vs containers
   - Docker commands (run, pull, push, exec)
   - Container lifecycle

6. [Dockerfiles](./03-dockerfiles.md)
   - Write Dockerfiles from scratch
   - Layer optimization
   - Multi-stage builds

7. [Volumes](./04-volumes.md) & [Networking](./04b-docker-networking.md)
   - Persist data beyond container lifecycle
   - Connect containers together
   - Expose services to the host

8. [Docker Compose](./05-docker-compose.md)
   - Define multi-container applications
   - One command to start entire stack

**Time**: 6-8 hours  
**Outcome**: Can containerize any application

---

### Module 3: Kubernetes Fundamentals

**Goal**: Deploy and manage containerized applications in production.

9. [Kubernetes Basics](./07-kubernetes.md)
   - Architecture and core concepts
   - Pods, Deployments, Services
   - Basic kubectl commands

10. [K8s Components](./07b-kubernetes-components.md)
    - Control plane deep dive
    - Worker node components
    - How Kubernetes works internally

11. [K8s Objects](./07c-kubernetes-objects.md)
    - All workload types
    - When to use what
    - StatefulSets for databases

12. [K8s Networking](./07d-kubernetes-networking.md) & [RBAC](./07e-kubernetes-rbac.md)
    - How pods communicate
    - Load balancing and DNS
    - Secure your cluster

13. [K8s Storage & Scaling](./07f-kubernetes-storage.md)
    - Persistent storage in K8s
    - Auto-scaling applications
    - Resource management

**Time**: 8-10 hours  
**Outcome**: Can deploy production-grade applications

---

### Module 4: Production Deployment

**Goal**: Run applications in real production environments.

14. [K8s Production Patterns](./08-kubernetes-production.md)
    - Secrets management
    - Ingress for routing
    - Health checks and lifecycle

15. [Cloud vs On-Premise](./07g-onpremise-vs-cloud.md)
    - Deployment options
    - Trade-offs and considerations
    - Setting up your own cluster

16. [Sample Files](./09-sample-files.md)
    - Complete real-world examples
    - Full-stack applications
    - Copy and customize

**Time**: 4-6 hours  
**Outcome**: Production-ready knowledge

---

### Module 5: Specialized (Optional)

17. [Embedded Systems](./06-embedded.md)
    - Containers on resource-constrained devices
    - FPGA, Raspberry Pi, Smart Cards

---

## Key Concepts

### Docker Is NOT Magic

```
Container = Isolated Linux process using:
├── Namespaces (what can it see?)
├── Cgroups (what can it use?)
└── Union FS (layered filesystem)
```

### OCI Standards Enable Portability

```
Docker Image  = OCI Image
├── Works in Docker
├── Works in Podman
├── Works in Kubernetes (containerd)
└── Works anywhere OCI-compliant
```

### Kubernetes Provides Orchestration

```
You Declare:    "I want 3 web pods"
Kubernetes:     Makes it happen
                ├── Schedules pods
                ├── Monitors health
                ├── Restarts failures
                ├── Load balances traffic
                └── Scales automatically
```

---

## Quick Start Commands

### Docker

```bash
# Build an image
docker build -t myapp:v1 .

# Run a container
docker run -d -p 8080:80 --name web myapp:v1

# Check running containers
docker ps

# View logs
docker logs web

# Stop and remove
docker stop web && docker rm web

# Multi-container app
docker compose up -d
docker compose down
```

### Kubernetes

```bash
# Apply configuration
kubectl apply -f deployment.yaml

# Get resources
kubectl get pods
kubectl get services
kubectl get deployments

# View details
kubectl describe pod <pod-name>
kubectl logs <pod-name>

# Scale application
kubectl scale deployment web --replicas=5

# Update image (rolling update)
kubectl set image deployment/web web=myapp:v2

# Access running pod
kubectl exec -it <pod-name> -- bash
```

---

## Hands-On Practice

### Use Live Demo Scripts

The [LIVE_DEMO_SCRIPTS.md](./LIVE_DEMO_SCRIPTS.md) contains step-by-step demonstrations:
- Building your first Docker image
- Running multi-container apps with Compose
- Deploying to Kubernetes
- Setting up CI/CD pipelines

### Experimentation Environments

- **Local**: Docker Desktop + Kubernetes enabled
- **Cloud Free Tiers**:
  - Play with Docker: https://labs.play-with-docker.com/
  - Play with Kubernetes: https://labs.play-with-k8s.com/
- **Production-like**: minikube, k3s, or kind

---

## Training Duration Estimates

```
Total Time: 20-30 hours minimum

Fast Track (Intense):
├── Module 1: 4 hours
├── Module 2: 6 hours
├── Module 3: 8 hours
└── Module 4: 4 hours
Total: 22 hours (over 5 days, 4-5 hours/day)

Comfortable Pace (Recommended):
├── Module 1: 6 hours (Week 1)
├── Module 2: 10 hours (Week 2-3)
├── Module 3: 12 hours (Week 4-5)
└── Module 4: 6 hours (Week 6)
Total: 34 hours (over 6 weeks, 5-6 hours/week)
```

---

## Additional Resources

### Official Documentation

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [OCI Specifications](https://opencontainers.org/)

### Interactive Learning

- [Docker Tutorial](https://www.docker.com/101-tutorial/)
- [Kubernetes by Example](https://kubernetesbyexample.com/)
- [Katacoda Scenarios](https://www.katacoda.com/)

### Books (Recommended)

- "Docker Deep Dive" by Nigel Poulton
- "Kubernetes Up & Running" by Kelsey Hightower
- "The Kubernetes Book" by Nigel Poulton

### YouTube Channels

- TechWorld with Nana
- That DevOps Guy
- Cloud Native Foundation

---

## Getting Help

- **Questions during training**: Ask your instructor or team lead
-** **Docker Community**: https://forums.docker.com/
- **Kubernetes Slack**: https://slack.k8s.io/
- **Stack Overflow**: Tag questions with `docker` or `kubernetes`

---

## What You'll Achieve

After completing this training, you will be able to:

- ✅ Explain how containers work at a fundamental level
- ✅ Containerize any application with Docker
- ✅ Build optimized, production-ready Docker images
- ✅ Deploy multi-container applications
- ✅ Run applications in Kubernetes clusters
- ✅ Scale applications automatically
- ✅ Implement CI/CD pipelines
- ✅ Troubleshoot container and orchestration issues
- ✅ Make informed decisions about deployment strategies
- ✅ Communicate effectively with DevOps teams

**Let's get started! Open [00-overview-big-picture.md](./00-overview-big-picture.md) to begin your journey.**

