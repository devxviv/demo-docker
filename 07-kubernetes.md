# Part 7: Kubernetes Fundamentals

## 7.1 What is Kubernetes?

Kubernetes (K8s) is a **container orchestration platform** that automates deployment, scaling, and management.

```
DOCKER ALONE:                    KUBERNETES:
┌──────────────────┐            ┌─────────────────────────────────┐
│  Single Machine  │            │  Cluster of Machines            │
│  ┌────────────┐  │            │  ┌───────┐ ┌───────┐ ┌───────┐ │
│  │ Container  │  │            │  │Node 1 │ │Node 2 │ │Node 3 │ │
│  └────────────┘  │            │  │ □ □ □ │ │ □ □   │ │ □ □ □ │ │
│                  │            │  └───────┘ └───────┘ └───────┘ │
│  Manual scaling  │            │  Auto-scaling, self-healing    │
│  Manual restart  │            │  Automatic restarts            │
└──────────────────┘            └─────────────────────────────────┘
```

---

## 7.2 Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER                           │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                      CONTROL PLANE (Master)                      ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ ││
│  │  │ API Server  │ │ Scheduler   │ │ Controller  │ │   etcd     │ ││
│  │  │ (kubectl)   │ │ (placement) │ │ (healing)   │ │ (database) │ ││
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                │                                      │
│                                ▼                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │   WORKER NODE 1  │  │   WORKER NODE 2  │  │   WORKER NODE 3  │   │
│  │  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌────────────┐  │   │
│  │  │  kubelet   │  │  │  │  kubelet   │  │  │  │  kubelet   │  │   │
│  │  │ kube-proxy │  │  │  │ kube-proxy │  │  │  │ kube-proxy │  │   │
│  │  ├────────────┤  │  │  ├────────────┤  │  │  ├────────────┤  │   │
│  │  │ Pod Pod Pod│  │  │  │ Pod Pod    │  │  │  │ Pod Pod Pod│  │   │
│  │  └────────────┘  │  │  └────────────┘  │  │  └────────────┘  │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Control Plane Components

| Component              | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| **API Server**         | Entry point for all commands (kubectl)     |
| **Scheduler**          | Decides which node to run pods on          |
| **Controller Manager** | Ensures desired state (restarts pods)      |
| **etcd**               | Distributed database storing cluster state |

### Worker Node Components

| Component             | Purpose                              |
| --------------------- | ------------------------------------ |
| **kubelet**           | Agent that runs pods on the node     |
| **kube-proxy**        | Network proxy handling routing       |
| **Container Runtime** | Docker/containerd running containers |

---

## 7.3 Key Kubernetes Objects

### Pod
Smallest deployable unit. Contains one or more containers.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
```

### Deployment
Manages multiple pod replicas with rolling updates.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3                    # Run 3 copies
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
```

### Service
Exposes pods to network traffic.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx                   # Finds pods with this label
  ports:
  - port: 80                     # Service port
    targetPort: 80               # Container port
  type: ClusterIP                # Internal only
```

---

## 7.4 Service Types

```
┌────────────────────────────────────────────────────────────────────┐
│                         SERVICE TYPES                               │
│                                                                     │
│  ClusterIP (Default):           NodePort:              LoadBalancer:│
│  ┌─────────────────────┐       ┌────────────────┐     ┌───────────┐│
│  │ Internal only       │       │ Node:30001     │     │ Cloud LB  ││
│  │ 10.96.x.x:80       │       │ Exposed on     │     │ External  ││
│  │                     │       │ all nodes      │     │ IP:80     ││
│  └─────────────────────┘       └────────────────┘     └───────────┘│
│          │                            │                      │     │
│          ▼                            ▼                      ▼     │
│  ┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐    │
│  │                        PODS                               │    │
│  └─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘    │
└────────────────────────────────────────────────────────────────────┘
```

| Type             | Use Case           | Access                  |
| ---------------- | ------------------ | ----------------------- |
| **ClusterIP**    | Internal services  | Inside cluster only     |
| **NodePort**     | Development        | `<node-ip>:30000-32767` |
| **LoadBalancer** | Production (cloud) | External IP             |

---

## 7.5 Essential kubectl Commands

### Cluster Info
```bash
kubectl cluster-info
kubectl get nodes
kubectl get nodes -o wide
```

### Pods
```bash
kubectl get pods
kubectl get pods -o wide              # Show node placement
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl logs -f <pod-name>            # Follow logs
kubectl exec -it <pod-name> -- bash   # Shell into pod
kubectl delete pod <pod-name>
```

### Deployments
```bash
kubectl get deployments
kubectl describe deployment <name>
kubectl scale deployment <name> --replicas=5
kubectl rollout status deployment <name>
kubectl rollout history deployment <name>
kubectl rollout undo deployment <name>    # Rollback
```

### Services
```bash
kubectl get services
kubectl get svc
kubectl describe svc <name>
kubectl port-forward svc/<name> 8080:80   # Local testing
```

### Apply/Delete Resources
```bash
kubectl apply -f deployment.yaml
kubectl apply -f ./k8s/                  # Apply all in directory
kubectl delete -f deployment.yaml
kubectl delete deployment <name>
```

### Debugging
```bash
kubectl get events --sort-by='.lastTimestamp'
kubectl top pods                          # Resource usage
kubectl top nodes
kubectl describe node <node-name>
```

---

## 7.6 Namespaces

Namespaces isolate resources within a cluster.

```bash
# List namespaces
kubectl get namespaces

# Create namespace
kubectl create namespace production

# Use namespace
kubectl get pods -n production
kubectl apply -f app.yaml -n production

# Set default namespace
kubectl config set-context --current --namespace=production
```

---

## 7.7 Labels and Selectors

Labels are key-value pairs for organizing resources.

```yaml
# In deployment
metadata:
  labels:
    app: backend
    environment: production
    team: platform

# Query by label
kubectl get pods -l app=backend
kubectl get pods -l environment=production
kubectl get pods -l 'app in (frontend, backend)'
```

---

**Next:** [Part 8: Kubernetes for Production](./08-kubernetes-production.md)
