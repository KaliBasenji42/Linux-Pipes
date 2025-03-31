### Imports ###

import sys
import os
import random
import time
import termios
import tty
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s: %(message)s',
    filename='app.log'
)

### Variables ###

run = True # Run Main Loop
mode = 0 # Mode (0 = Home, 1 = Game)
selPos = (0, 0) # Selected position (x, y)
renderHeight = 0 # Height of the render (for clearing the screen)

FPS = 20 # FPS

options = { # Options
  "Grid Width": 10, # Game Grid Width
  "Grid Height": 5, # Game Grid Height
  "Sources": 3, # Number of sources
  "Drains": 3, # Number of drains
}

grid = [] # Game Grid, containing all pipes
unresolved = [] # Unresolved pipes (for a selective flood algorithm)

characters = "━┃┏┓┗┛┣┫┳┻╋" # Characters for the pipes
charKey = { # Character Key: "chr": (hasTop, hasRight, hasBottom, hasLeft, "allRotations")
  "━": (False, True, False, True, "━┃━┃"),
  "┃": (True, False, True, False, "┃━┃━"),
  "┏": (False, True, True, False, "┏┓┛┗"),
  "┓": (False, False, True, True, "┓┛┗┏"),
  "┗": (True, True, False, False, "┗┏┓┛"),
  "┛": (True, False, False, True, "┛┗┏┓"),
  "┣": (True, True, True, False, "┣┳┫┻"),
  "┫": (True, False, True, True, "┫┻┣┳"),
  "┳": (False, True, True, True, "┳┫┻┣"),
  "┻": (True, True, False, True, "┻┣┳┫"),
  "╋": (True, True, True, True, "╋╋╋╋"),
}

homeScreenBase = [ # What to print when starting home screen
  '╷   ┬ ╷ ╷ ╷ ╷ ╷ ╷   ┏━┓ ┳ ┏━┓ ┏━╸ ┏━╸',
  '│   │ │╲│ │ │  ╳    ┣━┛ ┃ ┣━┛ ┣━╸ ┗━┓',
  '╰─╴ ┴ ╵ ╵ ╰─╯ ╵ ╵   ╹   ┻ ╹   ┗━╸ ╺━┛',
  '',
  '"WASD" to navigate',
  '"Q" & "E" to rotate pipes',
  '"F" to select',
  '"X" to quit',
  '',
  'PLAY',
  '',
  'OPTIONS:',
]
homeScreenSelPos = ( # Selectable positions on the home screen
  9, # Play
  12, # Grid Width
  13, # Grid Height
  14, # Sources
  15, # Drains
)

### Classes ###

class pipe:
  
  def __init__(self, chr, x, y):
    
    # Variables
    
    self.pos = (x, y) # Position
    self.chr = chr # Character
    self.sources = [] # Sources the pipe is connected to
    self.color = [0, 0, 0] # Color content (based on the sources)
    
  

class source:
  
  def __init__(self, x, color):
    
    # Variables
    
    self.x = x # X position
    self.color = color # Color content
    
    self.chr = "╻" # Character
    
  
sources = [] # List of all sources

class drain:
  
  def __init__(self, x, demand):
    
    # Variables
    
    self.x = x # X position
    self.demand = demand # Color demanded
    
    self.color = [0, 0, 0] # Color content
    self.chr = "╹" # Character
    
  
drains = [] # List of all drains

### Functions ###

def strToPosInt(string): # Converts string to positive integer, returns 0 if no number, ignores non-numeric characters
  
  numStr = ''
  
  for i in range(len(string)):
    if string[i].isnumeric(): numStr = numStr + string[i]
  
  if len(numStr) == 0: return 0
  
  else: return int(numStr)
  

def getKey():
  
  fd = sys.stdin.fileno()
  old = termios.tcgetattr(fd) # Old terminal settings
  
  try:
    tty.setraw(sys.stdin.fileno()) # Terminal to raw (non-conical & no echo)
    chr = sys.stdin.read(1) # Get char entered
    return chr
  finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old) # Restore terminal settings
  

def generateGame(): # Builds the grid
  
  global options
  
  # Create Sources
  
  # Create Drains
  
  # Create Paths (don't forget to randomize pipe rotations)
  
  # Fill rest with random pipes
  
  pass
  

def render(): # Renders the Screen
  
  # Clear screen
  
  global renderHeight, selPos, homeScreenBase, homeScreenSelPos
  
  for i in range(renderHeight):
    print('\033[K\033[F', end='')
  
  # Home Screen
  
  if mode == 0:
    
    homeScreen = [] # Initiate array of strings to be printed
    for val in homeScreenBase: homeScreen.append(val) # Add homeScreenBase
    for key, value in options.items(): homeScreen.append(key + ': ' + str(value)) # Add Options
    
    for i in range(len(homeScreen)):
      
      selected = False # Selected position
      
      if i == homeScreenSelPos[selPos[1]]: selected = True
      
      # Highlight selected position
      if selected: print('\033[7m' + homeScreen[i] + '\033[0m')
      else: print(homeScreen[i])
      
    
    renderHeight = len(homeScreen) # Set render height
    
  
  # Game Screen
  
  else:
    
    # Info bar
    
    # Sources
    
    # Grid
    
    # Drains
    
    # Message bar
    
    pass
    
  

### Pre Loop ###

render() # Initial render

### Main Loop ###

while run:
  
  ### Time/FPS ###
  
  time.sleep(1/FPS)
  
  ### Detect Key ###
  
  key = getKey().lower()
  
  # Escape
  
  if key == 'x' and mode == 0: run = False
  
  elif key == 'x' and mode == 1:
    
    selPos = (0, 0)
    grid = [] # Reset Vars
    
    mode = 0 # Mode set to Home
    
  
  # Navigation
  
  elif key == 'a':
    selPos = (selPos[0] - 1, selPos[1])
  elif key == 'd':
    selPos = (selPos[0] + 1, selPos[1])
  elif key == 'w':
    selPos = (selPos[0], selPos[1] - 1)
  elif key == 's':
    selPos = (selPos[0], selPos[1] + 1)
  
  # Select
  
  elif key == 'f' and mode == 0:
    if selPos[1] == 0: # Play
      
      selPos = (0, 0) # Reset selPos
      
      mode = 1 # Mode set to Game
      
      generateGame() # Generates Game
      
    elif selPos[1] == 1: # Grid Width
      options["Grid Width"] = min(strToPosInt(input("Grid Width: ")), 100)
      print('\033[K\033[F', end='')
    elif selPos[1] == 2: # Grid Height
      options["Grid Height"] = min(strToPosInt(input("Grid Height: ")), 100)
      print('\033[K\033[F', end='')
    elif selPos[1] == 3: # Sources
      options["Sources"] = max(min(strToPosInt(input("Sources: ")), options["Grid Width"]), 1)
      print('\033[K\033[F', end='')
    elif selPos[1] == 4: # Drains
      options["Drains"] = max(min(strToPosInt(input("Drains: ")), options["Grid Width"]), 1)
      print('\033[K\033[F', end='')
  
  # Clamp selected position
  
  if mode == 0:
    selPos = (0, max(min(selPos[1], len(homeScreenSelPos) - 1), 0))
  else:
    selPos = (max(min(selPos[0],  options["Grid Width"] - 1), 0), max(min(selPos[1],  options["Grid Height"] - 1), 0))
  
  ### Behavior ###
  
  ### Render ###
  
  render()
  
