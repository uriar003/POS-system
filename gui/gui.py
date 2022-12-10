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

import sqlite3

from pathlib import Path
import os, sys #for file paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)+"/backend") #Parent directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)+"/sql") #Parent directory
dir = os.getcwd()
i = dir.rfind('/')
PARENTDIR = dir[:i]
#PARENTDIR = str(Path(__file__).resolve().parent.parent)

#import sql.SQL_Database
import dataTransformation as dt
import SQL_Database as sdb
import Invoices_generating as ig

import cv2                          # OpenCV is under Apache License 2.0, so it is free to use commercially
import numpy as np
from pyzbar.pyzbar import decode    # PyzBar is under the MIT License, which among other things permits modification and re-sale

from kivylogin import login, helpScreen, adminLogin, adminMenu
from searchEngine import SearchEngine
from dataTransformation import LoadData

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
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.err = ""
        self.subtotal = 0
        self.tax = 0
        self.cart = []
        self.ids.total.text = "0.00"
        self.orderTotal = 0
        self.transactionConfirmed = False
        self.transactionId = None
        #self.ids.name.text = None
        #self.ids.name.text = None

    def getCartData(self):
        #make sure this is in main.kv under the Finish button:
        # root.manager.get_screen('cart').getCartData()
        dataset = screen_manager.get_screen('main').getTransaction()
        self.subtotal = dataset['Subtotal']
        self.tax = dataset['SalesTax']
        self.cart = dataset['Cart']
        self.orderTotal = float(self.subtotal * (1+ self.tax))
        self.isCC = False
        self.isCash = False
        
         
        self.ids.total.text = self.getDollar(self.orderTotal)

    def reset(self):
        self.ids.approval.text = "Approved?"

        
    def cashTransaction(self):
        try:
            customerPaid = int(self.ids.moneyPaid.text)
            changeDue = self.getDollar(self.orderTotal - customerPaid)
            self.ids.changeDue.text = changeDue
            self.isCC = False
            self.isCash = True
            print("Cash Transaction")
        except: pass

    def ccTransaction(self):
        print(self.ids.ccNum.text)
        if len(str(self.ids.ccNum.text)) > 0:
            self.ccVerificationNum = self.ids.ccNum.text
            self.isCC = True
            self.isCash = False
            print("CC Transaction")



    def getDollar(self,variable):
        #In case it ends at a 0, we need it to be xx.00 not xx.
        out = str("%.2f" % variable)
        if len(out[out.rfind('.')+1:]) == 1: out = out+"0"
        return "$"+out

    def sendEmail(self):
        #make_client_invoice('Julien Toulon', 'toulon.julien@gmail.com',items_bought,list_item)
        items_bought, list_item=ig.informations('1')
        name = self.ids.name.text 
        email = self.ids.email.text
        ig.make_client_invoice(name, email, items_bought, list_item) 

    def confirmTransaction(self):
        try:
            if not self.isCC and not self.isCash:   
                self.err = "Needs cash or CC." 
            else:                
                if self.isCC:
                    saleType = "CreditCard"
                    if not int(self.ccVerificationNum):
                        self.err = "Not a integer for CC id."
                        raise Exception 
                    cc = self.ccVerificationNum
                else:
                    saleType = "CASH"
                    cc = 0
                total = self.getDollar(self.subtotal * (1+ self.tax))[1:]
                print(total, type(total))
                order_data = [saleType,total , cc]
                print("working")
                date = sdb.add_transcation(order_data)
                self.ids.approval.text = "Transaction\nSuccess!"
                self.transactionId =sdb.SQL_Query_table_highest_id("money_transactions", "TRANSACTION_ID")
                # Continue to add items for the order.
                for product in self.cart:
                    print(product)
                    item_id = product[0]
                    prod = product[1]
                    price = product[5]
                    productDetails = sdb.format_list([self.transactionId, date, item_id, product[-1], price, self.tax])
                    sdb.add_item_boughts2(productDetails)
                
                #clearcart
                screen_manager.get_screen('main').cart_deleteall()
                self.getCartData()
                self.ids.moneyPaid.text = ""
                self.ids.changeDue.text = ""
                self.ids.ccNum.text = ""
        except Exception as e:
            self.ids.approval.text = f"Failed to transact.\n{self.err}"
            print(e)
        
class addInv(Screen):
    pass

