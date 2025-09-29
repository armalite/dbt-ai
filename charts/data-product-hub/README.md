# data-product-hub Helm Chart

A Helm chart for deploying data-product-hub MCP Server - a composite data product quality hub that integrates with AI agents.

## Description

This chart deploys data-product-hub as a hostable MCP (Model Context Protocol) server that provides:

- **dbt model analysis** with AI-powered suggestions
- **Metadata coverage checking** across your dbt project
- **Project lineage** visualization and dependency tracking
- **Composite data quality assessment** with Git integration
- **MCP server capabilities** for AI agent integration

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- A dbt project to analyze

## Installation

### Quick Start

```bash
# Add the dbt project as a volume (example using hostPath)
helm install data-product-hub ./charts/data-product-hub \
  --set persistence.hostPath="/path/to/your/dbt-project" \
  --set dbtAi.database="snowflake"
```

### Using Values File

```bash
# Create a values.yaml file
cat > my-values.yaml << EOF
dbtAi:
  database: "snowflake"

persistence:
  hostPath: "/path/to/your/dbt-project"

env:
  - name: OPENAI_API_KEY
    value: "your-openai-api-key"
EOF

helm install data-product-hub ./charts/data-product-hub -f my-values.yaml
```

### Production Deployment with Ingress

```bash
cat > production-values.yaml << EOF
replicaCount: 2

image:
  tag: "latest"

persistence:
  enabled: true
  size: 5Gi
  storageClass: "fast-ssd"

ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: data-product-hub.yourcompany.com
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 1
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
EOF

helm install data-product-hub ./charts/data-product-hub -f production-values.yaml
```

## Configuration

### Key Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `data-product-hub` |
| `image.tag` | Container image tag | `latest` |
| `dbtAi.database` | dbt database type | `snowflake` |
| `dbtAi.mcpServer.port` | MCP server port | `8080` |
| `persistence.enabled` | Enable persistent volume | `true` |
| `persistence.size` | Volume size | `1Gi` |
| `service.type` | Kubernetes service type | `ClusterIP` |

### dbt Project Configuration

You can provide your dbt project in several ways:

#### 1. Host Path (Development)
```yaml
persistence:
  hostPath: "/path/to/your/dbt-project"
```

#### 2. Persistent Volume (Production)
```yaml
persistence:
  enabled: true
  size: 5Gi
  storageClass: "your-storage-class"
```

#### 3. ConfigMap (Small projects)
```yaml
dbtProject:
  useConfigMap: true
  configMapName: "my-dbt-project"
```

### Environment Variables

```yaml
env:
  - name: OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: data-product-hub-secrets
        key: openai-api-key

  - name: DBT_AI_ADVANCED_MODEL
    value: "gpt-4o"
```

## Usage

### Connecting MCP Clients

Once deployed, AI agents can connect to your data-product-hub MCP server:

```bash
# Get the service endpoint
kubectl get service data-product-hub

# Connect from MCP clients
mcp+sse://data-product-hub.default.svc.cluster.local:8080
```

### Available MCP Tools

- `analyze_dbt_model(model_name)` - Analyze specific model
- `check_metadata_coverage()` - Check metadata across project
- `get_project_lineage()` - Get dependency information
- `assess_data_product_quality(model_name)` - Composite quality assessment
- `analyze_dbt_model_with_git_context(model_name)` - Enhanced analysis with Git
- `get_composite_server_status()` - Server status and capabilities

### Port Forwarding for Local Access

```bash
kubectl port-forward service/data-product-hub 8080:8080
# Now accessible at: mcp+sse://localhost:8080
```

## Upgrading

```bash
helm upgrade data-product-hub ./charts/data-product-hub -f your-values.yaml
```

## Uninstalling

```bash
helm uninstall data-product-hub
```

## Troubleshooting

### Common Issues

1. **Pod not starting**: Check if dbt project volume is mounted correctly
2. **Connection refused**: Verify the service and ingress configuration
3. **Git integration failing**: Ensure Git is available in the container

### Debug Commands

```bash
# Check pod logs
kubectl logs -l app.kubernetes.io/name=data-product-hub

# Get pod details
kubectl describe pod -l app.kubernetes.io/name=data-product-hub

# Test MCP server health
kubectl exec -it deploy/data-product-hub -- python -c "import requests; print(requests.get('http://localhost:8080/health').status_code)"
```

## Contributing

Please see the main [data-product-hub repository](https://github.com/armalite/data-product-hub) for contribution guidelines.