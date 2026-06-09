# scripts/smoke_test.sh
#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting smoke test..."
echo "Pinging Streamlit health endpoint..."

# Try to curl the health endpoint up to 5 times with a 5-second delay
for i in {1..5}; do
  if curl -s -f http://localhost:8501/_stcore/health; then
    echo -e "\n✅ Smoke test passed! Container is healthy and responding."
    exit 0
  fi
  echo "Waiting for application to start (Attempt $i/5)..."
  sleep 5
done

echo -e "\n❌ Smoke test failed! Application did not respond in time."
exit 1