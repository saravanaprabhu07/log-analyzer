# Deployment Guide

## Production Deployment Strategies

This guide covers deploying Intelligent Log Analyzer to production environments.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Security Hardening](#security-hardening)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate new `SECRET_KEY` (use `openssl rand -hex 32`)
- [ ] Configure `ALLOWED_ORIGINS` with actual domain(s)
- [ ] Set up database (PostgreSQL recommended)
- [ ] Configure logging and monitoring
- [ ] Set up SSL/TLS certificates
- [ ] Create database backups
- [ ] Review security settings
- [ ] Load test the application
- [ ] Test disaster recovery

## Environment Setup

### 1. Generate Secure Configuration

```bash
# Generate SECRET_KEY
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
echo "SECRET_KEY=$SECRET_KEY" >> .env

# Generate admin password
ADMIN_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(16))')
```

### 2. Prepare Environment File

```env
# .env for production
APP_NAME=Intelligent Log Analyzer
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@db-server:5432/log_analyzer
DATABASE_ECHO=False

# Security
SECRET_KEY=<generate-secure-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_UPLOAD_SIZE_MB=100
ALLOWED_FILE_EXTENSIONS=log,txt

# CORS
ALLOWED_ORIGINS=https://example.com,https://api.example.com
ALLOW_CREDENTIALS=True

# API
API_V1_PREFIX=/api/v1
PAGINATION_LIMIT=100

# Features
ENABLE_RATE_LIMITING=True
ENABLE_EMAIL_ALERTS=False
```

## Docker Deployment

### Production Docker Compose

```yaml
version: '3.9'

services:
  db:
    image: postgres:15-alpine
    container_name: log-analyzer-db
    environment:
      POSTGRES_USER: log_analyzer
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: log_analyzer
    volumes:
      - db-data:/var/lib/postgresql/data
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U log_analyzer"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: log-analyzer-cache
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: intelligent-log-analyzer
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://log_analyzer:${DB_PASSWORD}@db:5432/log_analyzer
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    container_name: log-analyzer-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl/cert.pem:/etc/nginx/ssl/cert.pem:ro
      - ./ssl/key.pem:/etc/nginx/ssl/key.pem:ro
    depends_on:
      - app
    networks:
      - app-network

volumes:
  db-data:

networks:
  app-network:
    driver: bridge
```

### Deploy with Docker Compose

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f app

# Scale app instances
docker-compose up -d --scale app=3

# Update deployment
docker-compose pull
docker-compose up -d
```

## Kubernetes Deployment

### Create Namespace

```bash
kubectl create namespace log-analyzer
```

### Create ConfigMap

```bash
kubectl create configmap log-analyzer-config \
  --from-literal=APP_NAME="Intelligent Log Analyzer" \
  --from-literal=DEBUG=false \
  -n log-analyzer
```

### Create Secrets

```bash
kubectl create secret generic log-analyzer-secrets \
  --from-literal=SECRET_KEY=$(openssl rand -hex 32) \
  --from-literal=DATABASE_URL=postgresql://user:password@db:5432/log_analyzer \
  -n log-analyzer
```

### Kubernetes Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: log-analyzer
  namespace: log-analyzer
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: log-analyzer
  template:
    metadata:
      labels:
        app: log-analyzer
    spec:
      serviceAccountName: log-analyzer
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      containers:
      - name: app
        image: intelligent-log-analyzer:1.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http

        envFrom:
        - configMapRef:
            name: log-analyzer-config
        - secretRef:
            name: log-analyzer-secrets

        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi

        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 2

        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL

        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: logs
          mountPath: /app/logs

      volumes:
      - name: tmp
        emptyDir: {}
      - name: logs
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: log-analyzer-service
  namespace: log-analyzer
spec:
  type: LoadBalancer
  selector:
    app: log-analyzer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: log-analyzer-hpa
  namespace: log-analyzer
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: log-analyzer
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deploy to Kubernetes

```bash
# Create namespace and secrets
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml

# Deploy application
kubectl apply -f deployment.yaml

# Check deployment
kubectl get pods -n log-analyzer
kubectl get services -n log-analyzer

# View logs
kubectl logs -f deployment/log-analyzer -n log-analyzer

# Scale manually
kubectl scale deployment log-analyzer --replicas=5 -n log-analyzer
```

## Cloud Platforms

### AWS ECS

```json
{
  "family": "log-analyzer",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "log-analyzer",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/log-analyzer:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "false"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:log-analyzer-db-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/log-analyzer",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/log-analyzer

# Deploy
gcloud run deploy log-analyzer \
  --image gcr.io/PROJECT_ID/log-analyzer:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEBUG=false,DATABASE_URL=<db-url> \
  --memory 512Mi \
  --cpu 1 \
  --timeout 600
```

## Security Hardening

### 1. SSL/TLS Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL certificates
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    # Strong SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Database Security

```sql
-- PostgreSQL hardening
-- Create dedicated user
CREATE USER log_analyzer WITH PASSWORD 'secure_password';

-- Grant limited permissions
GRANT CONNECT ON DATABASE log_analyzer TO log_analyzer;
GRANT USAGE ON SCHEMA public TO log_analyzer;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO log_analyzer;

-- Enable connection limits
ALTER ROLE log_analyzer CONNECTION LIMIT 10;
```

### 3. API Rate Limiting

Configure rate limiting in production:

```python
# Add to main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/logs/upload")
@limiter.limit("10/minute")
async def upload_log(request: Request, ...):
    pass
```

## Monitoring & Logging

### Application Monitoring

```python
# Add Prometheus metrics
from prometheus_client import Counter, Histogram

upload_counter = Counter('log_uploads_total', 'Total log uploads')
parse_duration = Histogram('log_parse_duration_seconds', 'Log parsing duration')

@router.post("/upload")
async def upload_log(...):
    upload_counter.inc()
    with parse_duration.time():
        # parsing logic
        pass
```

### Log Aggregation

Set up centralized logging with ELK Stack or similar:

```json
{
  "log_level": "INFO",
  "log_format": "json",
  "handlers": {
    "file": {
      "filename": "/var/log/log-analyzer/app.log",
      "formatter": "json"
    },
    "syslog": {
      "address": "/dev/log",
      "facility": "local0"
    }
  }
}
```

## Troubleshooting

### Database Connection Issues

```bash
# Test database connection
python -c "
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connected:', result.fetchone())
"
```

### Check Logs

```bash
# Docker
docker logs -f intelligent-log-analyzer

# Kubernetes
kubectl logs -f deployment/log-analyzer -n log-analyzer

# Local
tail -f logs/app.log
tail -f logs/errors.log
```

### Health Check

```bash
curl -v http://localhost:8000/health
curl -v http://localhost:8000/api/v1/health
```

---

For more information, see [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
