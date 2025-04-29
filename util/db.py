import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection(retries=10, delay=3):
    for i in range(retries):
        try:
            return psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST", "database"),
                port=os.getenv("DB_PORT", 5432),
                cursor_factory=RealDictCursor
            )
        except psycopg2.OperationalError as e:
            print(f"[Postgres Retry {i+1}/{retries}] {e}")
            time.sleep(delay)
    raise Exception("Could not connect to PostgreSQL after multiple attempts.")
    