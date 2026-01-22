# Part 10: Quick Reference Guide

## Docker Commands Cheat Sheet

### Images
```bash
docker images                         # List images
docker pull <image>                   # Download image
docker build -t name:tag .            # Build image
docker build -t name:tag -f File .    # Build with specific Dockerfile
docker push <image>                   # Push to registry
docker rmi <image>                    # Remove image
docker image prune                    # Remove unused images
docker history <image>                # View layers
```

### Containers
```bash
docker run <image>                    # Run container
docker run -d <image>                 # Run detached (background)
docker run -it <image> bash           # Interactive shell
docker run -p 8080:80 <image>         # Port mapping (host:container)
docker run -v /host:/container <image># Volume mount
docker run -e KEY=value <image>       # Environment variable
docker run --name myapp <image>       # Named container
docker run --rm <image>               # Remove after exit

docker ps                             # List running containers
docker ps -a                          # List all containers
docker stop <container>               # Stop container
docker start <container>              # Start stopped container
docker restart <container>            # Restart container
docker rm <container>                 # Remove container
docker rm -f <container>              # Force remove
docker kill <container>               # Kill container

docker logs <container>               # View logs
docker logs -f <container>            # Follow logs
docker logs --tail 100 <container>    # Last 100 lines

docker exec -it <container> bash      # Shell into container
docker exec <container> <command>     # Run command

docker inspect <container>            # Full details (JSON)
docker stats                          # Live resource usage
docker top <container>                # Show processes
```

### Volumes
```bash
docker volume create <name>           # Create volume
docker volume ls                      # List volumes
docker volume inspect <name>          # Volume details
docker volume rm <name>               # Remove volume
docker volume prune                   # Remove unused volumes
```

### Networks
```bash
docker network create <name>          # Create network
docker network ls                     # List networks
docker network inspect <name>         # Network details
docker network connect <net> <container>
docker network disconnect <net> <container>
```

### System
```bash
docker system df                      # Disk usage
docker system prune                   # Clean up everything
docker system prune -a                # Include unused images
```

---

## Docker Compose Cheat Sheet

```bash
docker compose up                     # Start all services
docker compose up -d                  # Detached mode
docker compose up --build             # Rebuild images
docker compose up <service>           # Start specific service
docker compose down                   # Stop and remove
docker compose down -v                # Also remove volumes

docker compose ps                     # List services
docker compose logs                   # View all logs
docker compose logs -f <service>      # Follow service logs

docker compose exec <service> bash    # Shell into service
docker compose restart <service>      # Restart service
docker compose stop                   # Stop services
docker compose start                  # Start services

docker compose build                  # Build images only
docker compose pull                   # Pull latest images
docker compose config                 # Validate compose file
```

---

## Kubernetes Cheat Sheet

### Cluster Info
```bash
kubectl cluster-info                  # Cluster details
kubectl get nodes                     # List nodes
kubectl get nodes -o wide             # With IPs
kubectl describe node <name>          # Node details
kubectl top nodes                     # Node resource usage
```

### Pods
```bash
kubectl get pods                      # List pods
kubectl get pods -o wide              # With node/IP
kubectl get pods -A                   # All namespaces
kubectl get pods -n <namespace>       # Specific namespace
kubectl get pods -l app=backend       # By label
kubectl get pods -w                   # Watch (live updates)

kubectl describe pod <name>           # Pod details
kubectl logs <pod>                    # Pod logs
kubectl logs -f <pod>                 # Follow logs
kubectl logs <pod> -c <container>     # Specific container
kubectl logs --previous <pod>         # Previous instance

kubectl exec -it <pod> -- bash        # Shell into pod
kubectl exec <pod> -- <command>       # Run command

kubectl delete pod <name>             # Delete pod
kubectl delete pod <name> --force     # Force delete
```

### Deployments
```bash
kubectl get deployments               # List deployments
kubectl get deploy                    # Short form
kubectl describe deployment <name>    # Details

kubectl create deployment <name> --image=<image>
kubectl scale deployment <name> --replicas=5
kubectl set image deployment/<name> container=image:tag

kubectl rollout status deployment/<name>
kubectl rollout history deployment/<name>
kubectl rollout undo deployment/<name>
kubectl rollout undo deployment/<name> --to-revision=2
kubectl rollout restart deployment/<name>
```

### Services
```bash
kubectl get services                  # List services
kubectl get svc                       # Short form
kubectl describe svc <name>           # Details
kubectl get endpoints <name>          # Pod IPs for service

kubectl expose deployment <name> --port=80 --type=NodePort
kubectl port-forward svc/<name> 8080:80  # Local access
```

### Other Resources
```bash
# ConfigMaps
kubectl get configmaps
kubectl create configmap <name> --from-file=config.yaml
kubectl describe configmap <name>

# Secrets
kubectl get secrets
kubectl create secret generic <name> --from-literal=key=value
kubectl get secret <name> -o yaml

# Ingress
kubectl get ingress
kubectl describe ingress <name>

# PersistentVolumeClaims
kubectl get pvc
kubectl describe pvc <name>

# Namespaces
kubectl get namespaces
kubectl create namespace <name>
kubectl config set-context --current --namespace=<name>
```

### Apply/Delete
```bash
kubectl apply -f <file.yaml>          # Create/update resource
kubectl apply -f ./k8s/               # Apply all in directory
kubectl delete -f <file.yaml>         # Delete resource
kubectl delete <type> <name>          # Delete by name
kubectl delete pods --all             # Delete all pods
```

### Debugging
```bash
kubectl get events                    # Recent events
kubectl get events --sort-by='.lastTimestamp'
kubectl top pods                      # Pod resource usage
kubectl describe <resource> <name>    # Detailed info
kubectl get <resource> -o yaml        # Full YAML output
```

---

## Common Patterns

### Check if service is reachable
```bash
kubectl run debug --rm -it --image=busybox -- /bin/sh
# Inside pod:
wget -qO- http://backend:8000/healthz
```

### Copy files to/from pod
```bash
kubectl cp <pod>:/path/to/file ./local-file
kubectl cp ./local-file <pod>:/path/to/file
```

### Port forwarding for testing
```bash
kubectl port-forward pod/<pod> 8080:80
kubectl port-forward svc/<service> 8080:80
kubectl port-forward deploy/<deploy> 8080:80
```

---

## Getting Help

```bash
docker --help                         # Docker help
docker <command> --help               # Command help

kubectl --help                        # Kubectl help
kubectl <command> --help              # Command help
kubectl explain <resource>            # Resource documentation
kubectl explain pod.spec.containers   # Specific field
```

---

## Quick Lookup Table

| Task             | Docker                            | Kubernetes                                 |
| ---------------- | --------------------------------- | ------------------------------------------ |
| **Run app**      | `docker run -d nginx`             | `kubectl run nginx --image=nginx`          |
| **View running** | `docker ps`                       | `kubectl get pods`                         |
| **View logs**    | `docker logs <id>`                | `kubectl logs <pod>`                       |
| **Shell access** | `docker exec -it <id> bash`       | `kubectl exec -it <pod> -- bash`           |
| **Stop**         | `docker stop <id>`                | `kubectl delete pod <pod>`                 |
| **Scale**        | `docker compose up --scale web=3` | `kubectl scale deploy/<name> --replicas=3` |
| **Update image** | `docker compose up --build`       | `kubectl set image deploy/<name> ...`      |

---

**End of Training Documentation**
