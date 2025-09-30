# Enterprise Self-Hosting Guide

This guide is for organizations wanting to deploy their own Data Product Hub instance with enhanced dbt-labs integration.

## Prerequisites

- **Python 3.12+** (required for official dbt-labs MCP integration)
- **FastMCP Cloud account** or container orchestration platform
- **GitHub App** with appropriate permissions

## Deployment Architecture Options

### Option 1: Dual-Server (Full Features - Recommended)

Deploy two separate MCP servers for maximum capabilities:

#### Step 1: Deploy dbt MCP Server

**FastMCP Cloud:**
```bash
Repository: your-fork/data-product-hub
Entry Point: dbt_server.py
Python Version: 3.12
Environment Variables: (none required)
```

**Docker:**
```bash
docker run -p 8000:8000 \
  -e PYTHON_VERSION=3.12 \
  your-registry/data-product-hub:latest \
  python dbt_server.py
```

#### Step 2: Deploy Data Product Hub Server

**FastMCP Cloud:**
```bash
Repository: your-fork/data-product-hub
Entry Point: server.py
Python Version: 3.12
Environment Variables:
  GITHUB_APP_ID=your_app_id
  GITHUB_PRIVATE_KEY_BASE64=your_private_key_base64
  DBT_MCP_SERVER_URL=https://your-dbt-mcp.fastmcp.app/mcp
```

**Docker:**
```bash
docker run -p 8080:8080 \
  -e GITHUB_APP_ID=your_app_id \
  -e GITHUB_PRIVATE_KEY_BASE64=your_private_key_base64 \
  -e DBT_MCP_SERVER_URL=http://dbt-server:8000/mcp \
  your-registry/data-product-hub:latest \
  python server.py
```

### Option 2: Single-Server (Basic Features)

Deploy only the main server with custom dbt implementation:

**FastMCP Cloud:**
```bash
Repository: your-fork/data-product-hub
Entry Point: server.py
Python Version: 3.12
Environment Variables:
  GITHUB_APP_ID=your_app_id
  GITHUB_PRIVATE_KEY_BASE64=your_private_key_base64
  # DBT_MCP_SERVER_URL not set - uses custom implementation
```

## Environment Variables

### Required: GitHub Integration
```bash
GITHUB_APP_ID=123456                                    # Your GitHub App ID
GITHUB_PRIVATE_KEY_BASE64=LS0tLS1CRUdJTi...            # Base64-encoded private key
```

### Optional: Enhanced dbt Integration
```bash
DBT_MCP_SERVER_URL=https://your-dbt-mcp.fastmcp.app/mcp # Official dbt MCP server URL
ENABLE_GIT_INTEGRATION=true                             # Enable Git MCP integration
DEFAULT_DBT_PROJECT_PATH=/optional/fallback/path        # Fallback dbt project
DATABASE=snowflake                                      # Default database type
```

### Optional: Logging and Performance
```bash
LOG_LEVEL=INFO                                          # Logging level
DBT_MCP_LOG_LEVEL=INFO                                  # dbt MCP logging level
DBT_PROFILES_DIR=/path/to/.dbt                         # dbt profiles directory
```

## GitHub App Setup

### 1. Create GitHub App

1. Go to **GitHub Settings → Developer settings → GitHub Apps**
2. Click **New GitHub App**
3. Fill in basic information:
   - **Name**: `your-org-data-product-hub`
   - **Homepage URL**: `https://your-org.com`
   - **Webhook URL**: Leave blank (not needed)

### 2. Configure Permissions

**Repository permissions:**
- **Contents**: Read
- **Metadata**: Read
- **Pull requests**: Read (optional, for enhanced features)

**Organization permissions:**
- **Members**: Read (optional, for user context)

### 3. Generate Private Key

1. Click **Generate a private key**
2. Download the `.pem` file
3. Convert to base64:
   ```bash
   base64 -i your-app.private-key.pem | tr -d '\n' > private-key-base64.txt
   ```

### 4. Install App

1. Go to **Install App** tab
2. Install on your organization
3. Select repositories containing dbt projects

## Kubernetes Deployment

### Using Helm

