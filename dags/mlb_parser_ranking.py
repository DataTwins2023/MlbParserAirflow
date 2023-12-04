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

import statsapi

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
    dag_id = 'mlb_parser_ranking',
    default_args = default_args,
    description = 'To gather the ranking info of mlb',
    start_date = datetime(2023, 9, 11),
    schedule_interval = '55 3 * * *'
) as dag:
    def get_rank():
        ranking_list = []
        # data_source
        data_source = statsapi.standings_data()
        # 每個div一個dict
        for x in data_source.keys():
            div_data = data_source[x]
            print(div_data)
            # teams是同一分區所有球隊資訊的list
            for y in div_data['teams']:
                team_data = [y['name'], y['w'], y['l']]
                ranking_list.append(team_data)
        ranking_df = pd.DataFrame(ranking_list, columns = ['Team', 'W', 'L'])
        ranking_df['Total_G'] = ranking_df['W'] + ranking_df['L']
        ranking_df

        team_convert_dict = {
            'Baltimore Orioles'     : 'BAL',
            'Tampa Bay Rays'        : 'TB',
            'Toronto Blue Jays'     : 'TOR',
            'New York Yankees'      : 'NYY',
            'Boston Red Sox'        : 'BOS',
            'Minnesota Twins'       : 'MIN',
            'Cleveland Guardians'   : 'CLE',
            'Detroit Tigers'        : 'DET',
            'Chicago White Sox'     : 'CWS',
            'Kansas City Royals'    : 'KC',
            'Houston Astros'        : 'HOU',
            'Seattle Mariners'      : 'SEA',
            'Texas Rangers'         : 'TEX',
            'Los Angeles Angels'    : 'LAA',
            'Oakland Athletics'     : 'OAK',
            'Atlanta Braves'        : 'ATL',
            'Philadelphia Phillies' : 'PHI',
            'Miami Marlins'         : 'MIA',
            'New York Mets'         : 'NYM',
            'Washington Nationals'  : 'WSH',
            'Milwaukee Brewers'     : 'MIL',
            'Chicago Cubs'          : 'CHC',
            'Cincinnati Reds'       : 'CIN',
            'Pittsburgh Pirates'    : 'PIT',
            'St. Louis Cardinals'   : 'STL',
            'Los Angeles Dodgers'   : 'LAD',
            'Arizona Diamondbacks'  : 'AZ',
            'San Francisco Giants'  : 'SF',
            'San Diego Padres'      : 'SD',
            'Colorado Rockies'      : 'COL'
        }

        ranking_df['Team_abb'] = ranking_df['Team'].map(team_convert_dict)
        ranking_df.reset_index(drop= True, inplace= True)
        print(ranking_df)
        dbUser = 'airflow'
        dbPwd = 'airflow'
        database = 'mlb_parser_DB'
        engine = create_engine('postgresql://'+ dbUser +':'+ dbPwd +'@postgres:5432/' + database)
        try:
            ranking_df.to_sql(name='mlb_team_grade_2023', con=engine, if_exists="replace", index=False)
        except Exception as e:
            print(f"An exception occurred: {str(e)}")
        finally:
            print("job done")
    

    task_get_rank = PythonOperator(
        task_id = 'get_rank',
        python_callable = get_rank
    )




    task_create_mlb_ranking_table = PostgresOperator(
        task_id = 'create_postgre_table_ranking',
        postgres_conn_id = 'postgres_mlb_parser_DB',
        sql = """
            create table if not exists mlb_team_grade_2023 (
                team varchar(40),
                w int,
                l int,
                total_g int,
                team_abb varchar(40),
                primary key(team)
            )
            """
    )

    task_create_mlb_ranking_table>> task_get_rank
