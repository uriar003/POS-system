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

        else:
            print("Invalid File type")
            return False

fn = 'vg_data__1.xls'

LoadData.load_inventory(fn)