```bash
# Add our Helm repository
helm repo add data-product-hub https://charts.data-product-hub.com
helm repo update

# Install with custom values
helm install data-product-hub data-product-hub/data-product-hub \
  --set image.tag="latest" \
  --set python.version="3.12" \
  --set github.appId="123456" \
  --set github.privateKeyBase64="LS0tLS1..." \
  --set dbt.mcpServerUrl="https://your-dbt-mcp.internal/mcp"
```

### Manual YAML

```yaml
# data-product-hub-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-product-hub
spec:
  replicas: 2
  selector:
    matchLabels:
      app: data-product-hub
  template:
    metadata:
      labels:
        app: data-product-hub
    spec:
      containers:
      - name: data-product-hub
        image: your-registry/data-product-hub:latest
        ports:
        - containerPort: 8080
        env:
        - name: GITHUB_APP_ID
          valueFrom:
            secretKeyRef:
              name: github-app-secrets
              key: app-id
        - name: GITHUB_PRIVATE_KEY_BASE64
          valueFrom:
            secretKeyRef:
              name: github-app-secrets
              key: private-key-base64
        - name: DBT_MCP_SERVER_URL
          value: "http://dbt-mcp-service:8000/mcp"
        - name: PYTHON_VERSION
          value: "3.12"
```

## Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  dbt-mcp:
    build: .
    ports:
      - "8000:8000"
    command: python dbt_server.py
    environment:
      - PYTHON_VERSION=3.12
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  data-product-hub:
    build: .
    ports:
      - "8080:8080"
    command: python server.py
    environment:
      - GITHUB_APP_ID=${GITHUB_APP_ID}
      - GITHUB_PRIVATE_KEY_BASE64=${GITHUB_PRIVATE_KEY_BASE64}
      - DBT_MCP_SERVER_URL=http://dbt-mcp:8000/mcp
      - PYTHON_VERSION=3.12
    depends_on:
      dbt-mcp:
        condition: service_healthy
```

## Monitoring and Observability

### Health Checks

The servers expose health endpoints:
- **Main server**: `http://your-server:8080/health`
- **dbt MCP server**: `http://your-dbt-server:8000/health`

### Logging

Configure structured logging:
```bash
LOG_LEVEL=INFO                    # INFO, DEBUG, WARNING, ERROR
DBT_MCP_LOG_LEVEL=INFO           # dbt MCP specific logging
```

### Metrics

Monitor these key metrics:
- Request latency and throughput
- GitHub API rate limit usage
- dbt MCP server connection health
- Repository analysis success rate

## Security Considerations

### Network Security
- Deploy behind a WAF/load balancer
- Use HTTPS for all external connections
- Restrict network access between services

### Secrets Management
- Store GitHub App credentials in secure secret management
- Rotate GitHub App private keys regularly
- Use environment-specific GitHub Apps

### Access Control
- Limit GitHub App installation to necessary repositories
- Monitor GitHub App usage via webhook logs
- Implement IP allowlisting if needed

## Troubleshooting

### Common Issues

**GitHub App Authentication Fails:**
```bash
# Check credentials
echo $GITHUB_APP_ID
echo $GITHUB_PRIVATE_KEY_BASE64 | base64 -d | head -1
# Should show: -----BEGIN RSA PRIVATE KEY-----
```

**dbt MCP Connection Issues:**
```bash
# Test connection
curl http://your-dbt-server:8000/mcp
# Should return MCP protocol response
```

**Repository Access Denied:**
- Verify GitHub App is installed on the repository
- Check GitHub App permissions
- Ensure repository is not archived or deleted

### Logs and Debugging

Enable debug logging:
```bash
LOG_LEVEL=DEBUG
DBT_MCP_LOG_LEVEL=DEBUG
```

Check service logs:
```bash
# Docker
docker logs data-product-hub-server
docker logs dbt-mcp-server

# Kubernetes
kubectl logs deployment/data-product-hub
kubectl logs deployment/dbt-mcp
```

## Support

- **Enterprise Support**: Contact us for dedicated support
- **Documentation**: [Full documentation](https://data-product-hub.fastmcp.app/docs)
- **Issues**: [GitHub Issues](https://github.com/data-product-hub/issues)