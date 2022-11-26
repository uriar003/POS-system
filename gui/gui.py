from functools import partial

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.image import Image

from kivymd.app import MDApp
from kivymd.uix.list import *

from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp #display pixels
import sqlite3

import cv2                          # OpenCV is under Apache License 2.0, so it is free to use commercially
import numpy as np
from pyzbar.pyzbar import decode    # PyzBar is under the MIT License, which among other things permits modification and re-sale
#import mysql.connector

Builder.load_file('frontPage.kv')
Builder.load_file('login.kv')
Builder.load_file('mainPOS.kv')
Builder.load_file('cart.kv')
Builder.load_file('reports.kv')
Builder.load_file('addInv.kv')
Builder.load_file('account.kv')
Builder.load_file('searchItem.kv')
Builder.load_file('helpScreen.kv')
#Builder.load_file('menu.kv')

screen_manager = ScreenManager()

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

class cart(Screen):
    pass

class addInv(Screen):
    pass

#screen_manager.add_widget(frontPage(name="front"))
#screen_manager.add_widget(login(name="login"))
#screen_manager.add_widget(mainPOS(name="main"))
#screen_manager.add_widget(cart(name="cart"))
#screen_manager.add_widget(reports(name="reports"))
#screen_manager.add_widget(addInv(name="invent"))
#screen_manager.add_widget(account(name="account"))

class mainPOS(Screen):
    # init is to explicitly initialize the launch instance to make it addressable as 'self'
    # for functionality and addressing below
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        # check camera every second or so for a barcode
        # Clock does not like passing a func with params, so oncvscan is a middle man
        Clock.schedule_interval(self.oncvscan, 1.0/1.0)
        self.cam = cv2.VideoCapture(1)
        self.prior = None      # bool to prevent barcode rescannning

    # params for additem are as follows
    # scr is screen for widget (list item to be added)
    # frame is the frame to be scanned for barcodes by decode func

    def oncvscan(self, *args):
        success, frame = self.cam.read()
        # you don't want camera to add items when off main item screen
        if(screen_manager.current == "main"):
            # if barcode was detected
            # self.prior conditional prevents overscanning a barcode
            if(len(decode(frame)) > 0 and decode(frame)[0].data != self.prior):
                print("barcode found")
                self.prior = decode(frame)[0].data
                print(decode(frame)[0], self.prior)
                self.addscanitem(frame)
            else:
                print("barcode not found")
                self.prior = ""     # reset prior check to allow rescan

    def addscanitem(self, frame):
        # note that decode gets ALL barcodes in a frame, but we only want the first one detected
        bdata = decode(frame)[0]
        bliteral = bdata.data.decode('utf-8')
        print("Added TYPE:", bdata.type, "| DATA:", bliteral,
                "| @ mem loc", self.ids.mdlITEMLIST)
        print(self.ids.mdlITEMLIST)

        # placeholder for barcode returning from SQL a list of relevant item properties
        mdlItem = [ "NAME", "$X.XX", bliteral, 2, "genericitem.png", bdata.type ]

        # create an item to be added to MDList with evident properties
        item = ThreeLineAvatarListItem(
            text = mdlItem[0],              # product name
            secondary_text = mdlItem[1],    # price
            tertiary_text = mdlItem[2]      # barcode
            )
        # attach to the MDList item a self-delete upon click function
        item.bind(on_release = self.deleteitem)

        # add to the MDList item a widget for the icon lest it just be text lines
        # notice 'item' is itself a widget, so widget within a widget
        item.add_widget(IconLeftWidget(icon = str(mdlItem[4])))     # product picture
        self.ids.mdlITEMLIST.add_widget(item)

    # placeholder func as of now, later this will cause a popup where one can add an item by barcode lookup
    def addmanualitem(self, barcode):
        # some code here to query SQL db, giving it barcode and 
        # returning name, price, barcode, amount to purchase, icon

        # hypothetical returned data example from SQL query
        lstItem = [ "NAME", "$X.XX", "ABC-abc-1234", 2, "genericitem.png" ]

        self.item = ThreeLineAvatarListItem(
            text = lstItem[0], 
            secondary_text = lstItem[1],
            tertiary_text = lstItem[2]
            )
        self.item.add_widget(IconLeftWidgetWithoutTouch(icon = str(lstItem[4])))
        self.ids.mdlITEMLIST.add_widget(self.item)
    
    # function to self delete MDList item upon click
    # the button passes itself (obj) as arg and you want to delete it,
    #   but the func needs to by invoked via the parent, with parameter being the child (obj) list item
    def deleteitem(self, obj):
        print("deleting item in: ", self, " | ", obj.parent)
        obj.parent.remove_widget(obj)

    def deleteallitems(self, obj):
        print("deleting all items in", self, " | ", obj)
        self.ids.mdlITEMLIST.clear_widgets()

class reports(Screen):
    def generatereport(self, *args):
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

    def build(self):
        #define screen
        screen = Screen()

        #Opening of the database
        conn = sqlite3.connect(r"C:\Users\jedla\Desktop\SQLtest\POS_database.db") #file path issue  (fixable)
        #Creation of the cursor ("robot to do database stuff for you")
        cursor = conn.cursor()
        #print("Database opened successfully") #WILL CREATE A NEW FILE IF NOT FOUND
        
        #store row data into records variable before building table
        cursor.execute("SELECT * FROM items")
        conn.commit()
        ##testing query
        #for row in cursor:
            #print(row)
        records = cursor.fetchall()
        #print(records)

        #close cursor and connection
        cursor.close()
        conn.close()       

        table = MDDataTable(
                pos_hint = {'center_x': 0.5, 'center_y': 0.5},
                size_hint = (0.9, 0.6),
                check = True,
                use_pagination = True, #allows for pages, view all rows
                #default = 5 items per page, can be changed using rows_num
                
                
            #Manually insert requested columns
                column_data = [
                    ("ITEM_ID", dp(30)),
                    ("NAME", dp(60)),
                    ("BARCODE", dp(30)),
                    ("PICTURE", dp(50)),
                    ("NUMBER", dp(30)),
                    ("PRICE", dp(30)),
                    ("DESCRIPTION", dp(30))
                ],

            #set row data to records variableF
            row_data = records
        )

        #Bind the table
        table.bind(on_check_press=self.checked)
        table.bind(on_row_press=self.row_checked)

        self.add_widget(table)
        return screen

    #Function for check presses
    def checked(self,instance_table, current_row):
        print(instance_table, current_row)  #testing function
    #Function for row presses
    def row_checked(self, instance_table, instance_row):
        print(instance_table, instance_row) #testing function, passes object on click

    def on_enter(self):
        self.build()

    

class helpScreen(Screen):
    def onpress(self, pressed, list_id):
        item = TwoLineAvatarListItem(text=f"Sales Report", secondary_text=f"Week_1")
        self.ids.itemlist.add_widget(item)


class posApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"

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
        screen_manager.add_widget(helpScreen(name="help"))

        return screen_manager

if __name__ == '__main__':
    posApp().run()