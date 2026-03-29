from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator  # Airflow 3.x
import sys
import os
import pendulum  

sys.path.append('/opt/airflow')
os.chdir('/opt/airflow')

from scripts.extract import run_extraction
from scripts.transform import save_transform_data
from scripts.load import load_silver_data, save_to_duckdb_and_parquet

def extract_task():
    os.environ['HEADLESS'] = 'true'
    run_extraction()

def transform_task():
    save_transform_data()

def load_task():
    df = load_silver_data()
    if not df.empty:
        save_to_duckdb_and_parquet(df)

with DAG(
    dag_id='scrapy_analytics_pipeline',
    start_date=pendulum.datetime(2026, 3, 1, tz="UTC"),  # ← pendulum com timezone
    schedule='@daily',
    catchup=False,
    tags=['scraping', 'playwright', 'movidas']
    # ← Sem default_args/retries
) as dag:

    extract = PythonOperator(
        task_id='extract_bronze',
        python_callable=extract_task
    )

    transform = PythonOperator(
        task_id='transform_silver',
        python_callable=transform_task
    )

    load = PythonOperator(
        task_id='load_gold',
        python_callable=load_task
    )

    extract >> transform >> load