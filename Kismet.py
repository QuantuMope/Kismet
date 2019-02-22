import pygame as pg
import pytmx
from pytmx.util_pygame import load_pygame
import sys
import os

def load_image(name):
    image = pg.image.load(name)
    return image

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
        screen = pg.display.set_mode((self.width, self.height))
        self.render(screen)

class Fursa_sprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.idle()

    def idle(self):
        self.directory = "C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Idle"
        os.chdir(self.directory)
        self.images = []
        for file in os.listdir(self.directory):
            self.images.append(load_image(file))

    def update(self):
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.index = 1

class Level_Start:
    def __init__(self):
        os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Level Start")
        self.map = TiledMap('Starting_Area.tmx')
        self.music = pg.mixer.music.load('301 - Good Memories.mp3')
        pg.mixer.music.play(loops = -1, start = 0.0)
        self.map.make_map()

# Game Start
def main():
    pg.init()
    os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet")
    screen = pg.display.set_mode((1280, 640))
    pg.display.set_caption('Kismet')

    Level_Starts = Level_Start()
    Fursa = Fursa_sprite()

    Sprites_list = pg.sprite.Group()
    Sprites_list.add(Fursa)


    while True:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

            if event.type == pg.KEYDOWN:
                user_input = (chr(event.key))
                if user_input == 'c':
                    sys.exit()
        Sprites_list.update()
        Sprites_list.draw(screen)
        pg.display.flip()

if __name__ == '__main__':
    main()
