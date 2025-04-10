### Imports ###

import sys
import os
import random
import time
import termios
import tty
import logging

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s | %(levelname)s: %(message)s',
    filename='app.log'
)
logging.debug('New Run: ')

### Variables ###

animateResolve = False # Wether to animate resolving process
ARSleep = 0.1 # SPF of resolve animation

run = True # Run Main Loop
mode = 0 # Mode (0 = Home, 1 = Game)
selPos = (0, 0) # Selected position (x, y)
renderHeight = 0 # Height of the render (for clearing the screen)
win = False # Win state
pastKeys = [''] * 4 # To detect if a key was an arrow/escape key, and sould not be returned

options = { # Options
  'Grid Width': 10, # Game Grid Width
  'Grid Height': 5, # Game Grid Height
  'Sources': 3, # Number of sources
  'Drains': 3, # Number of drains
}

grid = [] # Game Grid, containing all pipes
unresolved = [] # Unresolved pipes (for a selective flood algorithm)

characters = '━┃┏┓┗┛┣┫┳┻╋' # Characters for the pipes
charKey = { # Character Key: "chr": (hasTop, hasRight, hasBottom, hasLeft, "allRotations")
  '━': (False, True, False, True, '━┃━┃'),
  '┃': (True, False, True, False, '┃━┃━'),
  '┏': (False, True, True, False, '┏┓┛┗'),
  '┓': (False, False, True, True, '┓┛┗┏'),
  '┗': (True, True, False, False, '┗┏┓┛'),
  '┛': (True, False, False, True, '┛┗┏┓'),
  '┣': (True, True, True, False, '┣┳┫┻'),
  '┫': (True, False, True, True, '┫┻┣┳'),
  '┳': (False, True, True, True, '┳┫┻┣'),
  '┻': (True, True, False, True, '┻┣┳┫'),
  '╋': (True, True, True, True, '╋╋╋╋'),
}

homeScreenBase = [ # What to print when starting home screen
  '\033[31m┏━┓ \033[32m┳ \033[33m┏━┓ \033[34m┏━╸ \033[35m┏━╸',
  '\033[31m┣━┛ \033[32m┃ \033[33m┣━┛ \033[34m┣━╸ \033[35m┗━┓',
  '\033[31m╹   \033[32m┻ \033[33m╹   \033[34m┗━╸ \033[35m╺━┛\033[0m',
  '',
  '"WASD" to navigate',
  '"Q" & "E" to rotate pipes',
  '"F" to select',
  '"X" to quit',
  'When editing option, type number, then press [Enter] to set',
  '',
  'PLAY',
  '',
  'OPTIONS:',
]
homeScreenSelPos = ( # Selectable positions on the home screen
  10, # Play
  13, # Grid Width
  14, # Grid Height
  15, # Sources
  16, # Drains
)

velKey = ( # Key for Top-Right-Bottom-Left to displacment
  (0, -1),
  (1, 0),
  (0, 1),
  (-1, 0),
)

### Classes ###

