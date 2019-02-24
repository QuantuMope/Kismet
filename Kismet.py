import pygame as pg
import pytmx
from pytmx.util_pygame import load_pygame
import sys
import os

# Quick function to load images.
def load_image(name):
    image = pg.image.load(name)
    return image

# TiledMap class to render Tiled maps to surfaces.
class TiledMap:
    def __init__(self, filename):
        tm = load_pygame(filename)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tm = tm
        self.blockers = []

    # Renders two surfaces. back_surface is the surface that sprites appear in front of. top_surface vice versa.
    def render(self, back_surface, top_surface):
        ti = self.tm.get_tile_image_by_gid
        self.last_layer = 0
        self.layer_counter = 0
        # Determine last layer.
        for layer in self.tm.visible_tile_layers:
            self.last_layer += 1
        for layer in self.tm.visible_layers:
            self.layer_counter += 1
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = ti(gid)
                    if tile:
                        if self.layer_counter != self.last_layer:
                            back_surface.blit(tile, (x * self.tm.tilewidth, y * self.tm.tileheight))
                        else:
                            top_surface.blit(tile, (x * self.tm.tilewidth, y * self.tm.tileheight))
            elif isinstance(layer, pytmx.TiledObjectGroup):
                self.object_layer = layer
                for object in layer:
                    new_rect = pg.Rect(object.x, object.y, object.width, object.height)
                    self.blockers.append(new_rect)

    def blocks(self):
        self.blockers = []
        tl = self.tm.get_object_by_name('blocker')
        print(tl)
        #for tile_object in self.tm.get_object_by_name('blocker'):

            # properties = tile_object.__dict__
            # if properties['name'] == 'blocker':
            #     x = properties['x']
            #     y = properties['y']
            #     width = properties['width']
            #     height = properties['height']
            #     new_rect = pg.Rect(x, y, width, height)
            #     self.blockers.append(new_rect)
            #     print(self.blockers)


    def make_map(self):
        self.back_surface = pg.Surface((self.width, self.height))
        self.front_surface = pg.Surface((self.width, self.height), pg.SRCALPHA, 32)
        self.render(self.back_surface, self.front_surface)
        print(self.blockers)
        return self.back_surface, self.front_surface

# Fursa sprite. The main character of the game.
class Fursa_sprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frame_index = 0
        self.upload_frames()
        self.current_images = self.idle_images
        self.image = self.idle_images[0]
        self.rect = self.image.get_rect()
        self.key_pressed = False
        # self.change_state = True

    # Function that uploads and stores all possible frames Fursa may use. Is called in __init__.
    def upload_frames(self):
        self.idle_images = []
        self.walk_images = []
        self.all_images = [self.idle_images, self.walk_images]
        self.directories = ["C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Idle"   # Idle Animation
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Walk"]  # Walking Animation

        for i, directory in enumerate(self.directories):
            os.chdir(directory)
            for file in os.listdir(directory):
                self.all_images[i].append(pg.transform.scale(load_image(file), (156, 156)))
        self.frame_index_max = 12

    # Function that changes Fursa's animation depending on the action performed. Called in update().
    def change_state(self):
        if self.key_pressed:
            self.current_images = self.walk_images
        else:
            self.current_images = self.idle_images

    # Function that handles Fursa's key inputs. Called in update().
    def handle_keys(self):
        pg.event.pump()
        keys = pg.key.get_pressed()
        dist = 6
        if keys[pg.K_UP]:
            self.rect.y -= dist
        if keys[pg.K_RIGHT]:
            self.rect.x += dist
        if keys[pg.K_DOWN]:
            self.rect.y += dist
        if keys[pg.K_LEFT]:
            self.rect.x -= dist

    # Function that updates Fursa's frames and positioning. Called continuously in game loop main().
    def update(self):
        self.handle_keys()
        self.change_state()
        self.image = self.current_images[self.frame_index]
        self.frame_index += 1
        if self.frame_index == self.frame_index_max:
            self.frame_index = 0

# Starting area. Stores map and music data.
class Level_Start:
    def __init__(self):
        os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Level Start")
        self.map = TiledMap('Starting_Area.tmx')
        #self.music = pg.mixer.music.load('301 - Good Memories.mp3')
        #pg.mixer.music.play(loops = -1, start = 0.0)
        self.map.make_map()

# Game Loop
def main():
    # Game parameters.
    pg.init()
    os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet")
    screen = pg.display.set_mode((1280, 640))
    pg.display.set_caption('Kismet')
    clock = pg.time.Clock()

    # Declare objects.
    Starting_Area = Level_Start()
    Fursa = Fursa_sprite()
    Sprites_list = pg.sprite.Group()
    Sprites_list.add(Fursa)


    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                Fursa.key_pressed = True
            else:
                Fursa.key_pressed = False

        # Screen Background Refresh
        screen.blit(Starting_Area.map.back_surface, (0,0))

        # Sprites update.
        Sprites_list.update()
        Sprites_list.draw(screen)

        screen.blit(Starting_Area.map.front_surface, (0,0))

        clock.tick(10) # Framerate.

        pg.display.flip()

if __name__ == '__main__':
    main()
