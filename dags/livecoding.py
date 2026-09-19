from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator



def extraction():
    print("Extraction done!")

def transformation():
    print("Transformation done!")

def load():
    print("Load done!")

dag = DAG(
    dag_id="livecoding",
    description="Livecoding DAG",
    schedule="@daily",
    start_date=datetime(2026,9, 17),
    end_date = datetime(2026, 10, 17),
    catchup=False,
    max_active_runs=1,
    max_active_tasks = 1,
    tags=["etl"]
    )

Extraction = PythonOperator(
    task_id="extraction",
    dag=dag,
    python_callable=extraction
)

Transform = PythonOperator(
    task_id="transformation",
    dag=dag,
    python_callable=transformation
)


Load = PythonOperator(
    task_id="load",
    dag=dag,
    python_callable=load
)



Extraction >> Transform >> Load


################################################### or
with DAG(
    dag_id="livecoding",
    description="Livecoding DAG",
    schedule="@daily",
    start_date=datetime(2026,9, 17),
    end_date = datetime(2026, 10, 17),
    catchup=False,
    max_active_runs=1,
    max_active_tasks = 1,
    tags=["etl"]
    ) as dag:


    Extraction = PythonOperator(
        task_id="extraction",
        python_callable=extraction
    )

    Transform = PythonOperator(
        task_id="transformation",
        python_callable=transformation
    )

    Load = PythonOperator(
        task_id="load",
        python_callable=load
    )

    Extraction >> Transform >> Load