class pipe:
  
  def __init__(self, chr, x, y):
    
    # Variables
    
    self.pos = (x, y) # Position
    self.chr = chr # Character
    self.sources = set([]) # Sources the pipe is connected to
    self.color = [0.0, 0.0, 0.0] # Color content (based on the sources)
    
    # Neighbors
    
    nghbrsPos = [ # Potential neighbors' positions (clockwise/fits charKey order)
      (self.pos[0], self.pos[1] - 1, 0), # X, Y, ID/index for charKey (Up, Right, Down, Left)
      (self.pos[0] + 1, self.pos[1], 1),
      (self.pos[0], self.pos[1] + 1, 2),
      (self.pos[0] - 1, self.pos[1], 3),
    ]
    
    self.nghbrsPos = [] # All Neighbors
    
    for i in range(len(nghbrsPos)):
      
      add = True # Should add
      
      # Remove out-of-bound
      
      if nghbrsPos[i][0] < 0: add = False
      if nghbrsPos[i][1] < 0: add = False
      if nghbrsPos[i][0] >= options['Grid Width']: add = False
      if nghbrsPos[i][1] >= options['Grid Height']: add = False
      
      if add: self.nghbrsPos.append(nghbrsPos[i]) # Add
      
    
  
  def rotate(self, clockwise):
    
    # Rotate
    
    if clockwise: self.chr = charKey[self.chr][4][1]
    else: self.chr = charKey[self.chr][4][3]
    
    # Update Grid
    
    updateGrid()
    
  
  def update(self):
    
    global grid, sources
    
    # Get connected neighbors
    
    connected = [] # Connected Neighbors Positions
    
    for pos in self.nghbrsPos:
      
      nghbr = grid[pos[1]][pos[0]]
      
      addCnt = True # Add to connected
      
      if not charKey[self.chr][pos[2]]: addCnt = False # Self not connected
      if not charKey[nghbr.chr][(pos[2] + 2) % 4]: addCnt = False # Neighboor not connected
      
      if addCnt: connected.append(pos) # Add
      
    
    # Update pipe sources
    
    self.sources.clear()
    
    for src in sources: # From sources
      
      if self.pos[0] == src.x and charKey[self.chr][0] and self.pos[1] == 0:
        # Self x-pos aligns with src x-pos, self char connects upward, self y-pos is next to sources
        
        self.sources.add(src.x)
        
      
    
    for pos in connected: # From connected
      
      cnt = grid[pos[1]][pos[0]]
      
      self.sources = self.sources.union(cnt.sources)
      
    
    # Add non-matching connected to unresolved
    
    for pos in connected:
      
      cnt = grid[pos[1]][pos[0]]
      
      match = cnt.sources == self.sources # Sources match
      
      if not match: unresolved.append(
        grid[pos[1]][pos[0]] # Add cnt (from grid)
      )
      
    
    # Update color
    
    self.color = [0.0, 0.0, 0.0]
    
    for src in sources:
      
      for srcPos in self.sources:
        
        if srcPos == src.x:
          
          for i in range(len(src.color)):
            
            self.color[i] += src.color[i]
            
          
        
      
    
    # Debug
    
    dbgStr = 'Pipe:\n  Self: ' + str(self.pos) +  self.chr + '\n    Ngbrs: '
    
    for pos in self.nghbrsPos:
      dbgStr = (dbgStr + '\n      ' + 
                str(pos) + grid[pos[1]][pos[0]].chr + 
                ' SelfCnt: (' + str(pos[2]) + ') ' + str(charKey[self.chr][pos[2]]) + 
                ' NghbrCnt: (' + str((pos[2] + 2) % 4) + ') ' + str(charKey[grid[pos[1]][pos[0]].chr][(pos[2] + 2) % 4]))
    
    dbgStr = dbgStr + '\n    Cnctd:'
    
    for pos in connected:
      dbgStr = dbgStr + '\n      ' + str(pos) + grid[pos[1]][pos[0]].chr
    
    dbgStr = dbgStr + '\n  Sources: ' + str(self.sources)
    dbgStr = dbgStr + '\n  Color: ' + str(self.color)
    
    logging.debug(dbgStr)
    
  

class source:
  
  def __init__(self, x, color):
    
    # Variables
    
    self.x = x # X position
    self.color = color # Color content
    
    self.chr = '╻' # Character
    
  
  def update(self):
    
    global unresolved, grid
    
    sPipe = grid[0][self.x] # Pipe below
    
    if charKey[sPipe.chr][0]: # Upward connections
      unresolved.append(grid[sPipe.pos[1]][sPipe.pos[0]]) # Add to unresolved
    
  
sources = [] # List of all sources

class drain:
  
  def __init__(self, x, demand, srcs):
    
    # Variables
    
    self.x = x # X position
    self.demand = demand # Color demanded
    self.srcs = srcs # Sources (for generation only) (listed as index not x pos)
    
    self.color = [0.0, 0.0, 0.0] # Color content
    self.chr = '╹' # Character
    self.fulfilled = False # All demands met
    
  
  def update(self):
    
    global grid
    
    # Color
    
    self.color = [0.0, 0.0, 0.0]
    
    dPipe = grid[-1][self.x] # Pipe above
    
    if charKey[dPipe.chr][2]: # Downward connections
      self.color = dPipe.color
    
    # Fulfilled
    
    self.fulfilled = True
    
    for i in range(len(drn.color)):
      if drn.color[i] < drn.demand[i]: # Demand not met
        self.fulfilled = False
    
  
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
  

def arraysMatch(arr1, arr2): # Check if arrays match, order does not matter
  
  if len(arr1) != len(arr2): return False
  # Different lens, return False
    
  return all(item in arr1 for item in arr2)
  # Return if all items are contained in the other
  

def roll(arr, new): # Have an array roll in a new value, removing the first
  
  out = arr
  
  out.append(new) # Add new
  out.pop(0) # Remove first
  
  return out
  

