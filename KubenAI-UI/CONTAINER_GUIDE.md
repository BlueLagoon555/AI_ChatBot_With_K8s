# 🐳 Container Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker Desktop installed and running
- Your Azure OpenAI credentials ready

### 1. Using Pre-built Image from Registry

```bash
# Pull and run the latest image
docker run -d \
  --name ai-chat-assistant \
  -p 8501:8501 \
  -e AZURE_OPENAI_ENDPOINT="your_endpoint_here" \
  -e AZURE_OPENAI_API_KEY="your_api_key_here" \
  -e AZURE_OPENAI_API_VERSION="2025-01-01-preview" \
  -e AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name" \
  your-registry/ai-chat-assistant:latest
```

### 2. Building from Source

#### Build the Docker image locally
```bash
docker build -t ai-chat-assistant .
```

#### Run the locally built container
```bash
docker run -d \
  --name ai-chat-assistant \
  -p 8501:8501 \
  -e AZURE_OPENAI_ENDPOINT="your_endpoint_here" \
  -e AZURE_OPENAI_API_KEY="your_api_key_here" \
  -e AZURE_OPENAI_API_VERSION="2025-01-01-preview" \
  -e AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name" \
  ai-chat-assistant
```

### 3. Registry Operations

#### Tag image for registry
```bash
docker tag ai-chat-assistant your-registry.com/ai-chat-assistant:v1.0.0
```

#### Push to registry
```bash
docker push your-registry.com/ai-chat-assistant:v1.0.0
```

#### Pull from registry
```bash
docker pull your-registry.com/ai-chat-assistant:v1.0.0
```

### 4. Container Management

#### View running containers
```bash
docker ps
```

#### View container logs
```bash
docker logs ai-chat-assistant

# Follow logs in real-time
docker logs -f ai-chat-assistant
```

#### Stop and remove container
```bash
docker stop ai-chat-assistant
docker rm ai-chat-assistant
```

#### Update container with new image
```bash
docker stop ai-chat-assistant
docker rm ai-chat-assistant
docker pull your-registry.com/ai-chat-assistant:latest
docker run -d --name ai-chat-assistant -p 8501:8501 [environment variables] your-registry.com/ai-chat-assistant:latest
```

### 5. Health Monitoring

The container includes health checks that monitor the Streamlit application:

```bash
# Check container health status
docker ps

# View detailed health information
docker inspect ai-chat-assistant | grep -A 10 Health
```

### 6. Environment Variables

Required environment variables for the container:

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint URL | `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | `abc123...` |
| `AZURE_OPENAI_API_VERSION` | API version to use | `2025-01-01-preview` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Your model deployment name | `gpt-4` or `gpt-35-turbo` |

### 7. Troubleshooting

#### Container won't start
```bash
# Check logs for errors
docker logs ai-chat-assistant

# Verify environment variables
docker exec ai-chat-assistant env | grep AZURE
```

#### Health check failures
```bash
# Test health endpoint manually
curl http://localhost:8501/_stcore/health

# Check if Streamlit is running inside container
docker-compose exec chatbot-ui ps aux
```

#### Permission issues
```bash
# Rebuild with no cache
docker build --no-cache -t ai-chat-assistant .

# Check file permissions inside container
docker exec ai-chat-assistant ls -la /app
```

### 8. Performance Tuning

#### Resource limits
```bash
# Run with memory and CPU limits
docker run -d \
  --name ai-chat-assistant \
  --memory="512m" \
  --cpus="1.0" \
  -p 8501:8501 \
  [environment variables] \
  your-registry.com/ai-chat-assistant:latest
```

#### Volume mounts for development
```bash
# Mount source code for development (hot reload)
docker run -d \
  --name ai-chat-assistant \
  -p 8501:8501 \
  -v "$(pwd)/src:/app/src" \
  [environment variables] \
  ai-chat-assistant
```

### 9. Security Best Practices

- ✅ Non-root user in container
- ✅ Environment variables for secrets
- ✅ .dockerignore excludes sensitive files
- ✅ Health checks for monitoring
- ✅ Minimal base image (Python slim)

### 10. Deployment Options

| Method | Use Case | Command |
|--------|----------|---------|
| Local Development | Testing changes | `docker run -p 8501:8501 [env vars] ai-chat-assistant` |
| Production Server | Single server deployment | `docker run -d --restart=unless-stopped [options] registry/image` |
| Azure Container Instances | Serverless containers | `az container create --image registry/image` |
| Kubernetes | Scalable production | Create deployment + service manifests |

### 11. Registry Examples

#### Docker Hub
```bash
# Tag for Docker Hub
docker tag ai-chat-assistant username/ai-chat-assistant:v1.0.0

# Push to Docker Hub
docker push username/ai-chat-assistant:v1.0.0

# Run from Docker Hub
docker run -d -p 8501:8501 [env vars] username/ai-chat-assistant:v1.0.0
```

#### Azure Container Registry
```bash
# Login to ACR
az acr login --name myregistry

# Tag for ACR
docker tag ai-chat-assistant myregistry.azurecr.io/ai-chat-assistant:v1.0.0

# Push to ACR
docker push myregistry.azurecr.io/ai-chat-assistant:v1.0.0

# Run from ACR
docker run -d -p 8501:8501 [env vars] myregistry.azurecr.io/ai-chat-assistant:v1.0.0
```

## 🔐 Kubernetes Deployment with Secure Credentials

### Option 1: Kubernetes Secrets (Recommended)

Create and use Kubernetes secrets for Azure OpenAI credentials:

```bash
# Create secret
kubectl create secret generic azure-openai-credentials \
  --from-literal=AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/" \
  --from-literal=AZURE_OPENAI_API_KEY="your_api_key_here" \
  --from-literal=AZURE_OPENAI_API_VERSION="2025-01-01-preview" \
  --from-literal=AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name"

# Deploy using the secret
kubectl apply -f k8s-deployment.yaml
```

### Option 2: Azure Key Vault Integration (Most Secure)

For production environments, integrate with Azure Key Vault:

```bash
# Install CSI Secret Store driver
helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts
helm install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver --namespace kube-system

# Install Azure Key Vault provider
kubectl apply -f https://raw.githubusercontent.com/Azure/secrets-store-csi-driver-provider-azure/master/deployment/provider-azure-installer.yaml

# Deploy with Key Vault integration
kubectl apply -f k8s-keyvault-deployment.yaml
```

### Benefits of Each Approach:

| Method | Security | Complexity | Best For |
|--------|----------|------------|----------|
| Environment Variables | Low | Simple | Development/Testing |
| Kubernetes Secrets | Medium | Moderate | Staging/Production |
| Azure Key Vault | High | Complex | Enterprise Production |

### 🚨 Important Security Notes:

1. **Never bake credentials into the Docker image**
2. **Always use Kubernetes secrets or external secret management**
3. **Enable RBAC to control secret access**
4. **Rotate credentials regularly**
5. **Use Azure Managed Identity when possible**

---

**Ready to deploy! 🚀** Your AI chat assistant is now fully containerized and production-ready with secure credential management.
