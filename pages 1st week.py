from cmu_112_graphics import *
from tkinter import *
import os
import decimal
from scanning_code import Parser 
import PIL
from PIL import ImageOps
import pytesseract
#pytesseract.pytesseract.tesseract_cmd = r'c:/users/manya/appdata/local/programs/python/python39/lib/site-packages'


def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

class SplashScreenMode(Mode):
    def appStarted(mode):
        mode.buttonTop = mode.height/2 - 25
        mode.buttonLeft = mode.width/2 - 50
        mode.buttonRight = mode.width/2 + 50
        mode.buttonBottom = mode.height/2 + 25

    def timerFired(mode):
        mode.buttonTop = mode.height/2 - 25
        mode.buttonLeft = mode.width/2 - 50
        mode.buttonRight = mode.width/2 + 50
        mode.buttonBottom = mode.height/2 + 25

    def redrawAll(mode, canvas):
        # RESIZE THIS STUFF
        font = "Courier 26 bold"
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "light blue")
        canvas.create_text(mode.width/2, mode.height/2 - 150, text = "Sheet Music Parser & Audio Generator", font = font)
        canvas.create_rectangle(mode.buttonLeft, mode.buttonTop, 
                                mode.buttonRight, mode.buttonBottom, fill = "black")
        canvas.create_text(mode.width/2, mode.height/2, text = "Start", font = "Courier 13 bold", fill = "white")

    def mousePressed(mode, event):
        if (mode.buttonLeft <= event.x <= mode.buttonRight and 
            mode.buttonTop <= event.y <= mode.buttonBottom):
            mode.app.setActiveMode(mode.app.libraryMode)

