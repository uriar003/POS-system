from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp #display pixels

from kivymd.app import MDApp
from kivymd.uix.list import *
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)+"/backend") #Parent directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)+"/sql") #Parent directory

from login import Login as lg # ../backend/login.py


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