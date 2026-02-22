# db.py
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="tution_db",
        user="postgres",
        password="ABCD!@#$" \
        ""
    )
    return conn


