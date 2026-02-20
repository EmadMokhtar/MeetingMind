# Docker and Docker Compose Instructions

**Applies to:** `**/Dockerfile`, `**/docker-compose.yml`, `**/docker-compose.yaml`, `**/.dockerignore`

## Project-Specific Patterns

**This project uses:**
- ✅ **Artifactory registry**: `nn-docker-remote.artifactory.insim.biz` for all images
- ✅ **Multi-stage uv build**: `builder → third-party-dependencies → workspace-dependencies → runtime`
- ✅ **BuildKit secrets**: Artifactory credentials injected for each `uv sync` step
- ✅ **Bytecode compilation**: `compileall` for third-party and workspace dependencies
- ✅ **Runtime hardening**: Non-root user (`appuser`) in final image

## Dockerfile Patterns

### Multi-Stage Build with UV (Project Pattern)

```dockerfile
FROM nn-docker-remote.artifactory.insim.biz/python:3.12-slim AS builder
RUN apt-get update && apt-get install -y make && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.artifactory.insim.biz/astral-sh/uv:latest /uv /uvx /bin/

FROM builder AS third-party-dependencies
WORKDIR /api
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=secret,id=artifactory_username \
    --mount=type=secret,id=artifactory_password \
    export UV_INDEX_ARTIFACTORY_USERNAME=$(cat /run/secrets/artifactory_username) && \
    export UV_INDEX_ARTIFACTORY_PASSWORD=$(cat /run/secrets/artifactory_password) && \
    uv sync --frozen --no-install-workspace
RUN .venv/bin/python -m compileall -q /api/.venv/lib

FROM third-party-dependencies AS workspace-dependencies
COPY ./src .
RUN --mount=type=secret,id=artifactory_username \
    --mount=type=secret,id=artifactory_password \
    export UV_INDEX_ARTIFACTORY_USERNAME=$(cat /run/secrets/artifactory_username) && \
    export UV_INDEX_ARTIFACTORY_PASSWORD=$(cat /run/secrets/artifactory_password) && \
    uv sync --frozen --no-editable
RUN .venv/bin/python -m compileall -q /api/.venv/lib/python3.12/site-packages/{{ cookiecutter.__api_name_with_team_name_slug }}

FROM nn-docker-remote.artifactory.insim.biz/python:3.12-slim AS runtime
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser
WORKDIR /api
RUN chown -R appuser:appuser /api
USER 1000:1000
EXPOSE 8000
ENV PYTHONDONTWRITEBYTECODE=1
COPY --from=workspace-dependencies /api/.venv .venv
CMD [".venv/bin/python", "-m", "{{ cookiecutter.__api_name_with_team_name_slug }}.main"]
```

### Key Dockerfile Principles

- **Four-stage build**: Isolate tooling, third-party deps, workspace deps, and runtime image
- **Artifactory registry**: Use `nn-docker-remote.artifactory.insim.biz` for base images
- **Dependency layering**: Install third-party dependencies before copying workspace source
- **Two `uv sync` phases**: `--no-install-workspace` first, then `--no-editable` after copying `src/`
- **Bytecode optimization**: Compile dependencies with `python -m compileall`
- **Non-root user**: Create with `groupadd`/`useradd`, switch with `USER 1000:1000`
- **BuildKit secrets**: Use for build-time Artifactory credentials; never `ENV API_KEY=value`
- **Slim runtime**: Start runtime from a fresh Python base image and copy only `.venv`
- **Stable entrypoint**: Run app with `.venv/bin/python -m <package>.main`

### Compose Command Override Pattern

```yaml
services:
  app:
    build:
      context: .
      secrets:
        - artifactory_username
        - artifactory_password

  workers:
    build:
      context: .
      secrets:
        - artifactory_username
        - artifactory_password
    command: [".venv/bin/python", "-m", "your_package.workers.main"]  # Replace as needed
```

### User Creation Pattern

```dockerfile
# Create non-root user and group explicitly
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser

# Set permissions before switching user
RUN chown -R appuser:appuser /api

# Switch to non-root user
USER 1000:1000
```

### Health Check Pattern

**In Dockerfile:**
```dockerfile
# Healthcheck not defined in Dockerfile - defined in docker-compose for dev
```

