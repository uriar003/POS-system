from functools import partial


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

import sqlite3
import cv2                          # OpenCV is under Apache License 2.0, so it is free to use commercially
import numpy as np
import re
from pyzbar.pyzbar import decode    # PyzBar is under the MIT License, which among other things permits modification and re-sale
#import mysql.connector
import os, sys #for file paths
from kivylogin import login, helpScreen, adminLogin



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
#Builder.load_file('menu.kv')

screen_manager = ScreenManager()

# figures as of now are based on San Diego county
# there is A LOT that goes into sales tax, hoping the SQL db provides this info
state_tax = 0.06
county_tax = 0.0025
city_tax = 0.00
special_sales_tax = 0.015
value_added_tax = 0.00
currency_type = "$"

combined_sales_tax = state_tax + county_tax + city_tax + special_sales_tax + value_added_tax

# list to manage summary items amt list on the right above the sales totals
internal_itemlist = []

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
        #Clock.schedule_interval(self.oncvscan, 1.0/2.0)
        #self.cam = cv2.VideoCapture(1)
        self.prior = None      # bool to prevent barcode over-rescanning

    # frame is the frame to be scanned for barcodes by decode func
    def oncvscan(self, *args):
        success, frame = self.cam.read()
        # you don't want camera to add items when off main item screen
        if(screen_manager.current == "main"):
            # if barcode was detected | self.prior conditional prevents overscanning a barcode
            if(len(decode(frame)) > 0):
                if(decode(frame)[0].data != self.prior):
                    print("barcode found")
                    self.prior = decode(frame)[0].data
                    self.addscanitem(frame)
                else:
                    print("Repeated barcode scan! Briefly remove from camera and scan again.")
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
        # params: Item_id, Picture, Number_in_stock, Price, Description, barcode, current num in cart
        SQLitem = [ "NAME", "genericitem.png", 7, 2.55, "Nintendo", bliteral, 1 ]
        self.updatesummary(bliteral, SQLitem, True)

        # create an item to be added to MDList with evident properties
        mdlitem = ThreeLineAvatarListItem(
            text = str(SQLitem[0]),              # product name
            secondary_text = str(SQLitem[3]),    # price
            tertiary_text = str(SQLitem[5])      # barcode
            )
        

        # add to the MDList item a widget for the icon lest it just be text lines
        mdlitem.add_widget(IconLeftWidget(icon = str(SQLitem[4])))     # product picture        
        # attach to the MDList item a self-delete upon click function
        mdlitem.bind(on_release = self.deleteitem)

        newtotal = float(re.search("(\d+\.\d\d)", self.ids.lblsubtotal.text).group())
        newtotal += SQLitem[3]      # subtotal + new added item, used as basis for other cost calculations

        self.ids.lblstax.text = "Sales Tax: " + currency_type + "{:.2f}".format(newtotal * combined_sales_tax)
        self.ids.lblsubtotal.text = "Sub Total: " + currency_type + "{:.2f}".format(newtotal)
        self.ids.lbltotal.text = "Total: " + currency_type + "{:.2f}".format(newtotal + (newtotal * combined_sales_tax))
        self.ids.mdlITEMLIST.add_widget(mdlitem)

    def deleteitem(self, obj):
        # clear and rebuild the summary list based on internal list changes
        for i in internal_itemlist:
            if(obj.tertiary_text == i[5] and (i[6] > 1)):
                i[6] -= 1
                self.updatesummary("filler", internal_itemlist, False)
                break
            elif(obj.tertiary_text == i[5] and i[6] == 1):
                internal_itemlist.remove(i)
                self.updatesummary("filler", internal_itemlist, False)
                print(internal_itemlist)
                break

        print("deleting item in: ", self, " | ", obj.parent)
        obj.parent.remove_widget(obj)

        negtotal = float(re.search("(\d+\.\d\d)", self.ids.lblsubtotal.text).group())
        sub = float(re.search("(\d+\.\d\d)", obj.secondary_text).group())
        negtotal -= sub
        
        self.ids.lblstax.text = "Sales Tax: " + currency_type + "{:.2f}".format(negtotal * combined_sales_tax)
        self.ids.lblsubtotal.text = "Sub Total: " + currency_type + "{:.2f}".format(negtotal)
        self.ids.lbltotal.text = "Total: " + currency_type + "{:.2f}".format(negtotal + (negtotal * combined_sales_tax))

    def deleteallitems(self, obj):
        internal_itemlist.clear()
        self.updatesummary("filler", internal_itemlist, False)

        print("deleting all items in", self, " | ", obj)
        self.ids.mdlITEMLIST.clear_widgets()
        self.ids.lblstax.text = "Sales Tax: " + currency_type + "{:.2f}".format(0.00)
        self.ids.lblsubtotal.text = "Sub Total: " + currency_type + "{:.2f}".format(0.00)
        self.ids.lbltotal.text = "Total: " + currency_type + "{:.2f}".format(0.00)

    def updatesummary(self, bliteral, SQLitem, Add):
        itemAdded = False

        if(Add == True):
            # if there aren't any items in cart, unconditionally add an item, this is a unique condition
            if(len(internal_itemlist) > 0):
                # params: Item_id, Picture, Number_in_stock, Price, Description, barcode, current num in cart
                for i in internal_itemlist:
                    if(bliteral == i[5]):
                        i[6] += 1
                        itemAdded = True
            else:
                internal_itemlist.append(SQLitem)
                itemAdded = True

            if itemAdded == False:
                internal_itemlist.append(SQLitem)
        elif(Add == False):
            if(len(internal_itemlist) > 0):
                # params: Item_id, Picture, Number_in_stock, Price, Description, barcode, current num in cart
                for i in internal_itemlist:
                    if(bliteral == i[5]):
                        i[6] -= 1

        self.ids.mdlSUMMARY.clear_widgets()

        for i in internal_itemlist:
            self.ids.mdlSUMMARY.add_widget(OneLineListItem(text = str(i[0]) + " x " + str(i[6])))

        print(internal_itemlist)

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
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)

        #find correct file path
        path = os.path.dirname(os.path.abspath(__file__))
        database = os.path.join(path,'POS_database.db')

        #Opening of the database
        conn = sqlite3.connect(database)

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

    #Function for check presses
    def checked(self,instance_table, current_row):
        print(instance_table, current_row)  #testing function
    #Function for row presses
    def row_checked(self, instance_table, instance_row):
        print(instance_table, instance_row) #testing function, passes object on click

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
        screen_manager.add_widget(adminLogin(name="adminLogin"))
        screen_manager.add_widget(mainPOS(name="main"))
        screen_manager.add_widget(cart(name="cart"))
        screen_manager.add_widget(reports(name="reports"))
        screen_manager.add_widget(addInv(name="invent"))
        screen_manager.add_widget(account(name="account"))
        screen_manager.add_widget(searchItem(name="search"))
        screen_manager.add_widget(helpScreen(name="help"))
        #screen_manager.add_widget(login(name="help"))

        return screen_manager


    def loginLogic(self,data, key):
        # Runs the login function
        if key == "LOGIN":
            if login.interact(data,key):
                # If returns true, set the page to go to the POS.
                print(True)
                return "main"
        elif key == "CHANGEPASS":
            if helpScreen.interact(data, key):
                print("True")
                return("login")
        elif key == "ADMINLOGIN":
            if adminLogin.interact(data,key):
                print(True)
                return ("main") # Instead become admin page...
        # Else return nothing to do nothing, possibly later add text saying invalid
        
if __name__ == '__main__':
    posApp().run()