from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.label import Label
from kivymd.uix.list import *
#from kivy.clock import Clock
from kivy.uix.image import Image
#import mysql.connector

#screen_manager = ScreenManager()


Builder.load_file('frontPage.kv')
Builder.load_file('login.kv')
Builder.load_file('mainPOS.kv')
Builder.load_file('cart.kv')
Builder.load_file('reports.kv')
Builder.load_file('addInv.kv')
Builder.load_file('account.kv')
Builder.load_file('searchItem.kv')
#Builder.load_file('menu.kv')

class frontPage(Screen):
    #user=ObjectProperty(None)
    #password=ObjectProperty(None)
    pass


#class MyLayout(Screen):

    #def selected(self, filename):
        #try:
            # return file location
            #print(filename[0])
        #except:
            #pass

#class FileChooser(MDApp):
    #def build(self):
        #return MyLayout()

class login(Screen):
    pass

class mainPOS(Screen):
    pass

class cart(Screen):
    pass

class reports(Screen):
    pass

class addInv(Screen):
    pass

class account(Screen):
    pass

#screen_manager.add_widget(frontPage(name="front"))
#screen_manager.add_widget(login(name="login"))
#screen_manager.add_widget(mainPOS(name="main"))
#screen_manager.add_widget(cart(name="cart"))
#screen_manager.add_widget(reports(name="reports"))
#screen_manager.add_widget(addInv(name="invent"))
#screen_manager.add_widget(account(name="account"))

class mainPOS(Screen):
    def onpress(self, pressed, list_id):
        item = TwoLineAvatarListItem(text=f"soup", secondary_text=f"$2.99")
        item.add_widget(IconLeftWidget(icon="soup.png"))
        self.ids.itemlist.add_widget(item)

class reports(Screen):
    def onpress(self, pressed, list_id):
        item = TwoLineAvatarListItem(text=f"Sales Report", secondary_text=f"Week_1")
       #item.add_widget(IconLeftWidget(icon="soup.png"))
        self.ids.itemlist.add_widget(item)

class account(Screen):
    def onpress(self, pressed, list_id):
        item = TwoLineAvatarListItem(text=f"Sales Report", secondary_text=f"Week_1")
       #item.add_widget(IconLeftWidget(icon="soup.png"))
        self.ids.itemlist.add_widget(item)

class cart(Screen):
    def onpress(self, pressed, list_id):
        item = TwoLineAvatarListItem(text=f"Sales Report", secondary_text=f"Week_1")
       #item.add_widget(IconLeftWidget(icon="soup.png"))
        self.ids.itemlist.add_widget(item)


class searchItem(Screen):
    def onpress(self, pressed, list_id):
        item = TwoLineAvatarListItem(text=f"Sales Report", secondary_text=f"Week_1")
        self.ids.itemlist.add_widget(item)


class posApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        screen_manager = ScreenManager()

        #define data base stuff
        #mydb = mysql.connector.connect(
                #host = "localhost",
                #user = "root",
                #passwd = "password321",
        #)

        #create a cursor
        #c = mydb.cursor()

        #creat an actual database
        #c.execute("CREATE DATABASE IF NOT EXISTS second_db")

        #check to see if database was created
        #c.execute("SHOW DATABASES")
        #for db in c:
            #print(db)

        screen_manager.add_widget(frontPage(name="front"))
        screen_manager.add_widget(login(name="login"))
        screen_manager.add_widget(mainPOS(name="main"))
        screen_manager.add_widget(cart(name="cart"))
        screen_manager.add_widget(reports(name="reports"))
        screen_manager.add_widget(addInv(name="invent"))
        screen_manager.add_widget(account(name="account"))
        screen_manager.add_widget(searchItem(name="search"))

        return screen_manager

if __name__ == '__main__':
    posApp().run()
