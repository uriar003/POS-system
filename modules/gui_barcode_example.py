import time

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.label import Label
from kivymd.uix.list import *
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.properties import ListProperty

import cv2                          # OpenCV is under Apache License 2.0, so it is free to use commercially
import numpy as np
from pyzbar.pyzbar import decode    # PyzBar is under the MIT License, which among other things permits modification and re-sale

Builder.load_file('gui_barcode_example.kv')
mdlstItemlist = []

class mainPOS(Screen):
        def additem(self, *args):
            print("adding item")
            # adds dummy item, this isn't working
            self.ids.mdlstItems.add_widget(OneLineListItem(text = "newitem"))

        def onitempress(self, pressed, list_id):
            print(self)
            # these are the params we can use to populate from/to the sql
            item = TwoLineAvatarListItem(text="soup", secondary_text="$X.XX")
            item.add_widget(IconLeftWidget(icon="soup.png"))
            self.ids.mdlstItems.add_widget(item)
            mdlstItemlist.append(item)
            print(mdlstItemlist)

class posApp(MDApp):
    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(mainPOS(name="main"))

        # check camera every second or so for a barcode
        Clock.schedule_interval(self.oncvscan, 1.0/1.0)
        self.cap = cv2.VideoCapture(1)

        self.scr = screen_manager.get_screen("main")

        return screen_manager

    def oncvscan(self, *args):
        success, img = self.cap.read()


        # if barcode was detected
        if(len(decode(img)) > 0):

            # note that decode gets ALL barcodes in a frame, but we only want the first one detected
            barcode = decode(img)
            bdata = barcode[0].data.decode('utf-8')
            print("barcode found:", bdata)
            print(mainPOS().ids.mdlstItems)
            self.scr.ids.mdlstItems.add_widget(OneLineListItem(text = "newitem"))
            mainPOS().ids.mdlstItems.add_widget(OneLineListItem(text = "newitem"))
            # self.root.ids.mdlstItems.add_widget(OneLineListItem(text="newitem"))
        else:
            print("no barcode found")

if __name__ == '__main__':
    posApp().run()