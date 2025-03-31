# Imports

import sys
import os
import random
import pygame
import logging

pygame.init()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s: %(message)s',
    filename='app.log'
)

# Variables

run = True # Run Main Loop
mode = 0 # Mode (0 = Home, 1 = Game)
selPos = (0, 0) # Selected position
renderHeight = 16 # Height of the render (for clearing the screen)

clock = pygame.time.Clock() # Clock for FPS
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
  '"Enter" to select',
  '"Esc" to quit',
  '',
  'PLAY',
  '',
  'OPTIONS:',
  'Grid Width: 10',
  'Grid Height: 5',
  'Sources: 3',
  'Drains: 3',
]
homeScreenSelPos = ( # Selectable positions on the home screen
  10, # Play
  12, # Grid Width
  13, # Grid Height
  14, # Sources
  15, # Drains
)

# Classes

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

# Functions

def generateGame(width, height, numSources, numDrains): # Builds the grid
  
  # Create Sources
  
  # Create Drains
  
  # Create Paths (don't forget to randomize pipe rotations)
  
  # Fill rest with random pipes
  
  pass
  

def render(): # Renders the grid
  
  # Clear screen
  
  global renderHeight
  
  for i in range(renderHeight):
    print('\033[F\033[K', end='')
  
  # Home Screen
  
  if mode == 0:
    
    global selPos
    
    selPos = (0, 0) # Reset selected position
    
    for i in range(len(homeScreenBase)):
      
      selected = False # Selected position
      
      if i == homeScreenSelPos[selPos[0]]: selected = True
      
      # Highlight selected position
      if selected: print('\033[7m' + homeScreenBase[i] + '\033[0m')
      else: print(homeScreenBase[i])
      
    
    renderHeight = len(homeScreenBase) # Set render height
    
  
  # Game Screen
  
  else:
    
    # Info bar
    
    # Sources
    
    # Grid
    
    # Drains
    
    # Message bar
    
    pass
    
  

# Pre Loop

for entry in homeScreenBase: print(entry) # Print home screen base

# Main Loop

while run:
  
  clock.tick(FPS) # FPS
  
  # Events
  
  for event in pygame.event.get():
    
    if event.type == pygame.KEYDOWN:
      
      # Escape
      
      if event.key == pygame.K_ESCAPE: run = False
      
      # Navigation
      
      if event.key == pygame.K_w:
        selPos = (selPos[0] - 1, selPos[1])
      if event.key == pygame.K_s:
        selPos = (selPos[0] + 1, selPos[1])
      if event.key == pygame.K_a:
        selPos = (selPos[0], selPos[1] - 1)
      if event.key == pygame.K_d:
        selPos = (selPos[0], selPos[1] + 1)
      
      # Clamp selected position
      
      if mode == 0:
        selPos = (0, max(min(selPos[1], len(homeScreenSelPos) - 1), 0))
      
      logging.debug(f"Selected position: {selPos}")
      
    
  
  # Behavior
  
  # Render
  
  render()
  

pygame.quit() # Quit pygame