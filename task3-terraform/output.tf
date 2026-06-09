output "container_id" {
  value       = docker_container.app_container.id
  description = "The unique ID of the created container"
}

output "application_url" {
  value       = "http://localhost:${var.external_port}"
  description = "The web address to access your deployed control plane"
}