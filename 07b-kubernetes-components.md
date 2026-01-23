# Part 7b: Kubernetes Components Deep Dive

## 7b.1 Kubernetes Architecture - Complete View

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER                                      │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                    CONTROL PLANE (Master Node)                            │ │
│  │                                                                           │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │ │
│  │  │  API Server  │  │  Scheduler   │  │  Controller  │  │    etcd     │  │ │
│  │  │              │  │              │  │   Manager    │  │             │  │ │
│  │  │  - REST API  │  │  - Watches   │  │              │  │  - Key/Val  │  │ │
│  │  │  - Auth      │  │    for new   │  │  - Node      │  │    Store    │  │ │
│  │  │  - Validation│  │    pods      │  │    Controller│  │  - Raft     │  │ │
│  │  │  - Admission │  │  - Assigns   │  │  - Replication│  │    Consensus│  │ │
│  │  │    Control   │  │    to nodes  │  │    Controller│  │  - Cluster  │  │ │
│  │  │              │  │  - Filters   │  │  - Endpoint  │  │    State    │  │ │
│  │  │              │  │  - Scores    │  │    Controller│  │             │  │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬───────┘  │ │
│  │         │                  │                  │                │          │ │
│  │         └──────────────────┴──────────────────┴────────────────┘          │ │
│  │                                     │                                      │ │
│  └─────────────────────────────────────┼──────────────────────────────────────┘ │
│                                        │                                        │
│                                        ▼ (Secure API)                          │
│  ┌────────────────────────┐  ┌────────────────────────┐  ┌──────────────────┐│
│  │   WORKER NODE 1        │  │   WORKER NODE 2        │  │  WORKER NODE 3   ││
│  │                        │  │                        │  │                  ││
│  │  ┌──────────────────┐  │  │  ┌──────────────────┐  │  │  ┌─────────────┐││
│  │  │  kubelet         │  │  │  │  kubelet         │  │  │  │  kubelet    │││
│  │  │  - Pod lifecycle │  │  │  │  - Pod lifecycle │  │  │  │  -Pod lifecy│││
│  │  │  - Health checks │  │  │  │  - Health checks │  │  │  │  -Health chk│││
│  │  │  - Reports to API│  │  │  │  - Reports to API│  │  │  │  -Reports   │││
│  │  └──────────────────┘  │  │  └──────────────────┘  │  │  └─────────────┘││
│  │  ┌──────────────────┐  │  │  ┌──────────────────┐  │  │  ┌─────────────┐││
│  │  │  kube-proxy      │  │  │  │  kube-proxy      │  │  │  │  kube-proxy │││
│  │  │  - iptables rules│  │  │  │  - iptables rules│  │  │  │  -iptables  │││
│  │  │  - Service routing│ │  │  │  - Service routing│ │  │  │  -Service rt│││
│  │  └──────────────────┘  │  │  └──────────────────┘  │  │  └─────────────┘││
│  │  ┌──────────────────┐  │  │  ┌──────────────────┐  │  │  ┌─────────────┐││
│  │  │  Container       │  │  │  │  Container       │  │  │  │  Container  │││
│  │  │  Runtime         │  │  │  │  Runtime         │  │  │  │  Runtime    │││
│  │  │  (containerd)    │  │  │  │  (containerd)    │  │  │  │(containerd) │││
│  │  └──────────────────┘  │  │  └──────────────────┘  │  │  └─────────────┘││
│  │  ┌──────────────────┐  │  │  ┌──────────────────┐  │  │  ┌─────────────┐││
│  │  │  Pods            │  │  │  │  Pods            │  │  │  │  Pods       │││
│  │  │  □ □ □           │  │  │  │  □ □             │  │  │  │  □ □ □      │││
│  │  └──────────────────┘  │  │  └──────────────────┘  │  │  └─────────────┘││
│  └────────────────────────┘  └────────────────────────┘  └──────────────────┘│
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7b.2 Control Plane Components

### API Server (kube-apiserver)
**Purpose:** Front-end for Kubernetes control plane.

