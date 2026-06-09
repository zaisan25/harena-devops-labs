FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
RUN mkdir -p /app/logs
VOLUME ["/app/logs"]
EXPOSE 8501
CMD ["streamlit", "run", "ui/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
