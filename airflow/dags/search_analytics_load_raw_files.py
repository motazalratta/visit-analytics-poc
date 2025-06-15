from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import datetime
from operators.minio_to_clickhouse.MinIOToClickHouseOperator import MinIOToClickHouseOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

MINIO_CONN_ID = "minio_conn"
CLICKHOUSE_CONN_ID = "clickhouse_conn"
BUCKET = "search-analytics"
PREFIX = ""
DATABASE = "default"

with DAG(
    dag_id="search_analytics_load_raw_files",
    start_date=datetime(2025, 6, 1),
    schedule=None,
    catchup=False,
) as dag:

    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    s3 = S3Hook(aws_conn_id=MINIO_CONN_ID)
    keys = s3.list_keys(bucket_name=BUCKET, prefix=PREFIX)
    csv_keys = [key for key in keys if key.endswith(".csv")]

    for key in csv_keys:
        task_id = f"load_{key.split('/')[-1].replace('.csv', '')}"
        t = MinIOToClickHouseOperator(
            task_id=task_id,
            minio_conn_id=MINIO_CONN_ID,
            clickhouse_conn_id=CLICKHOUSE_CONN_ID,
            bucket=BUCKET,
            key=key,
            database=DATABASE,
        )
        start >> t >> end
