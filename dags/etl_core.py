# dags/core_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import text
import logging

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='load_core_layer',
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['core'],
) as dag:

    def load_dish_categories(**context):
        logger = logging.getLogger(__name__)
        hook = PostgresHook(postgres_conn_id='dwh_conn')
        engine = hook.get_sqlalchemy_engine()
        
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO core.dim_dish_categories (категория)
                SELECT DISTINCT категория_блюда 
                FROM ods.fct_checks
                WHERE категория_блюда NOT IN (SELECT категория FROM core.dim_dish_categories)
            """))
        logger.info(f"Categories loaded")

    def load_order_types(**context):
        hook = PostgresHook(postgres_conn_id='dwh_conn')
        engine = hook.get_sqlalchemy_engine()
        
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO core.dim_order_types (тип_заказа)
                SELECT DISTINCT тип_заказа 
                FROM ods.fct_checks
                WHERE тип_заказа NOT IN (SELECT тип_заказа FROM core.dim_order_types)
            """))

    def load_dishes(**context):
        hook = PostgresHook(postgres_conn_id='dwh_conn')
        engine = hook.get_sqlalchemy_engine()
        
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO core.dim_dishes (category_id, блюдо)
                SELECT DISTINCT c.id, o.блюдо
                FROM ods.fct_checks o
                JOIN core.dim_dish_categories c ON o.категория_блюда = c.категория
                WHERE o.блюдо NOT IN (SELECT блюдо FROM core.dim_dishes)
            """))

    def load_fct_checks(**context):
        logger = logging.getLogger(__name__)
        hook = PostgresHook(postgres_conn_id='dwh_conn')
        engine = hook.get_sqlalchemy_engine()
        
        with engine.begin() as conn:
            conn.execute(text("""
                DELETE FROM core.fct_checks
                WHERE учетный_день IN (SELECT DISTINCT учетный_день FROM ods.fct_checks)
            """))
            
            conn.execute(text("""
                INSERT INTO core.fct_checks (
                    учетный_день, номер_чека, время_открытия, время_закрытия,
                    dish_id, order_type_id, количество_блюд, количество_гостей, сумма_со_скидкой
                )
                SELECT 
                    o.учетный_день,
                    o.номер_чека,
                    o.время_открытия,
                    o.время_закрытия,
                    d.id,
                    ot.id,
                    o.количество_блюд,
                    o.количество_гостей,
                    o.сумма_со_скидкой
                FROM ods.fct_checks o
                JOIN core.dim_dishes d ON o.блюдо = d.блюдо
                JOIN core.dim_dish_categories c ON d.category_id = c.id AND o.категория_блюда = c.категория
                JOIN core.dim_order_types ot ON o.тип_заказа = ot.тип_заказа
            """))
        logger.info("Facts loaded")

    cat = PythonOperator(task_id='load_categories', python_callable=load_dish_categories)
    ot = PythonOperator(task_id='load_order_types', python_callable=load_order_types)
    dish = PythonOperator(task_id='load_dishes', python_callable=load_dishes)
    fact = PythonOperator(task_id='load_facts', python_callable=load_fct_checks)

    cat >> dish >> fact
    ot >> fact