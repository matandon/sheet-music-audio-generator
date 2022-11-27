from PIL import Image
import PIL
import os
from tkinter import *
from cmu_112_graphics import *
from pysine import sine
import time
#from final_audio_code import *


pitchMap = {}
pitchMap["G3"] = 195.9977
pitchMap["G#3"] = 207.6523
pitchMap["Ab3"] = 207.6523
pitchMap["A3"] = 220.0000
pitchMap["A#3"] = 233.0819
pitchMap["Bb3"] = 233.0819
pitchMap["B3"] = 246.9417
pitchMap["C4"] = 261.6256 
pitchMap["C#4"] = 277.1826
pitchMap["Db4"] = 277.1826
pitchMap["D4"] = 293.6648
pitchMap["D#4"] = 311.1270
pitchMap["Eb4"] = 311.1270
pitchMap["E4"] = 329.6276
pitchMap["E#4"] = 349.2282
pitchMap["Fb4"] = 329.6276
pitchMap["F4"] = 349.2282
pitchMap["F#4"] = 369.9944
pitchMap["Gb4"] = 369.9944
pitchMap["G4"] = 391.9954
pitchMap["G#4"] = 415.3047
pitchMap["Ab4"] = 415.3047
pitchMap["A4"] = 440.0000
pitchMap["A#4"] = 466.1638
pitchMap["Bb4"] = 466.1638 
pitchMap["B4"] = 493.8833
pitchMap["C5"] = 523.2511
pitchMap["C#5"] = 554.3653 
pitchMap["Db5"] = 554.3653 
pitchMap["D5"] = 587.3295 
pitchMap["D#5"] = 622.2540
pitchMap["Eb5"] = 622.2540
pitchMap["E5"] = 659.2551 
pitchMap["E#5"] = 698.4565 
pitchMap["Fb5"] = 659.2551
pitchMap["F5"] = 698.4565
pitchMap["F#5"] = 739.9888
pitchMap["Gb5"] = 739.9888
pitchMap["G5"] = 783.9909

trebleStaffNotes = ["E4", "D4", "G4", "F4", "B4", "A4", "D5", "C5", "F5", "E5"]
belowStaffNotes = ["C4", "B3", "A3", "G3"]
#trebleStaffNotes = "EDGFBADCFE"
#belowStaffNotes = "CBAG"

leftBubblePitches = "BAGFE" # add below bottom staff D?
rightBubblePitches = "FEDCB" # add above staff G

'''
    Goal
    Iterates over every measure and builds up a list of all notes present in the
    piece

    Input
    image: opened PIL Image object
    measureArray: 2d list of measure objects organized by line

    Output
    pieceInfo is a 2d list with the position of every note in the piece
'''
# organize pieceInfo by line instead of j having stray measures??
def findNotes(image, measureArray, extraStaffRows, condensedSections):
    pieceInfo = []
    rests = []
    for line in measureArray:
        lineInfo = []
        lineRests = []
        for measure in line:
            measureNotes, measureRests = [], []
            val = findMeasureNotes(image, measure, extraStaffRows)
            #val = findMeasureNotes(image, measureArray[2][3], extraStaffRows)
            notes = val[0]
            rests = val[1]
            for note in notes:
                measureNotes += [Note(note, 1)]
            
            rest = []
            sortedRests = []
            for column in range(len(rests)):
                if rest == []:
                    rest += [rests[column]]
                elif rest[-1][0] + 10 > rests[column][0]:
                    rest += [rests[column]]
                else:
                    sortedRests += [rest]
                    rest = []
            if rest != []:
                sortedRests += [rest]

            for rest in sortedRests:
                if rest != []:
                    measureRests += [Rest(rest, line.index(measure), measureArray.index(line))]
            measure.notes = measureNotes
            measure.rests = measureRests
            lineInfo += [val[0]]
            lineRests += [val[1]]
        pieceInfo += [lineInfo]
        rests += [lineRests]
    piece = Piece(measureArray)
    bubbleLocation = findBubble(image, pieceInfo, measureArray)
    findDuration(image, bubbleLocation, measureArray, extraStaffRows)
    piecePitches = findNotePitch(pieceInfo, measureArray, extraStaffRows, bubbleLocation)
    print(piecePitches)
    for lineIndex in range(len(piecePitches)):
        for measureIndex in range(len(piecePitches[lineIndex])):
            #(piecePitches[lineIndex][measureIndex])
            for noteIndex in range(len(piecePitches[lineIndex][measureIndex])):
                piece.piece[lineIndex][measureIndex].notes[noteIndex].pitch = piecePitches[lineIndex][measureIndex][noteIndex] 
    # playing sound code
    for line in piece.piece:
        for measure in line:
            measure.makeFullMeasure()
            for element in measure.fullMeasureData:
                if isinstance(element, Note):
                    #print(element.pitch, element.noteValue)
                    sine(frequency = pitchMap[element.pitch], duration = element.noteValue)
                else:
                    time.sleep(1.0)
                '''    sound = playPiece(pitchMap[element.pitch], measure.fullMeasureData.index(element), line.index(measure), piece.piece.index(line))
                    note = sound.play(0.5)
                else:
                    sound = playPiece(pitchMap[element.pitch], measure.fullMeasureData.index(element), line.index(measure), piece.piece.index(line))
                    note = sound.play(0.25)'''
                
    return pieceInfo, bubbleLocation, rests

