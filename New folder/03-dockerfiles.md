# Part 3: Writing Dockerfiles

## 3.1 Dockerfile Basics

A Dockerfile is a **recipe** for building an image.

```dockerfile
# Basic structure
FROM base-image          # Start from a base
RUN command              # Execute commands
COPY source dest         # Copy files
WORKDIR /path            # Set working directory
EXPOSE port              # Document exposed port
CMD ["command"]          # Default command to run
```

---

## 3.2 All Dockerfile Instructions

| Instruction   | Purpose                 | Example                          |
| ------------- | ----------------------- | -------------------------------- |
| `FROM`        | Base image              | `FROM python:3.11-slim`          |
| `RUN`         | Execute command         | `RUN pip install flask`          |
| `COPY`        | Copy from host          | `COPY app.py /app/`              |
| `ADD`         | Copy + extract archives | `ADD archive.tar.gz /app/`       |
| `WORKDIR`     | Set working dir         | `WORKDIR /app`                   |
| `ENV`         | Set environment var     | `ENV DEBUG=false`                |
| `ARG`         | Build-time variable     | `ARG VERSION=1.0`                |
| `EXPOSE`      | Document port           | `EXPOSE 8000`                    |
| `CMD`         | Default command         | `CMD ["python", "app.py"]`       |
| `ENTRYPOINT`  | Fixed command           | `ENTRYPOINT ["python"]`          |
| `USER`        | Run as user             | `USER appuser`                   |
| `VOLUME`      | Mount point             | `VOLUME /data`                   |
| `HEALTHCHECK` | Health check            | `HEALTHCHECK CMD curl localhost` |

---

## 3.3 Multi-Stage Builds (Image Size Optimization)

Multi-stage builds create smaller images by separating **build** from **runtime**.

```
SINGLE STAGE (BAD):
┌─────────────────────────────────┐
│  Final Image: 1.2 GB           │
│  - Build tools (gcc, npm)      │
│  - Source code                 │
│  - Compiled app                │
│  - Everything mixed together   │
└─────────────────────────────────┘

MULTI-STAGE (GOOD):
┌─────────────────┐    ┌─────────────────┐
│  Stage 1: Build │    │  Final Image    │
│  - gcc, npm     │ →  │  - Only runtime │
│  - Source code  │    │  - Compiled app │
│  - Compiling... │    │  50 MB ✓        │
│  1.2 GB         │    └─────────────────┘
└─────────────────┘    (build tools discarded)
```

### Multi-Stage Example: React Frontend

```dockerfile
# Stage 1: Build
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production (only static files)
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Result:** Image goes from ~1GB to ~25MB!

---

## 3.4 Image Size Optimization Tips

### 1. Use Slim/Alpine Base Images
```dockerfile
# BAD: 900MB
FROM python:3.11

# GOOD: 150MB
FROM python:3.11-slim

# BETTER: 50MB (but may need extra packages)
FROM python:3.11-alpine
```

### 2. Combine RUN Commands
```dockerfile
# BAD: Creates 3 layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get clean

# GOOD: Single layer, with cleanup
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
```

### 3. Use .dockerignore
```
# .dockerignore
node_modules
.git
*.log
__pycache__
.env
```

### 4. Order Instructions by Change Frequency
```dockerfile
# GOOD: Dependencies first (cached), code last
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .        # Rarely changes
RUN pip install -r requirements.txt  # Cached!
COPY . .                       # Changes often (rebuilds from here)
```

---

## 3.5 Frontend Examples

### Simple HTML/CSS/JS
```dockerfile
# Dockerfile.frontend
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/
COPY styles.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/
EXPOSE 80
```

### React Application
```dockerfile
# Dockerfile.react
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

---

## 3.6 Backend Examples

### Python (Flask/FastAPI)
```dockerfile
# Dockerfile.python
FROM python:3.11-slim

# Create non-root user
RUN useradd -m appuser

WORKDIR /app

# Install dependencies first (cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Java (Spring Boot) - Multi-Stage
```dockerfile
# Dockerfile.java
# Stage 1: Build
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

# Stage 2: Runtime
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

## 3.7 Build Commands

```bash
# Basic build
docker build -t myapp:v1 .

# Specify Dockerfile
docker build -t myapp:v1 -f Dockerfile.prod .

# Build with arguments
docker build --build-arg VERSION=2.0 -t myapp:v2 .

# No cache (force rebuild)
docker build --no-cache -t myapp:v1 .

# View build history (see layers)
docker history myapp:v1
```

---

**Next:** [Part 4: Volumes and Data Persistence](./04-volumes.md)
