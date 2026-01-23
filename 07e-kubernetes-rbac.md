# Part 7e: Kubernetes RBAC (Role-Based Access Control)

## 7e.1 RBAC Overview

RBAC controls **who** can do **what** on **which resources**.

```
┌──────────────────────────────────────────────────────────────┐
│                      RBAC COMPONENTS                          │
│                                                               │
│  WHO (Subject)          BINDING         WHAT (Role)          │
│  ┌──────────────┐         │         ┌──────────────┐         │
│  │  User        │         │         │  Role        │         │
│  │  Group       │─────────┼────────▶│  Permissions │         │
│  │ServiceAccount│         │         │  (rules)     │         │
│  └──────────────┘         │         └──────────────┘         │
│                     RoleBinding                               │
│                                                               │
│  Example:                                                     │
│  ServiceAccount "backend-sa" can "get,list,create" pods      │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 7e.2 RBAC Objects

| Object                 | Scope        | Purpose                           |
| ---------------------- | ------------ | --------------------------------- |
| **Role**               | Namespace    | Define permissions in a namespace |
| **ClusterRole**        | Cluster-wide | Define permissions across cluster |
| **RoleBinding**        | Namespace    | Assign Role to subjects           |
| **ClusterRoleBinding** | Cluster-wide | Assign ClusterRole to subjects    |

---

## 7e.3 ServiceAccount

Identity for pods (like a user account for applications).

```
┌──────────────────────────────────────────────────────────────┐
│                   SERVICEACCOUNT FLOW                         │
│                                                               │
│  1. Create ServiceAccount                                     │
│     └─▶ Kubernetes creates token Secret                      │
│                                                               │
│  2. Assign Role via RoleBinding                              │
│     └─▶ ServiceAccount gets permissions                      │
│                                                               │
│  3. Pod uses ServiceAccount                                   │
│     └─▶ Token mounted at /var/run/secrets/kubernetes.io/     │
│                                                               │
│  4. Pod calls Kubernetes API                                  │
│     └─▶ API authenticates using token                        │
│     └─▶ API authorizes based on Role                         │
└──────────────────────────────────────────────────────────────┘
```

### Example: Backend Pod Managing Other Pods

```yaml
# 1. ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: backend-sa
  namespace: default
---
# 2. Role (permissions)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-manager
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch", "create", "delete"]
---
# 3. RoleBinding (assign role to serviceaccount)
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: backend-pod-manager
  namespace: default
subjects:
- kind: ServiceAccount
  name: backend-sa
  namespace: default
roleRef:
  kind: Role
  name: pod-manager
  apiGroup: rbac.authorization.k8s.io
---
# 4. Pod uses ServiceAccount
apiVersion: v1
kind: Pod
metadata:
  name: backend
spec:
  serviceAccountName: backend-sa  # Important!
  containers:
  - name: app
    image: backend:v1
```

---

## 7e.4 Role and RoleBinding Deep Dive

### Role - Define Permissions
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
- apiGroups: [""]           # "" = core API group
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
  
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list"]
```

### Common Verbs
| Verb     | Action                 |
| -------- | ---------------------- |
| `get`    | Read single resource   |
| `list`   | List resources         |
| `watch`  | Watch for changes      |
| `create` | Create new resource    |
| `update` | Modify resource        |
| `patch`  | Partially modify       |
| `delete` | Delete resource        |
| `*`      | All verbs (dangerous!) |

### RoleBinding
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: myapp-sa
  namespace: default
- kind: User              # Can bind to users too
  name: jane
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader        # The role to assign
  apiGroup: rbac.authorization.k8s.io
```

---

## 7e.5 ClusterRole and ClusterRoleBinding

For cluster-wide permissions.

```
┌──────────────────────────────────────────────────────────────┐
│           ROLE vs CLUSTERROLE                                 │
│                                                               │
│  Role (Namespace-scoped):                                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Namespace: production                                 │  │
│  │  Can read pods in "production" only                    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ClusterRole (Cluster-wide):                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Can read pods in ALL namespaces                       │  │
│  │  Can read cluster-scoped resources (nodes, PVs)        │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### ClusterRole Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
- apiGroups: [""]
  resources: ["nodes"]     # Cluster-scoped resource
  verbs: ["get", "list"]
  
- apiGroups: [""]
  resources: ["pods"]      # Read pods in ALL namespaces
  verbs: ["get", "list"]
```

### ClusterRoleBinding
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: monitoring-nodes
subjects:
- kind: ServiceAccount
  name: prometheus
  namespace: monitoring
roleRef:
  kind: ClusterRole
  name: node-reader        # Cluster-level role
  apiGroup: rbac.authorization.k8s.io
```

---

## 7e.6 Real-World RBAC Scenarios

### Scenario 1: CI/CD Pipeline
```yaml
# Jenkins needs to deploy to production namespace
apiVersion: v1
kind: ServiceAccount
metadata:
  name: jenkins-deployer
  namespace: production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployer
  namespace: production
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "create", "update", "patch"]
- apiGroups: [""]
  resources: ["services", "configmaps", "secrets"]
  verbs: ["get", "list", "create", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: jenkins-deployer-binding
  namespace: production
subjects:
- kind: ServiceAccount
  name: jenkins-deployer
  namespace: production
roleRef:
  kind: Role
  name: deployer
  apiGroup: rbac.authorization.k8s.io
```

### Scenario 2: Developer Read-Only Access
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: developer-readonly
rules:
- apiGroups: ["", "apps", "batch"]
  resources: ["pods", "deployments", "jobs", "services"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: developers-readonly
subjects:
- kind: Group
  name: developers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: developer-readonly
  apiGroup: rbac.authorization.k8s.io
```

---

## 7e.7 Testing RBAC

```bash
# Check if ServiceAccount can perform action
kubectl auth can-i create pods \
  --as=system:serviceaccount:default:backend-sa

# Check as specific user
kubectl auth can-i delete deployments \
  --as=jane

# List all permissions for a service account
kubectl describe role pod-manager
kubectl describe rolebinding backend-pod-manager

# Impersonate to test
kubectl get pods --as=system:serviceaccount:default:backend-sa
```

---

## 7e.8 Common RBAC Patterns

### Pattern 1: Least Privilege
```yaml
# Only grant minimum required permissions
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]           # NOT "delete" unless needed
  resourceNames: ["specific-pod"]  # Optional: limit to specific resources
```

### Pattern 2: Namespace Isolation
```yaml
# Different teams, different namespaces
# Team A only accesses namespace-a
# Team B only accesses namespace-b
kind: RoleBinding  # NOT ClusterRoleBinding
metadata:
  namespace: team-a
```

### Pattern 3: Break Glass (Emergency)
```yaml
# Give cluster-admin only when absolutely necessary
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: emergency-admin
subjects:
- kind: User
  name: ops-lead
roleRef:
  kind: ClusterRole
  name: cluster-admin  # Built-in, full access
  apiGroup: rbac.authorization.k8s.io
```

---

## 7e.9 Built-In ClusterRoles

Kubernetes provides default roles:

| ClusterRole     | Permissions                      |
| --------------- | -------------------------------- |
| `cluster-admin` | Full cluster access (super user) |
| `admin`         | Full namespace access            |
| `edit`          | Read/write namespace resources   |
| `view`          | Read-only namespace resources    |

```bash
# Use built-in roles
kubectl create rolebinding dev-edit \
  --clusterrole=edit \
  --serviceaccount=default:developer \
  --namespace=development
```

---

**Next:** [Part 7f: Kubernetes Storage](./07f-kubernetes-storage.md)
