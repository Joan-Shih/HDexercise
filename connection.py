import mysql.connector
from mysql.connector import Error
from .config import settings
from icecream import ic

def connect_mysql():
    try:
        conn = mysql.connector.connect(host=settings.database_hostname,
                                       database=settings.database_name,
                                       user=settings.database_username,
                                       password=settings.database_password)
        cursor = conn.cursor(dictionary=True)
        yield cursor
    except Error as e:
        print(e)
    finally:
        #cursor.close()
        conn.commit()
        conn.close()
