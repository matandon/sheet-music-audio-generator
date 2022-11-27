from cmu_112_graphics import *
from tkinter import *

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
        # add line number?

    def makeFullMeasure(self):
        if self.rests != []:
            for rest in self.rests:
                for note in self.notes:
                    if rest.midCoord[0] < note.location[0]:
                        self.fullMeasureData += [rest]
                    elif rest.midCoord[0] > note.location[0]:
                        self.fullMeasureData += [note]
                if rest not in self.fullMeasureData:
                    self.fullMeasureData += [rest]
        else:
            self.fullMeasureData += self.notes

    def __repr__(self):
        return f"{self.measureNumber}"

class Rest(object):
    def __init__(self, restData, measureNumber, lineNumber):
        i = len(restData)//2
        self.restMidCoord = restData[i] #tuple of column, start, end
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
    def __init__(self, pitch, location, noteValue):
        self.pitch = pitch #letter pitch + octave as string
        self.location = location #tuple of column, start, end
        self.noteValue = noteValue #number of beats it gets in the measure

class Piece(object):
    def __init__(self, measureArray):
        self.piece = measureArray
        self.timeSig = None
        self.tempo = None
