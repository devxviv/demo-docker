# Project 1: Python Backend on Kubernetes

> **Stack**: FastAPI backend + PostgreSQL + Nginx frontend  
> **Environment**: Killercoda 2-node cluster (controlplane + node01)  
> **Namespace**: `python-demo`

---

## Quick Reference

| Resource | Name | Namespace |
|----------|------|-----------|
| Namespace | python-demo | — |
| ConfigMap | python-backend-config | python-demo |
| Secret | postgres-db-secret | python-demo |
| PVC | postgres-pvc | python-demo |
| DB Deployment | postgres-db | python-demo |
| DB Service | postgres-svc | python-demo (ClusterIP :5432) |
| Backend Deployment | python-backend | python-demo |
| Backend Service | python-backend-svc | python-demo (ClusterIP :8000) |
| Frontend Deployment | python-frontend | python-demo |
| Frontend Service | python-frontend-svc | python-demo (NodePort :30080) |

---

## Step 1: Build Docker Images (on controlplane)

```bash
cd /root/demo-docker/k8s-projects/project-1-python

# Build backend
docker build -t python-backend:v1 ./backend

# Build frontend
docker build -t python-frontend:v1 ./frontend

# Verify
docker images | grep python
```

---

## Step 2: Copy Images to Worker Node (multi-node setup)

**Images must exist on all nodes where pods may schedule.**

```bash
# Save images on controlplane
docker save python-backend:v1 python-frontend:v1 -o /tmp/images.tar

# Copy to node01
scp /tmp/images.tar node01:/tmp/

# On node01 - import to containerd (Kubernetes runtime)
ssh node01
ctr -n k8s.io images import /tmp/images.tar
ctr -n k8s.io images ls | grep python
exit
```

> **Why this step?** Docker and Kubernetes (containerd) have separate image stores. Images must be in containerd's `k8s.io` namespace to be accessible by Kubernetes.

---

## Step 3: Create Namespace & Infrastructure

We need a Namespace for isolation, a Secret for DB passwords, and a PVC for DB storage.

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/db-secret.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/configmap.yaml
```

---

## Step 4: Deploy Database

```bash
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

# Wait for DB to be running
kubectl get pods -n python-demo -w
```

---

## Step 5: Deploy Backend

```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

# Check pods
kubectl get pods -n python-demo -o wide
```

---

## Step 6: Deploy Frontend

```bash
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# View all resources
kubectl get all -n python-demo
```

---

## Step 7: Access the Application

```bash
# Get node IPs
kubectl get nodes -o wide

# Test from controlplane
curl http://localhost:30080
```
Open port 30080 in the Killercoda UI to see the frontend. You can now interact with the PostgreSQL database.

---

## Step 8: Scale & Load Balancing

```bash
# Scale to 4 replicas
kubectl scale deployment python-backend --replicas=4 -n python-demo

# Verify pods on different nodes
kubectl get pods -n python-demo -o wide
```

---

## Step 9: Cleanup

```bash
# Delete all resources
kubectl delete -f k8s/

# Or delete entire namespace
kubectl delete namespace python-demo
```

---

## Key Teaching Points

| Concept | Command | Lesson |
|---------|---------|--------|
| Namespace isolation | `-n python-demo` | Resources scoped to namespace |
| ConfigMap injection | `envFrom` in deployment | Externalize config from code |
| Image handling | `ctr -n k8s.io` | Docker ≠ containerd stores |
| Service discovery | `http://python-backend-svc:8000` | CoreDNS resolves service name |
| Load balancing | Multiple backend replicas | Service distributes traffic |
| NodePort | External access | `node-ip:30080` accessible from outside |

---

## Namespace Flag Summary

| Command | Without `-n` | With `-n python-demo` |
|---------|--------------|----------------------|
| `kubectl get pods` | Shows default namespace | Shows python-demo |
| `kubectl get configmaps` | Shows default namespace | Shows python-demo |
| `kubectl get services` | Shows default namespace | Shows python-demo |
| `kubectl apply -f file.yaml` | Uses namespace from YAML (if specified) | Uses namespace from YAML |

**Always specify `-n` when working with namespaced resources!**