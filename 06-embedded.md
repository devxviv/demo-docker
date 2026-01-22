# Part 6: Docker for Embedded Systems

## 6.1 Why Docker for Embedded?

| Challenge                 | Docker Solution                    |
| ------------------------- | ---------------------------------- |
| **Consistent toolchains** | Same compiler version everywhere   |
| **Cross-compilation**     | Build ARM binaries on x86 machines |
| **Testing environments**  | Simulate hardware interfaces       |
| **CI/CD pipelines**       | Automated builds and tests         |
| **Team onboarding**       | New devs get working env instantly |

---

## 6.2 Cross-Compilation Architecture

```
┌────────────────────────────────────────────────────────────────┐
│  DEVELOPMENT (x86_64 Linux/Windows)                            │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Docker Container (ARM toolchain)                       │   │
│  │  - arm-linux-gnueabihf-gcc                              │   │
│  │  - Cross-compile libraries                              │   │
│  │  - Your source code (mounted)                           │   │
│  │                                                         │   │
│  │  ./src/main.c  ──▶  arm-linux-gnueabihf-gcc  ──▶ app   │   │
│  └────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│                        app (ARM binary)                         │
└────────────────────────────────────────────────────────────────┘
                               │
                               ▼ (Copy to device)
┌────────────────────────────────────────────────────────────────┐
│  TARGET DEVICE (Raspberry Pi , etc )       │
│  - Runs ARM binary directly                                    │
└────────────────────────────────────────────────────────────────┘
```

---

## 6.3 Raspberry Pi Development

### Dockerfile for Cross-Compilation
```dockerfile
FROM debian:bullseye

# Install ARM cross-compiler
RUN apt-get update && apt-get install -y \
    gcc-arm-linux-gnueabihf \
    g++-arm-linux-gnueabihf \
    make \
    cmake \
    git

WORKDIR /src

# Cross-compile command
ENV CC=arm-linux-gnueabihf-gcc
ENV CXX=arm-linux-gnueabihf-g++
```

### Build Script
```bash
# Build ARM binary from x86 machine
docker build -t rpi-toolchain -f Dockerfile.rpi .

docker run --rm \
  -v $(pwd):/src \
  rpi-toolchain \
  make CROSS_COMPILE=arm-linux-gnueabihf-

# Copy to Raspberry Pi
scp ./output/myapp pi@192.168.1.100:/home/pi/
```

---

## 6.5 Development

### Dockerfile for SCard Testing
```dockerfile
FROM debian:bullseye

# Install PC/SC tools
RUN apt-get update && apt-get install -y \
    pcscd \
    pcsc-tools \
    libpcsclite-dev \
    opensc \
    opensc-pkcs11

# Install Python APDU tools
RUN pip3 install pyscard

WORKDIR /app
COPY . .

# Start PC/SC daemon
CMD ["pcscd", "-f"]
```

### USB Passthrough to Container
```bash
# Pass USB smart card reader to container
docker run -it --rm \
  --privileged \
  --device=/dev/bus/usb \
  -v /dev/bus/usb:/dev/bus/usb \
  smartcard-dev \
  pcsc_scan
```

### docker-compose.yml for SCard Testing
```yaml
version: "3.8"
services:
  smartcard-test:
    build: .
    privileged: true
    volumes:
      - /dev/bus/usb:/dev/bus/usb
      - ./tests:/app/tests
    devices:
      - /dev/bus/usb
    command: python3 tests/test_apdu.py
```

---

## 6.6 Multi-Architecture Builds

Build for multiple architectures at once (ARM, x86, etc.):

```bash
# Enable multi-arch builder
docker buildx create --name multiarch --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t myapp:latest \
  --push .
```

### Dockerfile for Multi-Arch
```dockerfile
FROM --platform=$TARGETPLATFORM python:3.11-slim

ARG TARGETPLATFORM
RUN echo "Building for $TARGETPLATFORM"

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

---

## 6.7 Embedded CI/CD Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

build-arm:
  stage: build
  image: docker:latest
  script:
    - docker buildx build --platform linux/arm64 -t myapp:arm64 .
    - docker push registry/myapp:arm64

test-hardware:
  stage: test
  tags:
    - raspberry-pi  # Run on Pi runner
  script:
    - docker compose -f docker-compose.test.yml up --abort-on-container-exit

deploy-device:
  stage: deploy
  script:
    - scp myapp.deb pi@device:/tmp/
    - ssh pi@device "sudo dpkg -i /tmp/myapp.deb"
```

---

**Next:** [Part 7: Kubernetes Fundamentals](./07-kubernetes.md)
