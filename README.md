# Sheet Music Audio Generator

## Description: 
Scans a simple image of sheet music and generates audio playing the piece.

## Demo of Sheet Music Audio Generator
https://drive.google.com/file/d/1jmvAlokDSsQ7GE-yQMZwD74f6GPMSSM6/view?usp=sharing

## About the Development
I created this app over the course of a month as my term project for CMU's introductory CS course [15-112](https://www.kosbie.net/cmu/fall-19/15-112/index.html), which I self-taught. I love music, but I'm not the best at sightreading and conceptualizing how music passages should sound without hearing them first, so I thought I'd create an application that could help me hear what I was seeing on paper. This proved to be a hefty endeavor.

## Implementation and Challenges
1. Cropping the images: To identify the edges of each line and bar of music, I used a brute-force cropping mechanism that calculated the ratio of black pixels in a row to the total number of pixels in that row and used appropriate thresholding to select out appropriate reference points to base subsequent note-searching. This posed challenges with large amounts of noise being present in some images, which meant I had to fine-tune the thresholds used to ensure correct cropping. This was a nested process, where I first identified each line of music, then each horizontal staff line within each line, and the vertical bar lines of music.
   
2. Finding notes: Often when the program would crop the measures, it would identify the stems on each note as a measure line, so I had to create specific filtering for measure lines with exceptions built in for stems that touched both the top and bottom staff lines. Additionally, after identifying stems by the ratio of staff height they took up, I had to determine where the head, or bubble portion, of the note was. But luckily, I could rely on some notes having their head to the bottom left of the stem, and some have them to the top right. This was done by checking both stem endpoints and doing a circular expansion search up to a maximal radius. Whichever endpoint had more black pixels above a certain threshold would be chosen as the head for the note. This algorithm worked for both hollow and filled noteheads, which allowed us to determine the duration of the note, based on the density of the notehead. I also checked for dots next to notes, to ensure we extended the value of the note by 1.5, which is standard across music repertoire. This algorithm is not holistic, and cannot support all note types, but does support quarter notes, half notes, and dotted half notes.
  
3. Identifying the Pitch of a Note: So, at this point, I had identified all five staff lines, the note stems, and the noteheads. With this information, I was able to map the center of the noteheads to the closest staff line, and based on whether they were on or between staff lines I could determine the note's pitch and octave. Using this information, I could access the pitch in Hz from a dictionary I had hardcoded with the standard range of most instruments.
   
4. General Comments: Examples of unused data in the images included the title, the composer, the cleff, the key signature, the time signature, and repeats. Examples of noise were variations in the thickness of lines, spurious non-white pixels, etc.. These were often read as either staff lines, measures, or notes. Most of these were able to be ignored programmatically through various thresholds on local pixel density, or relative locations to other well-defined landmarks. Some were solved by having the user manually crop certain areas of the image.

## Further Development
1. Support for Multiple Image Types: Currently, the application only supports grayscale images, and attempts to diversify the acceptable file types by converting them to grayscale have been unsuccessful. Further research to diagnose the issue is required to support more file types.
   
2. Improve Audio Quality: The audio generated is currently just a sin wave, rather than an imitation instrument. I would like to change how the sound is generated so that it sounds like a piano and more natural. 

3. Improve Consistency: The note identification is inconsistent in its accuracy, so a more accurate method of identifying the bubbles would help the quality of the project.
