import psycopg


def get_db_connection():
    return psycopg.connect(
        host="localhost",
        database="tution_db",
        user="postgres",
        password="123456789",
    )
