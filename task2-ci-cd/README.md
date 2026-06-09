# README.md
# DevOps Control Plane

![CI Status](https://github.com/nyharena/harena-devops-labs/actions/workflows/ci.yml/badge.svg)
![CD Status](https://github.com/nyharena/harena-devops-labs/actions/workflows/cd.yml/badge.svg)

## CI/CD Pipeline
This project uses GitHub Actions for continuous integration and deployment:
1. **CI (Pull Requests):** Validates Python syntax and runs a containerized smoke test against the Streamlit health check endpoint.
2. **CD (Main Branch):** Upon merging to `main`, the application is automatically built and pushed to Docker Hub (`nyharena/harena-devops-labs:latest`).

## How to run locally
```bash
docker run -d -p 8501:8501 nyharena/harena-devops-labs:latest