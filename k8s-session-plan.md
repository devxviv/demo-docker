# Kubernetes

## Session Flow Overview

| Section | Approach |
|---------|----------|
| Kubernetes Architecture Mental Model | Theory + Visualization |
| Imperative Commands (Pod, Deployment, Service) | Demo |
| Declarative YAML (All K8s Objects) | YAML Walkthrough |
| How to Read Official Docs | Reference Skills |
| Project Demo on Killercoda | Deployment |

---

# PART 1: Architecture Mental Model

## 1.1 The Problem Kubernetes Solves

```
┌─────────────────────────────────────────────────────────────────┐
│  Without K8s: You have 50 containers across 10 machines        │
│                                                                 │
│  ❌ Who restarts crashed containers?                           │
│  ❌ How do you update all 50 without downtime?                 │
│  ❌ How do you load balance?                                   │
│  ❌ How do you scale up/down automatically?                    │
│  ❌ Where are logs? Who monitors health?                       │
│                                                                 │
│  With Kubernetes: You manage "desired state", K8s makes it so │
│                                                                 │
│  ✅ "Keep 3 replicas running" → K8s restarts if one dies      │
│  ✅ "Update to v2" → K8s does rolling update                   │
│  ✅ Service → automatic load balancing                          │
│  ✅ HPA → auto-scale based on CPU/memory                       │
│  ✅ Built-in health checks, logging integrated                 │
└─────────────────────────────────────────────────────────────────┘
```

## 1.2 Kubernetes Architecture - The Core Components

```
┌────────────────────────────────────────────────────────────────────────┐
│                    KUBERNETES ARCHITECTURE                             │
│                                                                        │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                      CONTROL PLANE (Master)                    │  │
│   │   ┌──────────┐  ┌───────────┐  ┌──────────────────────┐        │  │
│   │   │API Server│  │ Scheduler│  │Controller Manager   │        │  │
│   │   │(frontdoor)│  │(decides  │  │(watches and fixes)   │        │  │
│   │   └────┬─────┘  │ where to │  └──────────┬───────────┘        │  │
│   │        │        │ put pods) │             │                    │  │
│   │        └───────┬┴──────────┴─────────────┘                    │  │
│   │                │                                               │  │
│   │           ┌────▼────┐    (The "brain" - stores all state)     │  │
│   │           │  etcd   │                                          │  │
│   │           └─────────┘                                          │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│            │                                                        │
│            │ (kubelet talks to API Server)                          │
│            ▼                                                        │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                      WORKER NODE (node01)                      │  │
│   │   ┌─────────┐ ┌──────────┐ ┌──────────────────┐               │  │
│   │   │ kubelet │ │kube-proxy│ │ containerd       │               │  │
│   │   │(foreman)│ │(network) │ │ (runs containers) │               │  │
│   │   └────┬────┘ └────┬─────┘ └────────┬───────────┘               │  │
│   │        │          │                 │                           │  │
│   │        ▼          ▼                 ▼                           │  │
│   │   ┌──────┐   ┌──────────┐    ┌──────────┐                    │  │
│   │   │ Pod  │   │  Pod     │    │   Pod    │                    │  │
│   │   │(your │   │(coredns) │    │(your app)│                    │  │
│   │   │ app) │   │          │    │          │                    │  │
│   │   └──────┘   └──────────┘    └──────────┘                    │  │
│   └─────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

**Analogy Summary:**
| Component | Role | Analogy |
|-----------|------|---------|
| API Server | Validates and stores requests | Receptionist |
| etcd | Cluster state database | Company records (source of truth) |
| Scheduler | Decides which node gets which pod | Office manager (assigns desks) |
| Controller Manager | Watches and fixes desired state | Supervisor |
| kubelet | Manages containers on each node | Foreman on each floor |
| kube-proxy | Network traffic routing | Reception switchboard |

## 1.3 How a Request Flows Through K8s

```
┌──────────────────────────────────────────────────────────────────────┐
│                    COMPLETE K8s REQUEST FLOW                        │
│                                                                      │
│  1. You run: kubectl apply -f deployment.yaml                      │
│       │                                                              │
│       ▼                                                              │
│  2. kubectl → HTTPS → API Server                                    │
│       │                                                              │
│       ▼                                                              │
│  3. API Server validates YAML → stores in etcd                     │
│       │                                                              │
│       ▼                                                              │
│  4. Deployment Controller (in controller-manager) sees new object │
│     → creates ReplicaSet                                           │
│       │                                                              │
│       ▼                                                              │
│  5. ReplicaSet Controller creates Pod objects (in etcd)             │
│     (Pods are "Pending" — no node assigned yet)                     │
│       │                                                              │
│       ▼                                                              │
│  6. Scheduler watches for unassigned Pods                          │
│     → picks best node → updates pod.spec.nodeName                  │
│       │                                                              │
│       ▼                                                              │
│  7. kubelet on that node sees "my pod got assigned here"           │
│     → calls containerd via CRI                                      │
│       │                                                              │
│       ▼                                                              │
│  8. containerd pulls image → creates sandbox → starts container  │
│       │                                                              │
│       ▼                                                              │
│  9. Pod is Running! kubelet reports status back to API Server       │
│       │                                                              │
│       ▼                                                              │
│  10. kube-proxy updates iptables rules for any Services            │
│      that select this Pod                                           │
│                                                                      │
│  Total time: typically 2-10 seconds                                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