def getKey():
  
  global pastKeys
  
  fd = sys.stdin.fileno()
  old = termios.tcgetattr(fd) # Old terminal settings
  
  try:
    tty.setraw(sys.stdin.fileno()) # Terminal to raw (non-conical & no echo)
    
    chr = sys.stdin.read(1) # Get char entered
    
    pastKeys = roll(pastKeys, chr) # Roll chr into pastKeys
    
    shouldReturn = False # Should it return chr?
    if pastKeys[-2] != '[': shouldReturn = True
    elif pastKeys[-3] != '\x1b': shouldReturn = True
    
    logging.debug('Key Press: ' + chr + ' (shouldReturn: ' + str(shouldReturn) + ', ' + str(pastKeys) + ')') # Logging
    
    if shouldReturn: return chr # Return
    return '' # Base case
    
  finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old) # Restore terminal settings
  

def updateGrid():
  
  # Clear Pipes
  
  for row in grid:
    for item in row:
      item.sources.clear()
      item.color = [0.0, 0.0, 0.0]
  
  # Update Sources
  
  for src in sources:
    src.update()
  

def generateGame(): # Builds the grid
  
  global options, characters, sources, drains, grid
  
  # Clear
  
  sources = []
  drains = []
  grid = []
  
  # Create Sources
  
  taken = [] # Taken positions
  
  for i in range(options['Sources']):
    
    pos = randomExc(0, options['Grid Width'] - 1, taken) # Rand x pos
    taken.append(pos)
    
    # Color
    
    color = [0.0, 0.0, 0.0]
    cPos = random.randint(0, 2)
    color[cPos] = 1 / random.randint(1, 2)
    
    sources.append(source(pos, color))
    
  
  # Create Drains
  
  taken = [] # Taken positions
  
  for i in range(options['Drains']):
    
    pos = randomExc(0, options['Grid Width'] - 1, taken) # Rand x pos
    taken.append(pos)
    
    # Color
    
    color = [0.0, 0.0, 0.0]
    srcs = [] # Associated sources, must have one, may have all
    
    for i in range(options['Sources']):
      
      src = random.randint(0, options['Sources'] - 1) # Source index to try to add
      
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
      
    
    drains.append(drain(pos, color, srcs))
    
  
  # Create paths
  
  gridPaths = [[[False] * 4 for _ in range(options['Grid Width'])] for _ in range(options['Grid Height'])]
  # Grid with an array for each pipe, where each value represents wether a connection is needed on that side
  # Same order as usual (Top, Right, Bottom, Left)
  
  for drn in drains:
    
    for src in drn.srcs:
      
      numRandPnts = random.randint(1, int(max(min(options['Grid Width'], options['Grid Height'] * 2) / 10, 1)))
      # Number of random mid points to pass through
      # Between 1 and the larger of Grid Width or Grid Height * 2, divided by 10, clamped to a min of 1
      
      points = [(drn.x, options['Grid Height'] - 1)]
      # List of points to pass through, first point at Drain
      
      for i in range(numRandPnts): # Random mid points
        points.append((random.randint(0, options['Grid Width'] - 1), 
                       random.randint(0, options['Grid Height'] - 1)))
      
      points.append((sources[src].x, 0)) # Last point at Source
      
      gridPaths[points[0][1]][points[0][0]][2] = True # Connect first to drain
      gridPaths[points[-1][1]][points[-1][0]][0] = True # Connect last to source
      
      logging.debug('Points: ' + str(points)) # Log points
      
      for i in range(len(points) - 1): # For each point except last
        
        pnt = points[i] # Current point
        pntN = points[i+1] # Next point
        
        crnt = pnt # Current point
        
        DBStr = 'Point Gen:\n  ' # Debug string
        DBStr = DBStr + 'pnt: ' + str(pnt) + ' pntN (Next Point): ' + str(pntN)
        
        while True: # While crnt is not pntN
          
          dispX = pntN[0] - crnt[0] # Displacement X
          dispY = pntN[1] - crnt[1] # Displacement Y
          
          if (dispX, dispY) == (0, 0): break # Exit if crnt == pntN
          
          chance = abs(dispX) / (abs(dispX) + abs(dispY)) # Chance to choose to move target horz. (not vert.)
          
          mvHorz = random.random() <= chance # To move target horz. (not vert.)
          
          mvDisp = (0, 0) # Displacement/Move
          
          if mvHorz: mvDisp = (dispX / abs(dispX), 0) # Horz
          else: mvDisp = (0, dispY / abs(dispY)) # Vert
          
          side = 0 # Side of the pipe to set to True
          
          for v in range(len(velKey)): # Use velKey to find side based on mvDisp
            if velKey[v] == mvDisp: side = v
          
          trgt = (int(crnt[0] + mvDisp[0]), int(crnt[1] + mvDisp[1])) # Target point
          
          # Debug
          DBStr = DBStr + '\n  '
          DBStr = DBStr + 'mvHorz: ' + str(chance * 100) + '% ' + str(mvHorz)
          DBStr = DBStr + ' | disp: ' + str((dispX, dispY)) + ' mv: ' + str(mvDisp)
          DBStr = DBStr + ' | crnt: ' + str(crnt) + ' ' + str(side)
          DBStr = DBStr + ' | trgt: ' + str(trgt) + ' ' + str((side + 2) % 4)
          
          gridPaths[crnt[1]][crnt[0]][side] = True # Set crnt pipe side to true
          gridPaths[trgt[1]][trgt[0]][(side + 2) % 4] = True # Set trgt pipe side to true
          
          crnt = trgt # Move crnt to trgt
          
        
        logging.debug(DBStr)
        
      
    
  
  # Debug & Set
  
  DBStr = 'Paths:' # Debug string
  
  for i in range(options['Grid Height']):
    
    row = gridPaths[i]
    
    rowStr = '\n  :' # Row in string
    
    gridRow = [] # Grid row
    
    for j in range(options['Grid Width']):
      
      list = row[j]
      
      chr = '?' # Charcater
      
      for key in charKey:
        
        match = True # If the character matches the list
        
        for k in range(len(list)):
          if list[k] != charKey[key][k]: match = False # Does not match
        
        if match: chr = key # Set
        
      
      if list == [False] * 4: chr = ' ' # Empty
      
      rowStr = rowStr + chr # Add to row
      
      # Set character
      
      if chr != '?' and chr != ' ': # Path
        chr = charKey[chr][4][random.randint(0,3)]
        gridRow.append(pipe(chr, j, i))
      else: # Random
        chr = characters[random.randint(0, len(characters) - 1)]
        gridRow.append(pipe(chr, j, i))
      
    
    DBStr = DBStr + rowStr # Add to DBStr
    
    grid.append(gridRow) # Add row to grid
    
  
  logging.debug(DBStr) # Log
  
  # Debug Raw
  
  DBStr = 'Paths Raw:'
  
  for row in gridPaths:
    
    # Row in string
    DBStr = DBStr + '\n  ' + str(row)
    
  
  logging.debug(DBStr) # Log
  
  # add pipes near sources to unresolved
  unresolved.extend(grid[0])
  

