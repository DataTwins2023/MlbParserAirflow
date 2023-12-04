from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner' : 'andy_hsu',
    'retries' : 5,
    'retry_delay' : timedelta(minutes = 2)
}

def greet(ti):
    first_name = ti.xcom_pull(task_ids = 'get_name', key = 'first_name')
    last_name  = ti.xcom_pull(task_ids = 'get_name', key = 'lastt_name')
    age        = ti.xcom_pull(task_ids = 'get_age', key = 'age')
    print(f"Hello World! My name is {first_name} {last_name},"
          f"and I am {age} years old!")
    
def get_name(ti):
    ti.xcom_push(key = 'first_name', value = 'Andy')
    ti.xcom_push(key = 'last_name' , value = 'hsu')

def get_age(ti):
    ti.xcom_push(key = 'age', value = 20)

with DAG(
    dag_id = 'our_dag_with_python_oerator_v05',
    default_args = default_args,
    description = 'Our first dag using python operator',
    start_date = datetime(2023, 9, 1),
    schedule_interval = '@daily'
) as dag:
    task1 = PythonOperator(
        task_id = 'greet',
        python_callable = greet
    )

    task2 = PythonOperator(
        task_id = 'get_name',
        python_callable = get_name
    )

    task3 = PythonOperator(
        task_id = 'get_age',
        python_callable = get_age
    )

    [task2, task3] >> task1