def findDuration(image, bubbleLocations, measureArray, extraStaffRows):
    bubbleWidth = measureArray[0][0].staffRows[1] - measureArray[0][0].staffRows[0]
    filled = None
    durations = []
    print(bubbleLocations, len(bubbleLocations))
    for line in bubbleLocations:
        for measure in line:
            for noteInfo in measure:
                if noteInfo[2] == "LEFT":
                    bubbleBound = image.getpixel((noteInfo[0] - bubbleWidth, noteInfo[1]))
                    if bubbleBound != 255:
                        filled = True
                    else:
                        filled = False
                else:
                    bubbleBound = image.getpixel((noteInfo[0] + bubbleWidth, noteInfo[1]))
                    if bubbleBound != 255:
                        filled = True
                    else:
                        filled = False
                        
                if filled:
                    durations += [1]
                else:
                    # for now hardcoded to 3 beats, fix later with added check for dot in dotted half note.
                    std = 2
                    if checkIfDottedNote(image, noteInfo, extraStaffRows, bubbleWidth):
                        durations += [1.5*std]
                    else:
                        durations += [2]

    print(len(durations))
    count = 0
    for line in measureArray:
        for measure in line:
            for note in measure.notes:
                count += 1
                if durations != []:
                    note.noteValue = durations.pop(0)
    print(count)
    '''else:
                    print(note)'''
    
def checkIfDottedNote(image, noteInfo, extraStaffRows, bubbleWidth):
    column, stemBound, _ = noteInfo
    notStaffLine = True
    for i in range(bubbleWidth):
        for j in range(bubbleWidth):
            pixelColor = image.getpixel((column + i, stemBound - j))
            if pixelColor == 0:
                for (staffRow, extraRows) in extraStaffRows.items():
                    if stemBound - j == staffRow or stemBound - j in extraRows:
                        notStaffLine = False
                
                if notStaffLine:
                    return True
    return False