**In docker-compose (dev only):**
```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Note**: Healthchecks in docker-compose override Dockerfile healthchecks. For this project, healthchecks are only in docker-compose.yml for local development.

### .dockerignore Template

```dockerignore
.git
.gitignore
__pycache__
*.py[cod]
.venv/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.vscode/
.idea/
.DS_Store
*.md
docs/
.github/
.env
.env.local
dist/
build/
*.log
logs/
tests/
```

## Docker Compose Patterns (LOCAL DEVELOPMENT ONLY)

**IMPORTANT**: Docker Compose is for **local development only**. We do NOT use docker-compose in production. Production deployments use Kubernetes or managed container services.

### Purpose
- ✅ Local development environment setup
- ✅ Running dependencies (DynamoDB, Redis, Jaeger)
- ✅ Testing full stack locally
- ❌ NOT for production deployments
- ❌ NOT for staging environments

### Key Compose Principles (Dev Only)

- **Health checks**: Define in Dockerfile; docker-compose healthcheck overrides it (use sparingly)
- **Resource limits**: Set memory/CPU limits to prevent exhaustion
- **Restart policies**: `always`, `unless-stopped`, `on-failure`
- **Named volumes**: For persistence (postgres-data, redis-data)
- **Bind mounts**: For dev with `:ro` flag when possible
- **Logging**: Limit with max-size/max-file to prevent disk issues
- **Secrets**: Use compose secrets for build-time Artifactory credentials only
- **Networks**: Isolate services with custom networks
- **Runtime secrets**: Use environment variables or secret management systems (Azure Key Vault, AWS Secrets Manager)

### Complete Template (Based on Project)

```yaml
secrets:
  artifactory_username:
    environment: UV_INDEX_ARTIFACTORY_USERNAME
  artifactory_password:
    environment: UV_INDEX_ARTIFACTORY_PASSWORD

services:
  app:
    container_name: "sidiap_azure_devops_agent"
    build:
      context: .
      secrets:
        - artifactory_username
        - artifactory_password
    env_file: .env
    environment:
      DB_DYNAMODB_CONNECTION_STRING: dynamodb://us-east-1/local/local?endpoint=http://dynamodb-local:8000
      UV_INDEX_ARTIFACTORY_USERNAME: ${UV_INDEX_ARTIFACTORY_USERNAME}
      UV_INDEX_ARTIFACTORY_PASSWORD: ${UV_INDEX_ARTIFACTORY_PASSWORD}
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
      OBSERVABILITY__OTLP_ENABLED: true
      OBSERVABILITY__OTLP_ENDPOINT: http://jaeger:4317
    ports:
      - "8000:8000"
    depends_on:
      - dynamodb-local
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - demo-network

  workers:
    container_name: "sidiap_azure_devops_agent_workers"
    build:
      context: .
      secrets:
        - artifactory_username
        - artifactory_password
    env_file: .env
    command: [".venv/bin/python", "-m", "your_package.workers.main"]  # Replace as needed
    environment:
      DB_DYNAMODB_CONNECTION_STRING: dynamodb://us-east-1/local/local?endpoint=http://dynamodb-local:8000
      UV_INDEX_ARTIFACTORY_USERNAME: ${UV_INDEX_ARTIFACTORY_USERNAME}
      UV_INDEX_ARTIFACTORY_PASSWORD: ${UV_INDEX_ARTIFACTORY_PASSWORD}
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
      OBSERVABILITY__OTLP_ENABLED: true
      OBSERVABILITY__OTLP_ENDPOINT: http://jaeger:4317
    depends_on:
      - dynamodb-local
      - redis
    networks:
      - demo-network

  dynamodb-local:
    container_name: "sidiap_azure_devops_agent-dynamodb-local"
    image: nn-docker-remote.artifactory.insim.biz/amazon/dynamodb-local:latest
    command: -jar DynamoDBLocal.jar -sharedDb -dbPath ./data
    user: root
    ports:
      - "8080:8000"
    volumes:
      - dynamodb-data:/home/dynamodblocal/data
    networks:
      - demo-network

  redis:
    container_name: sidiap_azure_devops_agent-redis
    image: nn-docker-remote.artifactory.insim.biz/redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - demo-network

  jaeger:
    container_name: sidiap_azure_devops_agent-jaeger
    image: nn-docker-remote.artifactory.insim.biz/jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC receiver
      - "4318:4318"    # OTLP HTTP receiver
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    networks:
      - demo-network

