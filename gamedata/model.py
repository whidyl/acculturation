import pygame
from eventmanager import *
pygame.font.init()

class GameEngine(object):
    """
    Tracks the game state.
    """

    def __init__(self, evManager):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        
        Attributes:
        running (bool): True while the engine is online. Changed via QuitEvent().
        """

        self.evManager = evManager
        evManager.RegisterListener(self)
        self.running = False
        self.state = StateMachine()
        self.mainMenu = MainMenu()
        # tileMap will be loaded once game starts
        self.tileMap = None
        # camera offsets will offset all game objects
        self.camera = Camera(posx = 4500, posy = 600)
    def notify(self, event):
        """
        Called by an event in the message queue. 
        """

        if isinstance(event, QuitEvent):
            self.running = False
        if isinstance(event, StateChangeEvent):
            # pop request
            if not event.state:
                # false if no more states are left
                if not self.state.pop():
                    self.evManager.Post(QuitEvent())
            else:
                # push a new state on the stack
                self.state.push(event.state)

    def run(self):
        """
        Starts the game engine loop.
        This pumps a Tick event into the message queue for each loop.
        The loop ends when this object hears a QuitEvent in notify(). 
        """
        self.running = True
        self.evManager.Post(InitializeEvent())
        self.state.push(STATE_MENU)
        while self.running:
            newTick = TickEvent()
            self.evManager.Post(newTick)


# State machine constants for the StateMachine class below
STATE_INTRO = 1
STATE_MENU = 2
STATE_HELP = 3
STATE_ABOUT = 4
STATE_PLAY = 5

class StateMachine(object):
    """
    Manages a stack based state machine.
    peek(), pop() and push() perform as traditionally expected.
    peeking and popping an empty stack returns None.
    """
    
    def __init__ (self):
        self.statestack = []
    
    def peek(self):
        """
        Returns the current state without altering the stack.
        Returns None if the stack is empty.
        """
        try:
            return self.statestack[-1]
        except IndexError:
            # empty stack
            return None
    
    def pop(self):
        """
        Returns the current state and remove it from the stack.
        Returns None if the stack is empty.
        """
        try:
            self.statestack.pop()
            return len(self.statestack) > 0
        except IndexError:
            # empty stack
            return None
    
    def push(self, state):
        """
        Push a new state onto the stack.
        Returns the pushed value.
        """
        self.statestack.append(state)
        return state

# SCREEN CONSTANTS
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768

class MainMenu(object):
    def __init__(self):
        # BUTTONS
        self.buttons = []
        self.buttonColor = pygame.Color(0, 0, 255)
        self.buttonHoverColor = pygame.Color(50, 50, 255)

        # play 
        self.buttonPlay = PrimButton(0, 0, 300, 50, self.buttonColor, self.buttonHoverColor, "PLAY")
        self.buttonPlay.rect.center = (SCREEN_WIDTH/2,  (SCREEN_HEIGHT/10) * 5.5)
        self.buttons.append(self.buttonPlay)

        # exit
        self.buttonExit = PrimButton(0, 0, 300, 50, self.buttonColor, self.buttonHoverColor, "EXIT")
        self.buttonExit.rect.center = (SCREEN_WIDTH/2,  (SCREEN_HEIGHT/10) * (5.5 + 1.2))
        self.buttons.append(self.buttonExit)

        self.buttonOptions = PrimButton(0, 0, 300, 50, self.buttonColor, self.buttonHoverColor, "OPTIONS")
        self.buttonOptions.rect.center = (SCREEN_WIDTH/2,  (SCREEN_HEIGHT/10) * (5.5+2.4))
        self.buttons.append(self.buttonOptions)


# GUI ELEMENTS

class PrimButton(object):
    """
    Primitive solid rectangular button with text.
    """
    def __init__(self, posx, posy, width, height, 
    color = pygame.Color(255, 0, 0), hoverColor = pygame.Color(0, 255, 0),
    text = 'Button', font = pygame.font.SysFont('arial', 20)
    ):
        self.rect = pygame.Rect(posx, posy, width, height)
        self.color = color
        self.text = text
        self.font = font
        self.hoverColor = hoverColor
        self.stroke = True
        self.hovered = False

# TILES
# constanst for terrain tileIds
GRASSLAND = 0
PLAINS = 1
DESERT = 2
GRAVEL = 3
SNOW = 4
LAKE = 5
OCEAN = 6
TUNDRA = 7

# constants for resource recIds
WHEAT = 100
MOUNTAIN = 101

terrainTextures = {
    GRASSLAND:  pygame.image.load("assets/terrain-tiles/t_grassland_0_32.png"),
    PLAINS: pygame.image.load("assets/terrain-tiles/t_plains_1_32.png"),
    DESERT:  pygame.image.load("assets/terrain-tiles/t_desert_2_32.png"),
    GRAVEL:  pygame.image.load("assets/terrain-tiles/t_gravel_3_32.png"),
    SNOW:  pygame.image.load("assets/terrain-tiles/t_snow_4_32.png"),
    LAKE:  pygame.image.load("assets/terrain-tiles/t_lake_5_32.png"),
    OCEAN:  pygame.image.load("assets/terrain-tiles/t_ocean_6_32.png"),
    TUNDRA:  pygame.image.load("assets/terrain-tiles/t_tundra_7_32.png")
}

resourceTextures = {
    WHEAT: pygame.image.load("assets/resources/r_wheat_100_32.png"),
    MOUNTAIN: pygame.image.load("assets/resources/r_mountain_101_32.png")
}

guiImages = {
    'TITLE_TEXT': pygame.image.load("assets/gui/title-text.png")
}

class TileMap(object):
    def __init__ (self, tileIds = [], tiles = []):
        self.tileIds = tileIds
        self.tiles = tiles
        self.tilesOnScreen = []

class Tile(object):
    def __init__ (self, tileId = 0, posx = 0, posy = 0, size = 32, resource = None):
        """
        Represents a single tile of terrain.
        TODO structure: Structure object
        """
        self.hovered = False
        self.tileId = tileId
        self.rect = pygame.Rect(posx, posy, size, size)
        self.size = size
        self.resource = resource
        if id == GRASSLAND:
            self.name = "grassland"
        elif id == PLAINS:
            self.name = "plains"
        elif id == DESERT:
            self.name = "desert" 
        
class Camera(object):
    def __init__ (self, posx = 0, posy = 0, width = SCREEN_WIDTH, height = SCREEN_HEIGHT):
        """
        Represents a camera. Only objects withing the camera rect are drawn.
        """
        #                                           \/ offset wh to fix screen glitch
        self.rect = pygame.Rect(posx, posy, width + 32, height + 32)
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT

class Resource(object):
    def __init__(self, parent, recId = WHEAT):
        """
        Represents any resource on a terrain tile. 
        """
        self.recId = recId
        if self.recId == WHEAT:
            self.name = "wheat"
        else:
            self.name = "ERROR"

# TODO structure object that represents building
# TODO HUD object that holds UI content
# TODO ? yield object that initiates based on a Tile and calculates the resource yield per second.
# TODO tooltip object that represents a box with info in it. Created when mouse is hovered on tile for a moment