# Docker Compose Simple Demo

A minimal full-stack application to demonstrate Docker Compose.

## Structure
1. **Frontend**: Simple HTML page (Nginx) - Port 8081
2. **Backend**: Simple Python API (FastAPI) - Port 9001 (Internal)
3. **Database**: PostgreSQL - Port 5432 (Internal)

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       YOUR LAPTOP (Host Machine)                        │
│                                                                         │
│  ┌─────────────┐                                                        │
│  │ YOUR BROWSER│                                                        │
│  │             │                                                        │
│  │ URL:        │                                                        │
│  │ http://LOCA │                                                        │
│  │ LHOST:8081  │                                                        │
│  └──────┬──────┘                                                        │
│         │                                                               │
│         │ 1. REQUEST                                                    │
│         │ (Mapped from Host:8081 -> Container:80)                       │
│         ▼                                                               │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  DOCKER NETWORK (demo-net)                                        │  │
│  │                                                                   │  │
│  │  ┌──────────────────────────┐                                     │  │
│  │  │ FRONTEND CONTAINER       │                                     │  │
│  │  │ (nginx)                  │                                     │  │
│  │  │                          │                                     │  │
│  │  │ 2. Nginx receives req    │                                     │  │
│  │  │    on Port 80            │                                     │  │
│  │  │                          │                                     │  │
│  │  │ 3. Nginx sees /api/      │                                     │  │
│  │  │    and proxies to:       │                                     │  │
│  │  │    http://backend:9001   │                                     │  │
│  │  └────────────┬─────────────┘                                     │  │
│  │               │                                                   │  │
│  │               │ 4. INTERNAL REQUEST (Inside Docker Network)       │  │
│  │               │    DNS resolves 'backend' to IP address           │  │
│  │               ▼                                                   │  │
│  │  ┌──────────────────────────┐                                     │  │
│  │  │ BACKEND CONTAINER        │                                     │  │
│  │  │ (FastAPI / Uvicorn)      │                                     │  │
│  │  │                          │                                     │  │
│  │  │ 5. App receives req      │                                     │  │
│  │  │    on Port 9001          │                                     │  │
│  │  │                          │                                     │  │
│  │  │ 6. App needs data,       │                                     │  │
│  │  │    calls DB at:          │                                     │  │
│  │  │    host='database'       │                                     │  │
│  │  └────────────┬─────────────┘                                     │  │
│  │               │                                                   │  │
│  │               │ 7. DB QUERY (Inside Docker Network)               │  │
│  │               │    DNS resolves 'database' to IP address          │  │
│  │               ▼                                                   │  │
│  │  ┌──────────────────────────┐                                     │  │
│  │  │ DATABASE CONTAINER       │                                     │  │
│  │  │ (PostgreSQL)             │                                     │  │
│  │  │                          │                                     │  │
│  │  │ 8. DB executes Query     │                                     │  │
│  │  │    Returns Data          │                                     │  │
│  │  └──────────────────────────┘                                     │  │
│  │                                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## How to Run

1. **Start**
   ```bash
   docker-compose up --build
   ```

2. **Open Browser**
   Go to: [http://localhost:8081](http://localhost:8081)

3. **Stop**
   Press `Ctrl+C` or run:
   ```bash
   docker-compose down
   ```