```
┌──────────────────────────────────────────────────────────────┐
│                      API SERVER FLOW                          │
│                                                               │
│  kubectl apply ──▶ API Server ──▶ Authentication             │
│                         │                                     │
│                         ▼                                     │
│                   Authorization (RBAC)                        │
│                         │                                     │
│                         ▼                                     │
│                   Admission Controllers                       │
│                         │                                     │
│                         ▼                                     │
│                   Validation                                  │
│                         │                                     │
│                         ▼                                     │
│                   Write to etcd                               │
│                         │                                     │
│                         ▼                                     │
│                   Notify watchers (controllers)               │
└──────────────────────────────────────────────────────────────┘
```

**Responsibilities:**
- Exposes Kubernetes API (REST)
- Authenticates users/service accounts
- Authorizes requests (RBAC)
- Validates and admits objects
- Persists state to etcd
- Only component that talks to etcd

**Check if running:**
```bash
kubectl get pods -n kube-system | grep apiserver
```

---

### Scheduler (kube-scheduler)
**Purpose:** Assigns pods to nodes.

```
┌──────────────────────────────────────────────────────────────┐
│                    SCHEDULING PROCESS                         │
│                                                               │
│  New Pod (unassigned) ──▶ Scheduler Watches API              │
│                                │                              │
│                                ▼                              │
│                           FILTERING                           │
│                      (Remove unsuitable nodes)                │
│                                │                              │
│                   ┌────────────┴────────────┐                │
│                   ▼                         ▼                │
│         Node has resources?    Node has right labels?        │
│         Node is ready?         Pod tolerates taints?         │
│                   │                         │                │
│                   └────────────┬────────────┘                │
│                                ▼                              │
│                            SCORING                           │
│                    (Rank remaining nodes)                     │
│                                │                              │
│                   Score by:                                   │
│                   - Resource balance                          │
│                   - Spread pods                               │
│                   - Affinity/Anti-affinity                    │
│                                │                              │
│                                ▼                              │
│                    Select highest score node                  │
│                                │                              │
│                                ▼                              │
│                    Bind pod to node (API call)                │
└──────────────────────────────────────────────────────────────┘
```

**Example:** Pod needs 2 CPUs and 4GB RAM
1. Filter: Remove nodes with insufficient resources
2. Score: Prefer nodes with balanced resource usage
3. Bind: Assign to best scoring node

---

### Controller Manager (kube-controller-manager)
**Purpose:** Runs controller processes that regulate cluster state.

```
┌──────────────────────────────────────────────────────────────┐
│              CONTROLLER MANAGER (Multiple Controllers)        │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Node Controller                                        │ │
│  │  - Watches for node failures                            │ │
│  │  - Marks nodes as NotReady after 40s                    │ │
│  │  - Evicts pods after 5m                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Replication Controller                                 │ │
│  │  - Ensures correct number of pod replicas              │ │
│  │  - Creates/deletes pods to match desired state         │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Endpoint Controller                                    │ │
│  │  - Populates Endpoints object (joins Services & Pods)  │ │
│  │  - Updates when pods start/stop                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  ServiceAccount Controller                              │ │
│  │  - Creates default ServiceAccount for namespaces       │ │
│  │  - Creates API tokens for ServiceAccounts              │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

**Control Loop Pattern:**
```
┌─────────────────────────────────────────────┐
│  Controller Loop (every controller follows) │
│                                              │
│  1. Watch resources via API                 │
│  2. Compare actual vs desired state         │
│  3. Take action to reconcile                │
│  4. Repeat forever                          │
└─────────────────────────────────────────────┘
```

---

### etcd
**Purpose:** Distributed key-value store for cluster state.

```
┌──────────────────────────────────────────────────────────────┐
│                        etcd CLUSTER                           │
│                                                               │
│  ┌────────┐  ┌────────┐  ┌────────┐                         │
│  │ etcd 1 │← │ etcd 2 │ →│ etcd 3 │  (Raft Consensus)       │
│  │Leader  │  │Follower│  │Follower│                          │
│  └───┬────┘  └────────┘  └────────┘                         │
│      │                                                        │
│      ▼                                                        │
│  Stores:                                                      │
│  /registry/pods/default/nginx-abc123                         │
│  /registry/services/default/backend                          │
│  /registry/secrets/default/db-password                       │
│  /registry/configmaps/default/app-config                     │
│  ...                                                          │
└──────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- Consistent and highly-available
- Source of truth for cluster state
- Uses Raft consensus algorithm
- Only API server writes to etcd
- Backup etcd = backup entire cluster