networks:
  demo-network:
    driver: bridge

volumes:
  dynamodb-data:
  redis-data:
```

### Key Compose Patterns Explained

**1. Command Override Pattern:**
- Build once from the same Dockerfile for all services
- Use Compose `command` to override the default runtime module when needed
- Keep build secrets in `build.secrets` for both app and workers

**2. Observability Setup:**
- Jaeger for distributed tracing
- OTLP endpoints for OpenTelemetry
- Jaeger UI on port 16686

**3. DynamoDB Local:**
- Local AWS DynamoDB for development
- Shared database mode with persistent volume
- Port 8080 (host) → 8000 (container)

**4. Secrets Management:**
- Compose secrets for Artifactory (build-time only)
- Environment variables for runtime configuration
- Never commit secrets to version control

**5. Service Dependencies:**
- `depends_on` ensures startup order
- Health checks ensure services are ready
- Named networks isolate services

```bash
# Usage (LOCAL DEVELOPMENT ONLY)
docker compose up --build -d
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Essential Commands (Local Development)

```bash
# Build and start local environment
docker compose up --build -d

# View logs (follow)
docker compose logs -f app

# Scale workers for local testing
docker compose up --scale worker=3 -d

# Execute command in container
docker compose exec app bash
docker compose exec app uv run pytest

# Stop and remove
docker compose down
docker compose down -v  # Include volumes

# Restart service
docker compose restart app

# View resource usage
docker compose stats

# Validate compose file
docker compose config

# Build with secrets
docker compose build --secret id=token,env=TOKEN
```

## Dockerfile Quick Reference

### Image Tags
```dockerfile
# ✅ Good
FROM python:3.12-slim
FROM postgres:16-alpine
FROM redis:7-alpine

# ❌ Bad
FROM python:latest
FROM postgres
```

### Layer Optimization
```dockerfile
# ✅ Good - dependencies cached separately
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . /app

# ❌ Bad - cache invalidated on every code change
COPY . /app
RUN uv sync
```

### Security
```dockerfile
# ✅ Good - BuildKit secrets
RUN --mount=type=secret,id=token \
    export TOKEN=$(cat /run/secrets/token) && \
    uv sync

# ❌ Bad - hardcoded
ENV TOKEN=secret123
RUN uv sync
```

## Docker Compose Quick Reference

### Service Dependencies
```yaml
services:
  app:
    depends_on:
      postgres:
        condition: service_healthy  # Wait for health check
      redis:
        condition: service_started  # Wait for start only
```

### Volume Patterns
```yaml
volumes:
  # Named volume (persisted)
  - postgres-data:/var/lib/postgresql/data

  # Bind mount read-only (dev)
  - ./src:/app/src:ro

  # Bind mount read-write
  - ./logs:/app/logs
```

### Environment Variables
```yaml
services:
  app:
    env_file: .env           # Load from file
    environment:
      DB_HOST: postgres      # Explicit value
      LOG_LEVEL: ${LOG_LEVEL:-info}  # With default
```

### Network Isolation
```yaml
services:
  app:
    networks:
      - frontend
      - backend

  postgres:
    networks:
      - backend  # Not exposed to frontend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
```

## Security Checklist

- ✅ **Build-time secrets**: Use BuildKit secrets for Artifactory credentials during `uv sync`
- ✅ **Runtime secrets**: Load from environment or secret managers (Azure Key Vault); never hardcode
- ✅ **Environment variables**: For non-sensitive config only; sensitive data needs proper secret management
- ✅ Run as non-root user (USER 1000)
- ✅ Use specific image tags (not :latest)
- ✅ Use official images from trusted registries (or internal Artifactory)
- ✅ Scan images: `docker scan myapp:latest`
- ✅ Use minimal base images (alpine, slim)
- ✅ Multi-stage builds to reduce attack surface
- ✅ Clean up caches in same layer
- ✅ Limit container capabilities with cap_drop/cap_add
- ✅ Keep images updated regularly
