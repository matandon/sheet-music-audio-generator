Sheet Music Audio Generator

Description: Scans a simple image of sheet music and generates audio of what it sounds like.

About the Development: I created this project as my term project for CMU's 15-112 course, which I self-taught. I love music, but I'm horrible at sightreading and conceptualizing how things should sound without hearing them first, so I thought I'd create an application that could help me hear what things are supposed to sound like. This proved to be a hefty endeavor.

Challenges:
1. Cropping the images: To read each image, I used a brute-force cropping mechanism that calculated the ratio of black pixels in a row to the total number of pixels in that row and used different thresholds to identify the edges of each line of music and each bar of music. This posed challenges with large amounts of noise being present in some images, which meant I had to fine-tune the thresholds used to ensure correct cropping.
2. Finding notes: Often when the program would crop the measures, it would identify the stems on each note as a measure line, so I had to create specific filtering for measure lines with exceptions built in for stems that touched both the top and bottom staff lines. Additionally, after finding all the stems by percent of black pixels, I had to determine where the "bubble" of the note was, as some notes have their bubble to the left of the stem, and some have them to the right. This was done by checking for white pixels on the edges of where the bubble should be. This allows the note to still be identified even if it is not filled, like a half note.
3. Identifying the Pitch of a Note: So, at this point, I had the information of all five staff lines, the stem, and the bubble. With this information, I was able to hardcode the note names on the staff to the pitches in Hz which made a note library, and identify what an identified note in the image's pitch was relative to the staff lines.
4. General Denoising: Examples of noise in the images included the title, the composer, the cleff, the key signature, the time signature, repeats, and variations in the thickness of lines. These were often read as either staff lines, measures, or notes. Most of these were able to be ignored programmatically through various thresholds on the amount of pixels, or the location in relation to other markings. Some were solved by having the user manually crop certain areas of the image.

Further Development:
1. Support for Multiple Image Types: Currently, the application only supports grayscale images, and attempts to diversify the acceptable file types by converting them to grayscale have been unsuccessful. Further research to diagnose the issue is required to support more file types. 
2. Improve Audio Quality: The audio generated is currently just a sin wave, rather than an imitation instrument. I would like to change how the sound is generated so that it sounds like a piano and more natural. 
3. Improve Consistency: The note identification is inconsistent in its accuracy, so a more accurate method of identifying the bubbles would help the quality of the project.

Demo of Sheet Music Audio Generator: https://drive.google.com/file/d/1jmvAlokDSsQ7GE-yQMZwD74f6GPMSSM6/view?usp=sharing
