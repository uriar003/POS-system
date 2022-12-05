import sys
import pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)+"/sql")
import SQL_Database as sdb
from datetime import datetime
DOWNLOAD_DIR = str(Path(__file__).resolve().parent.parent)+"/Inventory/Reports/"
globalHeader = ["ITEM_ID", "NAME", "BARECODE", "PICTURE", "COUNT", "PRICE", "DESCRIPTION"]

class LoadData:
    @staticmethod
    def export_template(fileloc:str=""):
        '''
        Exports a template that can be used for the format of uploading inventory.
        Parameters:
            we should know the file location of where to save this data...

        '''
        df = pd.DataFrame(columns=globalHeader[1:])
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
        money_header = [
            "TRANSACTION_ID",
            "DATE",
            "TRANSACTION_TYPE",
            "TOTAL_PRICE",
            "CREDIT_CARD_ID"
        ]
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
        pass

    @staticmethod
    def transactions():
        """
        This one could take in input for a month range...
        """
        pass
        

#SQL_Reports.dailyReport()
#SQL_Reports.totalProductSales()
#SQL_Reports.transactions()