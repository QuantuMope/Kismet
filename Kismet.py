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
        # Determine last tile layer.
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
                for object in layer:
                    new_rect = pg.Rect(object.x, object.y, object.width, object.height)
                    self.blockers.append(new_rect)

    def make_map(self):
        self.back_surface = pg.Surface((self.width, self.height))
        self.front_surface = pg.Surface((self.width, self.height), pg.SRCALPHA, 32)
        self.render(self.back_surface, self.front_surface)
        return self.back_surface, self.front_surface

# Fursa sprite. The main character of the game.
class Fursa_sprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frame_index = 0
        self.upload_frames()
        self.current_images = self.idle_images
        self.image = self.idle_images[0]
        self.state = 0
        self.rect = pg.Rect((0, 0), (156, 124)) # Spawn point and collision size.
        self.key_pressed = False
        self.gravity_dt = 0
        self.frame_dt = 0
        self.jump_dt = 0
        self.fall_rate = 1
        self.jump_rate = 20
        self.jump_index = 0
        self.dist = 1
        self.jump = False
        os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas")
        self.jump_noise = pg.mixer.Sound("jump_02.wav")

    # Function that uploads and stores all possible frames Fursa may use. Is called in __init__.
    def upload_frames(self):
        self.idle_images = []
        self.walk_images = []
        self.run_images = []
        self.attack_images = []
        self.shield_images = []
        self.death_images = []
        self.all_images = [self.idle_images, self.walk_images, self.run_images, self.attack_images, self.shield_images, self.death_images]

        self.directories = ["C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Idle"       # Idle animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Walk"       # Walking animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Run"        # Run animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Attack_01"  # Attack animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Attack_02"  # Shield animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Death"]     # Death animation.

        for i, directory in enumerate(self.directories):
            os.chdir(directory)
            for file in os.listdir(directory):
                self.all_images[i].append(pg.transform.scale(load_image(file), (156, 156)))
        self.frame_maxes = [len(images) for images in self.all_images]

    # Function that changes Fursa's animation depending on the action performed. Called in update().
    def change_state(self):
        if self.key_pressed:
            self.current_images = self.walk_images
            self.state = 1
        else:
            self.current_images = self.idle_images
            self.state = 0

    # Function that handles Fursa's key inputs. Called in update().
    def handle_keys(self):

        # Monitor held down keys. (movement)
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            self.rect.y -= self.dist
        if keys[pg.K_RIGHT]:
            self.rect.x += self.dist
        if keys[pg.K_DOWN]:
            self.rect.y += self.dist
        if keys[pg.K_LEFT]:
            self.rect.x -= self.dist

        # Pygame event loop.
        for event in pg.event.get():

            # Allow to quit game.
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            # Monitor single key presses. (actions)
            if event.type == pg.KEYDOWN:
                self.key_pressed = True

                # Jump input.
                if event.key == pg.K_SPACE:
                    self.jump_noise.play()
                    self.jump = True    # ----------------> Jump starts.

            else:
                self.key_pressed = False

        # Jumping animation triggered by space key press.
        # Jump code is placed outside event loop so that the animation can carry out.
        if self.jump is True:
            if (self.time - self.jump_dt) >= 40:
                self.jump_dt = self.time
                self.jump_rate *= 0.8 # Jump deceleration.
                self.jump_index += 1
                for i in range(int(self.jump_rate)):
                    self.rect.y -= 1
                    if self.jump_index == 5:
                        self.jump = False   # ----------------> Jump finishes.
                        self.jump_rate = 20
                        self.jump_index = 0
                        break

    # Function that updates Fursa's frames and positioning. Called continuously in game loop main().
    def update(self, blockers):

        self.time = pg.time.get_ticks()
        self.handle_keys()
        self.change_state()

        # Cycle through frames every 0.25 seconds.
        if (self.time - self.frame_dt) >= 250:
            self.frame_dt = self.time
            self.image = self.current_images[self.frame_index]
            self.frame_index += 1
            if self.frame_index == self.frame_maxes[self.state]:
                self.frame_index = 0

        # Gravity Emulation
        for block in blockers:
            if self.rect.colliderect(block):
                pass
            else:
                # Gravity is disabled when a jump animation is in progress.
                if (self.time - self.gravity_dt) >= 20 and self.jump is False:
                    self.gravity_dt = self.time
                    self.fall_rate *= 1.1 # Acceleration rate.
                    for i in range(int(self.fall_rate)):
                        self.rect.y += 1
                        if self.rect.colliderect(block):
                            self.fall_rate = 1
                            break

# Starting area. Stores map and music data.
class Level_Start:
    def __init__(self):
        os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Level Start")
        self.map = TiledMap('Starting_Area.tmx')
        self.music = pg.mixer.music.load('301 - Good Memories.mp3')
        pg.mixer.music.play(loops = -1, start = 0.0)
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

        # Screen background back surface refresh.
        screen.blit(Starting_Area.map.back_surface, (0,0))

        # Sprites update.
        Sprites_list.update(Starting_Area.map.blockers)
        Sprites_list.draw(screen)

        # Screen background front surface refresh.
        screen.blit(Starting_Area.map.front_surface, (0,0))

        clock.tick(120) # Framerate.

        pg.display.flip()

if __name__ == '__main__':
    main()
