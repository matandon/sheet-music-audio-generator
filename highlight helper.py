from PIL import Image
import PIL
import os
from tkinter import *
from cmu_112_graphics import *

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

class helper(App):
    def appStarted(self):
        self.image = self.loadImage("Sheet Music Library/Mary Had A Little Lamb Mason/page1.png")
        self.image = self.scaleImage(self.image, 4/12, 3/6)
        self.imWidth, self.imHeight = self.image.size
        self.pixelx, self.pixely = 0, 0
        self.pixelcolor = None

    def mouseMoved(self, event):
        if ((event.x >= self.width//2 - self.imWidth//2 and event.x <= self.width//2 + self.imWidth//2)
            and (event.y >= self.height//2 - self.imHeight//2 and event.y <= self.height//2 + self.imHeight//2)):
            self.pixelx = roundHalfUp((event.x - (self.width//2 - self.imWidth//2)))*2
            self.pixely = roundHalfUp((event.y - (self.height//2 - self.imHeight//2)))*3
            self.pixelcolor = self.image.getpixel((self.pixelx, self.pixely))

    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, fill = "black")
        canvas.create_image(self.width//2, self.height//2, image = ImageTk.PhotoImage(self.image))
        canvas.create_text((self.width//2 - self.imWidth//2) // 2, self.height//2, 
                            text = f"{self.pixelx, self.pixely, self.pixelcolor}", fill = "white")


helper(width = 800, height = 800)