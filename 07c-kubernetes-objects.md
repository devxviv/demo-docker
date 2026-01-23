# Part 7c: Kubernetes Objects Deep Dive

## 7c.1 Object Hierarchy and Relationships

```
┌──────────────────────────────────────────────────────────────────┐
│                  KUBERNETES OBJECT HIERARCHY                      │
│                                                                   │
│  Namespace                                                        │
│  └─┬─ Workload Resources                                         │
│    ├─ Pod (smallest unit)                                        │
│    ├─ ReplicaSet (manages identical pods)                        │
│    ├─ Deployment (manages ReplicaSets)                           │
│    ├─ StatefulSet (pods with identity)                           │
│    ├─ DaemonSet (one pod per node)                               │
│    ├─ Job (run to completion)                                    │
│    └─ CronJob (scheduled jobs)                                   │
│                                                                   │
│  └─┬─ Service Resources                                          │
│    ├─ Service (stable endpoint)                                  │
│    ├─ Endpoints (pod IPs for service)                            │
│    └─ Ingress (HTTP routing)                                     │
│                                                                   │
│  └─┬─ Config & Storage                                           │
│    ├─ ConfigMap (config data)                                    │
│    ├─ Secret (sensitive data)                                    │
│    ├─ PersistentVolume (storage)                                 │
│    └─ PersistentVolumeClaim (storage request)                    │
│                                                                   │
│  └─┬─ Access Control                                             │
│    ├─ ServiceAccount (pod identity)                              │
│    ├─ Role (namespace permissions)                               │
│    ├─ RoleBinding (assign role)                                  │
│    ├─ ClusterRole (cluster permissions)                          │
│    └─ ClusterRoleBinding (assign cluster role)                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7c.2 Pod Deep Dive

### Pod is NOT a Container
```
┌──────────────────────────────────────────────────────────────┐
│                           POD                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Shared Network Namespace (same IP)                    │  │
│  │  ┌──────────────┐  ┌──────────────┐                   │  │
│  │  │ Container 1  │  │ Container 2  │                   │  │
│  │  │   nginx:80   │  │  logger:8080 │                   │  │
│  │  │              │  │              │                   │  │
│  │  │ localhost:80 │← │localhost:8080│ (can talk)       │  │
│  │  └──────────────┘  └──────────────┘                   │  │
│  │                                                         │  │
│  │  Shared Volumes                                         │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │ /shared-data (both containers can access)        │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
│  Pod IP: 192.168.1.10                                        │
└──────────────────────────────────────────────────────────────┘
```

### Multi-Container Patterns

#### 1. Sidecar Pattern
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-with-logging
spec:
  containers:
  - name: web          # Main container
    image: nginx
    volumeMounts:
    - name: logs
      mountPath: /var/log/nginx
  
  - name: log-shipper # Sidecar
    image: fluentd
    volumeMounts:
    - name: logs
      mountPath: /logs
  
  volumes:
  - name: logs
    emptyDir: {}
```

#### 2. Ambassador Pattern
```yaml
# Local proxy to external service
containers:
- name: app
  image: myapp
  env:
  - name: DB_HOST
    value: localhost:5432  # Talks to ambassador
- name: ambassador
  image: cloud-sql-proxy   # Proxies to real DB
```

#### 3. Adapter Pattern
```yaml
# Standardizes output format
containers:
- name: app
  image: legacy-app  # Outputs custom format
- name: adapter
  image: prometheus-adapter  # Converts to Prometheus format
```

### Pod Lifecycle

```
┌──────────────────────────────────────────────────────────────┐
│                      POD LIFECYCLE                            │
│                                                               │
│  Pending ──▶ ContainerCreating ──▶ Running ──▶ Succeeded    │
│                       │                │                      │
│                       │                ▼                      │
│                       │            Failed                     │
│                       │                │                      │
│                       └────────────────┴──▶ Terminating      │
│                                                               │
│  Phase Details:                                               │
│  - Pending: Scheduled but images not pulled                  │
│  - ContainerCreating: Pulling images, creating containers    │
│  - Running: At least one container running                   │
│  - Succeeded: All containers terminated successfully          │
│  - Failed: At least one container failed                     │
│  - Unknown: Cannot determine state                           │
└──────────────────────────────────────────────────────────────┘
```

---

## 7c.3 Deployment vs ReplicaSet vs Pod

```
┌──────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT                                 │
│  (Manages rollouts, rollbacks, scaling)                       │
│  replicas: 3                                                  │
│  strategy: RollingUpdate                                      │
│  └───────────┬───────────────────────────────────────────┐  │
│              ▼                                            │   │
│  ┌────────────────────────────────────────────────────┐  │   │
│  │          REPLICASET (v2)                           │  │   │
│  │  (Ensures 3 pods running)                          │  │   │
│  │  ┌──────┐  ┌──────┐  ┌──────┐                     │  │   │
│  │  │ Pod  │  │ Pod  │  │ Pod  │                     │  │   │
│  │  │ v2   │  │ v2   │  │ v2   │                     │  │   │
│  │  └──────┘  └──────┘  └──────┘                     │  │   │
│  └────────────────────────────────────────────────────┘  │   │
│                                                           │   │
│  ┌────────────────────────────────────────────────────┐  │   │
│  │          REPLICASET (v1) - OLD                     │  │   │
│  │  (Scaled down to 0)                                │  │   │
│  │  replicas: 0                                       │  │   │
│  └────────────────────────────────────────────────────┘  │   │
└──────────────────────────────────────────────────────────────┘
```

