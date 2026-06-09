# Task 2 CI/CD Pipeline

## Objective
Create a GitHub Actions CI/CD pipeline for the DevOps Control Plane app that builds, tests, and pushes the Docker image to Docker Hub, then supports deployment handling. The pipeline was designed around build, test, push, and deploy stages. [file:1]

## What was implemented
The CI workflow validates the code with linting and then runs a containerized smoke test against the Streamlit health endpoint. The CD workflow logs in to Docker Hub and pushes the image after a successful build. [file:1]

## Project structure
- `.github/workflows/ci.yml` for CI. [file:1]
- `.github/workflows/cd.yml` for CD. [file:1]
- `scripts/smoketest.sh` for container smoke testing. [file:1]
- `README.md` for pipeline notes and status details. [file:1]

## Commands used
```bash
chmod +x task2-ci-cd/scripts/smoketest.sh
```

```bash
git add .
git commit -m "fix correct paths and workflow directory structure"
git push origin main
```

```bash
docker build -t devops-control-plane-test task1-dockerize
```

```bash
docker run -d -p 8501:8501 --name test-app devops-control-plane-test
```

```bash
curl http://localhost:8501/_stcore/health
```
These commands were used to prepare the smoke test, commit the workflows, and validate the container locally. [file:1]

## Configuration notes
The CI workflow was adjusted to point to the `task1-dockerize` folder so GitHub Actions can find the Dockerfile. The smoke test script must be executable, and the workflow file location must be under `.github/workflows` at the repository root. [file:1]

## Tests used
The static test used linting to catch syntax issues before running a container. The dynamic test used a smoke test that checked whether the running Streamlit container responded on the health endpoint. [file:1]

## Common issues
The most common issue was a wrong Docker build context, which caused GitHub Actions to fail with “Dockerfile not found.” Another common issue was incorrect workflow folder naming or a misspelled `smoketest.sh` file name. [file:1]

## Verification
The pipeline completed successfully when CI passed the lint and smoke stages and CD successfully pushed the image to Docker Hub. A yellow warning about Node.js 20 deprecation did not affect the success of the workflow. [file:1]

## Screenshot placeholder
Add your GitHub Actions success screenshot here.

## Final status
Task 2 completed successfully with working CI and CD workflows. [file:1]