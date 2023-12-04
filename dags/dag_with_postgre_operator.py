from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator


default_args = {
    'owner' : 'andy_hsu',
    'retries' : 5,
    'retry_delay' : timedelta(minutes = 2)
}

with DAG(
    dag_id = 'dag_with_postgres_operator_v02',
    default_args = default_args,
    description = 'This is our first dag that we write',
    start_date = datetime(2023, 9, 11),
    schedule_interval = '@daily'
) as dag:
    task1 = PostgresOperator(
        task_id = 'create_postgre_table',
        postgres_conn_id = 'postgres_localhost',
        sql = """
            create table if not exists dag_runs (
                dt date,
                dag_id character varying,
                primary key (dt, dag_id)
            )
            """
    )

    task2 = PostgresOperator(
        task_id = 'delete_data_from_table',
        postgres_conn_id = 'postgres_localhost',
        sql = """
            delete from dag_runs where dt = '{{  ds  }}' and dag_id values = '{{ dag.dag_id }}'
            """
    )

    task3 = PostgresOperator(
        task_id = 'insert_into_table',
        postgres_conn_id = 'postgres_localhost',
        sql = """
            insert into dag_runs (dt, dag_id) values ('{{  ds  }}', '{{ dag.dag_id }}')
            """
    )

    task1 >> task2 >> task3