# PART 2: Imperative Commands

## 2.1 Verify Your Cluster

```bash
# Check cluster is accessible
kubectl cluster-info

# See nodes in your cluster
kubectl get nodes -o wide

# What K8s version?
kubectl version --client
kubectl version --short

# See all namespaces
kubectl get namespaces
```

## 2.2 Pod - The Smallest Unit

```bash
# Create a single nginx pod (imperative - quick for testing)
kubectl run my-nginx --image=nginx:alpine --port=80

# Check pods
kubectl get pods
kubectl get pods -o wide

# See detailed info
kubectl describe pod my-nginx

# See logs
kubectl logs my-nginx

# Delete pod
kubectl delete pod my-nginx

# ⚠️ NEVER use bare pods in production - they don't self-heal!
```

## 2.3 Deployment - Self-Healing + Scaling

```bash
# Create deployment with 2 replicas
kubectl create deployment web --image=nginx:alpine --replicas=2

# Check hierarchy: Deployment → ReplicaSet → Pods
kubectl get deployments
kubectl get replicasets
kubectl get pods

# Scale up
kubectl scale deployment web --replicas=5

# Watch new pods come up
kubectl get pods -w

# Scale down
kubectl scale deployment web --replicas=2

# Self-healing demo - delete a pod, watch it come back
kubectl get pods
kubectl delete pod <ANY-POD-NAME>
kubectl get pods  # Notice: new pod created automatically!
```

## 2.4 Service - Stable Network Access

```bash
# Expose deployment as ClusterIP (internal only)
kubectl expose deployment web --port=80 --target-port=80 --name=web-svc

# Check service
kubectl get svc
kubectl get svc -o wide

# Test from inside cluster
kubectl run test --image=curlimages/curl --rm -it --restart=Never -- curl http://web-svc

# Expose as NodePort (external access)
kubectl expose deployment web --type=NodePort --port=80 --name=web-np

# Check NodePort
kubectl get svc web-np
# Look for port like 80:31234/TCP - access via http://<node-ip>:31234
```

## 2.5 Namespace - Resource Isolation

```bash
# Create namespace
kubectl create namespace demo

# List all namespaces
kubectl get namespaces

# Run pod in specific namespace
kubectl run test --image=nginx:alpine -n demo

# List pods in namespace
kubectl get pods -n demo

# Delete namespace (deletes everything inside!)
kubectl delete namespace demo
```

---

# PART 3: Declarative YAML - All K8s Objects

## 3.1 Pod YAML

```yaml
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-nginx
  labels:
    app: nginx
    env: demo
spec:
  containers:
    - name: nginx
      image: nginx:alpine
      ports:
        - containerPort: 80
      env:
        - name: APP_NAME
          value: "my-nginx"
```

```bash
# Apply and manage
kubectl apply -f pod.yaml
kubectl get pods
kubectl delete -f pod.yaml
```

## 3.2 Deployment YAML

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deploy
  labels:
    app: nginx
spec:
  replicas: 3
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
          # Health probes
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 10
          # Resource management
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
```

```bash
kubectl apply -f deployment.yaml
kubectl get deployments
kubectl get replicasets
kubectl get pods
```

## 3.3 Service YAML

```yaml
# service.yaml - ClusterIP (internal)
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
  labels:
    app: nginx
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
```

```yaml
# service-nodeport.yaml - NodePort (external)
apiVersion: v1
kind: Service
metadata:
  name: nginx-np
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
```

```bash
kubectl apply -f service.yaml
kubectl get svc
```

## 3.4 ConfigMap YAML

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_NAME: "my-app"
  APP_VERSION: "1.0.0"
  LOG_LEVEL: "info"
  DATABASE_URL: "postgres://db:5432/myapp"
```

