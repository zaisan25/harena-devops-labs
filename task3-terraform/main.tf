terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.2"
    }
  }
}

provider "docker" {
  # Connects directly to your local Linux docker daemon socket
  host = "unix:///var/run/docker.sock"
}

# Pulls your production image from Docker Hub
resource "docker_image" "app_image" {
  name         = "${var.docker_hub_username}/${var.docker_repo_name}:latest"
  keep_locally = false
}

# Provisions and starts the container
resource "docker_container" "app_container" {
  image = docker_image.app_image.image_id
  name  = var.container_name

  ports {
    internal = 8501
    external = var.external_port
  }

  restart = "unless-stopped"
}