def render(): # Renders the Screen
  
  global renderHeight, selPos, homeScreenBase, homeScreenSelPos, grid, sources, drains
  
  # Clear screen
  
  for i in range(renderHeight):
    
    if mode == 1: print('\033[F', end='') # Up one (do not clear/prevent flashing)
    else: print('\033[K\033[F', end='') # Clear row, up 1 row
    
  print('\033[K', end='') # Last row
  
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
    
    renderHeight = 0 # Initial renderHeight, ++ at each print()
    
    # Info bar
    
    if selPos[1] < options['Grid Height']:
      
      pipe = grid[selPos[1]][selPos[0]]
      
      info = 'Color: ' + str(pipe.color) + ' ' # Add color
      
    else:
      
      info = '[None]' # Base case
      
      for drn in drains:
        
        if drn.x == selPos[0]:
          
          info = 'Color : [' # Start
          
          for i in range(len(drn.color)):
            
            if drn.color[i] >= drn.demand[i]: # Demand met
              info = info + '\033[32m' # Green
            
            info = info + str(drn.color[i]) + ' / ' + str(drn.demand[i]) + '\033[0m, ' # Supply / Demand
            
          
          info = info[:-2] # Trim ', '
          info = info + ']'
          
        
      
    
    info = info + ' Win: '
    
    if win:
      info = info + '✅🎉'
    else:
      info = info + '❌'
    
    print(info)
    renderHeight += 1
    
    # Sources
    
    srcStr = ''
    
    for i in range(options['Grid Width']):
      
      subStr = ' ' # Base Case
      
      for src in sources:
        
        if src.x == i:
          
          c = src.color
          
          colorChr = '\033[38;2;' + str(int(255 * c[0])) + ';' + str(int(255 * c[1]))  + ';' + str(int(255 * c[2])) + 'm'
          # Color escape character for the src
          
          subStr = colorChr + src.chr
          
        
      
      srcStr = srcStr + subStr
      # Add substring
      
    
    srcStr = '\033[47m' + srcStr + '\033[0m' # Set background color and reset color on end
    print(srcStr + '  ')
    renderHeight += 1
    
    # Grid
    
    for row in grid:
      
      rowStr = ''
      
      for pipe in row:
        
        if pipe.pos == selPos: # Highlight selected position
          rowStr = rowStr + '\033[7m'
        
        c = pipe.color # Color
        
        colorChr = ('\033[38;2;' + 
                    str(int(min(255 * c[0], 255))) + ';' + 
                    str(int(min(255 * c[1], 255)))  + ';' + 
                    str(int(min(255 * c[2], 255))) + 'm')
        # Color escape character for the pipe
        
        rowStr = rowStr + '\033[47m' + colorChr + pipe.chr + '\033[0m'
        
      
      print(rowStr + '  ')
      renderHeight += 1
      
    
    # Drains
    
    drnStr = ''
    
    for i in range(options['Grid Width']):
      
      subStr = ' ' # Base case
      
      for drn in drains:
        
        if drn.x == i:
          
          c = drn.color
          
          colorChr = ('\033[38;2;' + 
                      str(int(min(255 * c[0], 255))) + ';' + 
                      str(int(min(255 * c[1], 255)))  + ';' + 
                      str(int(min(255 * c[2], 255))) + 'm')
          # Color escape character for the src
          
          if drn.fulfilled:
            colorChr = colorChr + '\033[42m'
          
          subStr = colorChr + drn.chr
          
        
      
      if i == selPos[0] and selPos[1] == options['Grid Height']: # Highlight selected position
        subStr = '\033[7m' + subStr
      
      drnStr = drnStr + '\033[47m' + subStr  + '\033[0m'
      # Add substrings
      
    
    print(drnStr + '  ')
    renderHeight += 1
    
  

