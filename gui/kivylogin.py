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
sys.path.insert(0, "../sql")
sys.path.insert(0, "../backend")

class login(Screen):

    @staticmethod
    def interact(data, key):
        if key == "LOGIN":
            return login.login(data)

    @staticmethod
    def login(data):
        username = data['user'].text
        password = data['pass'].text
        return Login.login(username, password)
