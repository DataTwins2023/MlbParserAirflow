# MlbParserAirflow
## description
this is an airflow DAG used to collect MLB data everyday and created an API to demonstrate the data

## project goal and tools
Comprison:
Project comprises three segement, including parsing data from MLB website, committing data to database and demonstrating data via API. 
Tools: 
Airflow, Docker and postgresql are used to collect data and send to database
Goals:
Eventually, I wish to train these data collected day by day to build a model used to predict MVP（Most Valueable Player）, which I had completed a [similar thing](https://medium.com/@andy.hsu871226/%E9%81%8B%E7%94%A8%E9%82%8F%E8%BC%AF%E6%96%AF%E5%9B%9E%E6%AD%B8%E9%A0%90%E6%B8%ACnba%E5%B9%B4%E5%BA%A6%E5%89%8D%E4%B8%89%E9%9A%8A-8956cb6498ec) in the field of NBA（National Basketball Association）,of MLB（Major League Baseball）.

![截圖 2023-12-04 下午12 48 13](https://github.com/DataTwins2023/MlbParserAirflow/assets/143244871/074bd95e-5ad5-4cea-99f7-e5f57398505c)
dag used to gain the data of players 

![截圖 2023-12-04 下午12 48 37](https://github.com/DataTwins2023/MlbParserAirflow/assets/143244871/50c9fc2c-8b79-4ca8-8209-629f69b956fd)
dag to update team ranking and grade

<img width="469" alt="截圖 2023-12-04 下午12 30 40" src="https://github.com/DataTwins2023/MlbParserAirflow/assets/143244871/ec12fefb-39b2-4b7f-86b8-9e4762d2cb51">

table in the database storing data

<img width="730" alt="截圖 2023-12-04 下午12 31 33" src="https://github.com/DataTwins2023/MlbParserAirflow/assets/143244871/486623ea-fd50-448a-a053-7126156f2b33">

ER model of these tables


## screenshot of each table(limit 10)


<img width="562" alt="截圖 2023-12-04 下午12 56 07" src="https://github.com/DataTwins2023/MlbParserAirflow/assets/143244871/35756b30-8b23-459b-b3f1-6153d1cc80fe">

team grade

<img width="973" alt="截圖 2023-12-04 下午12 57 23" src="https://github.com/DataTwins2023/MlbParserAirflow/assets/143244871/ddffc5a0-673f-4a4b-85ab-2243fa915142">

batter rank order by AVG

<img width="902" alt="截圖 2023-12-04 下午12 57 59" src="https://github.com/DataTwins2023/MlbParserAirflow/assets/143244871/a40a86ee-7ab0-419a-b397-4073d7f6df4d">

batter rank order by HR

<img width="819" alt="截圖 2023-12-04 下午1 00 55" src="https://github.com/DataTwins2023/MlbParserAirflow/assets/143244871/9b8d0016-7175-4fc0-893a-ca0d3af2a533">

raw data of batters without advanced query to get specific result









