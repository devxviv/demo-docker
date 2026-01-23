# Docker & Kubernetes Training Documentation

## Overview

This comprehensive training guide covers containerization and orchestration from fundamentals to production deployment, tailored for teams working with web applications and embedded systems.

---

## Table of Contents

| Part | Topic | Description |
| ---- | ----- || Part   | Topic                                              | Description                                     |
| ------ | -------------------------------------------------- | ----------------------------------------------- |
| **1**  | [Linux Fundamentals](./01-linux-fundamentals.md)   | Namespaces, cgroups, essential commands         |
| **2**  | [Docker Fundamentals](./02-docker-fundamentals.md) | Architecture, images, containers, OCI           |
| **3**  | [Dockerfiles](./03-dockerfiles.md)                 | Writing Dockerfiles, multi-stage builds         |
| **4**  | [Volumes](./04-volumes.md)                         | Data persistence, bind mounts, PostgreSQL       |
| **4b** | [Docker Networking](./04b-docker-networking.md)    | Bridge, host, overlay, port mapping             |
| **5**  | [Docker Compose](./05-docker-compose.md)           | Multi-container applications                    |
| **6**  | [Embedded Systems](./06-embedded.md)               | FPGA, RPi, Smart Cards, TPM, SPI                |
| **7**  | [Kubernetes Basics](./07-kubernetes.md)            | Architecture, pods, deployments, services       |
| **7b** | [K8s Components](./07b-kubernetes-components.md)   | Deep dive: API Server, Scheduler, etcd, kubelet |
| **7c** | [K8s Objects](./07c-kubernetes-objects.md)         | Pods, Deployments, StatefulSets, Jobs, CronJobs |
| **7d** | [K8s Networking](./07d-kubernetes-networking.md)   | Services, DNS, Endpoints, Network Policies      |
| **7e** | [K8s RBAC](./07e-kubernetes-rbac.md)               | ServiceAccounts, Roles, RoleBindings            |
| **7f** | [K8s Storage & Scale](./07f-kubernetes-storage.md) | StorageClasses, PVCs, HPA, VPA, resources       |
| **7g** | [Cloud vs On-Premise](./07g-onpremise-vs-cloud.md) | EKS/GKE vs kubeadm, MetalLB, local-path         |
| **8**  | [K8s Production](./08-kubernetes-production.md)    | Secrets, Ingress, production patterns           |
| **9**  | [Sample Files](./09-sample-files.md)               | Complete working examples                       |
| **10** | [Quick Reference](./10-quick-reference.md)         | Command cheat sheet                             |  |

---

## Learning Path

### Beginner (Week 1-2)
1. ✅ Part 1: Linux Fundamentals
2. ✅ Part 2: Docker Fundamentals
3. ✅ Part 3: Dockerfiles
4. ✅ Part 4: Volumes

### Intermediate (Week 3-4)
5. ✅ Part 5: Docker Compose
6. ✅ Part 6: Embedded Systems (team-specific)
7. ✅ Part 7: Kubernetes Basics

### Advanced (Week 5-6)
8. ✅ Part 8: Kubernetes Production
9. ✅ Part 9: Sample Files (hands-on)
10. ✅ Part 10: Quick Reference (ongoing)

---

## Key Takeaways

### Docker is NOT magic
- Uses Linux kernel features (namespaces, cgroups)
- Images are layered filesystems
- Containers are isolated processes

### OCI Standards
- Docker isn't the only way to build/run containers
- Podman, Buildah, kaniko are alternatives
- Images work everywhere if OCI-compliant

### Kubernetes for Production
- Declarative (describe desired state)
- Self-healing (restarts failed pods)
- Scalable (replicas, HPA)

---

## Quick Start Commands

```bash
# Docker
docker build -t myapp .
docker run -d -p 8080:80 myapp
docker compose up -d

# Kubernetes
kubectl apply -f deployment.yaml
kubectl get pods
kubectl logs <pod-name>
```

---

## Additional Resources

- [Docker Official Docs](https://docs.docker.com/)
- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Play with Docker](https://labs.play-with-docker.com/)
- [Katacoda K8s Scenarios](https://www.katacoda.com/courses/kubernetes)