### Why Use Deployment?
```bash
# Deployment handles:
kubectl set image deployment/app nginx=nginx:1.21  # Rolling update
kubectl rollout undo deployment/app                # Rollback
kubectl scale deployment/app --replicas=10         # Scale

# ReplicaSet only ensures count:
kubectl scale replicaset/app-v2 --replicas=5       # Manual, no rollout

# Pod is single instance:
kubectl run nginx --image=nginx                     # Just one pod
```

---

## 7c.4 StatefulSet

For applications needing stable identity and storage.

```
┌──────────────────────────────────────────────────────────────┐
│                      STATEFULSET                              │
│  (Ordered, stable network IDs and storage)                   │
│                                                               │
│  Pod: postgres-0              Pod: postgres-1                │
│  ┌─────────────────┐          ┌─────────────────┐           │
│  │ Hostname:       │          │ Hostname:       │           │
│  │ postgres-0      │          │ postgres-1      │           │
│  │                 │          │                 │           │
│  │ DNS:            │          │ DNS:            │           │
│  │ postgres-0.db   │          │ postgres-1.db   │           │
│  │ .default        │          │ .default        │           │
│  │ .svc            │          │ .svc            │           │
│  │                 │          │                 │           │
│  │ PVC:            │          │ PVC:            │           │
│  │ data-postgres-0 │          │ data-postgres-1 │           │
│  │ (10Gi)          │          │ (10Gi)          │           │
│  └─────────────────┘          └─────────────────┘           │
│                                                               │
│  Pod: postgres-2                                              │
│  ┌─────────────────┐                                         │
│  │ Hostname:       │                                         │
│  │ postgres-2      │                                         │
│  │ DNS:            │                                         │
│  │ postgres-2.db   │                                         │
│  │ PVC:            │                                         │
│  │ data-postgres-2 │                                         │
│  └─────────────────┘                                         │
│                                                               │
│  Ordering: 0 → 1 → 2 (creates in order)                     │
│  Termination: 2 → 1 → 0 (terminates reverse order)          │
└──────────────────────────────────────────────────────────────┘
```

### When to Use StatefulSet?
- Databases (PostgreSQL, MySQL, MongoDB)
- Message queues (Kafka, RabbitMQ)
- Distributed systems (Elasticsearch, Cassandra)

**NOT for stateless apps** (use Deployment)

---

## 7c.5 DaemonSet

One pod per node automatically.

```
┌──────────────────────────────────────────────────────────────┐
│                        DAEMONSET                              │
│  (Ensures one pod on every node)                             │
│                                                               │
│  Node 1             Node 2             Node 3                │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐           │
│  │          │      │          │      │          │           │
│  │ ┌──────┐ │      │ ┌──────┐ │      │ ┌──────┐ │           │
│  │ │ Pod  │ │      │ │ Pod  │ │      │ │ Pod  │ │           │
│  │ │logger│ │      │ │logger│ │      │ │logger│ │           │
│  │ └──────┘ │      │ └──────┘ │      │ └──────┘ │           │
│  │          │      │          │      │          │           │
│  └──────────┘      └──────────┘      └──────────┘           │
└──────────────────────────────────────────────────────────────┘
```

### Use Cases
- Log collectors (Fluentd, Logstash)
- Monitoring agents (Prometheus Node Exporter)
- Network plugins (Calico, Flannel)
- Storage daemons

---

## 7c.6 Job and CronJob

### Job - Run to Completion
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: database-backup
spec:
  template:
    spec:
      containers:
      - name: backup
        image: postgres:15
        command: ["pg_dump", "-h", "db", "-U", "admin", ">", "/backup/dump.sql"]
      restartPolicy: OnFailure  # Retry if fails
  backoffLimit: 4              # Max retries
  completions: 1               # Run once successfully
  parallelism: 1               # One at a time
```

### CronJob - Scheduled Jobs
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-backup
spec:
  schedule: "0 2 * * *"        # 2 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup-script:v1
          restartPolicy: OnFailure
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
```

```
┌──────────────────────────────────────────────────────────────┐
│                      CRONJOB SCHEDULE                         │
│                                                               │
│  Every day at 2 AM:                                          │
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐                            │
│  │Job │  │Job │  │Job │  │Job │                            │
│  │Day1│  │Day2│  │Day3│  │Day4│ ...                        │
│  └────┘  └────┘  └────┘  └────┘                            │
│    ✓      ✓       ✗       ✓    (Success/Fail)             │
│                   ▲                                          │
│                   └─ Kept in history (failedJobsHistory)    │
└──────────────────────────────────────────────────────────────┘
```

---

## 7c.7 ConfigMap and Secret

### ConfigMap - Non-Sensitive Config
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_host: "postgres.default.svc.cluster.local"
  log_level: "INFO"
  app.conf: |
    server {
      listen 80;
      server_name example.com;
    }
```

### Usage in Pod
```yaml
spec:
  containers:
  - name: app
    env:
    - name: DB_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database_host
    
    volumeMounts:
    - name: config
      mountPath: /etc/app/config
  
  volumes:
  - name: config
    configMap:
      name: app-config
```

### Secret - Sensitive Data
```bash
# Create secret
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=supersecret

# Use in pod
env:
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-secret
      key: password
```

---

**Next:** [Part 7d: Kubernetes Services and Networking](./07d-kubernetes-networking.md)
