-- init-multiple-dbs.sql

-- Airflow metadata database
CREATE USER airflow WITH PASSWORD 'airflow';
CREATE DATABASE airflow OWNER airflow;
\connect airflow
ALTER SCHEMA public OWNER TO airflow;
GRANT ALL ON SCHEMA public TO airflow;

-- MeteoRisk application database
CREATE USER meteorisk_user WITH PASSWORD 'meteorisk';
CREATE DATABASE meteorisk_db OWNER meteorisk_user;
\connect meteorisk_db
ALTER SCHEMA public OWNER TO meteorisk_user;
GRANT ALL ON SCHEMA public TO meteorisk_user;
