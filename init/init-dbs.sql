-- init-multiple-dbs.sql

-- Airflow metadata database
CREATE DATABASE airflow;
CREATE USER airflow WITH PASSWORD 'airflow';
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

-- MeteoRisk application database
CREATE DATABASE meteorisk_db;
CREATE USER meteorisk_user WITH PASSWORD 'meteorisk';
GRANT ALL PRIVILEGES ON DATABASE meteorisk_db TO meteorisk_user;