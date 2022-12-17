import sys
import pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)+"/sql")
import SQL_Database as sdb
from datetime import datetime
from collections import defaultdict
import openpyxl.cell._writer
import os
import json
#dir = os.getcwd()
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    PARENTDIR = sys._MEIPASS
    with open(PARENTDIR+"/settings.json", "r") as fn:
        db = json.load(fn)
else:
    #PARENTDIR = os.path.dirname(os.path.abspath(__file__))
    PARENTDIR = os.getcwd()
    i = PARENTDIR.rfind('/')
    PARENTDIR = PARENTDIR[:i] + "/json"
    PARENTDIR = str(Path(__file__).resolve().parent.parent)
    with open(PARENTDIR+"/json/settings.json", "r") as fn:
        db = json.load(fn)
    
DOWNLOAD_DIR = db["MainDirectory"] + "/Inventory/Reports/"


globalHeader = ["ITEM_ID", "NAME", "BARECODE", "PICTURE", "COUNT", "PRICE", "DESCRIPTION"]
itemsBoughtHeader = ["TRANSACTION_ID", "DATE", "ITEM_ID", "NUMBER", "PRICE", "TAX"]
money_header = [
            "TRANSACTION_ID",
            "DATE",
            "TRANSACTION_TYPE",
            "TOTAL_PRICE",
            "CREDIT_CARD_ID"
        ]

class LoadData:
    @staticmethod
    def export_template(fileloc:str=""):
        '''
        Exports a template that can be used for the format of uploading inventory.
        Parameters:
            we should know the file location of where to save this data...

        '''
        df = pd.DataFrame(columns=globalHeader[1:])
        #print(fileloc+"TemplateFile.xlsx")
        df.to_excel(fileloc+"TemplateFile.xlsx", index=False)


    @staticmethod
    def export_inventory(fileloc:str=""):
        '''
        Exports a copy of the exact inventory, so product price can be updated.

        Parameters:
            we should know the file location of where to save this data...

        '''
        df = pd.DataFrame(LoadData.get_inventory(), columns=globalHeader)
        df[globalHeader[1:]].to_excel(fileloc+"ExportedInventory.xlsx", index=False)

    @staticmethod
    def load_inventory(io:str):
        """
        Used for the File loader. This code will read in a set file.
        The code will either:
        - Load in New Products
        - Update the inventory count of a product via it's model Number.

        Returns:
            True is the data was inserted/Updated
            False if it did not.
        """
        i = io.rfind('.')
        if i != -1 and (io[i+1:] in ['xlsx', 'csv', '.xls']):
            if io[i+1:] == 'csv':
                df = pd.read_csv(io)
            else:
                df = pd.read_excel(io)            
            
            # Delete this line later once you fix the upload templates.
            df.set_axis(globalHeader[1:], axis=1, inplace=True) # Update the headers to match to work within the code.

            df2 = pd.DataFrame(LoadData.get_inventory(), columns=globalHeader)
            
            existingProducts = {prod[0] : (prod[1], prod[2]) for prod in df2[['NAME', 'PRICE', "ITEM_ID"]].to_numpy()}
            out = df[globalHeader[1:]].to_numpy().tolist()
            #print(existingProducts)
            # Lists for either updating old inventory, or adding new products.
            existingList = []
            nonExistingList = []
            for row in out:
                # If the product is in the database
                if existingProducts.get(row[0]):
                    #row[3] = existingProducts[row[0]][0] # Update the inventory count'
                    id = existingProducts[row[0]][1]
                    prodCount = row[3] # Get the new amount of product from the user.
                    existingList.append([prodCount, id])
                    # Format to update the product count to be whatever is new in the sheet. 
                else:
                    nonExistingList.append(row)
            #print("Existing:",existingList)
            #print("Nonexisting:",nonExistingList)
            if existingList:
                sdb.change_number_stock_bulk(existingList)
            if nonExistingList:
                    newList = []
                    for cell in nonExistingList:
                        newList.append([str(x).replace("'","") if type(x) == str else x for x in cell])
                    doesntExist = sdb.format_list(newList)
                    sdb.add_item(doesntExist)
            sdb.reconnectDb() # reconnect to the database.
            return True
        else:
            print("Invalid File type")
            return False

    @staticmethod
    def get_inventory():
        rows = sdb.SQL_Query_table("items")
        return rows

class SQL_Reports:
    @staticmethod
    def dailyReport():     
        today = datetime.today().strftime("%Y-%m-%d")
        rows = sdb.SQL_Query_table("money_transactions")
        df = pd.DataFrame(rows, columns = money_header)
        df = df.query(f'DATE.str.contains("{today}")')
        df.to_excel(DOWNLOAD_DIR+f"Daily_Report_{today}.xlsx", index=False)
    
    @staticmethod
    def totalProductSales():
        '''
        This report will take in a Sku, and it will search all orders where the product was sold.
        '''
        today = datetime.today().strftime("%Y-%m-%d")
        final_header=["ITEM_ID", "NAME", "DESCRIPTION", "SOLD_QUANTITY"]
        df1 = pd.DataFrame(sdb.SQL_Query_table("items"), columns=globalHeader)
        df2 = pd.DataFrame(sdb.SQL_Query_table("items_bought"),columns=itemsBoughtHeader)
        df2_list = df2.drop(["TRANSACTION_ID", "DATE", "PRICE", "TAX"],axis=1).to_numpy().tolist()
        temp_db = defaultdict(int)
        for tup in df2_list:
            temp_db[tup[0]] += tup[1]
        doc_list = []
        for _, row in df1.iterrows():
            if row["ITEM_ID"] in temp_db:
                doc_list.append([row["ITEM_ID"], row["NAME"], row["DESCRIPTION"], temp_db[row["ITEM_ID"]]])
        pd.DataFrame(doc_list, columns=final_header).to_excel(DOWNLOAD_DIR+f"Total_Product_Sales_{today}.xlsx", index=False)
        
    @staticmethod
    def transactions():
        """
        This one could take in input for a month range...
        """ 
        today = datetime.today().strftime("%Y-%m-%d")
        rows = sdb.SQL_Query_table("money_transactions")
        df1 = pd.DataFrame(rows, columns = money_header)
        df1 = df1.query(f'DATE.str.contains("{today}")')[["TRANSACTION_ID", "TOTAL_PRICE"]]
    
        
        
        rows = sdb.SQL_Query_table("items_bought")
        df2 = pd.DataFrame(rows, columns=itemsBoughtHeader)
        df2 = df2.query(f'DATE.str.contains("{today}")')


        df3 = pd.DataFrame(sdb.SQL_Query_table("items"), columns=globalHeader)
        df3 = df3[["ITEM_ID", "NAME"]]
        orderCost = {int(cell[0]) : cell[1] for cell in df1.to_numpy().tolist()}
        prodNames = {cell[0] : cell[1] for cell in df3.to_numpy().tolist()}
        #print("\n\n\n\n",orderCost)
        #print(prodNames)
        #print(df1)
        df2["NAME"] = df2["ITEM_ID"].apply(lambda x: prodNames[x])
        df2["TRANSACTION_TOTAL"] = df2["TRANSACTION_ID"].apply(lambda x: orderCost[x])
        df2 = df2[["ITEM_ID", "NAME", "NUMBER", "PRICE", "TAX", "TRANSACTION_TOTAL", "TRANSACTION_ID"]]
        #print(df2)
        df2.to_excel(DOWNLOAD_DIR+f"Todays_sold_products_{today}.xlsx", index=False)
        





        
        

#SQL_Reports.dailyReport()
#SQL_Reports.totalProductSales()
#SQL_Reports.transactions()