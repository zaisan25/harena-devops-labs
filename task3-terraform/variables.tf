variable "docker_hub_username" {
  type        = string
  description = "Your Docker Hub username"
  default     = "nyharena"
}

variable "docker_repo_name" {
  type        = string
  description = "The repository name on Docker Hub"
  default     = "harena-devops-labs"
}

variable "container_name" {
  type        = string
  description = "Name for the deployed container"
  default     = "control-plane-production"
}

variable "external_port" {
  type        = number
  description = "The public port to access the Streamlit dashboard"
  default     = 8501
}