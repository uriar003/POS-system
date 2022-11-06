from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

class wndwLogin(Screen):
    pass

class wndwPOS(Screen):
    pass

class WindowManager(ScreenManager):
    pass

kv = Builder.load_file('POSLayout.kv')      # global variable, it must be put here
                                            # above the MainApp func for some reason

# PostgreSQL Listen at port 5432
class MainApp(MDApp):
    # title = "Items List"
    def build(self):
        # set window size before launch
        Window.size = (1024, 768) # 4:3
        # Window.size = (1280, 720)   # 16:9 alt

        self.theme_cls.theme_style = "Dark"     # sets color to avoid eye-burning white of kivymd
        self.theme_cls.primary_palette = "BlueGray"     # ditto above

        sm = ScreenManager()

        # The order of widgets below is important in login loading first
        sm.add_widget(wndwLogin(name = 'Login'))
        sm.add_widget(wndwPOS(name = 'POS System'))

        return sm

    def onpress(self, pressed, list_id):
        print("this is a product")

if __name__ == '__main__':
    MainApp().run()