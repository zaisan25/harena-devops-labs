# Harena DevOps Labs

This repository contains four DevOps tasks that together build, package, deploy, and observe the **DevOps Control Plane** application. The project starts with a Streamlit dashboard, then adds CI/CD, infrastructure as code, and monitoring with an incident runbook. [file:1]

## Project overview

### Task 1: Dockerize the app
The first task creates the Streamlit dashboard application with system metrics, health checks, structured JSON logging, and a persistent logs volume. The app runs on port `8501` and stores logs in a named volume called `logs_volume`. [file:1]

### Task 2: CI/CD pipeline
The second task adds GitHub Actions workflows for build and test on pull requests, plus build-and-push on the `main` branch. The pipeline validates the app, runs a container smoke test, and publishes the image to Docker Hub. [file:1]

### Task 3: Terraform infrastructure
The third task uses Terraform to provision the runtime environment for the container image. In the local-first setup, Terraform manages the Docker provider and runs the published image on the local machine. [file:1]

### Task 4: Monitoring and runbook
The fourth task adds monitoring and observability for the running app. It includes Prometheus and Grafana, and it documents incident handling in a runbook. [file:1]

## Repository structure

```text
harena-devops-labs/
├── task1-dockerize/
├── task2-ci-cd/
├── task3-terraform/
└── task4-monitoring/
```

Each folder contains the files and configuration needed for that task. The workflows must live under `.github/workflows`, and the Docker build context for CI/CD must point to `task1-dockerize`. [file:1]

## Task 1: Dockerize the app

### What it includes
- `ui/dashboard.py` for the Streamlit UI. [file:1]
- `core/metrics.py` for CPU, RAM, and disk metrics. [file:1]
- `core/health.py` for readiness and liveness checks. [file:1]
- `infra/logger.py` for JSON logging to console and file. [file:1]
- `Dockerfile`, `.dockerignore`, `docker-compose.yml`, and `requirements.txt`. [file:1]

### Run locally
```bash
cd task1-dockerize
docker compose up --build
```

Open the app at:

```text
http://localhost:8501
```

## Task 2: CI/CD pipeline

### What it includes
- `.github/workflows/ci.yml` for linting, image build, and container smoke testing. [file:1]
- `.github/workflows/cd.yml` for login, build, and push to Docker Hub. [file:1]
- `scripts/smoke_test.sh` for checking the Streamlit health endpoint. [file:1]

### Pipeline behavior
- CI runs on pull requests to `main`. [file:1]
- CD runs on pushes to `main`. [file:1]
- The Docker build context points to `./task1-dockerize`. [file:1]
- The published image tag is `nyharena/harena-devops-labs:latest`. [file:1]

### Required secrets
Set these GitHub repository secrets before using the CD workflow:
- `DOCKERHUB_USERNAME`. [file:1]
- `DOCKERHUB_TOKEN`. [file:1]

## Task 3: Terraform infrastructure

### What it includes
- `main.tf` for provider and container resources. [file:1]
- `variables.tf` for configurable values. [file:1]
- `outputs.tf` for container and URL outputs. [file:1]
- `terraform.tfvars.example` as a sample input file. [file:1]

### Recommended local setup
This task is best used with the Terraform Docker provider on a local Linux machine, since it matches your current Docker-only workflow and avoids cloud costs. Terraform controls the local Docker daemon and pulls the published image from Docker Hub. [file:1]

### Terraform commands
```bash
cd task3-terraform
terraform init
terraform plan
terraform apply -auto-approve
```

To remove the resources:

```bash
terraform destroy -auto-approve
```

## Task 4: Monitoring and observability

### What it includes
- `task4-monitoring/docker-compose.yml` for the monitoring stack. [file:1]
- `prometheus/prometheus.yml` and `prometheus/alerts.yml`. [file:1]
- `grafana/datasources.yml` and dashboard JSON files. [file:1]
- `runbook.md` for incident response and recovery steps. [file:1]

### Monitoring stack
The recommended local stack is Prometheus and Grafana, with optional Loki and Promtail for logs if you want full log visualization. The app currently needs a `/metrics` endpoint or a container-level metrics approach before Prometheus can scrape application metrics. [file:1]

### Run the stack
```bash
cd task4-monitoring
docker compose up -d
```

Prometheus is available at:

```text
http://localhost:9090
```

Grafana is available at:

```text
http://localhost:3001
```

## Development notes

- Use `docker ps` to view running containers. [file:1]
- Use `docker logs <container>` to inspect logs. [file:1]
- Keep Terraform state files and `.terraform/` out of version control. [file:1]
- Keep Docker Hub credentials in GitHub Secrets, never in code. [file:1]

## End-to-end workflow

1. Build the app locally in `task1-dockerize`. [file:1]
2. Run CI to validate code and smoke test the container. [file:1]
3. Push the image to Docker Hub with CD. [file:1]
4. Use Terraform to run the published image locally. [file:1]
5. Deploy monitoring with Prometheus and Grafana. [file:1]

## Status

This repository is structured to show the full DevOps lifecycle: development, containerization, automation, infrastructure, and observability. [file:1]
