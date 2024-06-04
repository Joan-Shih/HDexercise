import pymysql
from config import settings
from mysql.connector import Error

def connect_mysql():
    timeout = 10
    try:
        conn = pymysql.connect(
           charset="utf8mb4",
           connect_timeout=timeout,
           cursorclass=pymysql.cursors.DictCursor,
           db=settings.database_name,
           host=settings.database_hostname,
           password=settings.database_password,
           read_timeout=timeout,
           port=21732,
           user=settings.database_username,
           write_timeout=timeout
           )
        cursor = conn.cursor() #dictionary=True
        yield cursor
    except Error as e:
        print(e)
    finally:
        #cursor.close()
        conn.commit()
        conn.close()