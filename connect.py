import psycopg2
from constants import *

def connect():
    conn = psycopg2.connect(
        database = DB_NAME,
        user = DB_USER,
        password = DB_PASSWORD,
        host = DB_HOST,
        port = "5432"
    )
    return conn