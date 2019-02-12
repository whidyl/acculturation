import pygame
import model
from eventmanager import *
from copy import *

class GraphicalView(object):
    """
    Draws the model state onto the screen.
    """

    def __init__(self, evManager, model):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        model (GameEngine): a strong reference to the game Model.
                
        Attributes:
        isinitialized (bool): pygame is ready to draw.
        screen (pygame.Surface): the screen surface.
        clock (pygame.time.Clock): keeps the fps constant.
        smallfont (pygame.Font): a small font.
        """
        
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = model
        self.isinitialized = False
        self.screen = None
        self.clock = None
        self.smallfont = None
    
    def notify(self, event):
        """
        Receive events posted to the message queue. 
        """

        if isinstance(event, InitializeEvent):
            self.initialize()
        elif isinstance(event, QuitEvent):
            # shut down the pygame graphics
            self.isinitialized = False
            pygame.quit()
        elif isinstance(event, TickEvent):
            if not self.isinitialized:
                return
            currentstate = self.model.state.peek()
            if currentstate == model.STATE_MENU:
                self.rendermenu()
            if currentstate == model.STATE_PLAY:
                self.renderplay()
            if currentstate == model.STATE_HELP:
                self.renderhelp()
            # limit the redraw speed to 30 frames per second
            self.clock.tick(30)
    
    def rendermenu(self):
        """
        Render the game menu.
        """
        menu = self.model.mainMenu
        self.screen.fill((0, 0, 0))
        # render tiles
        for tile in self.model.tileMap.tilesOnScreen:
           self.renderTile(tile)
        # render title image
        self.screen.blit(model.guiImages['TITLE_TEXT'], (0,0))
        # render buttons
        for button in menu.buttons:
            self.renderPrimButton(button)
        # render fps
        fpsText = self.smallfont.render(
            "FPS: " + str(self.clock.get_fps()),
            True, (255,0,255)
            )
        self.screen.blit(fpsText, (0, 0))
        pygame.display.flip()
        
    def renderplay(self):
        """
        Render the game play.
        """
        self.screen.fill((0,0,0))
        for tile in self.model.tileMap.tilesOnScreen:
           self.renderTile(tile)
        # render fps
        fpsText = self.smallfont.render(
            "FPS: " + str(self.clock.get_fps()),
            True, (255,0,255)
            )
        self.screen.blit(fpsText, (0, 0))
        pygame.display.flip()

        
        
    def renderhelp(self):
        """
        Render the help/debug screen.
        """

        self.screen.fill((0, 0, 0))
        somewords = self.smallfont.render(
                    'DEBUG', 
                    True, (0, 255, 0))
        self.screen.blit(somewords, (0, 0))
        pygame.display.flip()

    def renderPrimButton(self, primButton):
        """
        Render PrimitiveButton object as a rect with text that reacts to hovering
        """
        # change color if hovered
        buttonColor = deepcopy(primButton.color)
        if primButton.hovered:
            buttonColor = deepcopy(primButton.hoverColor)
        # render button
        pygame.draw.rect(self.screen, buttonColor, primButton.rect)
        textSurface = primButton.font.render(primButton.text, False, pygame.Color(255,255,255))
        # center text
        textW, textH = primButton.font.size(primButton.text)
        textX = primButton.rect.centerx
        textY = primButton.rect.centery
        textX -= textW/2
        textY -= textH/2
        self.screen.blit(textSurface, (textX, textY))
        # render stroke
        if primButton.stroke :
            pygame.draw.rect(self.screen, (0, 0,0), primButton.rect, 3)
    
    def renderTile(self, tile):
        """
        Render Tile object's terrain, resource, and structure in that order.
        Render rect over tile if hovered
        """
        # offset x and y depending on camera position
        xoffset = self.model.camera.rect.x
        yoffset = self.model.camera.rect.y
        x, y = (tile.rect.x - xoffset), (tile.rect.y - yoffset)
        w, h = tile.size, tile.size
        # determine which image to display based on tileId and blit it
        img = model.terrainTextures[tile.tileId]
        self.screen.blit(img,(x, y))
        # draw resource if tile has one
        if tile.resource: 
             img = model.resourceTextures[tile.resource.recId]
             self.screen.blit(img,(x,y))
        # if hovered, draw rect
        if tile.hovered:
            pygame.draw.rect(self.screen, pygame.Color(0, 0, 0), pygame.Rect(x, y, w, h), 1)

    def initialize(self):
        """
        Set up the pygame graphical display and loads graphical resources.
        """
        result = pygame.init()
        pygame.font.init()
        pygame.display.set_caption('demo game')
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.smallfont = pygame.font.Font(None, 20)
        self.isinitialized = True