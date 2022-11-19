import sys
import pandas as pd
sys.path.insert(0, "../sql")
import SQL_database as sdb




class LoadData:
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
            df2 = pd.DataFrame(LoadData.print_inventory(), columns=header)
            existingProducts = {prod[0] : prod[1] for prod in df2[['Name', 'Number']].to_numpy()}
            out = df[["Name", "Barcode", "Picture", "Number", "Price", "Description"]].to_numpy().tolist()
            for row in out:
                # If the product is in the database, update the 
                if existingProducts.get(row[0]):
                    row[3] += existingProducts[row[0]] # Update the inventory count 
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


###
#LoadData.print_inventory()

fn = 'vg_data__1.csv'

header = ["ID", "Name", "Barcode", "Picture", "Number", "Price", "Description"]
#LoadData.load_inventory(fn)
#df = pd.DataFrame(LoadData.print_inventory(), columns=header)
#print(df)
