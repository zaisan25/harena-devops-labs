# Incident Response Runbook: DevOps Control Plane

## 1. Alert: ServiceDown (Severity: CRITICAL)
### Criteria
Triggered when the `devops-control-plane` target metric `up == 0` for more than 15 seconds.

### Triage Steps
1. **Check Container Status:**
   Run `docker ps -a` to verify if the `control-plane-monitored` container is dead or continually restarting.
2. **Review Core System Logs:**
   Inspect internal system events to isolate runtime failures:
   ```bash
   docker logs control-plane-monitored