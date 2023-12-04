# MlbParserAirflow
this is an airflow DAG used to collect MLB data everyday and created an API to demonstrate the data

Project comprises three segement, including parsing data from MLB website, committing data to database and demonstrating data via API. 
Tools: Airflow, Docker and postgresql are used to collect data and send to database

![截圖 2023-12-04 下午12 48 13](https://github.com/DataTwins2023/MlbParserAirflow/assets/143244871/074bd95e-5ad5-4cea-99f7-e5f57398505c)
dag used to gain the data of players 

![截圖 2023-12-04 下午12 48 37](https://github.com/DataTwins2023/MlbParserAirflow/assets/143244871/50c9fc2c-8b79-4ca8-8209-629f69b956fd)


<img width="469" alt="截圖 2023-12-04 下午12 30 40" src="https://github.com/DataTwins2023/MlbParserAirflow/assets/143244871/ec12fefb-39b2-4b7f-86b8-9e4762d2cb51">
table in the database storing data

<img width="730" alt="截圖 2023-12-04 下午12 31 33" src="https://github.com/DataTwins2023/MlbParserAirflow/assets/143244871/486623ea-fd50-448a-a053-7126156f2b33">
ER model of these tables
