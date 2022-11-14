from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

screen_manager = ScreenManager()

Builder.load_file('frontPage.kv')
Builder.load_file('login.kv')
Builder.load_file('mainpos.kv')
Builder.load_file('cart.kv')
Builder.load_file('reports.kv')
Builder.load_file('addInv.kv')
Builder.load_file('account.kv')

class frontPage(Screen):
    #user=ObjectProperty(None)
    #password=ObjectProperty(None)
    pass

class login(Screen):
    pass

class mainPOS(Screen):
    pass

class cart(Screen):
    pass

class reports(Screen):
    pass

class addInv(Screen):
    pass

class account(Screen):
    pass

screen_manager.add_widget(frontPage(name="front"))
screen_manager.add_widget(login(name="login"))
screen_manager.add_widget(mainPOS(name="main"))
screen_manager.add_widget(cart(name="cart"))
screen_manager.add_widget(reports(name="reports"))
screen_manager.add_widget(addInv(name="invent"))
screen_manager.add_widget(account(name="account"))

def press(self):
    pass

class posApp(App):
    def build(self):
        return screen_manager

if __name__ == '__main__':
    posApp().run()
