import sqlite3
from datetime import datetime
from math import isnan
from pathlib import Path

import sys, os
'''
___________________________________________________________
______________Initialisation of the database_______________
___________________________________________________________
'''

#DATABASE_FILE = str(Path(__file__).resolve().parent)+"/POS_database.db"
# Opening of the database
import json
import sys, os
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    PARENTDIR = sys._MEIPASS
    with open(PARENTDIR+"/settings.json", "r") as fn:
        db = json.load(fn)
    DATABASE_FILE = db["MainDirectory"]+"/sql/POS_database.db"
else:
    #PARENTDIR = os.path.dirname(os.path.abspath(__file__))
    #DATABASE_FILE = "../sql/POS_database.db"
    DATABASE_FILE = str(Path(__file__).resolve().parent)+"/POS_database.db"

"""
dir = os.getcwd()
i = dir.rfind('/')
PARENTDIR = dir[:i]
"""

print(DATABASE_FILE)
conn = sqlite3.connect(DATABASE_FILE)
# Creation of the cursor
cursor = conn.cursor()
#print("Database opened successfully")

'''
___________________________________________________________
____________________Primary functions______________________
___________________________________________________________
'''

# Creation of all the tables if not exist.
def creation_tables():
    cursor.execute("""CREATE TABLE IF NOT EXISTS orders(
                       ORDER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                       CUSTOMER_ID INTEGER NON NULL,
                       DATE TEXT NON NULL,
                       TOTAL_PRICE FLOAT NON NULL,
                       STATUT TEXT NON NULL)
                       """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS items(
                        ITEM_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        NAME TEXT NON NULL UNIQUE,
                        BARECODE TEXT,
                        PICTURE TEXT,
                        NUMBER INTEGER NON NULL,
                        PRICE INTEGER NON NULL,
                        DESCRIPTION TEXT)
                        """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS customers(
                        CUSTOMER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        FIRST_NAME TEXT NON NULL,
                        LAST_NAME TEXT NON NULL,
                        EMAIL TEXT NON NULL,
                        PHONE_NUMBER TEXT NON NULL,
                        POSTAL_ADRESS TEXT NON NULL)
                        """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS items_bought(
                        TRANSACTION_ID INTEGER NON NULL,
                        DATE TEXT NON NULL,
                        ITEM_ID INTEGER NON NULL,
                        NUMBER INTEGER NON NULL,
                        PRICE FLOAT NON NULL,
                        TAX FLOAT NON NULL)
                        """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS money_transactions(
                        TRANSACTION_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        DATE TEXT NON NULL,
                        TRANSACTION_TYPE TEXT NON NULL,
                        TOTAL_PRICE FLOAT NON NULL,
                        CREDIT_CARD_ID INT NON NULL)
                        """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                        USER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        ADMIN INTEGER NOT NULL,     
                        USERNAME TEXT NON NULL UNIQUE,
                        PASSWORD TEXT NON NULL)   
                        """)  # Admin must be 0 or 1. (BOOL)


# Create an admin user if one doesnt exist


# Fonction to drop a table
def drop_table(table_name):
    command = "DROP TABLE ", table_name
    command = ''.join(command)
    cursor.execute(command)


# Fonction to add a value in a table
def add_values(table, attributs, values):
    command = "INSERT OR REPLACE INTO ", table, attributs, "VALUES", values
    command = ''.join(command)
    #print(command)
    conn.execute(command)
    conn.commit()


#
def add_values_only(table, attributs, values):
    command = "INSERT OR IGNORE INTO ", table, attributs, "VALUES", values
    command = ''.join(command)
    conn.execute(command)
    conn.commit()


def update_values(table, attribut, new_value, row, old_value):
    command = "UPDATE ", table, " set ", attribut, " = ", new_value, " where ", row, " = ", old_value
    command = ''.join(command)
    conn.execute(command)
    conn.commit()


def delete_values(table, attribut, value):
    command = 'DELETE FROM ', table, ' WHERE ', attribut, ' LIKE ', value
    command = ''.join(command)
    conn.execute(command)
    conn.commit()


def SQL_Query_with_target(target, request):
    target = target
    command = "SELECT", "FROM", "WHERE"
    #print(    request,
    #    (target,),)
    rows = cursor.execute(
        request,
        (target,),
    ).fetchall()
    #print(rows)  # Might need to remove #-Sean
    return rows


def SQL_Query_table(table):
    command = "SELECT * FROM ", table
    command = ''.join(command)
    rows = cursor.execute(command).fetchall()
    #print(rows)
    return rows

def SQL_Query_table_highest_id(table, column):
    command = "SELECT Max(", column, ") FROM ", table
    command = ''.join(command)
    rows = cursor.execute(command).fetchall()
    if not rows:
        return 0
    return rows[0][0] # Returns the largest id


def format_list(inputs: list, items=False) -> str:
    '''
    Takes in a list, and returns them as a list to be inserted into the
    '''
    '("1","13/08","12.34","+")'

    out = " "
    if type(inputs[0]) != list:
        out += '('
        for cell in inputs:
            if type(cell) in (float, int) and not isnan(cell):
                out += f"{cell},"
            else:
                out += f"'{cell}',"
        out = out[:-1] + ')'
    else:
        for row in inputs:
            out += '('
            ##print(row)
            for cell in row:
                if type(cell) in (float, int) and not isnan(cell):
                    out += f"{cell},"
                else:
                    out += f"'{cell}',"
            out = out[:-1] + '),'
        out = out[:-1]
    return out


def reconnectDb():
    '''Used if we add product, we need to refresh the database.'''
    global cursor
    global conn
    conn.commit()
    cursor.close()
    conn.close
    conn = sqlite3.connect(DATABASE_FILE)
    # Creation of the cursor
    cursor = conn.cursor()

'''
___________________________________________________________
___________________Secondary functions_____________________
___________________________________________________________
'''


# items functions
def add_item(values):
    add_values('items', ' (NAME,BARECODE,PICTURE,NUMBER,PRICE,DESCRIPTION) ', values)


def remove_item(value):
    delete_values('items', 'ITEM_ID', value)


def see_stock():
    SQL_Query_table('items')

def see_items(item_id):
    command = "SELECT ITEM_ID, NAME, NUMBER, PRICE FROM items WHERE ITEM_ID = ?"
    item = SQL_Query_with_target(item_id, command)
    return item


def change_number_stock(key, value):
    update_values('items', 'NUMBER', value, 'ITEM_ID', key)

def decrement_stock(key, count):
    #key is the itemID
    vList = conn.execute(f"SELECT NUMBER FROM ITEMS WHERE ITEM_ID == '{key}'").fetchall()
    value = str(vList[0][0] - count)
    update_values('items', 'NUMBER', value, 'ITEM_ID', str(key))

def change_number_stock_bulk(llist):
    for cell in llist:
        value = str(cell[0])
        key = str(cell[1])
        update_values('items', 'NUMBER', value, 'ITEM_ID', key)


def change_price_stock(key, value):
    update_values('items', 'PRICE', value, 'ITEM_ID', key)


# stock functions

def pay(key):
    update_values('orders', 'STATUT', 'paid', 'CUSTOMER_ID', key)


def add_order(values):
    date = str(datetime.now())
    values = values.split(',')
    date = '"', date, '"'
    date = ''.join(date)
    values.insert(1, date)
    statut = '"waiting")'
    values.append(statut)
    values = ','.join(values)
    add_values('orders', '(DATE,TOTAL_PRICE,STATUT)', values)



def search_order(customer_id,dateb,datee):
    command = "SELECT ORDER_ID, CUSTOMER_ID, DATE, TOTAL_PRICE, STATUT FROM orders WHERE CUSTOMER_ID = ?"
    order=SQL_Query_with_target(customer_id, command)
    #print(order)
    #print(type(order))
    dateb = dateb.split('/')
    datee = datee.split('/')
    order_between_two_dates=[]
    for element in order:
        date=element[2]
        date2=date.split(' ')
        date3=date2[0]
        date4=date3.split('-')
        if dateb[0] <= date4[0] <= datee[0] and dateb[1] <= date4[1] <= datee[1] and dateb[2] <= date4[2] <= \
                datee[2]:
            order_between_two_dates.append(element)
        else:
            continue
    return order_between_two_dates



# item_bought functions

def add_item_boughts(values):
    add_values('items_bought', '(TRANSACTION_ID,DATE,ITEM_ID,NUMBER,PRICE,TAX)', values)
    


def add_item_boughtsOLD(values):
    #print(values)
    #print(type(values))
    valuesbis=values.split(',')
    item_id = valuesbis[1]
    characters = '"'
    for x in range(len(characters)):
        item_id = item_id.replace(characters[x], "")
    item=see_items(item_id)
    item_price=str(item[0])
    item_price=item_price.split(',')
    item_price=item_price[3]
    item_price2=[]
    for element in item_price:
        if element != ')':
            item_price2.append(element)
        else:
            continue
    item_price=''.join(item_price2)
    #print(item_price)
    date = str(datetime.now())
    values = values.split(',')
    date = '"', date, '"'
    date = ''.join(date)
    values.insert(1, date)
    values.append(item_price)
    price=float(item_price)
    tax=(7.75/100)*float(price)
    tax='"' + str(tax) + '")'
    values.append(tax)
    values= ','.join(values)
    #print(values)
    add_values('items_bought', '(TRANSACTION_ID,DATE,ITEM_ID,NUMBER,PRICE,TAX)', values)

def see_item_bought_w_d(customer_id,dateb, datee):
    command = "SELECT TRANSACTION_ID,DATE,ITEM_ID,NUMBER,PRICE,TAX FROM items_bought WHERE TRANSACTION_ID = ?"
    items = SQL_Query_with_target(customer_id, command)
    items_between_two_dates=[]
    dateb=dateb.split('/')
    datee=datee.split('/')
    for element in items:
        element2=list(element)
        element3=element2[1]
        element4=element3.split(' ')
        element5=element4[0]
        element6=element5.split('-')
        if dateb[0] <= element6[0] <= datee[0] and dateb[1] <= element6[1] <= datee[1] and dateb[2] <= element6[2] <= \
                datee[2]:
            items_between_two_dates.append(element)
        else:
            continue
    return items_between_two_dates

def see_item_bought(values):
    command = "SELECT TRANSACTION_ID, DATE, ITEM_ID, NUMBER, PRICE, TAX FROM items_bought WHERE TRANSACTION_ID = ?"
    rows=SQL_Query_with_target(values, command)
    return rows


# money_transactions functions

def add_transcation(values):
    date = str(datetime.now())
    #values = values.split(',')
    date =  date
    date = ''.join(date)
    values.insert(0, date)
    #values = ','.join(values)
    values = format_list(values)
    add_values('money_transactions', '(DATE,TRANSACTION_TYPE,TOTAL_PRICE,CREDIT_CARD_ID)', values)
    return date

def calculate_balance(dateb, datee):
    balance = 0
    dates = []
    dates2 = []
    rows2 = []
    rows = conn.execute("SELECT DATE,TRANSACTION_TYPE,TOTAL_PRICE FROM money_transactions").fetchall()
    #print(rows)
    #print(type(rows))
    list = [x for elem in rows for x in elem]
    for k in range(0, len(list) - 1, 3):
        dates.append(list[k])
    #print(dates)
    for element in dates:
        var = element.split(' ')
        dates2.append(var[0])
    dateb = dateb.split('/')
    datee = datee.split('/')
    n = 0
    for element in dates2:
        #print(element)
        splitdate = element.split('-')
        #print(splitdate)
        if dateb[0] <= splitdate[0] <= datee[0] and dateb[1] <= splitdate[1] <= datee[1] and dateb[2] <= splitdate[2] <= \
                datee[2]:
            rows2.append(rows[n])
        n += 1
    for element in rows2:
        if element[1] == '+':
            balance += element[2]
        elif element[1] == '-':
            balance -= element[2]
        else:
            continue
    #print('Your balance between ', dateb, ' and ', datee, ' is ', balance, '$')
    return rows2


# customer functions

def add_customer(values):
    add_values('customers', '(FIRST_NAME,LAST_NAME,EMAIL,PHONE_NUMBER,POSTAL_ADRESS)', values)

def search_customer(customer_id):
    command = "SELECT CUSTOMER_ID, FIRST_NAME, LAST_NAME, EMAIL, PHONE_NUMBER, POSTAL_ADRESS FROM customers WHERE CUSTOMER_ID = ?"
    customer=SQL_Query_with_target(customer_id, command)
    return customer


def remove_customer(values):
    delete_values('customers', 'CUSTOMER_ID', values)

def qr_code_item(qr_code):
    command = "SELECT ITEM_ID, NAME, BARECODE, PICTURE, NUMBER, PRICE, DESCRIPTION FROM items WHERE BARECODE = ?"
    return SQL_Query_with_target(qr_code, command)


# Temp Functions
def createOrder():
    '''
    Creates an order with random information.
    '''
    ir = 9  # 1-9 are the items index ranges in the test DB


creation_tables()
#SQL_Query_with_target('Banana',"SELECT item_id, name, barecode, picture, number, price, description FROM items WHERE name = ?")
#add_values('orders','(customer_id,date,total_price,statut)','("1","13/08","12.34","+")')
#add_values('orders','(customer_id,date,total_price,statut)','("2","14/02","15.34","+")')
#add_values('orders','(customer_id,date,total_price,statut)','("3","17/05","16","+")')
#SQL_Query_table('orders')
#update_values('orders','total_price','45','CUSTOMER_ID','1')
#delete_values('orders', 'ORDER_ID', '1')
#add_item('("Watermelon","120873","watermelon.jpg","6","3.60","From California")')
#add_order('("1","18"')
#add_item_boughts('("1","1","12"')
#add_transcation('("15","+","1234.65","164534348393423051")')
#calculate_balance('2022/11/12','2022/11/14')
#add_customer("('BB', 'CC', 'cc001@csusm.edu', '+336127574678', '123 stAE')")
#remove_customer('2')
#see_item_bought('1')
#qr_code_item('124323')
#search_customer('1')
#value=see_item_bought_w_d('1','2022/11/30','2022/11/30')
##print(value)
#conn.close()
##print('Database closed successfully')
#list_order=search_order('6','2022/11/09','2022/11/11')
##print(list_order)