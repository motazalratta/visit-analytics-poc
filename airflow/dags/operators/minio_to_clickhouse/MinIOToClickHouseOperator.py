from airflow.models import BaseOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow_clickhouse_plugin.hooks.clickhouse import ClickHouseHook
import pandas as pd
from io import BytesIO
import re


class MinIOToClickHouseOperator(BaseOperator):
    def __init__(
        self,
        minio_conn_id: str,
        clickhouse_conn_id: str,
        bucket: str,
        key: str,
        database: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.minio_conn_id = minio_conn_id
        self.clickhouse_conn_id = clickhouse_conn_id
        self.bucket = bucket
        self.key = key
        self.database = database

    def auto_detect_datetime_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Automatically detect and convert datetime columns"""
        datetime_patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?',  # 2019-10-01 04:00:17.797
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',          # ISO format
            r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',          # MM/DD/YYYY HH:MM:SS
            r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}',          # YYYY/MM/DD HH:MM:SS
            r'\d{4}-\d{2}-\d{2}',                            # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',                            # MM/DD/YYYY
        ]
        
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].isna().all():  # Skip completely empty columns
                continue
                
            # Get sample of non-null values
            sample_values = df[col].dropna().head(100).astype(str)
            
            if len(sample_values) == 0:
                continue
            
            # Check if values match datetime patterns
            datetime_matches = 0
            for pattern in datetime_patterns:
                matches = sample_values.str.match(pattern, na=False).sum()
                datetime_matches = max(datetime_matches, matches)
            
            # If more than 80% of sample values match datetime patterns
            if datetime_matches > len(sample_values) * 0.8:
                try:
                    # This preserves the original datetime values as-is
                    df[col] = pd.to_datetime(df[col], errors='coerce', utc=False)
                    
                    # If pandas added timezone info, remove it to treat as naive datetime
                    if hasattr(df[col].dtype, 'tz') and df[col].dtype.tz is not None:
                        df[col] = df[col].dt.tz_localize(None)
                    
                    self.log.info(f"Auto-converted column '{col}' to datetime (timezone-naive)")
                except Exception as e:
                    self.log.warning(f"Failed to convert column '{col}' to datetime: {e}")
                    continue
        
        return df

    def infer_clickhouse_schema(self, df: pd.DataFrame):
        type_map = {
            'int64': 'Nullable(Int64)',
            'float64': 'Nullable(Float64)',
            'bool': 'Nullable(UInt8)',
            'object': 'Nullable(String)',
            'datetime64[ns]': 'Nullable(DateTime64(3))',
        }
        
        schema = {}
        for col, dtype in df.dtypes.items():
            dtype_str = str(dtype)
            
            # Handle datetime variants - use DateTime64(3) to preserve milliseconds
            if 'datetime64' in dtype_str:
                schema[col] = 'Nullable(DateTime64(3))'
            else:
                schema[col] = type_map.get(dtype_str, 'Nullable(String)')
        
        return schema

    def execute(self, context):
        # Step 1: Read CSV file from MinIO
        s3 = S3Hook(aws_conn_id=self.minio_conn_id)
        self.log.info(f"Loading file from MinIO: {self.key}")
        obj = s3.get_key(bucket_name=self.bucket, key=self.key)
        data = obj.get()['Body'].read()

        # Read CSV without any automatic datetime parsing to avoid timezone issues
        df = pd.read_csv(BytesIO(data), low_memory=False, parse_dates=False)
        
        # Apply dynamic datetime detection
        self.log.info("Detecting and converting datetime columns...")
        df = self.auto_detect_datetime_columns(df)
        
        # Log the final data types
        self.log.info(f"Final column types: {dict(df.dtypes)}")

        # Step 2: Build table name and schema
        table_name = self.key.split('/')[-1].replace('.csv', '').lower()
        full_table = f"{self.database}.{table_name}"

        schema = self.infer_clickhouse_schema(df)
        columns_sql = ", ".join(f"{col} {col_type}" for col, col_type in schema.items())

        # Convert NaN to None so ClickHouse will insert NULL
        df = df.astype(object).where(pd.notnull(df), None)

        # Step 3: Create table in ClickHouse
        ch = ClickHouseHook(clickhouse_conn_id=self.clickhouse_conn_id)
        conn = ch.get_conn()

        self.log.info(f"Dropping table {full_table} if it exists...")
        conn.execute(f"DROP TABLE IF EXISTS {full_table}")

        self.log.info(f"Creating table {full_table}...")
        self.log.info(f"Schema: {schema}")
        conn.execute(f"""
            CREATE TABLE {full_table} (
                {columns_sql}
            )
            ENGINE = MergeTree()
            ORDER BY tuple()
        """)

        # Step 4: Insert data into ClickHouse
        self.log.info(f"Table {full_table} created. Inserting data...")

        columns = list(df.columns)
        data = [tuple(row) for row in df.itertuples(index=False, name=None)]

        insert_query = f"INSERT INTO {full_table} ({', '.join(columns)}) VALUES"
        conn.execute(insert_query, data)

        self.log.info(f"Inserted {len(df)} rows into {full_table}")