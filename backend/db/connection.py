import psycopg2

def get_connection():
    conn = psycopg2.connect(
        dbname="loan_db",
        user="postgres",
        password="0921",  
        host="localhost",
        port="5432"
    )
    return conn