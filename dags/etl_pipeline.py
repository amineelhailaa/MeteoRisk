from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator


#ETl


def Extraction():
    print(" data extracted successfully ")

def Transformation():
    print("cleaning and transformation of data succeed")



def Load():
    print("data loaded into postgres db successfully")





dag = DAG(
    dag_id="live_coding",
    description="This is a live coding dag",
    schedule="@hourly",
    start_date = datetime(2026,9,17),
    catchup = False,
    tags = ["etl", "live_coding"],
    end_date = datetime(2026,9,20),
    max_active_runs = 1,
    max_active_tasks = 1,
)


E = PythonOperator(
    task_id = "lextraction",
    python_callable = Extraction,
    dag = dag,
)

T = PythonOperator(
    task_id = "transformation",
    python_callable = Transformation,
    dag = dag,
)

L = PythonOperator(
    task_id = "load",
    python_callable = Load,
    dag = dag,
)


E >> T >> L