class mainPOS(Screen):
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        # list to manage summary items amt list on the right above the sales totals
        self.list_cart = []
        self.list_searchresults = []
        self.subtotal = 0
        # constantly call camera for barcode frames
        # Clock.schedule_interval(self.tickerscanner, 1.0/2.0)
        # constantly call search bar for new query
        # Clock.schedule_interval(self.tickersearch, 1.0/2.0)
        # self.cam = cv2.VideoCapture(1)
        self.prior = None           # bool to prevent barcode over-rescanning
        self.priorsearch = None     # used to stop search if query is the same
        self.se = SearchEngine()

    def getTransaction(self):
        """
        Returns all the data needed for the final transaction screen
        in a dictionary
        """
        dataset = {
            "SalesTax" : combined_sales_tax,
            "Subtotal" : self.subtotal,
            "Cart"     : [cell[:8] for cell in self.list_cart] # removes all excess 1's
        }
        return dataset


    # frame is the frame to be scanned for barcodes by decode func
    def tickerscanner(self, *args):
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

    def tickersearch(self, *args):
        # query is the item i.e. "apple" sent to the SQL search which would \
        # ideally return a list of lists that I can loop through to populate the search list
        # se is the SearchEngine class from the backend library.
        if(self.priorsearch != self.ids.searchprompt.text):
            self.priorsearch = self.ids.searchprompt.text

            # Seans code
            searchedName = self.ids.searchprompt.text   # Replace this with the value that is searched.
            # I initialized self.se in the __init__ self.se = SearchEngine()
            searched_obj = self.se.search_product(userInput=searchedName, amount=4)
            countOfprod = next(searched_obj) # The first item will be the count
            # So if it's 0, then there are no results.
            # Otherwise, it'll return up to 4 values per search 
            listOfList = []
            for setOfProd in searched_obj: # Loop through and make a list of lists
                listOfList.append(setOfProd)

            #print(setOfProd)
            # Since the DB is so small, if we search Mario, only 4 items return   

            # ****
            # Keep in mind we need the product_id for the items_bought table.
            # So we need to pass that data along
            # Every row (so what results holds)
            # [id, name, price, barcode]
            self.list_searchresults = listOfList[0]

            # clear visual to repopulate search results
            self.ids.mdlSEARCHRESULTS.clear_widgets()

            for r in self.list_searchresults:
                rl = ThreeLineAvatarListItem(
                    text = str(r[1]),                               # product name
                    secondary_text = str("{:.2f}".format(r[5])),    # price
                    tertiary_text = str(r[0])                       # item ID
                    )
                rl.bind(on_release = self.addsearchitem)
                self.ids.mdlSEARCHRESULTS.add_widget(rl)
        else:
            print("Search not refreshed, query hasn't changed!")

    def addscanitem(self, frame):
        flag_exist = False
        # note that decode gets ALL barcodes in a frame, but we only want the first one detected
        bdata = decode(frame)[0]
        bliteral = bdata.data.decode('utf-8')

        # placeholder for barcode returning from SQL a list of relevant item properties
        # params: item id, name, barcode, picture, number in stock, price, desc, item in cart at first add
        # SQLitem = [ 27, "Name", barcode, "picture.jfif", num in stock, price, desc, 1 ]
        retSQL = sdb.qr_code_item(bliteral)
        print("Adding", bliteral)
        print("retrieved:", retSQL)
        # guard if barcode does not return a matching item result
        if(len(retSQL) > 0):
            SQLitem = [
                retSQL[0][0], retSQL[0][1], retSQL[0][2], retSQL[0][3], retSQL[0][4], retSQL[0][5], retSQL[0][6], 1
                ]

            for e in self.list_cart:
                if(SQLitem[2] == e[2]):
                    print("exists")
                    e[7] += 1
                    flag_exist = True
                    break
            if(flag_exist == False):
                self.list_cart.append(SQLitem)
        else:
            print("no item matching barcode")
            
            box = BoxLayout(orientation = "vertical", padding = 10)
            lb = Label(text = "No item found matching barcode ")
            yb = Button(text = "OK", size_hint = (0.6, 0.4), pos_hint = {"center_x": 0.5, "center_y": 0.5})
            box.add_widget(lb)
            box.add_widget(yb)
            
            pup_noitemfound = Popup(
                size_hint=(None, None),
                size=(self.width / 3, self.height / 3),
                title = "Alert",
                content = box,
            )
            yb.bind(on_press = pup_noitemfound.dismiss)
            pup_noitemfound.open()
        
        self.update_cart()

    def addsearchitem(self, search_item):
        flag_exist = False
        print("Cart:", self.list_cart)
        for i in self.list_searchresults:
            # if clicked mdlist tertiary text (id) equals item id in internal list, then add to cart
            # ThreeLineCompactItem cannot retain SQLitem (obj) data so I have to do this
            if(search_item.tertiary_text == str(i[0])):
                print("matched")
                # now compare the search sqlitem if it exists in the cart already
                for e in self.list_cart:
                    if(e[0] == i[0]):
                        print("exists")
                        i[7] += 1
                        flag_exist = True
                        break
                if(flag_exist == False):
                    i.append(1) # add index amt to end
                    self.list_cart.append(i)
                break

        self.update_cart()

    def update_cart(self):
        print("Cart", self.list_cart)
        self.ids.mdlCART.clear_widgets()
        self.subtotal = 0.00        

        for i in self.list_cart:
            # create an item to be added to MDList with evident properties
            mdlitem = ThreeLineCompactItem(
                text = str(i[1] + " X " + str(i[7])),                           # product name
                secondary_text = str(i[0]),                                     # item ID (needed to index)
                tertiary_text = str(currency_type) + "{:.2f}".format(i[5])      # price
                )
            mdlitem.bind(on_release = self.cart_deleteitem)
            self.ids.mdlCART.add_widget(mdlitem)
            self.subtotal += i[5] * i[7]

        self.ids.lblstax.text = "Sales Tax: " + currency_type + "{:.2f}".format(self.subtotal * combined_sales_tax)
        self.ids.lblsubtotal.text = "Sub Total: " + currency_type + "{:.2f}".format(self.subtotal)
        self.ids.lbltotal.text = "Total: " + currency_type + "{:.2f}".format(self.subtotal + (self.subtotal * combined_sales_tax))

    def cart_deleteitem(self, obj):
        for i in self.list_cart:
            if(obj.secondary_text == str(i[0])):
                if(i[7] > 1):
                    i[7] -= 1
                else:
                    self.list_cart.remove(i)

        self.update_cart()

    def cart_deleteall(self,obj=None):
        self.list_cart.clear()
        self.update_cart()

