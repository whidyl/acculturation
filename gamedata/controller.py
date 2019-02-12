import pygame
import model
import csv
from random import random
from eventmanager import *

class Keyboard(object):
    """
    Handles keyboard input.
    """

    def __init__(self, evManager, model):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        model (GameEngine): a strong reference to the game Model.
        """
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = model
        self.loadMap("assets/maps/classic-medium.csv")
        self.updateTilesOnScreen()

    def notify(self, event):
        """
        Receive events posted to the message queue. 
        """

        if isinstance(event, TickEvent):
            # Called for each game tick. We check our keyboard presses, mouse clicks, and mouse movement here.
            for event in pygame.event.get():
                # handle window manager closing our window
                if event.type == pygame.QUIT:
                    self.evManager.Post(QuitEvent())
                # handle key down events
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.evManager.Post(StateChangeEvent(None))
                    else:
                        currentstate = self.model.state.peek()
                        if currentstate == model.STATE_MENU:
                            self.keydownmenu(event)
                        if currentstate == model.STATE_PLAY:
                            self.keydownplay(event)
                        if currentstate == model.STATE_HELP:
                            self.keydownhelp(event)
                # handle mouse up events
                if event.type == pygame.MOUSEBUTTONUP:
                    currentstate = self.model.state.peek()
                    if currentstate == model.STATE_MENU:
                        self.mouseupmenu(event)
                # handle mouse move events
                if event.type == pygame.MOUSEMOTION:
                    currentstate = self.model.state.peek()
                    if currentstate == model.STATE_MENU:
                        self.mousemovemenu(event)
                    if currentstate == model.STATE_PLAY:
                        self.mousemoveplay(event)
            # We check for keyboard keys that are held down here.
            try: # try so we don't get an error after exiting
                keys = pygame.key.get_pressed()
                currentstate = self.model.state.peek()
                if currentstate == model.STATE_PLAY:
                    self.keyhelddownplay(keys)
            except:
                pass

    def keydownmenu(self, event):
        """
        Handles menu key events.
        """
        # escape pops the menu
        if event.key == pygame.K_ESCAPE:
            self.evManager.Post(StateChangeEvent(None))
        # space plays the game
        if event.key == pygame.K_SPACE:
            self.evManager.Post(StateChangeEvent(model.STATE_PLAY))
    
    def keydownhelp(self, event):
        """
        Handles help key events.
        """
        
        # space, enter or escape pops help
        if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN]:
            self.evManager.Post(StateChangeEvent(None))
    
    def keydownplay(self, event):
        """
        Handles play key events.
        """
        # ESC: exit current state
        if event.key == pygame.K_ESCAPE:
            self.evManager.Post(StateChangeEvent(None))
        # F1 shows the help
        if event.key == pygame.K_F1:    
            self.evManager.Post(StateChangeEvent(model.STATE_HELP))
        else:
            self.evManager.Post(InputEvent(event.unicode, None))
    def keyhelddownplay(self, keys):
        """
        Handles key held down events when playing
        """
        # WASD: move camera
        if keys[pygame.K_w]:
            self.model.camera.rect.y -= 16
            self.updateTilesOnScreen()
        if keys[pygame.K_s]:
            self.model.camera.rect.y += 16
            self.updateTilesOnScreen()
        if keys[pygame.K_a]:
            self.model.camera.rect.x -= 16
            self.updateTilesOnScreen()
        if keys[pygame.K_d]:
            self.model.camera.rect.x += 16
            self.updateTilesOnScreen()
        self.updateTilesHovered()
        # update tilesOnScreen

    def mouseupmenu(self, event):
        """
        Handles menu mouse up events
        """
        menu = self.model.mainMenu
        mousePos = pygame.mouse.get_pos()
        # if mouse is on button, do something.
        for button in menu.buttons:
            if (button.rect.collidepoint(mousePos)):
                # if play button is clicked, play game
                if (button.text == "PLAY"):
                    self.evManager.Post(StateChangeEvent(model.STATE_PLAY))
                # if exit button is clicked, exit
                if (button.text == "EXIT"):
                    self.evManager.Post(QuitEvent())
    
    def mousemovemenu(self, event):
        """
        Handles menu mouse move events
        """
        menu = self.model.mainMenu
        mousePos = pygame.mouse.get_pos()
        
        for button in menu.buttons:
            if (button.rect.collidepoint(mousePos)):
                button.hovered = True
            else:
                button.hovered = False

    def mousemoveplay(self, event):
        """
        Handles menu mouse move events
        """
        self.updateTilesHovered()

    # MAP GEN
    def loadMap(self, csvFileName):
        """
        Converts a CSV file into a set of Tile objects which are stored into a TileMap
        """
        tileSize = 32
        # generate tiles from CSV file into a set of tiles and a set of ids
        tiles = []
        tileIds = []
        with open(csvFileName) as csvFile:
            csvReader = csv.reader(csvFile, delimiter = ',')
            for row, line in enumerate(csvReader):
                # for each row, add a new row to tileIds list
                tileIds.append([])
                for col, tileId in enumerate(line):
                    # for each column, add id to tileIds and add Tile to tiles with a generated resource
                    tileIds[row].append(int(tileId))
                    generatedTile = model.Tile(int(tileId), tileSize*col, tileSize*row, tileSize)
                    generatedResource = self.generateResource(generatedTile)
                    generatedTile.resource = generatedResource
                    tiles.append(generatedTile)
        self.model.tileMap = model.TileMap(tileIds, tiles)
    
    def generateResource(self, tile):
        """
        returns a random resource (or none) depending on tile's tileId
        """

        if tile.tileId == model.GRASSLAND:
            # grassland probability distribution:
            # None: 97%
            # Wheat: 2.75%
            # Mountain: 0.25%
            randomNum =  random()
            if randomNum > 1 - 0.0275:
                return model.Resource(tile, model.WHEAT)
            elif randomNum > 1 - 0.03 :
                return model.Resource(tile, model.MOUNTAIN)
            else:
                return None
        elif tile.tileId == model.PLAINS:
            # plains probability distribution:
            # None: 80%
            # Wheat: 20%
            randomNum =  random()
            if randomNum > 0.8:
                return model.Resource(tile, model.WHEAT)
            else:
                return None
        elif tile.tileId == model.TUNDRA:
            # plains probability distribution:
            # None: 85%
            # Mountain: 15%
            randomNum =  random()
            if randomNum > 0.85:
                return model.Resource(tile, model.MOUNTAIN)
            else:
                return None
        else:
            return None

        

    # TILE UPDATES
    def updateTilesOnScreen(self):
        """
        Updates tileMap's tilesOnScreen property to contain only tiles which are on screen
        """
        self.model.tileMap.tilesOnScreen = []
        for tile in self.model.tileMap.tiles:
            #                                                  \/ offset tile x to fix visual glitch
            if self.model.camera.rect.collidepoint(tile.rect.centerx + 16, tile.rect.centery + 16):
                self.model.tileMap.tilesOnScreen.append(tile)
    
    def updateTilesHovered(self):
        """
        Updates hovered property of tile
        """
        x, y = pygame.mouse.get_pos()
        x += self.model.camera.rect.x
        y += self.model.camera.rect.y
        for tile in self.model.tileMap.tilesOnScreen:
            if tile.rect.collidepoint((x, y)):
                tile.hovered = True
            else:
                tile.hovered = False




                    

        

