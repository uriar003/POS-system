import sqlite3
from datetime import datetime
from math import isnan

'''
___________________________________________________________
______________Initialisation of the database_______________
___________________________________________________________
'''

#Opening of the database
conn = sqlite3.connect('../sql/POS_database.db')
#Creation of the cursor
cursor = conn.cursor()
print("Database opened successfully")

'''
___________________________________________________________
____________________Primary functions______________________
___________________________________________________________
'''

#Creation of all the tables if not exist.
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
                        CUSTOMER_ID INTEGER NON NULL,
                        DATE TEXT NON NULL,
                        ITEM_ID INTEGER NON NULL,
                        NUMBER INTEGER NON NULL,
                        PRICE FLOAT NON NULL)
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

#Fonction to drop a table
def drop_table(table_name):
    command = "DROP TABLE ", table_name
    command = ''.join(command)
    cursor.execute(command)

#Fonction to add a value in a table
def add_values(table, attributs, values):
    command = "INSERT OR REPLACE INTO ", table, attributs, "VALUES", values
    command = ''.join(command)
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
    rows = cursor.execute(
        request,
        (target,),
    ).fetchall()
    print(rows)  # Might need to remove #-Sean
    return rows


def SQL_Query_table(table):
    command = "SELECT * FROM ", table
    command = ''.join(command)
    rows = cursor.execute(command).fetchall()
    print(rows)
    return rows


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
            print(row)
            for cell in row:
                if type(cell) in (float, int) and not isnan(cell):
                    out += f"{cell},"
                else:
                    out += f"'{cell}',"
            out = out[:-1] + '),'
        out = out[:-1]
    return out


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


def change_number_stock(key, value):
    update_values('items', 'NUMBER', value, 'ITEM_ID', key)

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
    add_values('orders', '(CUSTOMER_ID,DATE,TOTAL_PRICE,STATUT)', values)


# item_bought functions

def add_item_boughts(values):
    date = str(datetime.now())
    values = values.split(',')
    date = '"', date, '"'
    date = ''.join(date)
    values.insert(1, date)
    values = ','.join(values)
    add_values('items_bought', '(CUSTOMER_ID,DATE,ITEM_ID,NUMBER,PRICE)', values)


# money_transactions functions

def add_transcation(values):
    date = str(datetime.now())
    values = values.split(',')
    date = "'", date, "'"
    date = ''.join(date)
    values.insert(1, date)
    values = ','.join(values)
    add_values('money_transactions', '(TRANSACTION_ID,DATE,TRANSACTION_TYPE,TOTAL_PRICE,CREDIT_CARD_ID)', values)


def calculate_balance(dateb, datee):
    balance = 0
    dates = []
    dates2 = []
    rows2 = []
    rows = conn.execute("SELECT DATE,TRANSACTION_TYPE,TOTAL_PRICE FROM money_transactions").fetchall()
    print(rows)
    print(type(rows))
    list = [x for elem in rows for x in elem]
    for k in range(0, len(list) - 1, 3):
        dates.append(list[k])
    print(dates)
    for element in dates:
        var = element.split(' ')
        dates2.append(var[0])
    dateb = dateb.split('/')
    datee = datee.split('/')
    n = 0
    for element in dates2:
        print(element)
        splitdate = element.split('-')
        print(splitdate)
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
    print('Your balance between ', dateb, ' and ', datee, ' is ', balance, '$')
    return rows2


# customer functions

def add_customer(values):
    add_values('customers', '(FIRST_NAME,LAST_NAME,EMAIL,PHONE_NUMBER,POSTAL_ADRESS)', values)


def remove_customer(values):
    delete_values('customers', 'CUSTOMER_ID', values)


def see_item_bought(values):
    command = "SELECT CUSTOMER_ID, DATE, ITEM_ID, NUMBER, PRICE FROM items_bought WHERE CUSTOMER_ID = ?"
    SQL_Query_with_target(values, command)

def qr_code_item(qr_code):
    command = "SELECT ITEM_ID, NAME, BARECODE, PICTURE, NUMBER, PRICE, DESCRIPTION FROM items WHERE BARECODE = ?"
    SQL_Query_with_target(qr_code, command)


# Temp Functions
def createOrder():
    '''
    Creates an order with random information.
    '''
    ir = 9 #1-9 are the items index ranges in the test DB
    




creation_tables()
# SQL_Query_with_target('Banana',"SELECT item_id, name, barecode, picture, number, price, description FROM items WHERE name = ?")
# add_values('orders','(customer_id,date,total_price,statut)','("1","13/08","12.34","+")')
# add_values('orders','(customer_id,date,total_price,statut)','("2","14/02","15.34","+")')
# add_values('orders','(customer_id,date,total_price,statut)','("3","17/05","16","+")')
# SQL_Query_table('orders')
# update_values('orders','total_price','45','CUSTOMER_ID','1')
# delete_values('orders', 'ORDER_ID', '1')
#add_item('("Banana","124323","banana.jpg","12","1.0","From California")')
# add_order('("6","18"')
# add_item_boughts('("1","1201","4","12")')
# add_transcation('("15","+","1234.65","164534348393423051")')
# calculate_balance('2022/11/12','2022/11/14')
# add_customer("('BB', 'CC', 'cc001@csusm.edu', '+336127574678', '123 stAE')")
# remove_customer('2')
# see_item_bought('1')
#qr_code_item('124323')
##

#conn.close()
#print('Database closed successfully')