import mysql.connector as connection
import pandas as pd
from sqlalchemy import create_engine
import pymysql

# Create a decorator that connects to the DB and closes the connection once the function is done
def start_connection():
    # For server use:
    conn = connection.connect(user='nick', password='usalud35',
                              host='localhost',
                              database='orders')
#     conn = connection.connect(user='nick', password='usalud35',
#                               host='mysql-11179-0.cloudclusters.net', port=11179,
#                               database='orders')
    cursor = conn.cursor()
    return conn, cursor
    
def stop_connection(conn, cursor):
    cursor.close()
    conn.close()
    
def init_db(force=False):
    conn, cursor = start_connection()
    ''' Check that the required tables exist, else create them'''
    ''':param force: Create tables again'''
    if force:
        cursor.execute('DROP TABLE IF EXISTS order_basket')
        cursor.execute('DROP TABLE IF EXISTS client_info')
    
    # Create a table in DB to store a user's order basket
    cursor.execute('''CREATE TABLE IF NOT EXISTS order_basket (
                        id INTEGER AUTO_INCREMENT PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        price FLOAT NOT NULL,
                        ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                        ) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci '''
                        )
    # Create a table in DB to store user addresses
    cursor.execute('''CREATE TABLE IF NOT EXISTS client_info (
                        id INTEGER AUTO_INCREMENT PRIMARY KEY REFERENCES order_basket(id),
                        user_id INTEGER NOT NULL,
                        latitude TEXT,
                        longitude TEXT, 
                        phone_number TEXT,
                        username TEXT
                        ) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci '''
                        )
    conn.commit()
    stop_connection(conn, cursor)
    
def add_order(user_id, name, quantity, price):
    ''' Добавляет единицу товара в таблицу'''
    conn, cursor = start_connection()
    cursor.execute('INSERT INTO order_basket (user_id, name, quantity, price) VALUES (%s, %s, %s, %s)', (user_id, name, quantity, price))
    conn.commit()
    stop_connection(conn, cursor)

    
def list_order(user_id):
    '''List the basket to the user'''
    conn, cursor = start_connection()
    cursor.execute('SELECT name, SUM(quantity), SUM(price) FROM order_basket WHERE user_id = %s GROUP BY price, name, quantity', (user_id, ))
    list_of_tuples = cursor.fetchall()
    
    # Unpack a list of tuples and add each tuple into a list
    res_list = []
    for count, tup in enumerate(list_of_tuples):
        tup = list(tup)
        res_list.append(tup)
        yield res_list[count]
    stop_connection(conn, cursor)

# Now transform the Excel price list into a table in the database
# def excel_connect():
#     engine = create_engine("mysql+pymysql://sql7356052:XrZadZZzmv@sql7.freemysqlhosting.net:3306/sql7356052?charset=utf8mb4")
#     # engine = create_engine("mysql+pymysql://sql7356052:XrZadZZzmv@sql7.freemysqlhosting.net:3306/sql7356052", encoding='utf8')

#     # conn = pymysql.connect(user='sql7356052', password='XrZadZZzmv',
#     #                           host='sql7.freemysqlhosting.net',
#     #                           database='sql7356052',charset='utf8')
#     conn = engine.connect()
#     prices = pd.read_excel('prices.xlsx', header=0)
#     prices.to_sql('prices', con=conn, if_exists='replace', index=False)
#     conn.close()

def access_price_list(name):
    '''Access a required position in the price list'''
    conn, cursor = start_connection()
    cursor.execute('SELECT name, price FROM prices WHERE name = %s', (name, ))
    tup = cursor.fetchone()
    stop_connection(conn, cursor)
    return tup # Returns a tuple of (name, price) type

def write_location(user_id, lat, long):
    conn, cursor = start_connection()
    cursor.execute('INSERT INTO client_info (user_id, latitude, longitude) VALUES (%s, %s, %s)', (user_id, lat, long))
    conn.commit()
    stop_connection(conn, cursor)
    
def write_username(user_id, username):
    conn, cursor = start_connection()
    cursor.execute('INSERT INTO client_info (user_id, username) VALUES (%s, %s)', (user_id, username))
    conn.commit()
    stop_connection(conn, cursor)

# Function that deletes user's order from DB after pressed "DONE" ??