### Pre Loop ###

try: render() # Initial render
except Exception as e: 
  logging.exception(e)
  print('\033[97;41mFatal Error\033[0m')

### Main Loop ###

try: 
  
  while run:
    
    ### Detect Key ###
    
    key = getKey().lower()
    
    # Escape
    
    if key == 'x' and mode == 0: run = False
    
    elif key == 'x' and mode == 1:
      
      selPos = (0, 0)
      grid = [] # Reset Vars
      sources = []
      drains = []
      
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
        updateGrid() # Initail Update
        
        for i in range(renderHeight):
          print('\033[K\033[F', end='') # Clear Row
        for i in range(renderHeight):
          print('') # Back to end
        
      elif selPos[1] == 1: # Grid Width
        options['Grid Width'] = max(min(strToPosInt(input('Grid Width: ')), 50), 1)
        options['Drains'] = min(options['Drains'], options['Grid Width']) # Re-Clamp
        options['Sources'] = min(options['Sources'], options['Grid Width'])
        print('\033[K\033[F', end='')
      elif selPos[1] == 2: # Grid Height
        options['Grid Height'] = max(min(strToPosInt(input('Grid Height: ')), 20), 1)
        print('\033[K\033[F', end='')
      elif selPos[1] == 3: # Sources
        options['Sources'] = max(min(strToPosInt(input('Sources: ')), options['Grid Width']), 1)
        print('\033[K\033[F', end='')
      elif selPos[1] == 4: # Drains
        options['Drains'] = max(min(strToPosInt(input('Drains: ')), options['Grid Width']), 1)
        print('\033[K\033[F', end='')
    
    # Clamp selected position
    
    if mode == 0:
      selPos = (0, max(min(selPos[1], len(homeScreenSelPos) - 1), 0))
    else:
      selPos = (max(min(selPos[0],  options['Grid Width'] - 1), 0), max(min(selPos[1],  options['Grid Height']), 0))
    
    # Rotate Pipe
    
    if mode == 1 and selPos[1] < options['Grid Height']:
      
      if key == 'q': # Counter-clockwise
        grid[selPos[1]][selPos[0]].rotate(False)
      elif key == 'e': # Clockwise
        grid[selPos[1]][selPos[0]].rotate(True)
      
    
    ### Behavior ###
    
    while True: # While there are unresolved pipes
      
      if len(unresolved) == 0: break # Break when empty 
      
      if animateResolve: # Animation
        render()
        time.sleep(ARSleep)
      
      unresolved[0].update() # Update first pipe
      unresolved.pop(0) # Remove pipe
      
    
    win = True # Initail win state
    
    for drn in drains: # Drains
      
      drn.update() # Update
      
      if not drn.fulfilled: win = False
      
    
    ### Render ###
    
    render()
    

except Exception as e:
  logging.exception(e)
  print('\033[97;41mFatal Error\033[0m')
