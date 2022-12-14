import pandas as pd
import sys

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)+"/sql")
import SQL_Database as sdb


class SearchEngine:
    '''
    2 Ways of going about it:
    Generate a Pandas DF to search or a SQL query every time
    '''
    def __init__(self):
        '''
        Generates the search engine.
        '''
        self.__getDatabase()
        #print(self.df)


    def __getDatabase(self):
        '''
        Generates the Database as a pandas dataframe.
        Pandas approach
        '''
        #self.df = pd.read_csv('vg_data.csv')
        self.df = pd.read_sql("SELECT * from items", sdb.conn)
        #self.inventory_df = ...
        # Get a SQL query (Maybe just do a test Excel for now... )

    def user_input(self,nodes=False):
        '''
        THIS IS A TESTING FUNCTION, WILL NOT MAKE IT TO LIVE.
        Used to test the search_product function.
        '''
        #here
        inp = input('Search for products.\nInput: ')
        countOf = 1
        if nodes:
            genObj = self.search_product_nodes(inp)
        else:
            genObj = self.search_product(inp)
        countMax = next(genObj) 
        for nodes in genObj:
            #count = nodes[0]
            nodeList = nodes
            count2 = countOf + len(nodeList) - 1

            for node in nodeList:
                print(node)
            print(f"Showing {countOf} -> {count2} of {countMax}")
            if count2 == countMax:
                break
            inp = input('Continue?')
            if inp.lower() == 'n':
                break
            countOf = count2 + 1
            

    def search_product(self, userInput:str, amount:int=4):
        '''
        This is a generator function that will be called and will give the user back {amount} many ProductNodes in a list, along with the length of the dataframe.
        '''
        self.__getDatabase()
        df = self.search(userInput) # Get the Dataframe of the objects.
        nodeArray = []
        counter = 0
        yield df.shape[0]
        for node in self.gen_data(df):
            nodeArray.append(node)
            counter += 1
            if counter == amount:
                counter = 0
                yield nodeArray
                nodeArray = []
        yield nodeArray

    def search_product_nodes(self, userInput:str, amount:int=4):
        '''
        This is a generator function that will be called and will give the user back {amount} many ProductNodes in a list, along with the length of the dataframe.
        '''
        self.__getDatabase()
        df = self.search(userInput) # Get the Dataframe of the objects.
        nodeArray = []
        counter = 0
        yield df.shape[0]
        for node in self.gen_data_nodes(df):
            nodeArray.append(node)
            counter += 1
            if counter == amount:
                counter = 0
                yield nodeArray
                nodeArray = []
        yield nodeArray


    def search(self, inp:str) -> pd.DataFrame:
        '''
        Given a string, will search the pandas dataframe for the value, followed 
        '''
        return self.df[self.df['NAME'].str.contains(inp, na=False, case=False)]

    def search_barcode(self, inp:str):
        '''
        Given a string, will search the pandas dataframe for the value, followed 
        '''
        return self.df[self.df['BARECODE'].str.contains(inp)].to_numpy().tolist()


    def gen_data(self,df, amount:int=12):
        '''
        A generator that will take in a dataframe, and will on yield return an {amount} back to the caller until empty.
        '''
        for _, row in df.iterrows():
            id = row['ITEM_ID']
            name = row['NAME']
            barcode = row['BARECODE']
            pic  = row['PICTURE']
            stock = row['NUMBER']
            price = row['PRICE']
            description = row['DESCRIPTION']
            #yield ProductNode(id, name, price)
            #yield [id, name, price, barcode]
            yield [id, name, barcode, pic, stock, price, description]

    def gen_data_nodes(self,df, amount:int=12):
        '''
        A generator that will take in a dataframe, and will on yield return an {amount} back to the caller until empty.
        '''
        for _, row in df.iterrows():
            id = row['ITEM_ID']
            name = row['NAME']
            barcode = row['BARECODE']
            pic  = row['PICTURE']
            stock = row['NUMBER']
            price = row['PRICE']
            description = row['DESCRIPTION']
            yield ProductNode(id, name, barcode, pic, stock, price, description)


class ProductNode:
    '''
    A ProductNode is an object that is meant to be used to communicate with
    the Gui the proper data and access it's information.
    '''
    
    def __init__(self, id, name, barcode, pic, stock, price, description):
        print(id, name, price)
        self.__id = id
        self.__name = name
        self.__barcode = barcode
        self.__picture = pic
        self.__price = float('%.2f' % price)
        self.__stock = stock
        self.__description = description

    def getId(self):
        return self.__id

    def getName(self):
        return self.__name

    def getBarcode(self):
        return self.__barcode
    
    def getPicture(self):
       return self.__picture
        
    def getStock(self):
        return self.__stock

    def getPrice(self):
        return self.__price
        
    def getDescription(self):
        return self.__description

    def __repr__(self):
        return 'ProductNode'

    def __str__(self):
        return f"Id :: {self.__id} | Name :: {self.__name} | Price  :: {self.__price}"


# Unnote to test
#x = SearchEngine()
#x.user_input()