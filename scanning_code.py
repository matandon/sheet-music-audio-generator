from PIL import Image
import PIL
import os
from tkinter import *
from cmu_112_graphics import *
from note_id import *
from PIL import ImageOps

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

class Parser():
    def __init__(self, fileName):
        self.fileName = fileName
        self.extraStaffRows = {}
    
    '''
        Goal
        Finds the top of a line of music, including all markings.

        Input
        topBlackRow: the top staff line of the line of music
        rowList: a list of tuples consisting of the row number of the image, number 
        of black pixels in that row, and number of white pixels in that row

        Output
        Returns the first row above all markings above the first staff line
    '''
    def findTopMargin(self, topBlackRow, rowList):
        markerMargin = 10
        for row in range(topBlackRow - 1, markerMargin - 1, -1):
            if rowList[row][1] == 0:
                allWhiteRowsAbove = False
                for i in range(row - 1, row - (markerMargin + 1), -1):
                    if rowList[i][1] != 0:
                        break
                    elif i == row - markerMargin:
                        allWhiteRowsAbove = True
                if allWhiteRowsAbove:
                    return rowList[row][0]

    '''
        Goal
        Finds the bottom of a line of music, including all markings.

        Input
        bottomBlackRow: the bottom staff line of the line of music
        nextBlackRow: the next row of music with a large number of black pixels
        rowList: a list of tuples consisting of the row number of the image, number 
        of black pixels in that row, and number of white pixels in that row

        Output
        Returns the first row below all markings below the last staff line.
    '''
    def findBottomMargin(self, bottomBlackRow, nextBlackRow, rowList):
        markerMargin = 10
        for i in range(bottomBlackRow + 1, nextBlackRow):
            if rowList[i][1] == 0:
                for j in range(i + 1, i + markerMargin + 1):
                    if rowList[j][1] != 0:
                        break
                    elif j == i + markerMargin:
                        return i
        # for cases where the piece has no all white rows below last staff line
        return nextBlackRow - 1


    '''
        Goal
        Remove all black rows that are not staff rows. (ex. lines indicating the 1st +
        2nd repeats)

        Input
        blackRows: list of all black rows found within the image

        Output
        List of all staff rows in the piece (Destructively modified the original 
        list)
    '''
    def findValidBlackRows(self, blackRows):
        i = 1
        if blackRows[0] + 20 < blackRows[1]:
            blackRows.pop(0)
        
        if blackRows[-1] - 20 > blackRows[-2]:
            blackRows.pop()

        while i < len(blackRows) - 1:
            if blackRows[i] + 20 < blackRows[i + 1] and blackRows[i] - 20 > blackRows[i - 1]:
                blackRows.pop(i)
            i += 1

    '''
        Goal
        Count the black and white pixels in a given column over a given range.

        Input
        image: opened PIL Image object
        x: column pixels are being counted in
        yIterateOver: tuple that provides the start, end, and step of the range to
        iterate over

        Output
        The number of black and white pixels present in the column over the given
        range.
    '''
    def countPixels(self, image, x, yIterateOver):
        blackPixels = 0
        whitePixels = 0
        for y in range(yIterateOver[0], yIterateOver[1], yIterateOver[-1]):
            color = None
            pixelVal = image.getpixel((x,y))
            # 1st case is in case the image is a multiband image, and the second
            # is for images that are greyscale. All current cases are greyscale,
            # and I'm not sure if it actually works on multiband images.
            if type(pixelVal) != tuple:
                color = (pixelVal, pixelVal, pixelVal)
            else:
                color = pixelVal

            if color != (255, 255, 255):
                blackPixels += 1
            else:
                whitePixels += 1
        return blackPixels, whitePixels
                
    '''
        Goal
        Find each line of music in the entire sheet of music.

        Input
        imgPath: path of sheet music page.

        Output:
        All lines of music in the piece, as well as the staff lines of each line.
        This function also provides the data needed to find each measure within each
        line of music.
    '''
    def getPieceData(self, condensedSections):
        rgbImage = PIL.Image.open(self.fileName)
        image = rgbImage.convert(mode = 'L')
        image.save("Sheet Music Library/mod twinkle.png")#.point(lambda x: 0 if x<200 else 255, '1')
        #image = ImageOps.grayscale(rgbImage)
        width, height = image.size
        rowList = []
        blackRows = []
        topMarginRow = None
        bottomMarginRow = None
        measureArray = []

        for y in range(height):
            blackPixels = 0
            whitePixels = 0
            for x in range(width):
                color = None
                pixelVal = image.getpixel((x,y))
                # 1st case is in case the image is a multiband image, and the second
                # is for images that are greyscale. All current cases are greyscale,
                # and I'm not sure if it actually works on multiband images.
                if type(pixelVal) != tuple:
                    color = (pixelVal, pixelVal, pixelVal)
                else:
                    color = pixelVal

                if color != (255, 255, 255):
                    blackPixels += 1
                else:
                    whitePixels += 1
            rowList += [(y, blackPixels, whitePixels)]
            if blackPixels >= 0.5*width:
                # This case is to avoid all rows that pass the check to be added
                if blackRows == []:
                    blackRows += [y]
                    self.extraStaffRows[y] = []

                # This case is to avoid multiple pixel rows being added for the same
                # staff line, if a staff line is multiple pixel lines thick.
                if y - blackRows[-1] > 5:
                    blackRows += [y]
                    self.extraStaffRows[y] = []
                else:
                    line = max(self.extraStaffRows)
                    self.extraStaffRows[line] += [y]
        self.findValidBlackRows(blackRows)
        #for i in range(0, 1):
        for i in range(len(blackRows)//5):
            topStaffLine = 5*i
            bottomStaffLine = 5*i + 5
            topMarginRow = self.findTopMargin(blackRows[topStaffLine], rowList)
            # The second case is to handle the last line on the page, as there is no
            # staff line after the last one on the page, which means to find the margin
            # it needs the height of the page.
            if bottomStaffLine != len(blackRows):
                # It's bottomStaffLine - 1 because you're actually an index ahead
                # when you add 5, but if you were to add 4 and change the second
                # argument, indexing problems occur.
                bottomMarginRow = self.findBottomMargin(blackRows[bottomStaffLine - 1], blackRows[bottomStaffLine], rowList)
            else:
                bottomMarginRow = self.findBottomMargin(blackRows[bottomStaffLine - 1], height, rowList)
            # line cropping
            lineOfMusic = image.crop((0, topMarginRow, width, bottomMarginRow))
            newPath = self.fileName.replace(os.path.basename(self.fileName), f"line {i + 1}.png") 
            lineOfMusic.save(newPath)
            lineMeasures = self.findMeasures(image, blackRows[topStaffLine:bottomStaffLine], topMarginRow, bottomMarginRow, i, condensedSections)
            measureArray += [lineMeasures]
        toColor, bubbleLocation, rests = findNotes(image, measureArray, self.extraStaffRows, condensedSections)
        return toColor, bubbleLocation, rests

    '''
        Goal
        Checks if given column in line of music is mostly comprised of black pixels with
        the exception of lines that are completely black. "Mostly black lines" are defined 
        as being between 50-80% black pixels. Used to differentiate measure lines or repeat
        lines from lines identified in the time signature, etc.

        Input
        image: opened PIL Image object
        x: column x-coordinate being tested
        topStaffRow: first staff line of current line of music
        bottomStaffRow: bottom staff line of current line of music

        Output
        Boolean value confirming whether or not the column is mostly black.
    '''
    def isMostlyBlack(self, image, x, topStaffRow, bottomStaffRow):
        blackCounter = 0
        width, _ = image.size
        if x < width:
            blackPixels, _ = self.countPixels(image, x, (topStaffRow, bottomStaffRow + 1, 1))
            blackCounter += blackPixels
        if (0.5*(bottomStaffRow - topStaffRow) <= blackCounter and 
            blackCounter <= 0.8*(bottomStaffRow - topStaffRow)):
            return True
        return False

    '''
        Goal
        Take a possible measure line and see if it is a measure line, or another line
        (ex. Lines that make a repeat, a note's stem, etc.)

        Input
        image: opened PIL Image object
        possMeasureLine: the column the possible measure line is in
        topStaffRow: first staff line of current line of music
        bottomStaffRow: bottom staff line of current line of music

        Output:
        Boolean value confirming whether or not the column is a valid measure line.
    '''
    def validMeasureLine(self, image, possMeasureLine, topStaffRow, bottomStaffRow):
        # isMostlyBlack() used to ignore junk lines found in time signature, cleff, etc.
        for i in range(1, 7):
            if (self.isMostlyBlack(image, possMeasureLine + i, topStaffRow, bottomStaffRow) or 
                self.isMostlyBlack(image, possMeasureLine - i, topStaffRow, bottomStaffRow)):
                return False
        if isSpecialNote(image, possMeasureLine, topStaffRow, bottomStaffRow):
            return False
        return True

    '''
        Goal
        Finds the columns that make up a repeat in a list of all possible measure lines.
        These groups of columns are called clusters.

        Input:
        measureLines: list of all columns of possible measure lines

        Output:
        Destructively modifies measureLines to remove any fake clusters, and returns
        completeClusterData, which is a list consisting of the columns that make up
        a cluster, and a tuple of the start and end indexes of the repeat in
        measureLines.
    '''
    def findRepeatClusters(self, measureLines):
        clusters = []
        newCluster = []
        fakeCluster = []
        completeClusterData = []
        for i in range(1, len(measureLines)-1):
            if measureLines[i] + 6 >= measureLines[i+1]:
                newCluster += [measureLines[i]] 
            elif measureLines[i] - 6 <= measureLines[i-1]: 
                newCluster += [measureLines[i]]
                if len(newCluster) > 5:
                    clusters.append(newCluster)
                else:
                    for i in newCluster[1:]:
                        fakeCluster += [i]
                newCluster = []
        if len(newCluster) >= 5:
            clusters.append(newCluster)
        else:
            fakeCluster += newCluster
        for fakeLine in fakeCluster:
            measureLines.remove(fakeLine)
        for cluster in clusters:
            startIdx = measureLines.index(cluster[0])
            endIdx = measureLines.index(cluster[-1])
            completeClusterData += [[cluster, (startIdx, endIdx)]]
        return completeClusterData

    '''
        Goal
        Determines whether a repeat is an opening or closing repeat and deletes the 
        multiple lines that make up the repeat based off of the earlier conclusion from
        measureLines.

        Input:
        repeatLines: a list consisting of the columns that make up a cluster, and a 
        tuple of the start and end indexes of the repeat in measureLines.
        measureLines: list of all columns of possible measure lines

        Output:
        The type of repeat (opening or closing), the pixel columns where the repeat 
        starts and ends, and a destructively modified measureLines with no lines
        corresponding to the repeat remaining within the list.
    '''
    def findRepeatData(self, repeatLines, measureLines):
        cluster = repeatLines[0]
        startIdx = repeatLines[-1][0]
        endIdx = repeatLines[-1][1]
        startPixel = cluster[0]
        endPixel = cluster[-1]
        for i in range(0, len(cluster) - 1):
            currLine = cluster[i]
            nextRepeatLine = cluster[i+1]
            halfWayPoint = cluster[len(cluster)//2]
            if currLine + 1 < nextRepeatLine:
                if currLine > halfWayPoint:
                    del measureLines[startIdx+1:endIdx+1]
                    return "OPEN", (startPixel, endPixel), measureLines
                else:
                    del measureLines[startIdx:endIdx + 1]
                    return "CLOSE", (startPixel, endPixel), measureLines

    '''
        Goal
        A wrapper function that removes the columns that make up a repeat from measureLines.

        Input
        measureLines: list of all columns of possible measure lines

        Output:
        Destructively modified measureLines, that only consists of all measure lines.
    '''
    def removeRepeatLines(self, measureLines):
        repeatClusters = self.findRepeatClusters(measureLines)
        repeatType = None
        repeatEndPts = None
        repeatData = []
        for repeat in repeatClusters:
            repeatType, repeatEndPts, measureLines = self.findRepeatData(repeat, measureLines)
            repeatData += [(repeatType, repeatEndPts)]
            # if both open + close repeats in same, line, it currently replaces the
            # data and only returns the data of the closing repeat, which messes up
            # the piece array's data
        return repeatData

    # identifies repeat in first measure, but won't work for repeat in 2nd measure
    '''if repeatEndPts[0] in measureLines:
    i = measureLines.index(repeatEndPts[0])
    if repeatType == "OPEN" and measureLines[i-1] == 0:
    measureLines.remove(repeat[0][0])'''

    '''
        Goal
        Given a line of music, to find all measures within that line.

        Input:
        imgPath: path of sheet music page.
        staffRows: list of all the rows that have a staffRow
        topMarginRow: the first row above the top staff line that also includes any 
        markings above the top staff line
        bottomMarginRow: the first row below the bottom staff line that also 
        includes any markings below the bottom staff line.

        Output:
        a list consisting of all the columns where a measure starts and ends
    '''
    def findMeasures(self, image, staffRows, topMarginRow, bottomMarginRow, lineNumber, condensedSections):
        #rgbImage = PIL.Image.open(self.fileName)
        #image = rgbImage.convert(mode = 'L')#.point(lambda x: 0 if x<200 else 255, '1')
        #image = rgbImage.convert(mode = "L")
        #image = ImageOps.grayscale(rgbImage)
        width, _ = image.size
        # need to case for first line first measure and rest of lines measure
        # since time sig doesn't appear in every like so need to change what this
        # is set to (2nd element 1st) once we get to second line
        if lineNumber == 0:
            edgeOfCondensed = condensedSections[-1][1]
        else:
            edgeOfCondensed = condensedSections[-2][1]
        measureLines = [edgeOfCondensed]
        columnList = []
        line = []
        targetMeasureLineLength = staffRows[4] - staffRows[0]
        
        for x in range(edgeOfCondensed + 1, width):
            blackPixels, whitePixels = self.countPixels(image, x, (staffRows[0], staffRows[-1] + 1, 1))
            if targetMeasureLineLength - 2 < blackPixels < targetMeasureLineLength + 2:
                if self.validMeasureLine(image, x, staffRows[0], staffRows[-1]):
                    measureLines += [x]
            columnList += [(x, blackPixels, whitePixels)]
        repeatData = self.removeRepeatLines(measureLines)
        for i in range(0, len(measureLines) - 1):
            measureBounds = (measureLines[i], measureLines[i+1], staffRows[0], staffRows[-1])
            marginBounds = (measureLines[i], measureLines[i+1] + 1, topMarginRow, bottomMarginRow)
            measureRepeatData = (None, None)
            for j in repeatData:
                if j[1][0] >= measureLines[i] and j[1][1] <= measureLines[i+1]:
                    measureRepeatData = j
            # fix measure number since i+1 doesn't work, gives measure number in terms of line
            line += [Measure(measureRepeatData, measureBounds, marginBounds, i+1, staffRows)]
        
        # measure cropping code
        for i in range(len(measureLines) - 1):
            measure = image.crop((measureLines[i], topMarginRow, measureLines[i+1] + 3, bottomMarginRow))
            text = f"line {lineNumber + 1} measure {i + 1} {os.path.basename(self.fileName)}"
            newPath = self.fileName.replace(os.path.basename(self.fileName), text)
            measure.save(newPath)
        return line

# store line number as well??
class Measure(object):
    def __init__(self, repeatData, measureBounds, marginBounds, measureNumber, staffRows):
        self.repeatType = repeatData[0]
        self.repeatCoord = repeatData[1]
        self.notes = None
        self.rests = None
        self.fullMeasureData = []
        self.measureBounds = measureBounds # left, right, top, bottom
        self.marginBounds = marginBounds # left, right, top, bottom
        self.measureNumber = measureNumber
        self.staffRows = staffRows
        # add line number??

    def makeFullMeasure(self):
        if self.rests != []:
            for rest in self.rests:
                for note in self.notes:
                    if rest.midCoord[0] < note.location[0]:
                        self.fullMeasureData += [rest]
                    elif rest.midCoord[0] > note.location[0]:
                        self.fullMeasureData += [note]
                if rest.midCoord[0] > note.location[0]:
                    self.fullMeasureData += [rest]
        else:
            self.fullMeasureData += self.notes

    '''def __repr__(self):
        return f"{self.measureNumber}"'''

#helper(width = 800, height = 800)

#scanning("Sheet Music Library/So Close Menken/page1.png")
#scanning("Sheet Music Library/Bohemian Rhapsody Mercury/page1.png")
#scanning("Sheet Music Library/Part Of Your World Menken/page1.png")
Parser("Sheet Music Library/Mary Had A Little Lamb Mason/page1.png")
Parser("Sheet Music Library/So Close Menken/page1.png")
#scanning("Sheet Music Library/Canon In D Pachelbel/page1.png")
'''scanning("Sheet Music Library/Moonlight Sonata Beethoven/page1.png")
scanning("Sheet Music Library/Nimrod Elgar/page1.png")
scanning("Sheet Music Library/Siciliano Bach/page1.png")
scanning("Sheet Music Library/We Are The World Jackson/page1.png"
scanning("Sheet Music Library/Ode To Joy Beethoven/page1.jpg") # doesn't work'''