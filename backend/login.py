'''    
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                        USER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        ADMIN INTEGER NOT NULL,     
                        USERNAME TEXT NON NULL UNIQUE,
                        PASSWORD TEXT NON NULL)   
                        """) # Admin must be 0 or 1. (BOOL)

'''
# Test
import sys
from enum import IntEnum

# Import the SQL commands
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)+"/sql")
import SQL_Database as sdb
import bcrypt as bc


#conn = sqlite3.connect('test_db.db')
#cursor=conn.cursor()
#print("Database opened successfully")

class Ui(IntEnum):
    '''Used for the user table as indexes.'''
    ID = 0
    ADMIN = 1
    USERNAME = 2
    PASSWORD = 3


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
            #print(fl)
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
            pass_check = Login.verify_password(password, user_data[int(Ui.PASSWORD)])
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
        return bc.checkpw(p_bytes, h_bytes) # Returns if the has1he's match.

    @staticmethod
    def admin_login(username:str, password:str) -> bool:
        isAdmin = sdb.SQL_Query_with_target(username, "SELECT ADMIN FROM users WHERE username = ?")
        if len(isAdmin):
            if isAdmin[0][0] and Login.login(username, password): # If the user is an Admin, and loged in correctly
                print("User is an Admin, And signed in properly")
                return True
        return False
            

    @staticmethod
    def change_password(username:str, password:str, newPassword:str) -> bool:
        '''
        Returns true if the password changed.
        '''
        if Login.login(username, password):
            # TODO: If login successful, we change the password.
            #update_values('orders','total_price','45','CUSTOMER_ID','1')
            new_p = Login.encrypt_password(newPassword)
            sdb.update_values("users", "PASSWORD", f"'{new_p}'", "USERNAME", f"'{username}'")
            print('Password updated.')
            return True
        return False

    @staticmethod
    def change_password_noverify(username:str, newPassword:str) -> bool:
        '''
        Returns true if the password changed.
        '''
        row = sdb.SQL_Query_with_target(username, "SELECT * FROM users WHERE username = ?")
        if len(row):
            new_p = Login.encrypt_password(newPassword)
            sdb.update_values("users", "PASSWORD", f"'{new_p}'", "USERNAME", f"'{username}'")
            print('Password updated.')
            return True
        return False

    @staticmethod
    def create_admin():
        # if there is no user in the database create an admin
        if not len(sdb.SQL_Query_table("users")):
            Login.create_user("admin", "admin", True)


# Creates an admin in case the database is empty.
Login.create_admin()


"""
print(sdb.SQL_Query_table('users'))

Login.create_user("Johnny3", "Password", True)
print(sdb.SQL_Query_table('users'))

x = Login.admin_Login("Johnny2", "Passw2ord")
print(x)

x = Login.admin_Login("Johnny3", "Password")
print(x)
Login.change_password("Johnny3", "Password", "NewPassword1!")
print(sdb.SQL_Query_table('users'))

print(Login.login("Henrdy", "NewPassword1!"))
"""
#print(type(Ui.ADMIN), int(Ui.ADMIN) == 1)