```bash
kubectl apply -f configmap.yaml
kubectl get configmap
kubectl describe configmap app-config
```

**Using ConfigMap in Pod:**

```yaml
# pod-with-configmap.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
    - name: app
      image: nginx:alpine
      # Method 1: All keys as env vars
      envFrom:
        - configMapRef:
            name: app-config
      # OR Method 2: Mount as files
      # volumeMounts:
      #   - name: config
      #     mountPath: /etc/config
  # volumes:
  #   - name: config
  #     configMap:
  #       name: app-config
```

## 3.5 Secret YAML

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  # echo -n "admin" | base64 → YWRtaW4=
  DB_USER: YWRtaW4=
  # echo -n "secret123" | base64 → c2VjcmV0MTIz
  DB_PASS: c2VjcmV0MTIz
```

```bash
# Create imperatively (easier)
kubectl create secret generic db-creds \
  --from-literal=DB_USER=admin \
  --from-literal=DB_PASS=secret123

# Apply YAML
kubectl apply -f secret.yaml
kubectl get secret
kubectl get secret db-creds -o yaml  # See base64 values
```

**Using Secret in Pod:**

```yaml
# pod-with-secret.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
    - name: app
      image: nginx:alpine
      env:
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-creds
              key: DB_USER
        - name: DB_PASS
          valueFrom:
            secretKeyRef:
              name: db-creds
              key: DB_PASS
```

## 3.6 Namespace YAML

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
  labels:
    project: demo
    environment: development
```

```bash
kubectl apply -f namespace.yaml
kubectl get namespace
kubectl get namespace my-namespace
```

---

# PART 4: How to Read Official Docs for YAML Reference

## 4.1 Official Documentation Links

| Resource | Docs Link | Quick Tip |
|----------|-----------|-----------|
| Pod | https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#pod-v1 | Start here for all container specs |
| Deployment | https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#deployment-v1-apps | Has replicas, strategy, template |
| Service | https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#service-v1 | Types: ClusterIP, NodePort, LoadBalancer |
| ConfigMap | https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#configmap-v1 | Simple key-value storage |
| Secret | https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#secret-v1 | base64 encoding, various types |
| Namespace | https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#namespace-v1 | Metadata only |

## 4.2 How to Navigate the API Reference

```
┌─────────────────────────────────────────────────────────────────┐
│  KUBERNETES API REFERENCE STRUCTURE                             │
│                                                                 │
│  1. Find your resource kind (e.g., "Deployment")              │
│    → Shows apiVersion, kind                                    │
│                                                                 │
│  2. Look at "Spec" for the main fields                        │
│    → replicas, selector, template                              │
│                                                                 │
│  3. Look at "Template" for pod spec                           │
│    → containers, volumes, env, etc.                           │
│                                                                 │
│  4. Check "Status" to understand what K8s returns            │
│    → phase, conditions, podIP, etc.                           │
│                                                                 │
│  5. Look for "Required" fields - must be present              │
│                                                                 │
│  6. Click on nested objects to drill down                    │
│    → containerSpec → env → envVar                             │
└─────────────────────────────────────────────────────────────────┘
```

## 4.3 Example: Finding "imagePullPolicy"

```
Search: "imagePullPolicy" in Pod spec
→ Found in container spec
→ Options: Always, IfNotPresent, Never
→ Default: IfNotPresent (for tagged images)
           Always (for :latest)
```

## 4.4 Common YAML Patterns

```yaml
# Always required fields
apiVersion: v1          # or apps/v1, batch/v1
kind: Pod              # or Deployment, Service, etc.
metadata:
  name: <unique-name>  # Required!
  namespace: <optional> # Defaults to "default"

# Most specs have:
spec:
  # Selector pattern (Deployment/Service/StatefulSet)
  selector:
    matchLabels:
      app: my-app

  # Pod template (Deployment/StatefulSet/DaemonSet)
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: container-name
          image: image:tag
```

---

# PART 5: Deploy Python App

## 5.1 Verify Environment

```bash
# On controlplane
kubectl cluster-info

# Check nodes
kubectl get nodes -o wide

# See system pods
kubectl get pods -A | head -20
```

## 5.2 Step 1: Build Docker Images

