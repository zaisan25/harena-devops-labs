# Task 4 Monitoring and Runbook

## Objective
Add monitoring and logging support for the DevOps Control Plane app and create an incident runbook. The focus was on container metrics and existing JSON logs. [file:1]

## What was implemented
The recommended monitoring setup uses Prometheus and Grafana, with optional Loki and Promtail for logs. Because the app did not expose Prometheus metrics by default, the plan included adding a metrics endpoint or using a lightweight alternative. [file:1]

## Project structure
- `task4-monitoring/docker-compose.yml` for the monitoring stack. [file:1]
- `task4-monitoring/prometheus/prometheus.yml` for scrape configuration. [file:1]
- `task4-monitoring/alerts.yml` for sample alert rules. [file:1]
- `task4-monitoring/grafana/datasources.yml` for Prometheus connection. [file:1]
- `task4-monitoring/dashboards/` for dashboard JSON definitions. [file:1]
- `runbook.md` or `incident-runbook.md` for incident response steps. [file:1]

## Commands used
```bash
cd task4-monitoring
docker compose up -d
```

```bash
docker compose logs -f
```

```bash
curl http://localhost:9090
```

```bash
curl http://localhost:3000
```

```bash
curl http://localhost:8501/_stcore/health
```
These commands were used to start the monitoring stack and verify Prometheus, Grafana, and the application health endpoint. [file:1]

## Configuration notes
Prometheus was configured to scrape the application’s metrics endpoint and its own target endpoint. Grafana was configured to use Prometheus as a datasource, and alert rules were planned for high CPU and service-down cases. [file:1]

## Gap and resolution
The app originally had health checks but no Prometheus metrics endpoint. That gap needed to be addressed either by adding a metrics library to the app or by using a container-level monitoring approach. [file:1]

## Verification
The monitoring stack was checked by opening the Prometheus and Grafana UIs and confirming target visibility. JSON logs from the app remained available for log-based troubleshooting. [file:1]

## Screenshot placeholder
Add your Grafana dashboard screenshot and alert screenshot here.

## Final status
Task 4 completed with a monitoring plan and an incident response runbook structure. [file:1]