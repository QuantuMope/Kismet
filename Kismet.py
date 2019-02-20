import pygame
import pytmx
from pytmx.util_pygame import load_pygame
import sys
import os

os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet")
pygame.init()
screen = pygame.display.set_mode((1280, 640))
pygame.display.set_caption('Kismet')

class TiledMap:
    def __init__(self, filename):
        tm = load_pygame(filename)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tm = tm

    def render(self, surface):
        ti = self.tm.get_tile_image_by_gid
        for layer in self.tm.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x*self.tm.tilewidth,y*self.tm.tileheight))

    def make_map(self):
        screen = pygame.display.set_mode((self.width, self.height))
        self.render(screen)

class Level_Start:
    def __init__(self):
        os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Level Start")
        self.map = TiledMap('Starting_Area.tmx')
        pygame.mixer.music.load('301 - Good Memories.mp3')
        pygame.mixer.music.play(loops = -1, start = 0.0)
        self.map.make_map()

# Game Start
Level_Starts = Level_Start()
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:
            user_input = (chr(event.key))
            if user_input == 'c':
                sys.exit()

    pygame.display.flip()
