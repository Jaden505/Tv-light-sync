from phue import Bridge
import numpy as np
from threading import Thread
import time
from PIL import ImageGrab
import cv2 as cv
import matplotlib.pyplot as plt
from skimage import color
from math import pow

b = Bridge('192.168.178.94')

b.connect()

class Lights:
    def __init__(self):
        b.set_group('Woonkamer', 'on', True)

    def allLights(self, x, y):
        b.set_group('Woonkamer', 'xy', [x, y], transitiontime=5)

    def tvLights(self,):
        pass

class Colors:
    def show_img_compar(self, img_1, img_2):
        print('Prepare showing')
        f, ax = plt.subplots(1, 2, figsize=(10,10))
        ax[0].imshow(img_1)
        ax[1].imshow(img_2)
        ax[0].axis('off')
        ax[1].axis('off')
        f.tight_layout()
        plt.show()

    def getImg(self,):
        img = np.array(ImageGrab.grab())
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img = cv.resize(img, (500, 300), interpolation=cv.INTER_AREA)
        self.img = cv.cvtColor(img, cv.COLOR_RGB2BGR)

    def getColor(self,):
        img_temp = self.img.copy()
        unique, counts = np.unique(img_temp.reshape(-1, 3), axis=0, return_counts=True)

        img_temp[:, :, 0], img_temp[:, :, 1], img_temp[:, :, 2] = unique[np.argmax(counts)]

        r,g,b = img_temp[0][0] / 255

        if r >= 0.04045:
            r = pow((r + 0.055) / (1.0 + 0.055), 2.4)
            r = r / 12.92
        if g >= 0.04045:
            g = pow((g + 0.055) / (1.0 + 0.055), 2.4)
            g = g / 12.92
        if b >= 0.04045:
            b = pow((b + 0.055) / (1.0 + 0.055), 2.4)
            b = b / 12.92

        X = r * 0.649926 + g * 0.103455 + b * 0.197109
        Y = r * 0.234327 + g * 0.743075 + b * 0.022598
        Z = r * 0.0000000 + g * 0.053077 + b * 1.035763

        for a in [X,Y,Z]:
            if a <= 0:
                X = 0.32
                Y = 0.32
                Z = 0.32

        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)

        # show_img_compar(img, img_temp)

        return x, y

l = Lights()
c = Colors()

while True:
    c.getImg()
    x,y = c.getColor()

    l.allLights(x,y)
