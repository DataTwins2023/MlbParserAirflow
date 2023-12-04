from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateEmptyDatasetOperator,
    BigQueryInsertJobOperator,
)
import requests
import typing
import pandas as pd
import bs4

default_args = {
    'owner' : 'andy_hsu',
    'retries' : 5,
    'retry_delay' : timedelta(minutes = 2)
}

with DAG(
    dag_id = 'FIBA_dag',
    default_args = default_args,
    description = 'This is our first dag that we write',
    start_date = datetime(2023, 9, 4),
    schedule_interval = '@daily'
) as dag:
    def requests_url(ti) -> str:
        if requests.get("https://www.fiba.basketball/basketballworldcup/2023/games").status_code == 200:
            ti.xcom_push(key = 'status_code', value = 'Success')
            ti.xcom_push(key = 'url', value = 'https://www.fiba.basketball/basketballworldcup/2023/games')
        else:
            ti.xcom_push(key = 'ststus_code', value = 'Fail')

    def parse_data_or_terminate(ti) -> str:
        status = ti.xcom_pull(task_ids = 'connect_check', key = 'status_code')
        if status == 'Success':
            return 'parse_data_sign'
        else:
            return 'terminate'
        
    def parse_data_sign() -> str:
        print("start_parse")

    def parse_data(ti) -> pd.DataFrame:
        all_match = []
        url = ti.xcom_pull(task_ids = 'connect_check', key = 'url')
        # print("url:", url)
        url_source = requests.get(url).text
        # print("url_source:", url_source)
        soup = bs4.BeautifulSoup(url_source, "lxml")
        today_sche = soup.find("div", class_ = 'custom_wrapper initial')
        # print("today_sche:", today_sche)
        today_matchs = today_sche.find_all("div", class_ = 'game_item')
        # print("today_match:", today_matchs)
        for m in today_matchs:
            left_part = m.find("table", class_ = 'country left').find("tr", class_ = 'country_name').find("td", class_ = 'country_col').find("div", class_ = 'name').find_all("span")[1].text
            # print("left_part:", left_part)
            right_part = m.find("table", class_ = 'country right').find("tr", class_ = 'country_name').find("td", class_ = 'country_col').find("div", class_ = 'name').find_all("span")[1].text
            # print("right_part:", right_part)
            left_point = m.find("table", class_ = 'points').find("div", class_ = 'score').find_all("span")[0].text.replace('\r\n','').strip()
            # print("left_point:", left_point)
            right_point = m.find("table", class_ = 'points').find("div", class_ = 'score').find_all("span")[2].text.replace('\r\n','').strip()
            # print("right_point:", right_point)
            all_match.append([left_part, right_part, left_point, right_point])
        print(all_match)



    task1 = PythonOperator(
        task_id = "connect_check",
        python_callable = requests_url
    )

    task2 = BranchPythonOperator(
        task_id = "parse_data_or_terminate",
        python_callable = parse_data_or_terminate
    )

    task3 = DummyOperator(
        task_id = "terminate"
    )

    task4 = PythonOperator(
        task_id = "parse_data_sign",
        python_callable = parse_data_sign
    )

    task5 = PythonOperator(
        task_id = "parse_data",
        python_callable = parse_data
    )

    create_dataset_task = BigQueryCreateEmptyDatasetOperator(
        gcp_conn_id="gcp_connection",
        task_id="create_dataset",
        dataset_id="test_dataset",
        location="eu",
    )

    task1 >> task2 >> [task3, task4] 
    task4 >> task5
    create_dataset_task