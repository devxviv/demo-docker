# Part 8: Kubernetes for Production

## 8.1 Production vs Development

| Aspect        | Development | Production               |
| ------------- | ----------- | ------------------------ |
| **Replicas**  | 1           | 2+ (High Availability)   |
| **Resources** | Unlimited   | Limits defined           |
| **Secrets**   | Hardcoded   | External secrets manager |
| **Storage**   | Local       | Persistent Volumes       |
| **Access**    | NodePort    | Ingress with domain      |
| **TLS**       | None        | HTTPS required           |

---

## 8.2 PostgreSQL in Kubernetes

### PostgreSQL Deployment (Testing)
```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          value: "admin"
        - name: POSTGRES_PASSWORD
          value: "devpassword"        # BAD for production!
        - name: POSTGRES_DB
          value: "myapp"
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-data
        emptyDir: {}                  # Data lost on restart!
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

---

## 8.3 Secrets Management

### Create Secrets
```bash
# From literal values
kubectl create secret generic postgres-secret \
  --from-literal=username=admin \
  --from-literal=password=supersecret

# From file
kubectl create secret generic tls-secret \
  --from-file=tls.crt=./cert.pem \
  --from-file=tls.key=./key.pem

# View secrets (base64 encoded)
kubectl get secret postgres-secret -o yaml
```

### Use Secrets in Pods
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  template:
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
```

---

## 8.4 Persistent Volumes (PV/PVC)

```
┌──────────────────────────────────────────────────────────────────┐
│  STORAGE ARCHITECTURE                                            │
│                                                                   │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐ │
│  │      Pod       │    │      PVC       │    │       PV       │ │
│  │  (Your App)    │───▶│ (Your Request) │───▶│ (Actual Disk)  │ │
│  │                │    │ "I need 10GB"  │    │ AWS EBS / NFS  │ │
│  └────────────────┘    └────────────────┘    └────────────────┘ │
│                                                                   │
│  StorageClass: Automates PV creation                             │
└──────────────────────────────────────────────────────────────────┘
```

### PersistentVolumeClaim (PVC)
```yaml
# postgres-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: local-path    # On-premise
  # storageClassName: gp2         # AWS EBS
  # storageClassName: standard    # GCP
```

### Use PVC in PostgreSQL
```yaml
apiVersion: apps/v1
kind: StatefulSet              # Better for databases!
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        envFrom:
        - secretRef:
            name: postgres-secret
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: local-path
      resources:
        requests:
          storage: 10Gi
```

---

## 8.5 Cloud vs On-Premise Comparison

| Feature          | AWS/GCP/Azure           | On-Premise             |
| ---------------- | ----------------------- | ---------------------- |
| **LoadBalancer** | Automatic               | MetalLB or hostNetwork |
| **Storage**      | EBS/PD dynamic          | NFS/local-path static  |
| **Secrets**      | AWS Secrets Manager     | K8s Secrets + Vault    |
| **TLS Certs**    | AWS Certificate Manager | cert-manager or manual |
| **DNS**          | Route 53                | Internal DNS           |

---

## 8.6 Ingress for Production

### On-Premise NGINX Ingress
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - myapp.company.com
    secretName: tls-secret
  rules:
  - host: myapp.company.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
```

### AWS ALB Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:...
spec:
  rules:
  - host: myapp.company.com
    http:
      paths:
      - path: /*
        pathType: ImplementationSpecific
        backend:
          service:
            name: frontend
            port:
              number: 80
```

---

## 8.7 Resource Limits

```yaml
containers:
- name: backend
  image: mybackend:v1
  resources:
    requests:              # Minimum guaranteed
      memory: "256Mi"
      cpu: "250m"          # 0.25 CPU cores
    limits:                # Maximum allowed
      memory: "512Mi"
      cpu: "500m"
```

---

## 8.8 Health Checks

```yaml
containers:
- name: backend
  image: mybackend:v1
  livenessProbe:           # Is it alive?
    httpGet:
      path: /healthz
      port: 8000
    initialDelaySeconds: 10
    periodSeconds: 10
  readinessProbe:          # Is it ready for traffic?
    httpGet:
      path: /ready
      port: 8000
    initialDelaySeconds: 5
    periodSeconds: 5
```

---

## 8.9 Complete Production Stack

```
┌─────────────────────────────────────────────────────────────────┐
│  PRODUCTION KUBERNETES ARCHITECTURE                             │
│                                                                  │
│  Internet                                                        │
│      │                                                           │
│      ▼                                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Ingress (NGINX) - TLS Termination                        │  │
│  │  Host: myapp.company.com                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│            │ /api/*                      │ /*                   │
│            ▼                             ▼                      │
│  ┌─────────────────┐        ┌─────────────────┐                │
│  │  Backend (x3)   │        │  Frontend (x2)  │                │
│  │  Deployment     │        │  Deployment     │                │
│  │  + HPA          │        │                 │                │
│  └────────┬────────┘        └─────────────────┘                │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │  PostgreSQL     │  │     Redis       │                      │
│  │  StatefulSet    │  │  Deployment     │                      │
│  │  + PVC (50Gi)   │  │  (cache)        │                      │
│  └─────────────────┘  └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

---

**Next:** [Part 9: Sample Files and Code](./09-sample-files.md)
