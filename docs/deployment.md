# CloudOps AI — Deployment Guide

CloudOps AI is an AI-assisted cloud monitoring and troubleshooting dashboard built with Flask, Prometheus, Grafana, cAdvisor, Redis, and Docker Compose.

This guide explains how to install, configure, run, and verify the application across local and cloud environments.

## Deployment Environments

| Environment | Validation Status |
|---|---|
| Local Docker Compose (macOS) | Verified |
| Linux AMD64 Docker image | Build and health checks verified |
| AWS EC2 | Deployment validation pending |
| Chameleon Cloud | Deployment validation pending |

## 1. Prerequisites

Install Git, Python 3, Docker Desktop or Docker Engine, Docker Compose v2, and Make.

Docker must be running before starting the application. The project uses Docker Compose for container orchestration.

## 2. Local Installation

Clone the repository and select the implementation branch:

```bash
git clone https://github.com/kbass-maker/kbass.git
cd kbass
git checkout project-implementation
```

Verify the prerequisites:

```bash
make check
```

Initialize the configuration:

```bash
make setup
```

The setup command creates a private `.env.cloudops` file with generated credentials and initializes the required directories. Existing configuration is preserved.

## 3. Start CloudOps AI

Build and start the Docker Compose services:

```bash
make up
```

Check container status:

```bash
make status
```

Wait until all five services report healthy before running the smoke tests.

## 4. Access the Services

| Service | Local URL |
|---|---|
| Flask application | http://localhost:8000 |
| Flask health endpoint | http://localhost:8000/health |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| cAdvisor | http://localhost:8081 |

Services are bound to localhost by default. Redis is accessible internally through the Docker Compose network.

## 5. Verify the Deployment

Run the deployment smoke tests:

```bash
make smoke
```

The smoke tests verify Flask, Prometheus, Grafana, cAdvisor, and Redis.

Run the automated Python tests from an environment with the project test dependencies installed:

```bash
make test
```

## 6. Stop the Application

```bash
make down
```

To stop services and remove orphan containers:

```bash
make clean
```

## 7. Cloud Deployment — AWS EC2 and Chameleon Cloud

CloudOps AI includes `compose.cloud.yaml` for cloud-specific configuration. Deployment on AWS EC2 and Chameleon Cloud is planned but has not yet been validated end to end.

The cloud override uses a separate `.env.cloud` configuration file and adds persistent Grafana storage. The cloud environment file must contain all required application settings. Before running cloud configuration validation, create `.env.cloud` from the appropriate deployment settings, including the required secrets. Do not commit this file to Git.

Validate the combined Compose configuration before deployment:

```bash
docker compose -f compose.yaml -f compose.cloud.yaml config --quiet
```

This checks configuration validity; it does not deploy or test the application on a remote server.

### Remote Access

The application, Prometheus, Grafana, and cAdvisor are bound to `127.0.0.1` by default. For initial cloud deployments, use SSH tunneling to access these services securely rather than exposing them directly to the internet.

### Security Considerations

- Never commit `.env.cloudops`, `.env.cloud`, API keys, or other credentials.
- Restrict SSH access using cloud firewall or security-group rules.
- Keep administrative dashboards inaccessible from the public internet unless protected by appropriate authentication and TLS.
- Enable hosted AI inference only with authorized provider credentials.
- Review incident information before sending it to external AI providers.
- Maintain backups of persistent application data and configuration.

Detailed AWS EC2 and Chameleon Cloud deployment procedures will be documented after testing on their respective environments.