**Backup etcd:**
```bash
ETCDCTL_API=3 etcdctl snapshot save backup.db
```

---

## 7b.3 Worker Node Components

### kubelet
**Purpose:** Agent that runs on each node, manages pod lifecycle.

```
┌──────────────────────────────────────────────────────────────┐
│                      KUBELET WORKFLOW                         │
│                                                               │
│  API Server ──▶ kubelet receives pod spec                    │
│                     │                                         │
│                     ▼                                         │
│              Pull container images                            │
│                     │                                         │
│                     ▼                                         │
│              Create containers (via CRI)                      │
│                     │                                         │
│                     ▼                                         │
│              Mount volumes                                    │
│                     │                                         │
│                     ▼                                         │
│              Start containers                                 │
│                     │                                         │
│                     ▼                                         │
│              Run health checks                                │
│                     │                                         │
│                     ▼                                         │
│              Report status to API server                      │
│                     │                                         │
│                     └──▶ (Repeat monitoring)                  │
└──────────────────────────────────────────────────────────────┘
```

**Responsibilities:**
- Watches API server for pod assignments
- Pulls images if not present
- Mounts volumes
- Runs containers via container runtime
- Probes (liveness, readiness, startup)
- Reports pod and node status
- Garbage collection of old containers/images

---

### kube-proxy
**Purpose:** Network proxy maintaining network rules on nodes.

```
┌──────────────────────────────────────────────────────────────┐
│                   KUBE-PROXY ROUTING                          │
│                                                               │
│  Service: backend (ClusterIP: 10.96.1.100)                   │
│  Selector: app=backend                                        │
│                                                               │
│  kube-proxy creates iptables rules:                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Traffic to 10.96.1.100:8000 → {                       │  │
│  │    25% → Pod 192.168.1.10:8000                         │  │
│  │    25% → Pod 192.168.1.11:8000                         │  │
│  │    25% → Pod 192.168.1.12:8000                         │  │
│  │    25% → Pod 192.168.1.13:8000                         │  │
│  │  }                                                      │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  Modes:                                                       │
│  - iptables (default, most common)                           │
│  - ipvs (better performance, more features)                  │
│  - userspace (legacy, slow)                                  │
└──────────────────────────────────────────────────────────────┘
```

**Responsibilities:**
- Watches Services and Endpoints
- Updates iptables/ipvs rules
- Load balances traffic to pods
- Implements ClusterIP routing

---

### Container Runtime (containerd/CRI-O)
**Purpose:** Software that runs containers.

```
┌──────────────────────────────────────────────────────────────┐
│              CONTAINER RUNTIME INTERFACE (CRI)                │
│                                                               │
│  kubelet ──▶ CRI (gRPC) ──▶ Container Runtime                │
│                                   │                           │
│                                   ├──▶ containerd             │
│                                   ├──▶ CRI-O                  │
│                                   └──▶ Docker (deprecated)    │
│                                                               │
│  Container Runtime:                                           │
│  1. Pull image from registry                                 │
│  2. Unpack image layers                                      │
│  3. Create Linux namespaces & cgroups                        │
│  4. Start container process                                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 7b.4 Add-On Components

### DNS (CoreDNS)
Provides DNS-based service discovery.

```yaml
# Pod can reach service by name
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    env:
    - name: DB_HOST
      value: "postgres.default.svc.cluster.local"
    # Or just: postgres
```

### CNI (Container Network Interface)
Examples: Calico, Flannel, Weave

Provides pod networking:
- Assigns IP addresses to pods
- Routes traffic between pods
- Enforces network policies

---

**Next:** [Part 7c: Kubernetes Objects](./07c-kubernetes-objects.md)
