'''    
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                        USER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        ADMIN INTEGER NOT NULL,     
                        USERNAME TEXT NON NULL UNIQUE,
                        PASSWORD TEXT NON NULL)   
                        """) # Admin must be 0 or 1. (BOOL)

'''

import sys

# Import the SQL commands
sys.path.insert(0, "../sql")
import SQL_database as sdb
import bcrypt as bc


#conn = sqlite3.connect('test_db.db')
#cursor=conn.cursor()
#print("Database opened successfully")


class Login:
    @staticmethod
    def create_user(username:str, password:str, isAdmin:bool=False):
        '''
        Creates a user, it will return true if the user creation was successful'

        Will return True if user was successfully created
        Will return False if the user already exists and was not successfully created.
        '''
        row_count = len(sdb.SQL_Query_with_target(username, "SELECT * FROM users WHERE username = ?"))
        if not row_count:
            hp = Login.encrypt_password(password)
            fl = sdb.format_list([int(isAdmin), username, hp])
            print(fl)
            sdb.add_values("users", "(ADMIN, USERNAME, PASSWORD)", fl)
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

    @staticmethod
    def admin_Login(username:str, password:str) -> bool:
        isAdmin = sdb.SQL_Query_with_target(username, "SELECT ADMIN FROM users WHERE username = ?")
        if len(isAdmin):
            if isAdmin[0][0] and Login.login(username, password): # If the user is an Admin, and loged in correctly
                print("User is an Admin, And signed in properly")
                return True
        return False
            

#Login.create_user("Johnny3", "Password")
Login.admin_Login("Johnny2", "Passw2ord")
