# Part 7f: Kubernetes Storage and Scalability

## 7f.1 Storage Classes Explained

StorageClasses define **types** of storage available in your cluster.

```
┌──────────────────────────────────────────────────────────────┐
│                   STORAGE CLASS WORKFLOW                      │
│                                                               │
│  Developer ──▶ PVC (Request) ──▶ StorageClass ──▶ PV Created│
│                "I need 10GB"     "Use AWS EBS"   (Automatic) │
│                                                               │
│  Without StorageClass: Admin manually creates PVs            │
│  With StorageClass: Automatic (Dynamic Provisioning)         │
└──────────────────────────────────────────────────────────────┘
```

### Cloud Provider Storage Classes

#### AWS EBS
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3                # SSD type
  iopsPerGB: "50"
  encrypted: "true"
volumeBindingMode: WaitForFirstConsumer
```

#### GCP Persistent Disk
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
  replication-type: regional-pd
```

---

### On-Premise Storage Classes

#### local-path (Rancher/K3s)
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-path
provisioner: rancher.io/local-path
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
```

```
┌──────────────────────────────────────────────────────────────┐
│                  LOCAL-PATH STORAGE                           │
│                                                               │
│  Node 1                    Node 2                             │
│  ┌──────────────┐         ┌──────────────┐                   │
│  │/opt/local-   │         │/opt/local-   │                   │
│  │path-provisioner       │path-provisioner                   │
│  │  /pvc-abc    │         │  /pvc-xyz    │                   │
│  │  /pvc-def    │         │              │                   │
│  └──────────────┘         └──────────────┘                   │
│        ▲                         ▲                            │
│        │                         │                            │
│  ┌─────┴────┐              ┌─────┴────┐                      │
│  │ Pod + PVC│              │ Pod + PVC│                       │
│  └──────────┘              └──────────┘                       │
│                                                               │
│  Note: Volume is tied to one node!                           │
│  Pod must run on same node as volume                         │
└──────────────────────────────────────────────────────────────┘
```

**Limitation:** Not portable between nodes (pod stuck to one node).

#### NFS (Shared Storage)
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-storage
provisioner: nfs.csi.k8s.io
parameters:
  server: nfs-server.example.com
  share: /exports
```

```
┌──────────────────────────────────────────────────────────────┐
│                      NFS STORAGE                              │
│                                                               │
│  ┌──────────────────────────────────────────────────┐        │
│  │            NFS Server                             │        │
│  │            /exports/pvc-abc                       │        │
│  └─────────────────┬────────────────────────────────┘        │
│                    │                                          │
│         ┌──────────┼──────────┐                               │
│         ▼          ▼          ▼                               │
│    Node 1      Node 2      Node 3                             │
│    ┌──────┐   ┌──────┐   ┌──────┐                            │
│    │ Pod  │   │ Pod  │   │ Pod  │                            │
│    │+PVC  │   │+PVC  │   │+PVC  │                            │
│    └──────┘   └──────┘   └──────┘                            │
│                                                               │
│  Pods on any node can access same volume                     │
│  Good for: ReadWriteMany scenarios                           │
└──────────────────────────────────────────────────────────────┘
```

---

## 7f.2 PVC with StorageClass

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: local-path  # Use this StorageClass
  resources:
    requests:
      storage: 10Gi
```

**StorageClass creates PV automatically:**
```bash
kubectl get pvc
# NAME           STATUS   VOLUME                 CAPACITY   STORAGECLASS
# postgres-pvc   Bound    pvc-abc123             10Gi       local-path

kubectl get pv
# NAME        CAPACITY   ACCESS MODES   STORAGECLASS   STATUS
# pvc-abc123  10Gi       RWO            local-path     Bound
```

---

## 7f.3 Access Modes

| Mode              | Abbreviation | Description                |
| ----------------- | ------------ | -------------------------- |
| **ReadWriteOnce** | RWO          | Single node, read-write    |
| **ReadOnlyMany**  | ROX          | Multiple nodes, read-only  |
| **ReadWriteMany** | RWX          | Multiple nodes, read-write |

```
┌──────────────────────────────────────────────────────────────┐
│                      ACCESS MODES                             │
│                                                               │
│  RWO (Block storage like AWS EBS):                           │
│  One pod (on one node) can mount                             │
│  ┌────────┐                                                   │
│  │ Pod ✓  │──▶ Volume                                        │
│  └────────┘                                                   │
│  ┌────────┐                                                   │
│  │ Pod ✗  │ Cannot mount (different node)                    │
│  └────────┘                                                   │
│                                                               │
│  RWX (Network storage like NFS):                             │
│  Multiple pods can mount                                      │
│  ┌────────┐  ┌────────┐                                      │
│  │ Pod ✓  │  │ Pod ✓  │──▶ Volume                            │
│  └────────┘  └────────┘                                      │
└──────────────────────────────────────────────────────────────┘
```

---

## 7f.4 Horizontal Pod Autoscaler (HPA)

Automatically scale pods based on metrics.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

```
┌──────────────────────────────────────────────────────────────┐
│                      HPA IN ACTION                            │
│                                                               │
│  Load increases:                                              │
│  CPU: 30% ──▶ 50% ──▶ 80%                                    │
│                        ▲ Exceeds 70% threshold                │
│                        │                                      │
│  Replicas: 2 ────────▶ 4 (HPA scales up)                     │
│                                                               │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                        │
│  │ Pod  │ │ Pod  │ │ Pod  │ │ Pod  │                        │
│  │ 80%  │ │ 80%  │ │ New  │ │ New  │                        │
│  └──────┘ └──────┘ └──────┘ └──────┘                        │
│                                                               │
│  Load decreases:                                              │
│  CPU: 40% (below threshold)                                   │
│  Replicas: 4 ────────▶ 2 (HPA scales down after cooldown)   │
└──────────────────────────────────────────────────────────────┘
```

**Requirements:**
- Metrics Server installed
- Resource requests defined in pods

```bash
# Check HPA status
kubectl get hpa
kubectl describe hpa backend-hpa
```

---

## 7f.5 Vertical Pod Autoscaler (VPA)

Adjusts resource requests/limits for pods.

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: backend-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  updatePolicy:
    updateMode: "Auto"  # Recreate pods with new resources
  resourcePolicy:
    containerPolicies:
    - containerName: app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2
        memory: 2Gi
```

