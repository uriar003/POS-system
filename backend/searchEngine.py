import pandas as pd
import math


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
        print(self.df)


    def __getDatabase(self):
        '''
        Generates the Database as a pandas dataframe.
        Pandas approach
        '''
        self.df = pd.read_csv('vg_data.csv')
        #self.inventory_df = ...
        # Get a SQL query (Maybe just do a test Excel for now... )

    def user_input(self):
        '''
        THIS IS A TESTING FUNCTION, WILL NOT MAKE IT TO LIVE.
        Used to test the search_product function.
        '''
        #here
        inp = input('Search for products.\nInput: ')
        countOf = 1
        for nodes in self.search_product(inp):
            count = nodes[0]
            nodeList = nodes[1]
            count2 = countOf + len(nodeList) - 1
            
            for node in nodeList:
                print(node)
            print(f"Showing {countOf} -> {count2} of {count}")
            if count2 == count:
                break
            inp = input('Continue?')
            if inp.lower() == 'n':
                break
            countOf = count2 + 1
            

    def search_product(self, userInput:str, amount:int=12):
        '''
        This is a generator function that will be called and will give the user back {amount} many ProductNodes in a list, along with the length of the dataframe.
        '''
        df = self.search(userInput) # Get the Dataframe of the objects.
        nodeArray = []
        counter = 0
        for node in self.gen_data(df):
            nodeArray.append(node)
            counter += 1
            if counter == amount:
                counter = 0
                yield (df.shape[0], nodeArray)
                nodeArray = []
        yield (df.shape[0], nodeArray)

    def search(self, inp:str) -> pd.DataFrame:
        '''
        Given a string, will search the pandas dataframe for the value, followed 
        '''
        return self.df[self.df['Item_id'].str.contains(inp)]


    def gen_data(self,df, amount:int=12):
        '''
        A generator that will take in a dataframe, and will on yield return an {amount} back to the caller until empty.
        '''
        for index, row in df.iterrows():
            name = row['Item_id']
            pic  = row['Picture']
            stock = row['Number_in_stock']
            price = row['Price']
            description = row['Description']
            yield ProductNode(name, pic, price, stock, description)


class ProductNode:
    '''
    A ProductNode is an object that is meant to be used to communicate with
    the Gui the proper data and access it's information.
    '''
    
    def __init__(self, name, picture, price, stock, description):
        self.__name = name
        self.__picture = f"../imgs/{picture}"
        self.__price = float('%.2f' % price)
        self.__stock = stock
        self.__description = description

    def getName(self):
        return self.__name
    
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
        return f"Name :: {self.__name} | Picture :: {self.__picture} | Price  :: {self.__price} | Description :: {self.__description} | Stock :: {self.__stock}"




# Unnote to test
#x = SearchEngine()
#x.user_input()