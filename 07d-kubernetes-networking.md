# Part 7d: Kubernetes Services and Networking

## 7d.1 Why Services?

Pods are ephemeral - they get IPs that change when they restart.

```
┌──────────────────────────────────────────────────────────────┐
│              PROBLEM: POD IPS CHANGE                          │
│                                                               │
│  Day 1:                     Day 2 (pod restarted):           │
│  frontend → backend         frontend → backend               │
│  calls 192.168.1.10:8000    192.168.1.10 gone! ❌           │
│                             New IP: 192.168.1.25             │
│                                                               │
│              SOLUTION: USE SERVICE                            │
│                                                               │
│  frontend → Service → backend (any IP)                       │
│  calls backend:8000  ✓                                       │
└──────────────────────────────────────────────────────────────┘
```

**Service provides:**
- Stable DNS name
- Stable IP (ClusterIP)
- Load balancing across pods
- Service discovery

---

## 7d.2 Service Types Detailed

### 1. ClusterIP (Default)

```
┌──────────────────────────────────────────────────────────────┐
│                    CLUSTERIP SERVICE                          │
│                                                               │
│  Service: backend (ClusterIP: 10.96.1.100)                   │
│  DNS: backend.default.svc.cluster.local                      │
│                                                               │
│  ┌──────────────┐                                            │
│  │  frontend    │─────────┐                                  │
│  │  pod         │         │                                  │
│  └──────────────┘         ▼                                  │
│                    backend:8000                               │
│                    (10.96.1.100:8000)                        │
│                           │                                   │
│                ┌──────────┼───────────┐                      │
│                ▼          ▼           ▼                      │
│         ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│         │ Pod      │ │ Pod      │ │ Pod      │              │
│         │192.168.1 │ │192.168.2 │ │192.168.3 │              │
│         │  .10     │ │  .11     │ │  .12     │              │
│         └──────────┘ └──────────┘ └──────────┘              │
│                                                               │
│  Accessible: Inside cluster only                             │
│  Use case: Internal microservices                            │
└──────────────────────────────────────────────────────────────┘
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  type: ClusterIP        # Default
  selector:
    app: backend         # Finds pods with this label
  ports:
  - port: 8000           # Service port
    targetPort: 8000     # Pod port
```

---

### 2. NodePort

```
┌──────────────────────────────────────────────────────────────┐
│                      NODEPORT SERVICE                         │
│                                                               │
│  External Traffic                                             │
│       │                                                       │
│       ▼                                                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                      │
│  │ Node 1  │  │ Node 2  │  │ Node 3  │                      │
│  │:30001   │  │:30001   │  │:30001   │  ← Same port on all │
│  └────┬────┘  └────┬────┘  └────┬────┘                      │
│       │            │            │                            │
│       └────────────┼────────────┘                            │
│                    ▼                                          │
│            Service: backend                                   │
│            (ClusterIP: 10.96.1.100)                          │
│                    │                                          │
│         ┌──────────┼───────────┐                             │
│         ▼          ▼           ▼                             │
│    ┌────────┐ ┌────────┐ ┌────────┐                         │
│    │ Pod 1  │ │ Pod 2  │ │ Pod 3  │                         │
│    └────────┘ └────────┘ └────────┘                         │
│                                                               │
│  Access: http://any-node-ip:30001                           │
│  Port range: 30000-32767                                     │
└──────────────────────────────────────────────────────────────┘
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  type: NodePort
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
    nodePort: 30001      # Optional, auto-assigned if omitted
```

---

### 3. LoadBalancer (Cloud)

```
┌──────────────────────────────────────────────────────────────┐
│                  LOADBALANCER SERVICE (Cloud)                 │
│                                                               │
│  Internet                                                     │
│      │                                                        │
│      ▼                                                        │
│  ┌──────────────────────────┐                                │
│  │   Cloud Load Balancer    │  ← Provisioned by cloud       │
│  │   (External IP: 1.2.3.4) │                                │
│  └────────────┬─────────────┘                                │
│               │                                               │
│               ▼                                               │
│         Service: frontend                                     │
│         (ClusterIP: 10.96.2.50)                              │
│               │                                               │
│    ┌──────────┼──────────┐                                   │
│    ▼          ▼          ▼                                   │
│  ┌────┐    ┌────┐    ┌────┐                                 │
│  │Pod │    │Pod │    │Pod │                                 │
│  └────┘    └────┘    └────┘                                 │
│                                                               │
│  AWS: Creates ELB/ALB/NLB                                    │
│  GCP: Creates L4/L7 load balancer                            │
│  Azure: Creates Azure Load Balancer                          │
│  On-premise: Requires MetalLB or similar                     │
└──────────────────────────────────────────────────────────────┘
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
```

**On-premise:** Use MetalLB or stays in `<pending>` state.

---

### 4. ExternalName

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-database
spec:
  type: ExternalName
  externalName: my-db.rds.amazonaws.com
