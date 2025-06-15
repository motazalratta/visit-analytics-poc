# Stage 1: Build the docs
FROM python:3.10-slim AS builder

# Install dbt
RUN pip install --no-cache-dir \
    dbt-core>=1.9.3 \
    dbt-clickhouse>=1.9.3 \
    clickhouse-driver>=0.2.9 \
    setuptools>=81.0.0

# Create dbt dirs
WORKDIR /app
COPY dbt /app

