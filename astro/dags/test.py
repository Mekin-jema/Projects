from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task 
from airflow.utils.dates import days_ago

# Corrected: Removed trailing comma to keep LATITUDE as a string
LATITUDE = '51.5074'
LONGITUDE = '0.1278'
POSTGRES_CONN_ID = 'postgres_default'
API_CONN_ID = 'OPEN_METO_API'

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1)
}

# DAG
with DAG(
    dag_id='weather_data_pipeline', 
    default_args=default_args, 
    schedule_interval='@daily',
    catchup=False
) as dag:

    @task()
    def extract_weather_data():
        http_hook = HttpHook(http_conn_id=API_CONN_ID, method='GET')
        endpoint = f'/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true'
        response = http_hook.run(endpoint)
        return response.json()

    @task()
    def transform_weather_data(weather_data):
        current_weather = weather_data.get('current_weather', {})
        transformed_data = {
            'latitude': LATITUDE,
            'longitude': LONGITUDE,
            'temperature': current_weather.get('temperature'),
            'windspeed': current_weather.get('windspeed'),
            'winddirection': current_weather.get('winddirection'),
            'weathercode': current_weather.get('weathercode'),
            'timestamp': current_weather.get('time')
        }
        return transformed_data

    @task()
    def load_weather_data(transformed_data):
        postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

        # Create table if it does not exist
        create_table_query = """
            CREATE TABLE IF NOT EXISTS weather (
                latitude FLOAT,
                longitude FLOAT,
                temperature FLOAT,
                windspeed FLOAT,
                winddirection FLOAT,
                weathercode INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        postgres_hook.run(create_table_query)

        # Insert data matching table schema
        insert_query = """
            INSERT INTO weather (latitude, longitude, temperature, windspeed, winddirection, weathercode, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        postgres_hook.run(insert_query, parameters=(
            transformed_data['latitude'],
            transformed_data['longitude'],
            transformed_data['temperature'],
            transformed_data['windspeed'],
            transformed_data['winddirection'],
            transformed_data['weathercode'],
            transformed_data['timestamp']
        ))

    # Task execution pipeline
    weather_data = extract_weather_data()
    transformed_data = transform_weather_data(weather_data)
    load_weather_data(transformed_data)