```bash
cd /root/demo-docker/k8s-projects/project-1-python

# Build both images
docker build -t python-backend:v1 ./backend
docker build -t python-frontend:v1 ./frontend

# Verify
docker images | grep -E "python-backend|python-frontend"
```

## 5.3 Step 2: Copy Images to Worker Node

```bash
# On controlplane - save images
docker save python-backend:v1 python-frontend:v1 -o /tmp/images.tar

# Copy to node01
scp /tmp/images.tar node01:/tmp/

# On node01 - import to containerd
ssh node01 "ctr -n k8s.io images import /tmp/images.tar"

# Verify on node01
ssh node01 "ctr -n k8s.io images ls | grep python"

# Verify on controlplane (crictl sees what kubelet sees)
crictl images | grep python
```

## 5.4 Step 3: Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml

# Verify
kubectl get namespace python-demo
```

## 5.5 Step 4: Create ConfigMap

```bash
kubectl apply -f k8s/configmap.yaml

# Verify
kubectl get configmap -n python-demo
kubectl describe configmap python-backend-config -n python-demo
```

## 5.6 Step 5: Deploy Backend

```bash
kubectl apply -f k8s/backend-deployment.yaml

# Watch pods come up
kubectl get pods -n python-demo -w

# Check status
kubectl get pods -n python-demo -o wide
kubectl get rs -n python-demo
kubectl get deployments -n python-demo
```

## 5.7 Step 6: Create Backend Service

```bash
kubectl apply -f k8s/backend-service.yaml

# Verify
kubectl get svc -n python-demo
kubectl get endpoints -n python-demo  # Should show pod IPs

# Test internal DNS
kubectl run test --image=busybox --rm -it --restart=Never -n python-demo -- \
  wget -qO- http://python-backend-svc:8000/api/hello
```

## 5.8 Step 7: Deploy Frontend

```bash
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# Verify all
kubectl get all -n python-demo

# Check frontend is accessible
kubectl get nodes -o wide  # Get node IP
curl http://<NODE-IP>:30080
curl http://<NODE-IP>:30080/api/hello
```

## 5.9 Step 8: Demonstrate Scaling

```bash
# Scale backend to 4 replicas
kubectl scale deployment python-backend --replicas=4 -n python-demo

# Verify pods on different nodes
kubectl get pods -n python-demo -o wide

# Test load balancing
for i in {1..8}; do
  kubectl run test$i --image=busybox --rm -it --restart=Never -n python-demo -- \
    wget -qO- http://python-backend-svc:8000/api/hello | grep hostname
done
```

## 5.10 Step 9: Cleanup

```bash
# Delete all resources
kubectl delete -f k8s/

# Or delete entire namespace
kubectl delete namespace python-demo

# Verify cleanup
kubectl get all -n python-demo
```

---

# Summary Checklist

## Imperative Commands (Quick Testing)
```bash
kubectl run <name> --image=<image>
kubectl create deployment <name> --image=<image> --replicas=N
kubectl expose deployment <name> --port=<port> --type=NodePort
kubectl scale deployment <name> --replicas=N
kubectl delete <type> <name>
```

## Declarative YAML (Production)
```bash
kubectl apply -f <file.yaml>
kubectl get <type> -n <namespace>
kubectl describe <type> <name> -n <namespace>
kubectl delete -f <file.yaml>
```

## Common Debug Commands
```bash
kubectl get pods -n <ns>
kubectl describe pod <name> -n <ns>
kubectl logs <name> -n <ns>
kubectl exec -it <name> -- sh -n <ns>
kubectl get events -n <ns> --sort-by='.lastTimestamp'
```

---

# Key Teaching Points

| Concept | Remember |
|---------|----------|
| Pod | Smallest deployable unit, wraps containers |
| Deployment | Manages ReplicaSet, provides self-healing + updates |
| Service | Stable IP + DNS for pod traffic |
| ConfigMap | Non-sensitive config as key-value |
| Secret | Sensitive data (base64, not encrypted) |
| Namespace | Resource isolation |
| kubectl apply | Declarative (desired state) |
| kubectl run/create | Imperative (do this now) |

---

# Production Best Practices (From docker-kubernetes skill)

1. **One process per container** - A container should do exactly one thing
2. **Never use :latest tag** - Pin image tags in production
3. **Always use health probes** - liveness + readiness for every deployment
4. **Set resource requests/limits** - requests for scheduler, limits for protection
5. **Use exec form CMD** - `CMD ["node", "server.js"]` not `CMD node server.js`
6. **Declarative over imperative** - All cluster state in YAML, checked into git

---

