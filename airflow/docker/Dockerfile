# Use the specified version of Apache Airflow as the base image
ARG AIRFLOW_VERSION=3.0.1
FROM apache/airflow:${AIRFLOW_VERSION}
# Copy requirements into the container
COPY requirements.txt /requirements.txt

# Set environment variables for pip constraints
ENV AIRFLOW_VERSION=${AIRFLOW_VERSION}
ENV CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.12.txt"
# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies with constraint to ensure compatibility
RUN pip install --no-cache-dir -r /requirements.txt --constraint "${CONSTRAINT_URL}"

USER airflow
# Create a virtual environment for dbt & cosmos (inside user's home dir to avoid permission issues)
ENV DBT_VENV_PATH=/home/airflow/dbt-venv
RUN python -m venv ${DBT_VENV_PATH} && \
    ${DBT_VENV_PATH}/bin/pip install --upgrade pip && \
    ${DBT_VENV_PATH}/bin/pip install --upgrade \
    dbt-core>=1.9.3 \
    dbt-clickhouse>=1.9.3 \
    clickhouse-driver>=0.2.9 \
    setuptools>=81.0.0
