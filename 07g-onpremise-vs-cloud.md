# Part 7g: On-Premise vs Cloud Kubernetes

## 7g.1 Setup Comparison

|                    | **Cloud (EKS/GKE/AKS)** | **On-Premise (kubeadm)**     |
| ------------------ | ----------------------- | ---------------------------- |
| **Infrastructure** | Managed by provider     | You manage servers           |
| **Control Plane**  | Provider manages        | You install/maintain         |
| **Networking**     | Automatic (VPC)         | CNI plugin (Calico/Flannel)  |
| **Load Balancer**  | Cloud LB (automatic)    | MetalLB / NodePort / Ingress |
| **Storage**        | Cloud disks (EBS/PD)    | NFS / local-path / Ceph      |
| **Auto-scaling**   | Node groups             | Manual + cloud-init          |
| **Cost**           | Pay per hour            | Upfront hardware             |
| **Maintenance**    | Provider patches        | You patch everything         |

---

## 7g.2 Cloud Kubernetes (AWS EKS Example)

```
┌──────────────────────────────────────────────────────────────┐
│             AWS ELASTIC KUBERNETES SERVICE (EKS)              │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  CONTROL PLANE (Managed by AWS)                        │  │
│  │  - You don't see it                                    │  │
│  │  - Highly available across AZs                         │  │
│  │  - Automatic backups                                   │  │
│  │  - AWS handles upgrades                                │  │
│  └─────────────────────┬──────────────────────────────────┘  │
│                        │                                      │
│                        ▼                                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  WORKER NODES (EC2 Instances)                          │  │
│  │  - You manage (or use managed node groups)             │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │  │  Node 1  │  │  Node 2  │  │  Node 3  │             │  │
│  │  │ (t3.medium│  │(t3.medium│  │(t3.medium│             │  │
│  │  └──────────┘  └──────────┘  └──────────┘             │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  INTEGRATIONS (Automatic)                              │  │
│  │  - Load Balancer: AWS ELB/ALB                          │  │
│  │  - Storage: EBS CSI Driver                             │  │
│  │  - IAM: ServiceAccounts → IAM Roles (IRSA)            │  │
│  │  - Networking: AWS VPC CNI                             │  │
│  │  - Logging: CloudWatch Logs                            │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Create EKS Cluster
```bash
eksctl create cluster \
  --name production \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 10
```

---

## 7g.3 On-Premise Kubernetes (kubeadm)

```
┌──────────────────────────────────────────────────────────────┐
│           ON-PREMISE KUBERNETES (kubeadm Setup)               │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  CONTROL PLANE (Your Responsibility)                   │  │
│  │  - Install manually with kubeadm                       │  │
│  │  - You backup etcd                                     │  │
│  │  - You upgrade K8s versions                            │  │
│  │  ┌──────────────────────────────────────┐             │  │
│  │  │  Master Node (Your Server)           │             │  │
│  │  │  - etcd                               │             │  │
│  │  │  - API Server                         │             │  │
│  │  │  - Scheduler                          │             │  │
│  │  │  - Controller Manager                 │             │  │
│  │  └──────────────────────────────────────┘             │  │
│  └────────────────────────────────────────────────────────┘  │
│                        │                                      │
│                        ▼                                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  WORKER NODES (Your Servers)                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │  │  Node 1  │  │  Node 2  │  │  Node 3  │             │  │
│  │  │(Your VM) │  │(Your VM) │  │(Your VM) │             │  │
│  │  └──────────┘  └──────────┘  └──────────┘             │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  MANUAL SETUP REQUIRED                                 │  │
│  │  - CNI: Install Calico/Flannel manually                │  │
│  │  - Load Balancer: MetalLB or use NodePort              │  │
│  │  - Storage: NFS server or local-path                   │  │
│  │  - Ingress: NGINX Ingress Controller                   │  │
│  │  - Monitoring: Prometheus/Grafana (if needed)          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### kubeadm Installation
```bash
# On master node
sudo kubeadm init \
  --pod-network-cidr=192.168.0.0/16 \
  --apiserver-advertise-address=10.10.11.184

# Install CNI (Calico)
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# Join worker nodes
sudo kubeadm join 10.10.11.184:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```

---

## 7g.4 NGINX Ingress Controller

### Cloud (AWS)
```bash
# Install
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/aws/deploy.yaml

# Automatic: Creates AWS Network Load Balancer
kubectl get svc -n ingress-nginx
# NAME                   TYPE           EXTERNAL-IP
# ingress-nginx-controller LoadBalancer  abc-123.elb.amazonaws.com
```

### On-Premise
```bash
# Install
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/baremetal/deploy.yaml

# Uses NodePort (no cloud LB)
kubectl get svc -n ingress-nginx
# NAME                   TYPE       EXTERNAL-IP   PORT(S)
# ingress-nginx-controller NodePort   <none>        80:31024/TCP,443:31963/TCP
```

#### Enable hostNetwork for Port 80
```bash
kubectl edit deployment ingress-nginx-controller -n ingress-nginx

# Add:
spec:
  template:
    spec:
      hostNetwork: true                    # Bind to node's port 80
      dnsPolicy: ClusterFirstWithHostNet
```

Now access: `http://node-ip/` (port 80, no :31024)

---

## 7g.5 Storage Classes Comparison

### Cloud (AWS EBS)
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
volumeBindingMode: WaitForFirstConsumer
```

**Automatic:** Creates EBS volume on demand.

### On-Premise (local-path)
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-path
provisioner: rancher.io/local-path
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
```

**Manual:** Install local-path-provisioner:
```bash
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.24/deploy/local-path-storage.yaml
```

**Limitation:** Volume tied to single node.

### On-Premise (NFS - Better)
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-storage
provisioner: nfs.csi.k8s.io
parameters:
  server: nfs-server.local
  share: /exports
```

**Manual:** Set up NFS server, install NFS CSI driver.

---

## 7g.6 Load Balancer Comparison

### Cloud
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  type: LoadBalancer  # Cloud creates LB automatically
  selector:
    app: frontend
  ports:
  - port: 80
```

**Result:** External IP assigned by cloud.

### On-Premise (MetalLB)
```bash
# Install MetalLB
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.7/config/manifests/metallb-native.yaml

# Configure IP pool
kubectl apply -f - <<EOF
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: production
  namespace: metallb-system
spec:
  addresses:
  - 10.10.11.200-10.10.11.250  # Your available IPs
EOF
```

**Result:** LoadBalancer services get IPs from pool.

---

## 7g.7 Decision Matrix

| Requirement             | Recommendation                    |
| ----------------------- | --------------------------------- |
| **Quick setup**         | Cloud (EKS/GKE)                   |
| **Full control**        | On-premise (kubeadm)              |
| **Budget constraints**  | On-premise (if you have hardware) |
| **Auto-scaling**        | Cloud                             |
| **Data sovereignty**    | On-premise                        |
| **High availability**   | Cloud (easier)                    |
| **Compliance/Security** | On-premise (air-gapped)           |

---

**Next:** [Updated README](./README.md)
