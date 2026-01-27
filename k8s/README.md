# Kubernetes Deployment Guide

## Prerequisites
- DigitalOcean Kubernetes cluster created
- kubectl configured to connect to your cluster
- Docker images pushed to registry

## Setup Instructions

### 1. Create Secrets
First, create your secrets file from the template:

```bash
# Copy template
cp secrets.yaml.template secrets.yaml

# Encode your values
echo -n 'your-postgres-host' | base64
echo -n 'your-postgres-password' | base64

# Edit secrets.yaml with your base64-encoded values
# DO NOT commit secrets.yaml to git!
```

### 2. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create secrets
kubectl apply -f secrets.yaml

# Deploy persistent volume for n8n
kubectl apply -f n8n-pvc.yaml

# Deploy applications
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
kubectl apply -f n8n-deployment.yaml
kubectl apply -f n8n-service.yaml
```

### 3. Get External IPs

```bash
kubectl get services -n projetml1
```

Wait for LoadBalancers to get external IPs assigned.

### 4. Update Frontend Environment

Once you have the backend external IP, update the frontend deployment:

```bash
kubectl set env deployment/frontend -n projetml1 \
  NEXT_PUBLIC_API_URL=http://<BACKEND_EXTERNAL_IP>:8080
```

## Useful Commands

```bash
# Check pod status
kubectl get pods -n projetml1

# View logs
kubectl logs -f deployment/backend -n projetml1
kubectl logs -f deployment/frontend -n projetml1
kubectl logs -f deployment/n8n -n projetml1

# Scale deployments
kubectl scale deployment/backend --replicas=3 -n projetml1

# Delete all resources
kubectl delete namespace projetml1
```

## DigitalOcean Specific

### Connect to your cluster
```bash
doctl kubernetes cluster kubeconfig save <your-cluster-name>
```

### Check cluster info
```bash
kubectl cluster-info
kubectl get nodes
```