**HPA vs VPA:**
|            | HPA              | VPA                       |
| ---------- | ---------------- | ------------------------- |
| **What**   | More/fewer pods  | Bigger/smaller pods       |
| **When**   | Traffic spikes   | Resource tuning           |
| **Metric** | CPU/memory usage | Historical usage patterns |

---

## 7f.6 Cluster Autoscaler

Adds/removes nodes based on pending pods.

```
┌──────────────────────────────────────────────────────────────┐
│               CLUSTER AUTOSCALER                              │
│                                                               │
│ Scenario: Too many pods, not enough nodes                    │
│                                                               │
│  ┌────────┐ ┌────────┐           ┌────────┐                 │
│  │ Node 1 │ │ Node 2 │           │ Pod    │                 │
│  │  Full  │ │  Full  │           │Pending │ ← No space!     │
│  └────────┘ └────────┘           └────────┘                 │
│                                                               │
│  Cluster Autoscaler detects pending pods                     │
│                 │                                             │
│                 ▼                                             │
│  Requests cloud provider to add node                         │
│                 │                                             │
│                 ▼                                             │
│  ┌────────┐ ┌────────┐ ┌────────┐                           │
│  │ Node 1 │ │ Node 2 │ │ Node 3 │ ← New!                    │
│  │  Full  │ │  Full  │ │ Pod ✓  │                           │
│  └────────┘ └────────┘ └────────┘                           │
└──────────────────────────────────────────────────────────────┘
```

**On-premise:** Requires infrastructure automation (e.g., Terraform + kubeadm).

---

## 7f.7 Resource Requests vs Limits

```yaml
containers:
- name: app
  resources:
    requests:      # Minimum guaranteed
      cpu: "250m"
      memory: "256Mi"
    limits:        # Maximum allowed
      cpu: "500m"
      memory: "512Mi"
```

```
┌──────────────────────────────────────────────────────────────┐
│              REQUESTS VS LIMITS                               │
│                                                               │
│  ┌────────────────────────────────────────┐                  │
│  │ Node Capacity: 4 CPU, 8GB RAM         │                  │
│  ├────────────────────────────────────────┤                  │
│  │ Pod 1: Request 1 CPU, Limit 2 CPU     │ ◄─ Scheduled     │
│  │ Pod 2: Request 1 CPU, Limit 2 CPU     │ ◄─ Scheduled     │
│  │ Pod 3: Request 1 CPU, Limit 2 CPU     │ ◄─ Scheduled     │
│  │ Pod 4: Request 1 CPU, Limit 2 CPU     │ ◄─ Scheduled     │
│  │ Pod 5: Request 1 CPU, Limit 2 CPU     │ ◄─ Pending!      │
│  └────────────────────────────────────────┘   (No capacity)  │
│                                                               │
│  Scheduler checks: Requests sum (4 CPU) fits in node         │
│  Runtime:          Pods can burst up to Limits (2 CPU each)  │
│  If exceed limit:  Container killed (OOMKilled)              │
└──────────────────────────────────────────────────────────────┘
```

---

## 7f.8 Scalability Best Practices

### 1. Set Resource Requests
```yaml
# Always define requests for predictable scheduling
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
```

### 2. Use HPA for Stateless Apps
```yaml
# Auto-scale web servers, backends
kind: HorizontalPodAutoscaler
```

### 3. Use StatefulSets for Stateful Apps
```yaml
# Manual scaling for databases
kubectl scale statefulset postgres --replicas=3
```

### 4. PodDisruptionBudget
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: backend-pdb
spec:
  minAvailable: 2  # Keep at least 2 pods during disruptions
  selector:
    matchLabels:
      app: backend
```

---

**Next:** [Part 7g: On-Premise vs Cloud K8s](./07g-onpremise-vs-cloud.md)
