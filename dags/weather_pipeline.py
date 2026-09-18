from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from extraction import fetch_weather_data
from load.service import load_weather_csv
from transformation.transform import transform_weather_data


#ETL
def extract():
    fetch_weather_data.execute_load()
    print("Extracting data...")

def transformD():
    transform_weather_data()
    print("Transforming data...")

def load():
    load_weather_csv()
    print("Loading data...")




with DAG(
    dag_id="Weather",
    schedule_interval="@weekly",
    catchup=False,
    start_date= datetime(2026, 9, 16) ) as dag:


    extraction = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )

    transformation = PythonOperator(
        task_id="transform",
        python_callable=transformD,
    )

    load = PythonOperator(
        task_id="load",
        python_callable=load,
    )


    extraction >> transformation >> load
