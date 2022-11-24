from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix import Screen
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp #display pixels


#from SQL database.py
import sqlite3
from datetime import datetime
from math import isnan



class MainApp(MDApp):
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

        #define table
        table = MDDataTable(
            pos_hint = {'center_x': 0.5, 'center_y': 0.5},
            size_hint = (0.9, 0.6),
            check = True,
            use_pagination = True, #allows for pages, view all rows; oddly works only on Light Mode
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

            #set row data to records variable
            row_data = records
        )
        
        #Bind the table
        table.bind(on_check_press=self.checked)
        table.bind(on_row_press=self.row_checked)

        self.theme_cls.theme_style = "Light" 
        self.theme_cls.primary_palette = "BlueGray"
        screen.add_widget(table)
        return screen

    #Function for check presses
    def checked(self,instance_table, current_row):
        print(instance_table, current_row)  #testing function
    #Function for row presses
    def row_checked(self, instance_table, instance_row):
        print(instance_table, instance_row) #testing function, passes object on click

MainApp().run()