import sys
import pandas as pd
sys.path.insert(0, "../sql")
import SQL_database as sdb




class LoadData:
    
    @staticmethod
    def export_template(fileloc:str=""):
        '''
        Exports a template that can be used for the format of uploading inventory.
        
        Parameters:
            we should know the file location of where to save this data...

        '''
        header = ["Name", "Barcode", "Picture", "Number", "Price", "Description"]
        df = pd.DataFrame(columns=header)
        df.to_excel(fileloc+"TemplateFile.xlsx", index=False)


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
        header = ["Name", "Barcode", "Picture", "Number", "Price", "Description"]
        i = io.rfind('.')
        if i != -1 and (io[i+1:] in ['xlsx', 'csv', '.xls']):
            if io[i+1:] == 'csv':
                df = pd.read_csv(io)
            else:
                df = pd.read_excel(io)
            df2 = pd.DataFrame(LoadData.print_inventory(), columns=header)
            existingProducts = {prod[0] : prod[1] for prod in df2[['Name', 'Number']].to_numpy()}
            out = df[["Name", "Barcode", "Picture", "Number", "Price", "Description"]].to_numpy().tolist()
            existingList = []
            nonExistingList = []
            for row in out:
                # If the product is in the database
                if existingProducts.get(row[0]):
                    row[3] += existingProducts[row[0]] # Update the inventory count
                    existingList.append(row)
                else:

                    nonExistingList.append(row)
            print(existingList)
            print(nonExistingList)
            llist = sdb.format_list(out)
            sdb.add_item(llist)
            return True
        else:
            print("Invalid File type")
            return False

    @staticmethod
    def print_inventory():
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
        



###
#LoadData.print_inventory()

def run():
    fn = 'vg_data__1.csv'

    header = ["ID", "Name", "Barcode", "Picture", "Number", "Price", "Description"]
    LoadData.load_inventory(fn)
    df = pd.DataFrame(LoadData.print_inventory(), columns=header)
    print(df)

#LoadData.export_template()
run()
