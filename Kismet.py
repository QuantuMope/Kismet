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
        self.surface = pg.Surface((self.width, self.height))
        self.render(self.surface)
        return self.surface

class Fursa_sprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # self.idle()
        self.frame_index = 0
        self.movex = 1
        self.movey = 1

    def idle(self):
        self.directory = "C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Idle"
        os.chdir(self.directory)
        self.images = []
        for file in os.listdir(self.directory):
            self.images.append(pg.transform.scale(load_image(file), (156, 156)))
        self.frame_index_max = len(self.images)

    def walk(self):
        self.directory = "C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Walk"
        os.chdir(self.directory)
        self.images = []
        for file in os.listdir(self.directory):
            self.images.append(pg.transform.scale(load_image(file), (156, 156)))
        self.frame_index_max = len(self.images)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

    def handle_keys(self):
        self.spaceholder = 9
        # if event.type == pg.KEYDOWN:
        #     dist = 1
        #     if event.key == pygame.K_UP:
        #         angle = 0
        #         head.rotate(angle, 0, -8)
        #     elif event.key == pygame.K_RIGHT:
        #         angle = 270
        #         head.rotate(angle, 8, 0)
        #     elif event.key == pygame.K_DOWN:
        #         angle = 180
        #         head.rotate(angle, 0, 8)
        #     elif event.key == pygame.K_LEFT:
        #         angle = 90
        #         head.rotate(angle, -8, 0)
        #     counter = 0

    def update(self):
        self.image = self.images[self.frame_index]
        self.frame_index += 1
        if self.frame_index == self.frame_index_max:
            self.frame_index = 0
        self.rect.x += 1

class Level_Start:
    def __init__(self):
        os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Level Start")
        self.map = TiledMap('Starting_Area.tmx')
        self.music = pg.mixer.music.load('301 - Good Memories.mp3')
        pg.mixer.music.play(loops = -1, start = 0.0)
        self.map.make_map()

# Game Loop
def main():
    pg.init()
    os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet")
    screen = pg.display.set_mode((1280, 640))
    Sprite_surface = pg.Surface((1280, 640))
    pg.display.set_caption('Kismet')
    clock = pg.time.Clock()

    Starting_Area = Level_Start()
    Fursa = Fursa_sprite()
    Fursa.walk()
    Sprites_list = pg.sprite.Group()
    Sprites_list.add(Fursa)


    while True:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                user_input = (chr(event.key))
                if user_input == 'c':
                    sys.exit()

        # Screen Background Refresh
        screen.blit(Starting_Area.map.surface, (0,0))
        Sprites_list.update()
        Sprites_list.draw(screen)

        clock.tick(10)
        pg.display.flip()

if __name__ == '__main__':
    main()
