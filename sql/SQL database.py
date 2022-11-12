import sqlite3
from datetime import datetime


'''
___________________________________________________________
______________Initialisation of the database_______________
___________________________________________________________
'''

conn = sqlite3.connect('POS_database.db')
cursor=conn.cursor()
print("Database opened successfully")

'''
___________________________________________________________
____________________Primary functions______________________
___________________________________________________________
'''


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
                        NAME TEXT NON NULL,
                        BARECODE TEXT NON NULL,
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


def drop_table(table_name):
    command="DROP TABLE ", table_name
    command=''.join(command)
    cursor.execute(command)

def add_values(table,attributs,values):
    command="INSERT OR REPLACE INTO ",table,attributs,"VALUES",values
    command=''.join(command)
    conn.execute(command)
    conn.commit()

def update_values(table,attribut,new_value,row,old_value):
    command="UPDATE ", table, " set ", attribut, " = ", new_value, " where ", row, " = ", old_value
    command=''.join(command)
    conn.execute(command)
    conn.commit()

def delete_values(table,attribut,value):
    command='DELETE FROM ', table, ' WHERE ', attribut, ' LIKE ',value
    command=''.join(command)
    conn.execute(command)
    conn.commit()

def SQL_Query_with_target(target,request):
    target = target
    command = "SELECT","FROM","WHERE"
    rows = cursor.execute(
        request,
        (target,),
    ).fetchall()
    print(rows)
    return rows

def SQL_Query_table(table):
    command="SELECT * FROM ", table
    command=''.join(command)
    rows= cursor.execute(command).fetchall()
    print(rows)

'''
___________________________________________________________
___________________Secondary functions_____________________
___________________________________________________________
'''

#items functions
def add_item(values):
    add_values('items',' (NAME,BARECODE,PICTURE,NUMBER,PRICE,DESCRIPTION) ',values)

def remove_item(value):
    delete_values('items','ITEM_ID',value)

def see_stock():
    SQL_Query_table('items')

def change_number_stock(key,value):
    update_values('stock', 'NUMBER', value,'ITEM_ID', key)

def change_price_stock(key,value):
    update_values('stock', 'PRICE', value,'ITEM_ID', key)

#stock functions

def pay(key):
    update_values('orders','STATUT','paid','CUSTOMER_ID',key)

def add_order(values):
    date = str(datetime.now())
    values=values.split(',')
    date='"',date, '"'
    date=''.join(date)
    values.insert(1,date)
    statut='"waiting")'
    values.append(statut)
    values = ','.join(values)
    add_values('orders','(CUSTOMER_ID,DATE,TOTAL_PRICE,STATUT)',values)

#item_bought functions

def add_item_boughts(values):
    date = str(datetime.now())
    values = values.split(',')
    date = '"', date, '"'
    date = ''.join(date)
    values.insert(1, date)
    values= ','.join(values)
    add_values('items_bought','(CUSTOMER_ID,DATE,ITEM_ID,NUMBER,PRICE)',values)

#money_transactions functions

def add_transcation(values):
    date = str(datetime.now())
    values = values.split(',')
    date = "'", date, "'"
    date = ''.join(date)
    values.insert(1,date)
    values= ','.join(values)
    add_values('money_transactions','(TRANSACTION_ID,DATE,TRANSACTION_TYPE,TOTAL_PRICE,CREDIT_CARD_ID)',values)


def calculate_balance(dateb,datee):
    balance=0
    dates=[]
    dates2=[]
    rows2=[]
    rows = conn.execute("SELECT DATE,TRANSACTION_TYPE,TOTAL_PRICE FROM money_transactions").fetchall()
    print(rows)
    print(type(rows))
    list = [x for elem in rows for x in elem]
    for k in range(0,len(list)-1,3):
        dates.append(list[k])
    print(dates)
    for element in dates:
        var=element.split(' ')
        dates2.append(var[0])
    dateb=dateb.split('/')
    datee=datee.split('/')
    n=0
    for element in dates2:
        print(element)
        splitdate=element.split('-')
        print(splitdate)
        if dateb[0]<=splitdate[0]<=datee[0] and dateb[1]<=splitdate[1]<=datee[1] and dateb[2]<=splitdate[2]<=datee[2]:
            rows2.append(rows[n])
        n+=1
    for element in rows2:
        if element[1]=='+':
            balance+=element[2]
        elif element[1]=='-':
            balance-=element[2]
        else:
            continue
    print('Your balance between ', dateb, ' and ', datee, ' is ',balance,'$')
    return rows2

#customer functions

def add_customer(values):
    add_values('customers', '(FIRST_NAME,LAST_NAME,EMAIL,PHONE_NUMBER,POSTAL_ADRESS)', values)

def remove_customer(values):
    delete_values('customers','CUSTOMER_ID', values)

def see_item_bought(values):
    command="SELECT CUSTOMER_ID, DATE, ITEM_ID, NUMBER, PRICE FROM items_bought WHERE CUSTOMER_ID = ?"
    SQL_Query_with_target(values,command)


creation_tables()
#SQL_Query_with_target('Banana',"SELECT item_id, name, barecode, picture, number, price, description FROM items WHERE name = ?")
#add_values('orders','(customer_id,date,total_price,statut)','("1","13/08","12.34","+")')
#add_values('orders','(customer_id,date,total_price,statut)','("2","14/02","15.34","+")')
#add_values('orders','(customer_id,date,total_price,statut)','("3","17/05","16","+")')
#SQL_Query_table('orders')
#update_values('orders','total_price','45','CUSTOMER_ID','1')
#delete_values('orders', 'ORDER_ID', '1')
#add_item('("Banana","124321","banana.jpg","12","1.0","From California")')
#add_order('("6","18"')
#add_item_boughts('("1","1201","4","12")')
#add_transcation('("15","+","1234.65","164534348393423051")')
#calculate_balance('2022/11/12','2022/11/14')
#add_customer("('BB', 'CC', 'cc001@csusm.edu', '+336127574678', '123 stAE')")
#remove_customer('2')
#see_item_bought('1')


conn.close()
print('Database closed successfully')








