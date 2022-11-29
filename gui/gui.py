from functools import partial

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp #display pixels
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from kivymd.app import MDApp
from kivymd.uix.list import *
from kivymd.uix.datatables import MDDataTable

from pathlib import Path
import os, sys #for file paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, "../backend")
import sql.SQL_database


import sqlite3
import cv2                          # OpenCV is under Apache License 2.0, so it is free to use commercially
import numpy as np
from pyzbar.pyzbar import decode    # PyzBar is under the MIT License, which among other things permits modification and re-sale

from kivylogin import login, helpScreen, adminLogin, adminMenu
from searchEngine import SearchEngine

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

# Sales Tax factors
state_tax = 0.06
county_tax = 0.0025
city_tax = 0.00
special_sales_tax = 0.015
value_added_tax = 0.00
currency_type = "$"

combined_sales_tax = state_tax + county_tax + city_tax + special_sales_tax + value_added_tax

# list to manage summary items amt list on the right above the sales totals
internal_itemlist = []

class ThreeLineCompactItem(BaseListItem):
    """A three line list item."""

    _txt_top_pad = NumericProperty("4dp")
    _txt_bot_pad = NumericProperty("4dp")
    _height = NumericProperty()
    _num_lines = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.height = dp(64) if not self._height else self._height

class frontPage(Screen):
    pass

class cart(Screen):
    pass

class addInv(Screen):
    pass

class mainPOS(Screen):
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        
        Clock.schedule_interval(self.oncvscan, 1.0/2.0) # schedule oncvscan() to be called twice a second forever
        self.cam = cv2.VideoCapture(1)
        self.prior = None      # bool to prevent barcode over-rescanning
        self.se = SearchEngine()

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
        print("Adding TYPE:", bdata.type, "| DATA:", bliteral)

        # placeholder for barcode returning from SQL a list of relevant item properties
        # params: Item_id, Picture, Number_in_stock, Price, Description, barcode, current num in cart
        # SQLitem = [ "ITEM", "genericitem.png", 7, 2.55, "Nintendo", bliteral, 1 ]
        SQLitem = [
            "ITEM_ID",      # item id
            "NAME",         # item name
            bliteral,       # barcode data
            "soup.png",     # picture
            7,              # in stock amount
            2.99,           # price * current amt in amount
            "description here",     # description
            1               # counter for current amount in cart
        ]
        self.update_cart(SQLitem, True)

    def delete_cartitem(self, obj):

        subtotal = 0.00

        for i in internal_itemlist:
            if(obj.secondary_text == i[2] and (i[7] > 1)):
                print("subtracting", obj)
                break
            elif(obj.secondary_text == i[2] and (i[7] == 1)):
                print("deleting", obj)
                internal_itemlist.remove(i)
                break

        self.update_cart(i, False)

    def delete_cartall(self, obj):
        internal_itemlist.clear()
        self.update_cart(internal_itemlist, False)

        print("deleting all items in", self, " | ", obj)
        self.ids.lblstax.text = "Sales Tax: " + currency_type + "{:.2f}".format(0.00)
        self.ids.lblsubtotal.text = "Sub Total: " + currency_type + "{:.2f}".format(0.00)
        self.ids.lbltotal.text = "Total: " + currency_type + "{:.2f}".format(0.00)

    def update_cart(self, SQLitem, Add):
        itemAdded = False

        if(Add == True):
            # if there aren't any items in cart, unconditionally add an item, this is an edge case
            if(len(internal_itemlist) > 0):
                for i in internal_itemlist:
                    # if barcode is already in list, add to existing elem count
                    if(SQLitem[2] == i[2]):
                        i[7] += 1
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
                    if(SQLitem[2] == i[2]):
                        if(i[7] > 0):
                            i[7] -= 1
                        else:
                            internal_itemlist.remove(i)

        self.ids.mdlCART.clear_widgets()
        subtotal = 0.00

        for i in internal_itemlist:
            # create an item to be added to MDList with evident properties
            mdlitem = ThreeLineCompactItem(
                text = str(i[1] + " X " + str(i[7])),       # product name
                secondary_text = i[2],                      # barcode (I need this to index)
                tertiary_text = str(i[5])                   # price
                )
            mdlitem.bind(on_release = self.delete_cartitem)
            self.ids.mdlCART.add_widget(mdlitem)
            subtotal += i[5] * i[7]

        self.ids.lblstax.text = "Sales Tax: " + currency_type + "{:.2f}".format(subtotal * combined_sales_tax)
        self.ids.lblsubtotal.text = "Sub Total: " + currency_type + "{:.2f}".format(subtotal)
        self.ids.lbltotal.text = "Total: " + currency_type + "{:.2f}".format(subtotal + (subtotal * combined_sales_tax))

        print(internal_itemlist)

    def on_mdquery(self, query):
        print("dummy function here, query the SQL then retrieve the generator - then populate ")
        # query is the item i.e. "apple" sent to the SQL search which would \
        # ideally return a list of lists that I can loop through to populate the search list
        # se is the SearchEngine class from the backend library.

        #results = [
        #     ["apple", 2.99, "ABC-abc-1234"], 
        #     ["applet", 89.99, "TUV-abc-4321"], 
        #     ["application", 204.99, "XYZ-abc-6626"] 
        #    ]
        
        # Seans code
        searchedName = "Mario" # Replace this with the value that is searched.

        # I initialized self.se in the __init__ self.se = SearchEngine()
        searched_obj = self.se.search_product(userInput=searchedName, amount=4)
        countOfprod = next(searched_obj) # The first item will be the count
        # So if it's 0, then there are no results.
        # Otherwise, it'll return up to 4 values per search 
        listOfList = []
        for setOfProd in searched_obj: # Loop through and make a list of lists
            print(setOfProd)
            listOfList.append(setOfProd)
        # Since the DB is so small, if we search Mario, only 4 items return   
        print(listOfList)
        results = listOfList[0]

        # clear to repopulate search results
        self.ids.mdlSEARCHRESULTS.clear_widgets()

        for r in results:
            rl = ThreeLineAvatarListItem(
                text = str(r[0]),              # product name
                secondary_text = str(r[1]),    # price
                tertiary_text = str(r[2])      # barcode
                )

            self.ids.mdlSEARCHRESULTS.add_widget(rl)

        # as of now I just want it to work as proof of concept, so no automatic search updating mid-typing,
        #       only update results from SQL searcher upon button press

class reports(Screen):
    def generatereport(self, *args):
        item = TwoLineAvatarListItem(text=f"Sales Report", secondary_text=f"Week_1")
       #item.add_widget(IconLeftWidget(icon="soup.png"))
        self.ids.itemlist.add_widget(item)

class account(Screen):
    def on_press(self, pressed, list_id):
        item = TwoLineAvatarListItem(text=f"Sales Report", secondary_text=f"Week_1")
       #item.add_widget(IconLeftWidget(icon="soup.png"))
        self.ids.itemlist.add_widget(item)

class cart(Screen):
    def on_press(self, pressed, list_id):
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

    def on_press(self, pressed, list_id):
        item = TwoLineAvatarListItem(text=f"Sales Report", secondary_text=f"Week_1")
        self.ids.itemlist.add_widget(item)




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
                return ("adminMenu")
                
        elif key in ["ADMINCHANGEUSERPASS", "CREATEUSER"]:
            adminMenu.interact(data,key)
            return ("adminMenu")
        # Else return nothing to do nothing, possibly later add text saying invalid
        return "front"
        
if __name__ == '__main__':
    posApp().run()