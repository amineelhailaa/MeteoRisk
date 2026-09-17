METEO RISK

This project aims to provide weather risk analysis for various locations. It utilizes OpenWeatherMap API to fetch weather data and perform risk assessment based on temperature, precipitation, and other relevant factors.

## Airflow import path

Airflow automatically adds `/opt/airflow/dags` to Python's module search path, but the project modules are mounted in `/opt/airflow/extraction`, `/opt/airflow/transformation`, and `/opt/airflow/load`. Without `/opt/airflow` in `PYTHONPATH`, the DAG cannot import these modules and Airflow reports `ModuleNotFoundError`, so the DAG does not appear in the UI.

The Airflow service must therefore define:

```yaml
PYTHONPATH=/opt/airflow
```

Changing DAG or project source files does not require an image rebuild because they are mounted as volumes. Changing this environment variable requires recreating the Airflow container, while changing the Dockerfile or Python requirements requires rebuilding the image.

Only `/opt/airflow/logs` is persisted for Airflow. Persisting the entire `/opt/airflow` directory can preserve stale runtime PID files after a container is replaced, causing the webserver to incorrectly believe that it is already running.

## Airflow local login

Local development credentials:

```text
Username: admin
Password: QWt5UA4Dvxp23hAW
```

These credentials are intended for local development only and must be changed before publishing or deploying the project.
