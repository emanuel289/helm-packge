# Web App Helm Chart

This Helm chart deploys the Star Trek Website Collection application on Kubernetes.

## Prerequisites

- Kubernetes cluster (Docker Desktop with Kubernetes enabled)
- Helm 3.x installed
- kubectl configured to work with your cluster
- Docker images for frontend and backend built and available

## Installation

1. First, build and tag the Docker images:
```bash
# From the project root directory
docker build -t web-app-frontend:latest ./web-app/frontend
docker build -t web-app-backend:latest ./web-app/backend
```

2. Add the Bitnami repository for MongoDB dependency:
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

3. Install the chart:
```bash
helm install web-app ./helm-charts/web-app
```

## Configuration

The following table lists the configurable parameters of the web-app chart and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.replicaCount` | Number of frontend replicas | `1` |
| `frontend.image.repository` | Frontend image repository | `web-app-frontend` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `backend.replicaCount` | Number of backend replicas | `1` |
| `backend.image.repository` | Backend image repository | `web-app-backend` |
| `backend.image.tag` | Backend image tag | `latest` |
| `mongodb.auth.rootPassword` | MongoDB root password | `secretpassword` |

To override any of these values, create a values.yaml file and use it during installation:
```bash
helm install web-app ./helm-charts/web-app -f my-values.yaml
```

## Accessing the Application

1. The application will be available through the Ingress controller:
   - Frontend: http://localhost/
   - Backend API: http://localhost/api

2. If you need to access MongoDB directly:
```bash
kubectl port-forward svc/mongodb 27017:27017
```

## Uninstalling the Chart

To uninstall/delete the deployment:
```bash
helm uninstall web-app
```

## Troubleshooting

1. Check pod status:
```bash
kubectl get pods
```

2. View pod logs:
```bash
kubectl logs -l app=frontend
kubectl logs -l app=backend
```

3. Check services:
```bash
kubectl get svc
```

4. Check ingress:
```bash
kubectl get ingress
```
