import os
import pendulum

from airflow.models.dag import DAG

from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig, RenderConfig
from cosmos.profiles import ClickhouseUserPasswordProfileMapping

# --- Environment Variables ---
DBT_PROJECT_PATH = os.environ.get("DBT_PROJECT_DIR")
DBT_VENV_PATH = os.environ.get("DBT_VENV_PATH")
DBT_EXECUTABLE_PATH = os.path.join(DBT_VENV_PATH, "bin/dbt") if DBT_VENV_PATH else None

# Fail fast if env vars are missing
if not DBT_PROJECT_PATH or not DBT_EXECUTABLE_PATH:
    raise ValueError("Both DBT_PROJECT_DIR and DBT_VENV_PATH environment variables must be set.")

# --- dbt Profile Configuration ---
profile_config = ProfileConfig(
    profile_name="profile",
    target_name="dev",
    profile_mapping=ClickhouseUserPasswordProfileMapping(
        conn_id="clickhouse_conn_http",
        profile_args={
            "schema": "default",
            "driver": "http",
            "secure": False,
            "verify": False,
            "connect_timeout": 60,
            "send_receive_timeout": 300,
            "ca_cert": None,
            "client_name": "dbt-clickhouse",
            "allow_experimental_lightweight_delete": True,
            "allow_experimental_object_type": True,
        },
    ),
)

# --- DAG Definition ---
with DAG(
    dag_id="search_analytics_dbt_dag",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    doc_md=__doc__
) as dag:

    dbt_task_group = DbtTaskGroup(
        group_id="dbt_tasks",

        project_config=ProjectConfig(
            dbt_project_path=DBT_PROJECT_PATH,
            partial_parse=False,
        ),
        
        profile_config=profile_config,

        execution_config=ExecutionConfig(
            dbt_executable_path=DBT_EXECUTABLE_PATH,
        ),

        render_config=RenderConfig(
            select=["path:models/"],  
            emit_datasets=True,
        ),

        operator_args={
            "install_deps": False,
            "append_env": True,
            "retries": 1,
            "retry_delay": pendulum.duration(minutes=5),
            "execution_timeout": pendulum.duration(hours=1),
            "env": {
                "DBT_PROFILES_DIR": "/tmp/cosmos/profile",
                "PYTHONPATH": DBT_VENV_PATH,
            },
        },
        
        default_args={
            "depends_on_past": False,
            "email_on_failure": False,
            "email_on_retry": False,
        },
    )