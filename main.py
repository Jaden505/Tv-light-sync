from phue import Bridge
import numpy as np
from PIL import ImageGrab
import cv2 as cv
import matplotlib.pyplot as plt
from math import pow
import webbrowser
import socket
import discoverhue
import re
import importlib

def getBridgeIP():
    found = discoverhue.find_bridges()
    for bridge in found:
        bridge_ip = (re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', found[bridge]).group())
    return bridge_ip

b = Bridge(getBridgeIP())

# print(b)

b.connect()

class Stream:
    def startStream(self,):
        RaspCam.startStream()

    def get_ip(self,):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def openStream(self,):
        url = f'http://{self.get_ip()}:8000'
        webbrowser.open(url)

class Lights:
    def __init__(self):
        b.set_group('Woonkamer', 'on', True)

    def allLights(self, x, y):
        b.set_group('Woonkamer', 'xy', [x, y], transitiontime=5)

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

    def getColors(self,):
        img_temp = self.img.copy()
        img_temp2 = self.img.copy()

        unique, counts = np.unique(img_temp.reshape(-1, 3), axis=0, return_counts=True)
        unique2, counts2 = np.unique(img_temp2.reshape(-1, 3), axis=0, return_counts=True)

        sorted = np.argsort(counts)
        sorted2 = np.argsort(counts2)

        img_temp[:, :, 0], img_temp[:, :, 1], img_temp[:, :, 2] = unique[sorted[-1]]
        img_temp2[:, :, 0], img_temp2[:, :, 1], img_temp2[:, :, 2] = unique2[sorted2[-2]]

        # self.img = (np.average(np.arange(img_temp, img_temp2)))
        self.img = np.mean(np.array([img_temp, img_temp2]), axis=0)

    def translateColors(self):
        r, g, b = self.img[0][0] / 255

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

        if X <= 0:
            X = 0.32
        if Y <= 0:
            Y = 0.32
        if Z <= 0:
            Z = 0.32

        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)

        # show_img_compar(img, img_temp)

        return x, y


if __name__ == "__main__":
    c = Colors()
    l = Lights()
    s = Stream()

    # s.openStream()

    while True:
        c.getImg()
        c.getColors()
        x,y = c.translateColors()

        l.allLights(x,y)
