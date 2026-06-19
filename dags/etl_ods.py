from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import logging

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='load_ods_layer',
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['ods'],
) as dag:

    def load_fact_checks(**context):
        logger = logging.getLogger(__name__)
        from py_scripts.fact_etl import fact_transform, fact_load_ods
        
        hook = PostgresHook(postgres_conn_id='dwh_conn')
        engine = hook.get_sqlalchemy_engine()
        
        filepath_1 = context['params']['fact_file_1']
        filepath_2 = context['params']['fact_file_2']
        
        logger.info("Transforming fact data...")
        df = fact_transform(filepath_1, filepath_2)
        logger.info(f"Transformed {len(df)} rows")
        
        fact_load_ods(df, engine, 'ods', 'fct_checks')
        logger.info("Fact checks loaded to ODS")

    def load_plan_metrics(**context):
        logger = logging.getLogger(__name__)
        from py_scripts.plan_etl import plan_transform, plan_load_ods
        
        hook = PostgresHook(postgres_conn_id='dwh_conn')
        engine = hook.get_sqlalchemy_engine()
        
        filepath = context['params']['plan_file']
        sheetname = context['params']['plan_sheet']
        
        logger.info("Transforming plan data...")
        df = plan_transform(filepath, sheetname)
        logger.info(f"Transformed {len(df)} rows")
        
        plan_load_ods(df, engine, 'ods', 'restaurant_metrics')
        logger.info("Plan metrics loaded to ODS")

    load_fact = PythonOperator(
        task_id='load_fact_checks',
        python_callable=load_fact_checks,
        params={
            'fact_file_1': './files/факт 02 2025.csv',
            'fact_file_2': './files/факт 02 2026.csv',
        },
    )

    load_plan = PythonOperator(
        task_id='load_plan_metrics',
        python_callable=load_plan_metrics,
        params={
            'plan_file': './files/план 02 2026.xlsx',
            'plan_sheet': 'план 02 2026',
        },
    )

    trigger_core = TriggerDagRunOperator(
        task_id='trigger_core',
        trigger_dag_id='etl_core',
        wait_for_completion=True,
    )

    load_fact >> load_plan >> trigger_core
