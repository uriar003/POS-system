import sys
import pandas as pd
sys.path.insert(0, "../sql")
import SQL_database as sdb




class LoadData:
    @staticmethod
    def load_inventory(io:str):
        i = io.rfind('.')
        if i != -1 and (io[i+1:] in ['xlsx', 'csv', '.xls']):
            if io[i+1:] == 'csv':
                df = pd.read_csv(io)
            else:
                df = pd.read_excel(io)
            print(df)
            llist = sdb.format_items(df.to_numpy().tolist())
            print(llist)
            sdb.add_item(llist)
        else:
            print("Invalid File type")
            return False
    @staticmethod
    def print_inventory():
        rows = sdb.SQL_Query_table("items")
        print(rows)
fn = 'vg_data__1.xlsx'

#LoadData.print_inventory()
#LoadData.load_inventory(fn)
LoadData.print_inventory()