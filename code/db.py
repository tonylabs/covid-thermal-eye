import conf.db as db
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

def insert_book(unique_id, celsius):
    query = "INSERT INTO `tlabs_user_temperature` (`unique_id`, `celsius`) " \
            "VALUES(%s, %s)"
    args = (unique_id, celsius)
    try:
        conn = mysql.connector.connect(user=db.mysql["user"], password=db.mysql["password"], host=db.mysql["host"], database=db.mysql["db"])
        cursor = conn.cursor()
        cursor.execute(query, args)
        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')
        conn.commit()
    except Error as error:
        print(error)
    finally:
        cursor.close()
        conn.close()