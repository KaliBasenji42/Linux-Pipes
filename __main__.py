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
  

def randomExc(lo, hi, exc): # Returns a random number in range lo to hi (inclusive), excluding values in exc
  
  poss = [] # Possible outputs
  
  for i in range(lo, hi + 1):
    
    listed = False # Is i listed in exc
    
    for val in exc:
      if i == val: listed = True
    
    if not listed: poss.append(i)
    
  
  return poss[random.randint(0, len(poss) - 1)]
  

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
  
  global options, characters
  
  # Create Sources
  
  taken = [] # Taken positions
  
  for i in range(options["Sources"]):
    
    pos = randomExc(0, options["Grid Width"] - 1, taken) # Rand x pos
    
    # Color
    
    color = [0, 0, 0]
    cPos = random.randint(0, 2)
    color[cPos] = 1 / random.randint(1, 2)
    
    sources.append(source(pos, color))
    
  
  # Create Drains
  
  taken = [] # Taken positions
  
  for i in range(options["Drains"]):
    
    pos = randomExc(0, options["Grid Width"] - 1, taken) # Rand x pos
    
    # Color
    
    color = [0, 0, 0]
    srcs = [] # Associated sources, must have one, may have all
    
    for i in range(options["Sources"]):
      
      src = random.randint(0, options["Sources"] - 1) # Source index to try to add
      
      listed = False # Is already listed
      
      for val in srcs:
        if src == val: listed = True
      
      if not listed: srcs.append(src)
      
    
    for val in srcs:
      
      c = sources[val].color # Source color
      
      # Add
      
      color[0] = color[0] + c[0]
      color[1] = color[1] + c[1]
      color[2] = color[2] + c[2]
      
    
    color[0] = min(color[0], 1) # Clamp color values
    color[1] = min(color[1], 1)
    color[2] = min(color[2], 1)
    
    drains.append(drain(pos, color))
    
  
  # Create Paths (don't forget to randomize pipe rotations)
  
  # Fill rest with random pipes
  
  for i in range(options["Grid Height"]):
    
    row = []
    
    for j in range(options["Grid Width"]):
      
      chr = characters[random.randint(0, len(characters) - 1)]
      
      row.append(pipe(chr, j, i))
      
    
    grid.append(row)
    
  

def render(): # Renders the Screen
  
  global renderHeight, selPos, homeScreenBase, homeScreenSelPos
  
  # Clear screen
  
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
    
    print('Info')
    
    # Sources
    
    srcStr = ' ' * options["Grid Width"]
    
    for src in sources:
      
      index = src.x # Insert Index
      c = src.color
      
      colorChr = "\033[38;2;" + str(int(255 * c[0])) + ';' + str(int(255 * c[2]))  + ';' + str(int(255 * c[2])) + 'm'
      # Color escape character for the src
      
      srcStr[:index - 1] + colorChr + src.chr + '\033[0m' # Add color, then character, then reset
      
    
    print(srcStr)
    
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
  
