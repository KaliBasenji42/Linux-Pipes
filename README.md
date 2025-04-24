# General

Pipe connect game made for Linux terminal, uses Python.

## Screenshots
### Home Screen
![Screenshot 2025-04-23 134641](https://github.com/user-attachments/assets/e6ac81c8-c00d-47ba-a8e3-fee8da091fb4)
### Game
![Screenshot 2025-04-23 134726](https://github.com/user-attachments/assets/f823eab4-08a4-4494-94b2-a4d2d604c1c2)
### Game - Win
![Screenshot 2025-04-23 134811](https://github.com/user-attachments/assets/07470e81-9af9-4126-bd47-f07ecdb45ef0)

# Printed Documentation

<pre style="overflow-x: scroll;">
"WASD" to navigate
"Q" & "E" to rotate pipes
"F" to select
"X" to quit
"R" to show record
When editing option, type number, then press [Enter] to set
</pre>

# How to Play

## Goal:

Connect the piped RGB values from the sources (╻) at the top to the drains (╹) at the bottom, so that the drains' demand is met (or exceeded). Do this by rotating pipes. Note: Case does not matter for inputs.

## Instructions

1. Set the options (optional)
    1. Use "W" and "S" to navigate
    2. Select ("F") the target option when it is highlighted
    3. Type the number to set (it will make a number out of the numeric characters, and then clamp it. So it will always make a number no matter the characters, but might make a weird one if you try this)
    4. Press \[Enter\]
2. Select ("F") "PLAY" to start
3. Move around using "WASD"
    * The info bar will show the selected pipe's RGB contents, if it is a drain it will show the demand aswell: "{Supply} / {Demand}" for each RGB value
4. Rotate pipes using "Q" and "E"
5. Supply each demand of each drain to win
    * Green means it is supplied, see Game - Win screenshot
6. To exit to the home screen press "X"
7. To exit the program press "X" again, or press "R" to show the record

# File Structure

## record.txt

<pre style="overflow-x: scroll;">
Grid Width: {#}, Grid Height: {#}, Sources: {#}, Drains: {#}
  Least Pipes: {#}
  Least Moves: {#}
  Best Time: {#.##}s
{Scores for other options...}
</pre>

EX:

<pre style="overflow-x: scroll;">
Grid Width: 10, Grid Height: 5, Sources: 3, Drains: 3
  Least Pipes: 36
  Least Moves: 3
  Best Time: 4.64s
Grid Width: 20, Grid Height: 10, Sources: 3, Drains: 5
  Least Pipes: 107
  Least Moves: 10
  Best Time: 23.33s
</pre>

## \_\_main\_\_.py

<pre style="overflow-x: scroll;">
Imports & Logging Setup

Variables

Classes

Functions

Pre-Loop (try render)

Main Loop (in try) {
  
  Detect Key / Input
  
  Behavior (of pipe, sources, & drains)
  
  Record (if win == True)
  
  Render
  
}

except:
  Log & Print Error
</pre>