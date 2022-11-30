import sys
import pandas as pd
sys.path.insert(0, "../sql")
import SQL_database as sdb
from datetime import datetime

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
            print(existingProducts)
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
                alreadyExist = sdb.format_list(existingList)
                print(alreadyExist)
                #sdb.change_number_stock_bulk(alreadyExist)
                sdb.change_number_stock_bulk(existingList)
            if nonExistingList:
                doesntExist = sdb.format_list(nonExistingList)
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
    def displayInventory():
        pass

    @staticmethod
    def displayProductOrders(prodSku:str):
        '''
        This report will take in a Sku, and it will search all orders where the product was sold.
        '''
        pass

    @staticmethod
    def displaySoldProducts():
        """
        This one could take in input for a month range...
        """
        
class Transaction:
    
    @staticmethod
    def generateInvoice(productList:list, cost:float, tax:float, cc:int=0):
        """
        productList will come in as a list of lists
        [[item_id, Name, price, Barcode?(barcode can be removed but doesnt need to be)],....]

        """
        today = datetime.today().date()
        total = float('%.2f' % (cost*(1+tax)))
        transaction_details = sdb.format_list([today, total, "SOLD"]) # Format the input for the order
        sdb.add_order(transaction_details)
        # Get the newly created id. (Will be the highest ID)
        newId =sdb.SQL_Query_table_highest_id("money_transactions", "TRANSACTION_ID")
        for product in productList:
            item_id = product[0]
            #prod = product[1]
            price = product[2]
            productDetails = sdb.format_list([newId, today, item_id, 1, price, tax])
            sdb.add_item_boughts(productDetails)


###
#LoadData.print_inventory()

def run():
    fn = 'vg_data__1.xlsx'
    

    LoadData.load_inventory(fn)
    df = pd.DataFrame(LoadData.get_inventory(), columns=globalHeader)
    print(df)

#LoadData.export_template()
#run()
#df = pd.DataFrame(LoadData.get_inventory(), columns=header)#
#print(df)
#run()
#LoadData.export_inventory()

"""today = datetime.today().date()
cost = 20
tax = .0775
total = float('%.2f' % (cost*(1+tax)))
transaction_details = sdb.format_list([today, total, "SOLD"])
#print(x)
newId =sdb.SQL_Query_table_highest_id("money_transactions", "TRANSACTION_ID")
z = sdb.SQL_Query_table("items")"""