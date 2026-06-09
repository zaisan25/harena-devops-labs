# Task 3 Terraform Infrastructure as Code

## Objective
Provision infrastructure for running the DevOps Control Plane container image built in Task 2. The target was to deploy the container through infrastructure-as-code using Terraform. [file:1]

## What was implemented
Terraform was used to prepare a container deployment setup, including image pulling, container resource creation, and output values such as the application URL. The task also covered fixing provider initialization and handling image availability issues. [file:1]

## Project structure
- `main.tf` for infrastructure resources. [file:1]
- `variables.tf` for input variables. [file:1]
- `outputs.tf` for outputs like IP and URL. [file:1]
- `terraform.tfvars.example` for sample values. [file:1]
- `README.md` for init, plan, apply, and destroy commands. [file:1]

## Commands used
```bash
terraform init
```

```bash
terraform plan
```

```bash
terraform apply -auto-approve
```

```bash
terraform destroy -auto-approve
```

```bash
docker build -t nyharenaharena-devops-labslatest task1-dockerize
```

```bash
docker ps
```
These commands were used to initialize Terraform, deploy the container, and verify the runtime environment. [file:1]

## Configuration notes
Terraform requires the provider to be initialized before planning or applying. The image build context needed to point to the `task1-dockerize` directory, and the container port mapping was kept on 8501 for Streamlit. [file:1]

## Common issues
The main issue was Terraform not finding the Docker image immediately, which usually happens when the image is not built locally or the repository reference is wrong. Another common issue was forgetting to run `terraform init` before `plan` or `apply`. [file:1]

## Verification
The infrastructure was verified by checking the running container with `docker ps` and opening `http://localhost:8501` in the browser. When the container started correctly, the Streamlit UI was reachable. [file:1]

## Screenshot placeholder
Add your Terraform plan/apply or running container screenshot here.

## Final status
Task 3 completed successfully once Terraform could pull or find the image and start the container. [file:1]