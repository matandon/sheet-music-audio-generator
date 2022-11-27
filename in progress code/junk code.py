# from findBubble in note_id
'''
#assert(foundLeftBubble != foundRightBubble)
if foundLeftBubble:
                    staffRowIdx = 1
                    belowCheck = False
                    for pitchIdx in range(len(leftBubblePitches)):
                        if pitchIdx % 2 == 0:
                            belowCheck = False
                            staffRowIdx += 1
                        else:
                            belowCheck = True
                        
                        if belowCheck:
                            if staffRows[staffRowIdx] + 3 < stemEnd < staffRows[staffRowIdx + 1] - 3:
                                pitch = leftBubblePitches[pitchIdx]
                                break
                        else:
                            if staffRows[staffRowIdx] - 3 <= stemEnd <= staffRows[staffRowIdx] + 3:
                                pitch = leftBubblePitches[pitchIdx]
                                break

                elif foundRightBubble:
                    staffRowIdx = -1
                    belowCheck = False
                    for pitchIdx in range(len(rightBubblePitches)):
                        if pitchIdx % 2 == 0:
                            belowCheck = False
                            staffRowIdx += 1
                        else:
                            belowCheck = True

                        if belowCheck:
                            if staffRows[staffRowIdx] + 3 <= stemStart <= staffRows[staffRowIdx + 1] - 3:
                                pitch = rightBubblePitches[pitchIdx]
                                break
                        else:
                            if staffRows[staffRowIdx] - 3 <= stemStart <= staffRows[staffRowIdx] + 3:
                                pitch = rightBubblePitches[pitchIdx]
                                break               
                measurePitches += [pitch]
            linePitches += [measurePitches]
        piecePitches += [linePitches]'''


'''#assert(foundLeftBubble != foundRightBubble)
                if foundLeftBubble:
                    staffRowIdx = 1
                    belowCheck = False
                    for pitchIdx in range(len(leftBubblePitches)):
                        if pitchIdx % 2 == 0:
                            belowCheck = False
                            staffRowIdx += 1
                        else:
                            belowCheck = True
                        
                        if belowCheck:
                            if staffRows[staffRowIdx] + 3 < stemEnd < staffRows[staffRowIdx + 1] - 3:
                                pitch = leftBubblePitches[pitchIdx]
                                break
                        else:
                            if staffRows[staffRowIdx] - 3 <= stemEnd <= staffRows[staffRowIdx] + 3:
                                pitch = leftBubblePitches[pitchIdx]
                                break

                elif foundRightBubble:
                    staffRowIdx = -1
                    belowCheck = False
                    for pitchIdx in range(len(rightBubblePitches)):
                        if pitchIdx % 2 == 0:
                            belowCheck = False
                            staffRowIdx += 1
                        else:
                            belowCheck = True

                        if belowCheck:
                            if staffRows[staffRowIdx] + 3 <= stemStart <= staffRows[staffRowIdx + 1] - 3:
                                pitch = rightBubblePitches[pitchIdx]
                                break
                        else:
                            if staffRows[staffRowIdx] - 3 <= stemStart <= staffRows[staffRowIdx] + 3:
                                pitch = rightBubblePitches[pitchIdx]
                                break               
                measurePitches += [pitch]
            linePitches += [measurePitches]
        piecePitches += [linePitches]'''