def findBubble(image, pieceInfo, measureArray):
    #piecePitches = []
    bubbleLocation = []
    for i in range(len(pieceInfo)):
        #linePitches = []
        lineBubbleLocation = []
        for j in range(len(pieceInfo[i])):
            measureBubbleLocation = []
            #measurePitches = []
            #staffRows = measureArray[2][1].staffRows
            staffRows = measureArray[i][j].staffRows
            bubbleWidth = staffRows[1] - staffRows[0]
            #for note in pieceInfo[2][1]:
            for note in pieceInfo[i][j]:
                #foundLeftBubble = False
                #foundRightBubble = False
                column, stemStart, stemEnd = note
                print(note)
                #pitch = None

                bubbleBound = image.getpixel((column - bubbleWidth//2, stemEnd))
                if bubbleBound != 255:
                    #foundLeftBubble = True
                    measureBubbleLocation += [(column, stemEnd, "LEFT")]
                    continue
                

                bubbleBound = image.getpixel((column + bubbleWidth//2, stemStart - 2))
                if column == 311:
                    print(bubbleBound, column + bubbleWidth//2, stemStart - 2)
                if bubbleBound != 255:
                    #foundRightBubble = True
                    measureBubbleLocation += [(column, stemStart - 5, "RIGHT")]
            
            lineBubbleLocation += [measureBubbleLocation]
        bubbleLocation += [lineBubbleLocation]
    #print("piecePitches:", piecePitches)
    return bubbleLocation

def findBelowStaffNotePitch(stemEnd, i, lastStaffLine):
    pitch = None
    for pitchIdx in range(len(belowStaffNotes)):
        if pitchIdx % 2 == 0:
            onCheck = True
        else:
            onCheck = False

        ledgerLine = lastStaffLine + (i*(pitchIdx + 1))
        
        if onCheck:
            if ledgerLine - 5 <= stemEnd <= ledgerLine + 5:
                pitch = belowStaffNotes[pitchIdx]
                break
        else:
            if ledgerLine < stemEnd < ledgerLine + i:
                pitch = belowStaffNotes[pitchIdx]
                break
    print("here", pitch)
    return pitch

def findNotePitch(pieceInfo, measureArray, extraStaffRows, bubbleLocation):
    piecePitches = []
    for i in range(len(pieceInfo)):
        linePitches = []
        for j in range(len(pieceInfo[i])):
            measurePitches = []
            #staffRows = measureArray[2][2].staffRows
            staffRows = measureArray[i][j].staffRows
            staffLineWidth = staffRows[1] - staffRows[0]
            for note in pieceInfo[i][j]:
            #for note in pieceInfo[2][2]:
                belowCheck = False
                column, stemStart, stemEnd = note
                staffRowIdx = len(staffRows) - 1
                pitch = None
                stemBoundToCheck = stemEnd
                switchIdx = 6
                for pitchIdx in range(len(trebleStaffNotes)):
                    '''if pitchIdx >= switchIdx:
                        stemBoundToCheck = stemStart
                    elif trebleStaffNotes[pitchIdx] == "B4":
                        stemBoundToCheck = stemStart
                    elif trebleStaffNotes[pitchIdx] == "A4":
                        stemBoundToCheck = stemEnd'''
                    
                    if bubbleLocation[i][j][pieceInfo[i][j].index(note)][2] == "LEFT":
                        stemBoundToCheck = stemEnd
                    else:
                        stemBoundToCheck = stemStart

                    if pitchIdx % 2 == 0:
                        belowCheck = False
                        if pitchIdx != 0:
                            staffRowIdx -= 1
                    else:
                        belowCheck = True

                    '''print("Below Check: ", belowCheck)
                    print("column, stemStart, stemEnd: ", column, stemStart, stemEnd)
                    print("stemBoundToCheck: ", stemBoundToCheck)
                    print("staffRowIdx: ", staffRowIdx)
                    print("pitch: ", pitch)
                    print("pitchIdx: ", pitchIdx)
                    print("trebleStaffnotes[pitchIdx]: ", trebleStaffNotes[pitchIdx])
                    print("staffRows: ", staffRows)
                    print("\n\n")'''
                    
                    largestStaffPixelLine = findMaxArg(staffRows[staffRowIdx], extraStaffRows)

                    if belowCheck:
                        if largestStaffPixelLine <= stemBoundToCheck < largestStaffPixelLine + staffLineWidth:
                            pitch = trebleStaffNotes[pitchIdx]
                            break
                    else:
                        if staffRows[staffRowIdx] - 2 <= stemBoundToCheck <= largestStaffPixelLine + 2:
                            pitch = trebleStaffNotes[pitchIdx]
                            break
                        elif stemBoundToCheck >= largestStaffPixelLine + staffLineWidth:
                            pitch = findBelowStaffNotePitch(stemEnd, staffLineWidth, largestStaffPixelLine)
                            break
                    
                if pitch != None:
                    measurePitches += [pitch]
                '''elif stemEnd >= largestStaffPixelLine + staffLineWidth:
                    pitch = 
                    if pitch != None:
                        measurePitches += [pitch]'''
            linePitches += [measurePitches]
        piecePitches += [linePitches]
    return piecePitches

'''
    Goal
    Identify the position of every note in a given measure

    Input
    image: opened PIL Image object
    measure: instance of the measure object

    Output
    list of tuples of each note's position, with each tuple containing the 
    column the stem is located in, and the rows each stem starts and ends in
'''
def findMeasureNotes(image, measure, extraStaffRows):
    # +5 and -5 to ignore measure lines being counted as stems
    startPixel = measure.measureBounds[0] + 5
    endPixel = measure.measureBounds[1] - 5
    # topStaffRow, bottomStaffRow = measure.measureBounds[2], measure.measureBounds[3]
    minStemLength = measure.staffRows[2] - measure.staffRows[0]
    maxStemLength = measure.staffRows[-1] - measure.staffRows[0]
    notes = []
    possRests = []
    # to ignore the repeat's lines from being counted, 
    # +5 and -5 to ignore the gap repeat line being counted as a stem
    if measure.repeatType == "OPEN":
        startPixel = measure.repeatCoord[1] + 5
    elif measure.repeatType == "CLOSE":
        endPixel = measure.repeatCoord[0] - 5
    
    margin = (measure.staffRows[1] - measure.staffRows[0])//3

    #for column in range(1):
    for column in range(startPixel, endPixel):
        blackPixels = findLongestRun(image, column, measure.staffRows)
        if (minStemLength - margin <= blackPixels <= maxStemLength + margin):
            # find entire stem
            startRow, endRow = findStem(image, column, measure.staffRows, measure.marginBounds, extraStaffRows)
            if startRow != None and endRow != None:
                if not isRest(image, column, measure.staffRows, startRow, endRow):
                    if notes != [] and notes[-1][0] + 3 >= column:
                        prevLine = notes.pop()
                        notes += [(prevLine[0], min(prevLine[1], startRow), max(prevLine[2], endRow))]
                    else:
                        notes += [(column, startRow, endRow)]
                else:
                    possRests += [(column, startRow, endRow)]
    return (notes, possRests)

def isRest(image, column, staffRows, startRow, endRow):
    cBulkRegion = staffRows[2] - staffRows[1]   
    cBlackPixels = 0
    gBulkRegion = (staffRows[3] - staffRows[2])//2
    gBlackPixels = 0
    for i in range(3, cBulkRegion//2):
        cBlackPixels += countPixels(image, column + i, (staffRows[1], staffRows[2], 1))[0]
        cBlackPixels += countPixels(image, column - i, (staffRows[1], staffRows[2], 1))[0]
    for i in range(3, gBulkRegion):
        gBlackPixels += countPixels(image, column - i, (staffRows[2] + gBulkRegion, staffRows[3], 1))[0]
    if cBlackPixels > 30 and gBlackPixels > 30:
        return True
    return False

'''
    Goal
    Find the longest stretch of continuous black pixels, ie. run, in a given column

    Input
    image: opened PIL Image object
    column: x coordinate represented as an integer
    staffRows: list of rows representing the staff lines of the measure the 
    column is contained in

    Output
    the length of the longest run found in the column
'''
def findLongestRun(image, column, staffRows):
    blackPixels = []
    runsLen = []
    for y in range(staffRows[0], staffRows[4] + 1):
        color = None
        pixelVal = image.getpixel((column,y))
        # 1st case is in case the image is a multiband image, and the second
        # is for images that are greyscale. All current cases are greyscale,
        # and I'm not sure if it actually works on multiband images.
        if type(pixelVal) != tuple:
            color = (pixelVal, pixelVal, pixelVal)
        else:
            color = pixelVal
        if color != (255, 255, 255):
            blackPixels += [y]
        elif color == (255, 255, 255):
            runsLen += [len(blackPixels)]
            blackPixels = []
    if blackPixels != []:
        runsLen += [len(blackPixels)]
    return max(runsLen)

def onStaffRows(i, staffRows, extraStaffRows): 
    maxArg = findMaxArg(staffRows[0], extraStaffRows)
    if staffRows[0] <= i <= maxArg:
        return True
    
    maxArg = findMaxArg(staffRows[1], extraStaffRows)
    if staffRows[1] <= i <= maxArg:
        return True

    maxArg = findMaxArg(staffRows[2], extraStaffRows)
    if staffRows[2] <= i <= maxArg:
        return True
    return False

def findMaxArg(staffRow, extraStaffRows):
    maxArg = None
    if extraStaffRows[staffRow] == []:
        maxArg = staffRow
    else:
        maxArg = max(extraStaffRows[staffRow])
    return maxArg

'''
    Goal
    Find the start and end rows of a note stem present in a column.

    Input
    image: opened PIL Image object
    column: x coordinate represented as an integer
    staffRows: list of rows representing the staff lines of the measure the 
    column is contained in
    boundRows: list of the left, right, top, and bottom bounds of the measure
    that allow for all markings to be included.

    Output
    The start and end rows of the note stem in the column given
'''
def findStem(image, column, staffRows, boundRows, extraStaffRows):
    currPixel = image.getpixel((column, staffRows[0]))
    nextPixel = image.getpixel((column, staffRows[0] + 1))
    prevPixel = image.getpixel((column, staffRows[0] - 1))
    topBound = None
    bottomBound = None

    if nextPixel <= 10:
        #case for top of stem above top staff line
        if prevPixel <= 10:
            i = staffRows[0] - 1
            while i > boundRows[2]:
                currPixel = image.getpixel((column, i))
                if currPixel == 255:
                    topBound = i
                    break
                else:
                    i -= 1
        # case for top of stem line exactly on top staff line
        else:
            topBound = staffRows[0]
    #case for top of stem line in staff lines
    else:
        i = staffRows[0] + 1
        while i <= staffRows[2] + 5:
            currPixel = image.getpixel((column, i))
            if currPixel != 255 and not onStaffRows(i, staffRows, extraStaffRows): #i not in staffRows:
            #if currPixel <= 100 and i not in staffRows:
                topBound = i
                break
            else:
                i += 1
    if topBound != None:
        j = topBound + 1
        while True:
            currPixel = image.getpixel((column, j))
            if currPixel == 255:
                bottomBound = j
                break
            elif j == boundRows[3]:
                bottomBound = j
                break
            else:
                j += 1
    
    return topBound, bottomBound

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
def countPixels(image, x, yIterateOver):
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
    Differentiates between a note line that goes through all 5 staff lines ie. a
    special note, and a measure line, by checking for the note head. The check 
    also identifies lines near key changes and slurs as speacial notes, due to 
    the pixel density of each symbol registering as a note head.

    Input:
    image: opened PIL Image object
    noteLine: column being checked
    topStaffRow: first staff line of current line of music
    bottomStaffRow: bottom staff line of current line of music

    Output:
    boolean value confirming whether or not the given column is a special note
'''
def isSpecialNote(image, noteLine, topStaffRow, bottomStaffRow):
    blackCounter = 0
    for x in range(1, 11):
        for y in range(1, 11):
            # only check staff lines because any line being passed in here will
            # go through all 5 staff lines, and so part of its bubble must be 
            # above or below the staff line, therefore can just check from top
            # and bottom staff lines
            width, height = image.size
            if noteLine - x >= 0 and noteLine + x < width:
                pixelVal = image.getpixel((noteLine - x, bottomStaffRow + y))

                if type(pixelVal) != tuple:
                    color = (pixelVal, pixelVal, pixelVal)
                else:
                    color = pixelVal

                if color != (255, 255, 255):
                    blackCounter += 1
                pixelVal = image.getpixel((noteLine + x, topStaffRow - y))

                if type(pixelVal) != tuple:
                    color = (pixelVal, pixelVal, pixelVal)
                else:
                    color = pixelVal

                if color != (255, 255, 255):
                    blackCounter += 1
    if blackCounter >= 25:
        return True
    return False

class Rest(object):
    def __init__(self, restData, measureNumber, lineNumber):
        i = len(restData)//2
        self.midCoord = restData[i] #tuple of column, start, end
        self.measureNumber = measureNumber
        self.lineNumber = lineNumber

    def __eq__(self, other):
        if isinstance(other, Rest):
            if (self.restMidCoord == other.restMidCoord and 
                self.measureNumber == other.measureNumber and
                self.lineNumber == other.lineNumber):
                return True
        return False

    def __repr__(self):
        return f"({self.measureNumber})" 

class Note(object):
    def __init__(self, location, noteValue):
        self.pitch = None #letter pitch + octave as string
        self.location = location #tuple of column, start, end
        self.noteValue = noteValue #number of beats it gets in the measure

    def __repr__(self):
        return f"{self.pitch, self.noteValue}"

class Piece(object):
    def __init__(self, measureArray):
        self.piece = measureArray
        self.timeSig = None
        self.tempo = None