class reports(Screen):
    @staticmethod
    def dailySales():
        dt.SQL_Reports.dailyReport()

    @staticmethod
    def totalProductSales():
        dt.SQL_Reports.totalProductSales()

    @staticmethod
    def salesTransactions():
        dt.SQL_Reports.transactions()

class account(Screen):
    #placeholder for a selected file path
    selectedFile = ''
    dir = os.getcwd()
    i = dir.rfind('/')
    exports = PARENTDIR
    print(exports)
    def selected(self, filename):
        try:
            #return file path on click
            account.selectedFile = filename[0]
            #displays file path on bottom of screen
            self.ids.fileString.text = "File Selected: " + account.selectedFile                                       
        except:
            pass

    #current path
    #path = os.path.dirname(os.path.abspath(__file__))
    #path to exports folder
    #exports = os.path.relpath('..\\Inventory\\exports\\New',path)
    #exports = str(Path(__file__).resolve().parent.parent)+"/Inventory/exports/"
    
    def submitImport(self):
        print("loading...")
        print(self.selectedFile)
        LoadData.load_inventory(self.selectedFile)
        print("Inventory loaded")

    def sendExport(self):
        print("generating...")
        LoadData.export_inventory(self.exports)
        print("Database Exported")
    
    def sendTExport(self):
        print("generating...")
        LoadData.export_template(self.exports)
        print("Template Exported")

class searchItem(Screen):
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)

        #find correct file path
        #path = os.path.dirname(os.path.abspath(__file__))
        path = str(Path(__file__).resolve().parent.parent)+"/sql"
        database = os.path.join(path,'POS_database.db')

        #Opening of the database
        #conn = sqlite3.sdb.connect(database)

        #Creation of the sdb.cursor ("robot to do database stuff for you")
        #cursor = sdb.conn.sdb.cursor()
        #print("Database opened successfully") #WILL CREATE A NEW FILE IF NOT FOUND

        #store row data into records variable before building table
        sdb.cursor.execute("SELECT ITEM_ID, NAME, NUMBER, PRICE, DESCRIPTION FROM items")
        sdb.conn.commit()
        ##testing query
        #for row in sdb.cursor:
            #print(row)
        records = sdb.cursor.fetchall()
        #print(records)

 

        table = MDDataTable(
                pos_hint = {'center_x': 0.5, 'center_y': 0.5},
                size_hint = (0.9, 0.75),
                use_pagination = True, #allows for pages, view all rows
                #default = 5 items per page, can be changed using rows_num
                rows_num = 10,
                
                
            #Manually insert requested columns
                column_data = [
                    ("ITEM_ID", dp(50)),
                    ("NAME", dp(75)),
                    #("BARCODE", dp(30)),
                    #("PICTURE", dp(50)),
                    ("NUMBER", dp(50)),
                    ("PRICE", dp(50)),
                    ("DESCRIPTION", dp(50))
                ],

            #set row data to records variable
            row_data = records
        )

        self.add_widget(table)

class posApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"

        screen_manager.add_widget(frontPage(name="front"))
        screen_manager.add_widget(login(name="login"))
        screen_manager.add_widget(adminLogin(name="adminLogin"))
        screen_manager.add_widget(mainPOS(name="main"))
        screen_manager.add_widget(cart(name="cart"))
        screen_manager.add_widget(reports(name="reports"))
        screen_manager.add_widget(addInv(name="invent"))  # May need to delete. Is this not needed?**
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

    def cartLogic(self):
        """
        Once run, it will load the information from mainPOS
        over to the cart.
        """
        z = screen_manager.get_screen('main').list_cart
        print(z)

if __name__ == '__main__':
    posApp().run()
    #close sdb.cursor and sdb.connection
    sdb.cursor.close()
    sdb.conn.close()      
