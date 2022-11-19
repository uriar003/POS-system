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
        """
        i = io.rfind('.')
        if i != -1 and (io[i+1:] in ['xlsx', 'csv', '.xls']):
            if io[i+1:] == 'csv':
                df = pd.read_csv(io)
            else:
                df = pd.read_excel(io)
            out = df.to_numpy().tolist()
            llist = sdb.format_list(out)
            sdb.add_item(llist)
        else:
            print("Invalid File type")
            return False

    @staticmethod
    def print_inventory():
        rows = sdb.SQL_Query_table("items")
        return rows
fn = 'vg_data__1.csv'
###
#LoadData.print_inventory()
header = ["ID", "Name", "Barcode", "Picture", "Number", "Price", "Description"]
LoadData.load_inventory(fn)
df = pd.DataFrame(LoadData.print_inventory(), columns=header)

