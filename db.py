# db.py
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="tution_db",
            user="postgres",
            password="123456789"
        )
        return conn
    except psycopg2.Error:
        return None
