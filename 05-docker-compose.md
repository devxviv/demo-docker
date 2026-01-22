# Part 5: Docker Compose

## 5.1 What is Docker Compose?

Docker Compose lets you define and run **multi-container applications** with a single file.

```
WITHOUT COMPOSE (Manual):
docker network create mynet
docker run -d --name db --network mynet postgres
docker run -d --name api --network mynet -e DB_HOST=db myapi
docker run -d --name web --network mynet -p 80:80 nginx

WITH COMPOSE (One command):
docker compose up
```

---

## 5.2 docker-compose.yml Structure

```yaml
version: "3.8"           # Compose file version

services:                # Define containers
  web:
    image: nginx
    ports:
      - "80:80"

  api:
    build: ./backend
    environment:
      - DB_HOST=db

  db:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:                 # Define volumes
  pgdata:

networks:                # Define networks (optional)
  default:
    driver: bridge
```

---

## 5.3 All Compose Options

| Option        | Purpose               | Example                         |
| ------------- | --------------------- | ------------------------------- |
| `image`       | Use existing image    | `image: nginx:alpine`           |
| `build`       | Build from Dockerfile | `build: ./app`                  |
| `ports`       | Port mapping          | `ports: ["8080:80"]`            |
| `volumes`     | Mount volumes         | `volumes: ["./data:/app/data"]` |
| `environment` | Env variables         | `environment: [DEBUG=true]`     |
| `env_file`    | Load from file        | `env_file: .env`                |
| `depends_on`  | Start order           | `depends_on: [db]`              |
| `restart`     | Restart policy        | `restart: unless-stopped`       |
| `networks`    | Custom network        | `networks: [backend]`           |
| `command`     | Override CMD          | `command: npm run dev`          |
| `healthcheck` | Health check          | See example below               |

---

## 5.4 Complete Full-Stack Example

### Project Structure
```
myproject/
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env
├── frontend/
│   ├── Dockerfile
│   └── src/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
└── postgres/
    └── init.sql
```

### docker-compose.yml (Development)
```yaml
version: "3.8"

services:
  # Frontend (React)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src    # Live reload
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

  # Backend (Python FastAPI)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend/app:/app/app     # Live reload
    environment:
      - DATABASE_URL=postgresql://admin:devpass@db:5432/myapp
      - DEBUG=true
    depends_on:
      db:
        condition: service_healthy

  # Database (PostgreSQL)
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=devpass
      - POSTGRES_DB=myapp
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d myapp"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

### .env File
```bash
# .env
POSTGRES_USER=admin
POSTGRES_PASSWORD=devpass
POSTGRES_DB=myapp
DEBUG=true
```

---

## 5.5 Docker Compose Commands

```bash
# Start all services
docker compose up

# Start in background
docker compose up -d

# Build and start
docker compose up --build

# Stop all services
docker compose down

# Stop and remove volumes (CAREFUL!)
docker compose down -v

# View logs
docker compose logs
docker compose logs -f backend    # Follow specific service

# List running services
docker compose ps

# Execute command in service
docker compose exec backend bash
docker compose exec db psql -U admin -d myapp

# Restart a service
docker compose restart backend

# Scale a service
docker compose up -d --scale backend=3
```

---

## 5.6 Production Compose File

### docker-compose.prod.yml
```yaml
version: "3.8"

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    environment:
      - DEBUG=false
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    volumes:
      - pgdata:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 1G

volumes:
  pgdata:
```

### Run with Production Config
```bash
# Combine base + production config
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 5.7 Networking in Compose

All services in a compose file are on the **same network** by default.

```yaml
# Services can reach each other by name
# backend can connect to: db:5432
# frontend can connect to: backend:8000
```

```
┌────────────────────────────────────────────────────────┐
│  DOCKER COMPOSE NETWORK (default)                      │
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│  │ frontend │   │ backend  │   │    db    │           │
│  │          │──▶│          │──▶│          │           │
│  │ :3000    │   │ :8000    │   │ :5432    │           │
│  └──────────┘   └──────────┘   └──────────┘           │
│       │                                                │
│       ▼ (port 3000 exposed to host)                   │
└───────┼────────────────────────────────────────────────┘
        │
   HOST: localhost:3000
```

---

**Next:** [Part 6: Docker for Embedded Systems](./06-embedded.md)
