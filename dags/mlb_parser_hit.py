from datetime import datetime, timedelta
import sys
import time
import typing

import requests
import re
import bs4
import pandas as pd
from pydantic import BaseModel
from sqlalchemy import create_engine
import psycopg2

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner' : 'andy_hsu',
    'retries' : 1,
    'retry_delay' : timedelta(minutes = 2)
}

with DAG(
    dag_id = 'mlb_parser',
    default_args = default_args,
    description = 'This is our first dag that we write',
    start_date = datetime(2023, 9, 11),
    schedule_interval = '0 4 * * *'
) as dag:
    # 第一個 task 做這個
    def select_team(ti):
        ti.xcom_push(key = 'team_parsered', value = ['nationals', 'braves', 'mets', 'marlins', 'phillies',
                                                     'brewers', 'cubs', 'reds', 'pirates', 'cardinals',
                                                     'dodgers', 'giants', 'padres', 'rockies', 'dbacks',
                                                     'astros', 'angels', 'rangers', 'athletics', 'mariners',
                                                     'twins', 'guardians', 'tigers', 'whitesox', 'royals',
                                                     'orioles', 'rays', 'bluejays', 'redsox', 'yankees'])


    # 第二個 task，從task 1拿資料出來
    def crawler_team(
        team: str,
    ) -> pd.DataFrame:
        url = f"https://www.mlb.com/{team}/stats/"
        print(url)
        res = requests.get(url)
        soup = bs4.BeautifulSoup(res.text, "lxml")
        # 全部球員的紀錄
        players_record = []
        try:
            # soup 變成tbody
            soup = soup.find("tbody", class_= 'notranslate')
            # records
            records = soup.find_all('tr')
            for record in records:
                # name 相關的資料
                name_relate = record.find_all("span",class_= "full-3fV3c9pF")
                name = name_relate[0].text + " " + name_relate[1].text
                position = record.find("div", class_ = "position-28TbwVOg").text

                # 個別球員的記錄
                play_record = [name, position]

                bat_records = record.find_all("td", scope = "row")
                for bat_record in bat_records:
                    header = bat_record["headers"][0]
                    if re.search(r'tb-\d+-header-col[2|3|4|5|6|7|8|9|10|11|12|13|15|16]', header):
                        play_record.append(bat_record.text)
                    else:
                        pass

                players_record.append(play_record)
                df = pd.DataFrame(players_record, columns = ['Name', 'POS', 'Team', 'G', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'SO', 'SB', 'CS', 'AVG', 'OBP', 'SLG', 'OPS'])
        except:
            df = "Error"
        return df

    def clear_data(
        df: pd.DataFrame
    ) -> pd.DataFrame:
        for x in ['G', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'SO', 'SB', 'CS']:
            df[x] = df[x].apply(lambda x: int(x))
        for x in ['AVG', 'OBP', 'SLG', 'OPS']:
            df[x] = df[x].apply(lambda x: float(x))

        df = df[(df['AB'] != 0) & (df['POS'] != 'P')]
        df = df.drop(columns = ['AVG', 'OPS'])

        df = df.rename(columns = {
                    '2B':'Double',
                    '3B':'Third'
                    })

        return df

    class BaseballRecord(BaseModel):
        Name: str
        POS: str
        Team: str
        G: int
        AB: int
        R: int
        H: int
        Double: int
        Third: int
        HR: int
        RBI: int
        BB: int
        SO: int
        SB: int
        CS: int
        OBP: float
        SLG: float

    def check_schema(
            df: pd.DataFrame,
    ) -> pd.DataFrame:
        """檢查資料型態, 確保每次要上傳資料庫前, 型態正確"""
        df_dict = df.to_dict("records")
        df_schema = [
            BaseballRecord(**dd).__dict__
            for dd in df_dict
        ]
        df = pd.DataFrame(df_schema)
        return df
        
        
    def clean_data(ti) -> pd.DataFrame:
        teams = ti.xcom_pull(task_ids = 'select_team', key = 'team_parsered')
        print(teams)
        all_team = pd.DataFrame({})
        for t in teams:
            team_record = crawler_team(t)
            team_record = clear_data(team_record)
            team_record = check_schema(team_record)
            all_team = pd.concat([all_team, team_record], ignore_index=True)
        all_team.reset_index(inplace= True, drop= True)
        #establishing the connection
        dbUser = 'airflow'
        dbPwd = 'airflow'
        database = 'mlb_parser_DB'
        engine = create_engine('postgresql://'+ dbUser +':'+ dbPwd +'@postgres:5432/' + database)
        all_team.to_sql(name='mlb_data_2023', con=engine, if_exists="replace")
        return None
    
    def avg_df(ti):
        avg_list = ti.xcom_pull(task_ids = 'get_avg_high')
        # print(avg_list)
        # print(pd.DataFrame(avg_list))

    def hr_df(ti):
        hr_list = ti.xcom_pull(task_ids = 'get_hr_high')
        # print(hr_list)
        # print(pd.DataFrame(hr_list))

    def avg_standing_to_sql(ti):
        avg_data = ti.xcom_pull(task_ids = 'get_avg_high')
        avg_data_df = pd.DataFrame(avg_data)
        avg_data_df.columns = ['name', 'pos', 'team', 'g', 'ab', 'h', 'bb', 'so', 'obp', 'slg', 'avg', 'record_date']
        avg_data_df.reset_index(drop= True, inplace= True)
        print(avg_data_df)
        dbUser = 'airflow'
        dbPwd = 'airflow'
        database = 'mlb_parser_DB'
        engine = create_engine('postgresql://'+ dbUser +':'+ dbPwd +'@postgres:5432/' + database)
        try:
            avg_data_df.to_sql(name='mlb_avg_lead_2023', con=engine, if_exists="append", index=False)
        except Exception as e:
            print(f"An exception occurred: {str(e)}")
        finally:
            print("job done")

    def hr_standing_to_sql(ti):
        hr_data = ti.xcom_pull(task_ids = 'get_hr_high')
        hr_data_df = pd.DataFrame(hr_data)
        hr_data_df.columns = ['name', 'pos', 'team', 'g', 'ab', 'hr', 'rbi', 'bb', 'so', 'obp', 'slg', 'record_date']
        hr_data_df.reset_index(drop= True, inplace= True)
        print(hr_data_df)
        dbUser = 'airflow'
        dbPwd = 'airflow'
        database = 'mlb_parser_DB'
        engine = create_engine('postgresql://'+ dbUser +':'+ dbPwd +'@postgres:5432/' + database)
        try:
            hr_data_df.to_sql(name='mlb_hr_lead_2023', con=engine, if_exists="append", index=False)
        except Exception as e:
            print(f"An exception occurred: {str(e)}")
        finally:
            print("job done")
    
    def dag_finish():
        return "Finish"
    
    task_select_team = PythonOperator(
        task_id = "select_team",
        python_callable = select_team
    )

    task_data_clean = PythonOperator(
        task_id = "data_clean",
        python_callable = clean_data
    )

    task_create_mlb_data_table = PostgresOperator(
        task_id = 'create_postgre_table_mlb_data',
        postgres_conn_id = 'postgres_mlb_parser_DB',
        sql = """
            create table if not exists mlb_data_2023 (
                Name varchar(40),
                POS varchar(5),
                Team varchar(20),
                G int,
                AB int,
                R int,
                H int,
                Double int,
                Third int,
                HR int,
                RBI int,
                BB int,
                SO int,
                SB int,
                CS int, 
                OBP float,
                SLG float,
                primary key(Name, POS, Team)
            )
            """
    )

    task_create_mlb_hr_table = PostgresOperator(
        task_id = 'create_postgre_table_hr',
        postgres_conn_id = 'postgres_mlb_parser_DB',
        sql = """
            create table if not exists mlb_hr_lead_2023 (
                Name varchar(40),
                POS varchar(5),
                Team varchar(20),
                G int,
                AB int,
                HR int,
                RBI int,
                BB int,
                SO int,
                OBP float,
                SLG float,
                Record_date date,
                primary key(name, pos, team, record_date)
            )
            """
    )

    task_create_mlb_avg_table = PostgresOperator(
        task_id = 'create_postgre_table_avg',
        postgres_conn_id = 'postgres_mlb_parser_DB',
        sql = """
            create table if not exists mlb_avg_lead_2023 (
                Name varchar(40),
                POS varchar(5),
                Team varchar(20),
                G int,
                AB int,
                H int,
                BB int,
                SO int,
                OBP float,
                SLG float,
                AVG float,
                Record_date date,
                primary key(name, pos, team, record_date)
            )
            """
    )

    task_avg_high = PostgresOperator(
        task_id = 'get_avg_high',
        postgres_conn_id = 'postgres_mlb_parser_DB',
        sql = """
            SELECT
                "Name",
                "POS",
                "Team",
                "G",
                "AB",
                "H",
                "BB",
                "SO",
                "OBP",
                "SLG",
                (CAST("H" AS float) / CAST("AB" AS float)) AS "Average_Bat",
                CURRENT_DATE AS "date"
                FROM mlb_data_2023
                WHERE "AB" > (
                    SELECT AVG("AB") FROM mlb_data_2023
                )
                ORDER BY "Average_Bat" DESC
                LIMIT 10;
            """
    )

    task_avg_df = PythonOperator(
        task_id = "output_avg_df",
        python_callable = avg_df
    )

    task_hr_high = PostgresOperator(
        task_id = 'get_hr_high',
        postgres_conn_id = 'postgres_mlb_parser_DB',
        sql = """
            SELECT
                "Name",
                "POS",
                "Team",
                "G",
                "AB",
                "HR",
                "RBI",
                "BB",
                "SO",
                "OBP",
                "SLG",
                CURRENT_DATE AS "date"
                FROM mlb_data_2023
                WHERE "HR" >= (SELECT DISTINCT("HR") AS "HR" FROM mlb_data_2023 ORDER BY "HR" DESC LIMIT 1 OFFSET 9)
                ORDER BY "HR" DESC;
            """
    )

    task_hr_df = PythonOperator(
        task_id = "output_hr_df",
        python_callable = hr_df
    )

    task_data_standing = PythonOperator(
        task_id = "data_standing_finish",
        python_callable = dag_finish
    )

    task_hr_lead_to_sql = PythonOperator(
        task_id = "task_hr_lead_to_sql",
        python_callable = hr_standing_to_sql
    )

    task_avg_lead_to_sql = PythonOperator(
        task_id = "task_avg_lead_to_sql",
        python_callable = avg_standing_to_sql
    )
    
    task_create_mlb_data_table
    task_create_mlb_hr_table
    task_create_mlb_avg_table
    task_select_team >> task_data_clean >> task_avg_high >> task_avg_df >> task_data_standing
    task_select_team >> task_data_clean >> task_hr_high   >> task_hr_df  >> task_data_standing
    task_data_standing >> [task_hr_lead_to_sql, task_avg_lead_to_sql]

