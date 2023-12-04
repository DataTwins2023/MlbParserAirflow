from datetime import datetime, timedelta

from airflow.decorators import dag, task


default_args = {
    'owner' : 'andy_hsu',
    'retries' : 5,
    'retry_delay' : timedelta(minutes = 2)
}

@dag(dag_id = 'dag_with_taskflow_api_v01',
     default_args = default_args, 
     start_date = datetime(2023, 9, 1),
     schedule_interval = '@daily')
def hello_world_etl():
        

    @task()
    def get_name():
        return "Jerry"
        
    @task()
    def get_age():
        return 19

    @task()
    def greet(name, age):
        print(f"Hello World! My name is {name} "
              f"and I am {age} years old!")
            
    name = get_name()
    age  = get_age()
    greet(name = name, age = age)

greet_dag = hello_world_etl()
        
