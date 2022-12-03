from functools import partial
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp #display pixels
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
#from kivy.uix.popup import Popup   #want to use this one
from kivymd.app import MDApp
from kivymd.uix.list import *
from kivymd.uix.datatables import MDDataTable

### will be used when path works ###

from pathlib import Path
import os, sys #for file paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, "../backend")
#import sql.SQL_database


#from login import Login as lg  #../backend/login.py



##### Build .kv files #####

Builder.load_file('frontPage.kv')
Builder.load_file('login.kv')
Builder.load_file('mainPOS.kv')
Builder.load_file('cart.kv')
Builder.load_file('reports.kv')
Builder.load_file('addInv.kv')
Builder.load_file('account.kv')
Builder.load_file('searchItem.kv')
Builder.load_file('helpScreen.kv')
Builder.load_file('adminLogin.kv')
Builder.load_file("adminMenu.kv")

screen_manager = ScreenManager()


##### Front Screen/Other Screens for regular customers #####

class addInv(Screen):
    pass

class account(Screen):
    pass

class cart(Screen):
    pass

class frontPage(Screen):
    pass

class reports(Screen):
    pass

class searchItem(Screen):
    pass


##### Main Pos Screen #####

class mainPOS(Screen):
    pass



##### Log In and Admin Related Classes #####

class adminLogin(Screen):

    @staticmethod
    def interact(data, key):
        if key == "ADMINLOGIN":
            return adminLogin.admin_login(data)


    @staticmethod
    def admin_login(data):
        username = data['user'].text
        password = data['pass'].text
        return lg.admin_login(username, password)

    @staticmethod
    def change_password_override(data):
        username = data['user'].text
        password = data['pass'].text
        return lg.admin_login(username, password)


class adminMenu(Screen):
    @staticmethod
    def interact(data, key):
        if key == "ADMINCHANGEUSERPASS":
            username = data['user'].text
            password = data['pass'].text
            lg.change_password_noverify(username, password)
            print(f"{username}'s password was updated.")

        elif key == "CREATEUSER":
            username = data['user'].text
            password = data['pass'].text
            lg.create_user(username, password)
            print(f"{username} created.")
  
            
class helpScreen(Screen):
    def onpress(self, pressed, list_id):
        item = TwoLineAvatarListItem(text=f"Sales Report", secondary_text=f"Week_1")
        self.ids.itemlist.add_widget(item)

    @staticmethod
    def interact(data, key):
        if key == "CHANGEPASS":
            return helpScreen.change_password(data)
        
    @staticmethod
    def change_password(data):
        username = data['user'].text
        password = data['pass'].text
        newPassword = data['pass2'].text
        return lg.change_password(username, password, newPassword)            

    
class login(Screen):

    @staticmethod
    def interact(data, key):
        if key == "LOGIN":
            return login.login(data)
        elif key == "CHANGEPASS":
            return login.change_password(data)
        
    @staticmethod
    def change_password(data):
        username = data['user'].text
        password = data['pass'].text
        newPassword = data['pass2'].text
        return lg.change_password(username, password, newPassword)
    @staticmethod
    def login(data):
        username = data['user'].text
        password = data['pass'].text
        return lg.login(username, password)
    
        
    @staticmethod
    def admin_login(data):
        username = data['user'].text
        password = data['pass'].text
        return lg.admin_login(username, password)

    @staticmethod
    def change_password_override(data):
        username = data['user'].text
        password = data['pass'].text
        return lg.admin_login(username, password)



##### Windows Manager Class That will run pages #####

class posApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"

        screen_manager.add_widget(frontPage(name="front"))
        screen_manager.add_widget(login(name="login"))
        screen_manager.add_widget(adminLogin(name="adminLogin"))
        screen_manager.add_widget(mainPOS(name="main"))
        screen_manager.add_widget(cart(name="cart"))
        screen_manager.add_widget(reports(name="reports"))
        screen_manager.add_widget(addInv(name="invent"))
        screen_manager.add_widget(account(name="account"))
        screen_manager.add_widget(searchItem(name="search"))
        screen_manager.add_widget(helpScreen(name="help"))
        screen_manager.add_widget(adminMenu(name="adminMenu"))

        return screen_manager

##### Runs posAPP ####

if __name__ == '__main__':
    posApp().run()