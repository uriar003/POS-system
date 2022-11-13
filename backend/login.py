'''    
cursor.execute("""CREATE TABLE IF NOT EXISTS orders(
                ORDER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CUSTOMER_ID INTEGER NON NULL,
                DATE TEXT NON NULL,
                TOTAL_PRICE FLOAT NON NULL,
                STATUT TEXT NON NULL)
                """)
'''

import sqlite3
import os, sys

# Import the SQL commands
sys.path.insert(0, "../sql")
import SQL_database as sdb
import bcrypt as bc


#conn = sqlite3.connect('test_db.db')
#cursor=conn.cursor()
#print("Database opened successfully")


class Login:
    @staticmethod
    def create_user(username:str, password:str):
        '''
        Creates a user, it will return true if the user creation was successful'

        Will return True if user was successfully created
        Will return False if the user already exists and was not successfully created.
        '''
        row_count = len(sdb.SQL_Query_with_target(username, "SELECT * FROM users WHERE username = ?"))
        if not row_count:
            hp = Login.encrypt_password(password)
            fl = sdb.format_list([username, hp])
            print(fl)
            sdb.add_values("users", "(USERNAME, PASSWORD)", fl)
            print(sdb.cursor.execute('SELECT * FROM users').fetchall())
            return True
        else:
            print("User already exists")
            return False
             

    @staticmethod
    def login(username:str, password:str)->bool:
        row = sdb.SQL_Query_with_target(username, "SELECT * FROM users WHERE username = ?")
        if len(row):
            user_data = row[0]
            pass_check = Login.verify_password(password, user_data[-1])
            if pass_check:
                return True
        return False
            


    @staticmethod
    def encrypt_password(password:str)->str:
        p_bytes = password.encode() # Convert password to bytes.
        salt = bc.gensalt(14) # Generate the salt
        password_hash_bytes = bc.hashpw(p_bytes, salt)
        return password_hash_bytes.decode() # Returned the hashed password as a string

    @staticmethod
    def verify_password(password:str, db_hash:str)-> bool:
        p_bytes = password.encode()
        h_bytes = db_hash.encode()
        return bc.checkpw(p_bytes, h_bytes) # Returns if the hashe's match.

 