```

**Use case:** Give external service a DNS name inside cluster:
```bash
# Pods call: external-database.default.svc.cluster.local
# Resolves to: my-db.rds.amazonaws.com
```

---

## 7d.3 Service Discovery - DNS

```
┌──────────────────────────────────────────────────────────────┐
│                    SERVICE DNS RESOLUTION                     │
│                                                               │
│  Full DN

S form:                                                │
│  <service>.<namespace>.svc.cluster.local                     │
│                                                               │
│  Examples:                                                    │
│  backend.default.svc.cluster.local                           │
│  postgres.production.svc.cluster.local                       │
│                                                               │
│  Short forms (from same namespace):                          │
│  backend                    ✓ (same namespace)               │
│  backend.default            ✓ (specify namespace)            │
│  backend.default.svc        ✓ (with svc)                     │
│                                                               │
│  Pod DNS (StatefulSet):                                      │
│  <pod-name>.<service>.<namespace>.svc.cluster.local          │
│  postgres-0.postgres.default.svc.cluster.local               │
└──────────────────────────────────────────────────────────────┘
```

---

## 7d.4 Endpoints - Connecting Services to Pods

```
┌──────────────────────────────────────────────────────────────┐
│               SERVICE → ENDPOINTS → PODS                      │
│                                                               │
│  Service: backend                                             │
│  selector: app=backend  ──────┐                              │
│                                │                              │
│  Endpoints: backend      ◄─────┘ (Created automatically)     │
│  Addresses:                                                   │
│  - 192.168.1.10:8000 ────────▶ Pod 1 (app=backend)           │
│  - 192.168.1.11:8000 ────────▶ Pod 2 (app=backend)           │
│  - 192.168.1.12:8000 ────────▶ Pod 3 (app=backend)           │
│                                                               │
│  kube-proxy uses endpoints to update iptables/ipvs           │
└──────────────────────────────────────────────────────────────┘
```

```bash
# View endpoints
kubectl get endpoints backend

# Output:
# NAME      ENDPOINTS                                    AGE
# backend   192.168.1.10:8000,192.168.1.11:8000,...     5m
```

---

## 7d.5 Headless Service

No ClusterIP assigned - returns pod IPs directly.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  clusterIP: None          # Headless!
  selector:
    app: postgres
  ports:
  - port: 5432
```

```bash
# DNS lookup returns ALL pod IPs
nslookup postgres.default.svc.cluster.local
# Returns:
# 192.168.1.10
# 192.168.1.11
# 192.168.1.12
```

**Use case:** StatefulSets where you need direct pod access.

---

## 7d.6 Kubernetes Networking Model

```
┌──────────────────────────────────────────────────────────────┐
│              KUBERNETES NETWORKING RULES                      │
│                                                               │
│  1. All pods can communicate with all other pods             │
│     without NAT                                               │
│                                                               │
│  2. All nodes can communicate with all pods                  │
│     without NAT                                               │
│                                                               │
│  3. The IP a pod sees itself as is the same IP               │
│     others see it as                                          │
│                                                               │
│  Implementation: CNI plugins (Calico, Flannel, Weave)        │
└──────────────────────────────────────────────────────────────┘
```

### Pod-to-Pod Communication

```
┌──────────────────────────────────────────────────────────────┐
│                   POD-TO-POD NETWORKING                       │
│                                                               │
│  Node 1                          Node 2                       │
│  ┌──────────────────┐           ┌──────────────────┐         │
│  │  Pod A           │           │  Pod B           │         │
│  │  192.168.1.10    │           │  192.168.2.20    │         │
│  └────────┬─────────┘           └──────┬───────────┘         │
│           │                            │                      │
│           │    ┌──────────────┐       │                      │
│           └───▶│ CNI Plugin   │◄──────┘                      │
│                │ (Calico/     │                               │
│                │  Flannel)    │                               │
│                └──────────────┘                               │
│                       │                                       │
│                       ▼                                       │
│            Creates overlay network                            │
│            or routes between nodes                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 7d.7 Network Policies

Control traffic between pods (firewall rules).

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  
  policyTypes:
  - Ingress
  - Egress
  
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend    # Only frontend can access backend
    ports:
    - protocol: TCP
      port: 8000
  
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database    # Backend can only access database
    ports:
    - protocol: TCP
      port: 5432
```

```
┌──────────────────────────────────────────────────────────────┐
│                    NETWORK POLICY EFFECT                      │
│                                                               │
│  ┌──────────┐                  ┌──────────┐                  │
│  │frontend  │─────✓───────────▶│ backend  │                  │
│  └──────────┘                  └────┬─────┘                  │
│                                      │                        │
│                                      ✓                        │
│                                      ▼                        │
│  ┌──────────┐                  ┌──────────┐                  │
│  │  other   │─────✗───────────▶│ database │                  │
│  │  pod     │   (blocked)       └──────────┘                 │
│  └──────────┘                                                 │
└──────────────────────────────────────────────────────────────┘
```

**Note:** Requires CNI plugin that supports Network Policies (Calico, Weave).

---

**Next:** [Part 7e: Kubernetes RBAC](./07e-kubernetes-rbac.md)