class LibraryMode(Mode):
    def appStarted(mode):
        mode.libraryFiles = []
        mode.lengthOfNames = []
        mode.notDisplayedDown = []
        mode.notDisplayedUp = []
        mode.notFit = False
        url = "https://static.thenounproject.com/png/59745-200.png"
        mode.downArrow = mode.loadImage(url)
        mode.scaledDownArrow = mode.scaleImage(mode.downArrow, 0.05*mode.width/mode.downArrow.size[0])
        mode.upArrow = mode.loadImage("up arrow.png")
        mode.scaledUpArrow = mode.scaleImage(mode.upArrow, 0.05*mode.width/mode.upArrow.size[0])
        for folderName in os.listdir("Sheet Music Library"):
            mode.libraryFiles += [folderName]
        for folderName in mode.libraryFiles:
            mode.lengthOfNames += [len(folderName)]
        mode.minDimension = min(roundHalfUp(mode.width - (1/10)*mode.width), roundHalfUp(mode.height))
        mode.fontSize = min(mode.minDimension//len(mode.libraryFiles), mode.minDimension//(max(mode.lengthOfNames)))
    
    def mousePressed(mode, event):
        mode.app.setActiveMode(mode.app.parserMode)

    def timerFired(mode):
        mode.minDimension = min(roundHalfUp(mode.width - (1/10)*mode.width), roundHalfUp(mode.height))
        mode.fontSize = min(mode.minDimension//len(mode.libraryFiles), mode.minDimension//(max(mode.lengthOfNames)))
        mode.scaledDownArrow = mode.scaleImage(mode.downArrow, 0.05*mode.width/mode.downArrow.size[0])
        mode.scaledUpArrow = mode.scaleImage(mode.upArrow, 0.05*mode.width/mode.upArrow.size[0])
        while 1.4*len(mode.libraryFiles)*mode.fontSize > mode.height:
            mode.notDisplayedDown += [mode.libraryFiles.pop()]
            if mode.notFit == False:
                mode.notFit = True

    def keyPressed(mode, event):
        if event.key == "Down":
            if mode.notDisplayedDown != []:
                mode.notDisplayedUp += [mode.libraryFiles.pop(0)]
                mode.libraryFiles += [mode.notDisplayedDown.pop(0)]
        elif event.key == "Up":
            if mode.notDisplayedUp != []:
                mode.libraryFiles.insert(0, mode.notDisplayedUp.pop())
                mode.notDisplayedDown.insert(0, mode.libraryFiles.pop())

    def redrawAll(mode, canvas):
        font = f"Courier {mode.fontSize}"
        height = 0.5*mode.fontSize*1.4
        origHeight = height*2
        for piece in mode.libraryFiles:
            title = " ".join(piece.split()[:-1])
            composer = piece.split()[-1]
            canvas.create_text(mode.width*0.02, height, text = title, font = font, anchor = "w")
            if mode.notFit:
                canvas.create_text(mode.width - mode.width*0.1, height, text = composer, font = font, anchor = "e")
            else:
                canvas.create_text(mode.width - mode.width*0.02, height, text = composer, font = font, anchor = "e")
            height += 1.4*mode.fontSize
        if mode.notFit:
            canvas.create_image(mode.width - 0.05*mode.width, mode.height - 0.05*mode.width, 
                                image = ImageTk.PhotoImage(mode.scaledDownArrow))
            canvas.create_image(mode.width - 0.05*mode.width, 0.05*mode.height, 
                                image = ImageTk.PhotoImage(mode.scaledUpArrow))        

class ParserMode(Mode):
    def appStarted(mode):
        mode.fileName = "Sheet Music Library/Mary Had A Little Lamb Mason/page1.png"
        mode.windowX1, mode.windowY1, mode.windowX2, mode.windowY2 = None, None, None, None
        image = PIL.Image.open(mode.fileName)
        mode.image = ImageOps.grayscale(image)
        mode.newImg = mode.image.convert('RGB')
        mode.pixels = mode.newImg.load()
        mode.i = 0
        mode.makeButton = False
        mode.startWindowX = 0
        mode.condensedSections =  []
        # for each tuple go thru and chg pixels
        mode.iwidth, height = mode.image.size
        mode.newImg = mode.scaleImage(mode.newImg, 800/mode.iwidth, 800/height)
        scaleW, _ = mode.newImg.size
        mode.offset = mode.width//2 - scaleW//2

    def chgPixelGreen(mode, column, topRow, bottomRow):
        for j in range(topRow, bottomRow + 1):
            mode.pixels[column, j] = (0, 255, 0)

    def chgPixelRed(mode, column, topRow, bottomRow):
        for j in range(topRow, bottomRow + 1):
            mode.pixels[column, j] = (255, 0, 0)

    def mousePressed(mode, event):
        if mode.windowX2 != None and mode.windowY2 != None:
            mode.windowX2, mode.windowY2 = None, None
        mode.windowX1, mode.windowY1 = event.x, event.y

    def mouseDragged(mode, event):
        mode.windowX2, mode.windowY2 = event.x, event.y

    def mouseReleased(mode, event):
        # fix the way the path names work
        pathNames = ["trebleCleff.png", "timeSig.png", "keySig.png"]
        if mode.windowX1 != None and mode.windowX2 != None and mode.windowY2 != None and mode.windowY1 != None and mode.i <= 2:
            mode.windowX1 -= mode.offset
            mode.windowX2 -= mode.offset
            timeSig = mode.newImg.crop((mode.startWindowX, 0, mode.windowX2, mode.windowY2))
            timeSig.save(f"Sheet Music Library/Mary Had A Little Lamb Mason/{pathNames[mode.i]}")
            mode.condensedSections += [(mode.startWindowX*mode.iwidth//800, mode.windowX2*mode.iwidth//800)]
            mode.i += 1
            mode.startWindowX = mode.windowX2

        if mode.i == 2:
            mode.makeButton = True

        if (mode.width//2 - 50 <= event.x <= mode.width//2 + 50 and
            mode.height//5 - 25 <= event.y <= mode.height//5 + 25):
            mode.i += 1

        if mode.i > 2:
            mode.imageParsing()

        mode.windowX1, mode.windowX2, mode.windowY1, mode.windowY2 = None, None, None, None
        #timeSigText = pytesseract.image_to_string(f"Sheet Music Library/Mary Had A Little Lamb Mason/{pathNames[1]}")
        #print(timeSigText)

    def imageParsing(mode):
        parser = Parser(mode.fileName)
        pieceInfo, bubbleLocation, rests = parser.getPieceData(mode.condensedSections)
        for line in pieceInfo:
            for measure in line:
                for note in measure:
                    mode.chgPixelRed(note[0], note[1], note[2]) # list of tuples column top+bot row
        for line in rests:
            for measure in line:
                for rest in measure:
                    mode.chgPixelGreen(rest[0], rest[1], rest[2])

        for location in bubbleLocation:
            mode.makePixelGreen(location[0], location[1])
        print("done")

    def makePixelGreen(mode, x, y):
        mode.pixels[x, y] = (0, 255, 0)
        for i in range(5): # change to 5 if need more visibility
            mode.pixels[x+i, y] = (0, 255, 0)
            mode.pixels[x-i, y] = (0, 255, 0)

    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "black")
        canvas.create_image(mode.width//2, mode.height//2, image = ImageTk.PhotoImage(mode.newImg))
        canvas.create_rectangle(mode.width//2 - 150, mode.height//8 - 25, 
                                    mode.width//2 + 150, mode.height//8 + 25, fill = "white")
        canvas.create_text(mode.width//2, mode.height//8, text = "crop cleff, time sig, and key sig")
        if mode.windowX1 != None and mode.windowX2 != None and mode.windowY2 != None and mode.windowY1 != None:
            canvas.create_line(mode.windowX1, mode.windowY1, mode.windowX2, mode.windowY2)
        if mode.makeButton:
            canvas.create_rectangle(mode.width//2 - 50, mode.height//5 - 25, 
                                    mode.width//2 + 50, mode.height//5 + 25, fill = "yellow")
            canvas.create_text(mode.width//2, mode.height//5, text = "Skip")
        

class MyModalApp(ModalApp):
    def appStarted(app): #add path requirement here and for each class, then pass down so it's dynamic
        app.splashScreenMode = SplashScreenMode()
        app.libraryMode = LibraryMode()
        app.parserMode = ParserMode()
        app.setActiveMode(app.splashScreenMode)

app = MyModalApp(width=800, height=800)
