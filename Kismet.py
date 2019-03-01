import pygame as pg
import pytmx
from pytmx.util_pygame import load_pygame
import sys
import os
from time import sleep

""" For Fursa class, due to the length, separate functions within the class are
    separated by teal dashed lines as shown below."""
    #----------------------------------------------------


# Quick function to load images.
def load_image(name):
    image = pg.image.load(name).convert_alpha()
    return image

# Spritesheet class to split sprite sheets into proper single frames.
class spritesheet(object):
    def __init__(self, filename):
        self.sheet = pg.image.load(filename).convert()

    # Load a specific image from a specific rectangle.
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pg.RLEACCEL)
        return image

    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates"
        return [self.image_at(rect, colorkey) for rect in rects]

    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

# TiledMap class to properly render Tiled maps by layer to surfaces.
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
        self.back_surface = pg.Surface((self.width, self.height)).convert()
        self.front_surface = pg.Surface((self.width, self.height), pg.SRCALPHA, 32).convert_alpha()
        self.render(self.back_surface, self.front_surface)
        return self.back_surface, self.front_surface

# ----------------------------------------------------PLAYER-------------------------------------------------------------------
# Fursa sprite. The main character of the game.
class Fursa_sprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frame_index = 0
        self.upload_frames() # Uploads all frames. Function found below.
        self.current_images = self.all_images[0]
        self.image = self.current_images[0]
        self.state = 0
        self.facing_right = True
        self.frame_override = True
        self.rect = pg.Rect((0, 0), (128, 102)) # Spawn point and collision size.
        self.key_pressed = False
        self.gravity_dt = 0
        self.frame_dt = 0
        self.jump_dt = 0
        self.fall_rate = 1
        self.jump_rate = 20
        self.jump_index = 0
        self.speed = 1 # @pixel/frame. At approx 80 fps --> 80 pixel/sec
        self.jump = False
        self.attack = False
        self.frame_speed = 200

        # Load sound effects.
        os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas")
        self.jump_noise = pg.mixer.Sound("jump_02.wav")
        self.attack_noise = pg.mixer.Sound("Electro_Current_Magic_Spell.wav")
        self.attack_charge = pg.mixer.Sound("charge_up.wav")

#-------------------------------------------------------------------------------------------------------------------------------
    # Function that uploads and stores all possible frames Fursa may use. Is called in __init__.
    # Created separately for organizational purposes.
    def upload_frames(self):
        idle_images = []
        walk_images = []
        run_images = []
        attack_images = []
        shield_images = []
        death_images = []

        # State IDs
        #-----------------------0------------1------------2------------3--------------4--------------5-----------#
        self.all_images = [idle_images, walk_images, run_images, attack_images, shield_images, death_images]

        directories =      ["C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Idle"          # Idle animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Walk"          # Walking animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Run"           # Run animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Attack_01"     # Attack animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Attack_02"     # Shield animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas/Death"]        # Death animation.

        # Create a list containing lists with all animation frames. Each list is referenceable by the state ID shown above.
        for i, directory in enumerate(directories):
            os.chdir(directory)
            for file in os.listdir(directory):
                self.all_images[i].append(pg.transform.scale(load_image(file), (128, 128)))

        # Create a list of number of frames for each animation.
        self.frame_maxes = [len(images) for images in self.all_images]

#-------------------------------------------------------------------------------------------------------------------------------
    # Function that changes Fursa's animation depending on the action performed.
    # Continuously called in self.update().
    def change_state(self):

        # Each frame list has a state ID that can be found outlined in self.upload_frames().
        # Each animation type has its own fps.
        if self.attack:
            self.state = 3
            self.current_images = self.all_images[self.state]
            self.frame_speed = 75
        elif self.key_pressed and self.shift:
            self.state = 2
            self.current_images = self.all_images[self.state]
            self.frame_speed = 100
        elif self.key_pressed:
            self.state = 1
            self.current_images = self.all_images[self.state]
            self.frame_speed = 150
        else:
            self.state = 0
            self.current_images = self.all_images[self.state]
            self.frame_speed = 200
#-------------------------------------------------------------------------------------------------------------------------------

    """
        Function that handles Fursa's key inputs. Called in update().
        Split into two sections:
        1. Monitoring held down keys and combinations.
        2. Monitoring single key press events.
        Due to the nature of pygame, both have to be used in tandem to
        create fluid game controls.
    """

    def handle_keys(self):

        # Monitor held down keys. (movement)
        # If attack animation is not in progress, move in the direction of the pressed key.
        if self.attack == False:
            keys = pg.key.get_pressed()
            if keys[pg.K_w]:
                self.rect.y -= self.speed
            if keys[pg.K_d]:
                self.rect.x += self.speed
                self.key_pressed = True  # Self.key_pressed() is fed back to change_state(). Found several times throughout handle_keys().
            if keys[pg.K_s]:
                self.rect.y += self.speed
            if keys[pg.K_a]:
                self.rect.x -= self.speed
                self.key_pressed = True
            # Running changes speed by holding down shift.
            # Self.shift is fed back to change_state().
            if keys[pg.K_LSHIFT]:
                self.shift = True
                self.speed = 2
            else:
                self.shift = False
                self.speed = 1

        # Pygame event loop.
        for event in pg.event.get():

            # Allow to quit game. Included in this portion to be able to keep only one event loop.
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            # Monitor single key presses. (actions)
            # If a key is pressed and an attack animation is not in progress, register the key press.
            if event.type == pg.KEYDOWN and self.attack == False:

                self.key_pressed = True
                self.frame_index = 0 # Frame reset when key is pressed.

                # Registers which way Fursa should be facing. Fed to self.update().
                if event.key == pg.K_d:
                    self.facing_right = True
                if event.key == pg.K_a:
                    self.facing_right = False

                # Enables attack animation.
                # Self.attack set to True prevents other key inputs to be registered until the animation is completed.
                if event.key == pg.K_r:
                    self.attack = True
                    self.attack_charge.play()

                # Jump input.
                if event.key == pg.K_SPACE:
                    self.jump_noise.play()
                    self.jump = True    # ----------------> Jump starts.

            # Frame reset when key is no longer held down. Self.key_pressed set to False to change state to idle.
            elif event.type == pg.KEYUP and self.attack == False:
                self.frame_index = 0
                self.key_pressed = False

            else:
                self.key_pressed = False

        # Jumping animation triggered by space key press.
        # Jump code is placed outside event loop so that the animation can carry out.
        # Decelerates every 60 ms.
        if self.jump is True:
            if (self.time - self.jump_dt) >= 60:
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
#-------------------------------------------------------------------------------------------------------------------------------

    # Function that updates Fursa's frames and positioning. Called continuously in game loop main().
    # Must be fed the blockers of the current map.
    def update(self, blockers):

        # Previous functions.
        self.time = pg.time.get_ticks()
        self.handle_keys()
        self.change_state()

        """
            Cycle through frames depending on self.frame_speed that is set in self.change_state().
            Flip the frame image vertically depending on which direction Fursa is facing.
            Self.frame_override is a boolean representing the previous state of self.facing_right.
            If the direction that Fursa is facing has changed before a frame can be refreshed,
            bypasses frame timer and resets the to avoid Fursa momentarily moving facing the wrong direction.
        """

        if (self.time - self.frame_dt) >= self.frame_speed or self.facing_right != self.frame_override:
            self.frame_dt = self.time

            if self.facing_right:
                self.image = self.current_images[self.frame_index]
                self.frame_index += 1
                self.frame_override = True
            else:
                self.image = pg.transform.flip(self.current_images[self.frame_index], True, False)
                self.frame_index += 1
                self.frame_override = False

            # Resets frame index if the max for a certain animation is reached.
            # Also, sets attack animation back to False in case the action was an attack.
            if self.frame_index == self.frame_maxes[self.state]:
                self.attack = False
                self.frame_index = 0

            # Play attack noise at the correct frame.
            if self.attack == True and self.frame_index == 8:
                self.attack_noise.play()

        # Gravity emulation with current map blockers.
        for block in blockers:
            # Checks to see if Fursa is in contact with the ground.
            if self.rect.colliderect(block):
                pass
            else:
                # If not in contact with the ground, accelerates falling down every 20 ms.
                # Gravity is disabled when a jump animation is in progress.
                if (self.time - self.gravity_dt) >= 20 and self.jump is False:
                    self.gravity_dt = self.time
                    self.fall_rate *= 1.1 # Acceleration rate.
                    for i in range(int(self.fall_rate)):
                        self.rect.y += 1
                        # Halts falling when Fursa lands on a block.
                        if self.rect.colliderect(block):
                            self.fall_rate = 1
                            break

# ----------------------------------------------------ENEMIES-------------------------------------------------------------------
class skeleton(pg.sprite.Sprite):
    def __init__(self, frames):
        super().__init__()
        self.frames = frames.skeleton_frames
        self.frame_max = len(frames.skeleton_frames[0])
        self.idle = self.frames[0]
        self.image = self.idle[0]
        self.rect = pg.Rect(400, 400, 96, 96)
        self.i = 0

    def update(self, blockers):
        self.image = self.idle[self.i]
        self.i += 1
        if self.i == self.frame_max:
            self.i = 0
        self.blockers = blockers

class enemy_frames():
    def __init__(self):
        self.skeleton_frames = []
        self.skeleton_frames_func()

    def skeleton_frames_func(self):
        directory = "C:/Users/Andrew/Desktop/Python_Projects/Kismet/Enemies/Skeleton/Sprite Sheets"
        os.chdir(directory)

        # Spritesheet coordinates.                                                               Indexes
        coordinates = [
                         [(24 * i, 0, 24, 32) for i in range(0, 11)]       # Idle. -----------------0
                        ,[(22 * i, 0, 22, 33) for i in range(0, 13)]       # Walking----------------1
                        ,[(22 * i, 0, 22, 32) for i in range(0, 4 )]       # React------------------2
                        ,[(43 * i, 0, 43, 37) for i in range(0, 18)]       # Attacking--------------3
                        ,[(30 * i, 0, 30, 32) for i in range(0, 8) ]       # Hit--------------------4
                        ,[(33 * i, 0, 33, 32) for i in range(0, 15)]       # Death------------------5
                      ]

        sizes = [(72,96), (66,99), (66,96), (129,111), (90,96), (99,96)]

        spritesheets = [spritesheet(file) for file in os.listdir(directory)]
        spritesheets_separate = [spritesheet.images_at(coordinates[i], colorkey = (0, 0, 0)) for i, spritesheet in enumerate(spritesheets)]

        for i, ss_sep in enumerate(spritesheets_separate):
            scaled_frames = [pg.transform.scale(ss_sep[e], sizes[i]) for e in range(0, len(ss_sep))]
            self.skeleton_frames.append(scaled_frames)


# Class simply containing projectile frames of various attacks.
# Created to avoid having to load from the hard drive every time a projectile is created.
class blast_frames():
    def __init__(self):

        # Fursa's attack blast properly separated into frames into a list from a spritesheet.
        os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Furas")
        coordinates = [(128 * i, 0, 128, 128) for i in range(0,8)]
        blast_image_ss = spritesheet('EnergyBall.png')
        blast_images_separate = blast_image_ss.images_at(coordinates, colorkey = (0, 0, 0))
        self.blast_images = [pg.transform.scale(blast_images_separate[i], (48, 48)) for i in range(0, len(blast_images_separate))]

# Fursa's blast projectile sprite.
class Fursa_blast(pg.sprite.Sprite):
    def __init__(self, blast_images):
        super().__init__()
        self.images = blast_images
        self.image = blast_images[0]
        self.rect = pg.Rect(-100, 0, 64, 64) # Random spawn location off map just for initialization.
        self.spawn = False
        self.i = 0
        self.already_spawned = False

    def update(self, Fursa, particle_sprites):

        # At the proper frame during Fursa's attack animation, place blast coming out of Fursa's hand.
        if Fursa.attack == True and Fursa.frame_index == 8:
            # Self.already_spawned is initially set to False. Once Fursa summons the blast it is set to True,
            # so that existing blasts aren't affected by additional attacks in the future.
            if self.already_spawned == False:
                self.rect.x = Fursa.rect.x + 70
                self.rect.y = Fursa.rect.y + 52
                self.image = self.images[0]
                self.spawn = True
                self.already_spawned = True

                # Creates another blast sprite and stores it in sprite group ready for Fursa.
                sleep(0.05) # Waits 50 ms to allow frame index to change so two blasts are not spawned.
                blast_particle = Fursa_blast(self.images)
                particle_sprites.add(blast_particle)

        # Once blast is spawned by Fursa, will keep traveling across map until it hits the
        # right of left edge of the map in which case the sprite will be killed.
        if self.spawn:
            self.rect.x += 3
            self.i += 1
            self.image = self.images[self.i] # Frame changing.
            if self.i == 7:
                self.i = 0

            if self.rect.right > 1280 or self.rect.right < 0:
                self.kill()

# Starting area. Stores map and music data.
class Level_Start:
    def __init__(self):
        os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Level Start")
        self.map = TiledMap('Starting_Area.tmx')
        self.music = pg.mixer.music.load('301 - Good Memories.mp3')
        #pg.mixer.music.play(loops = -1, start = 0.0)
        self.map.make_map()

# Game Start.
def main():

    # Game parameters.
    pg.mixer.pre_init(44100, -16, 2, 512)
    pg.init()
    os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet")
    size = width, height = 1280, 640
    screen = pg.display.set_mode(size)
    pg.display.set_caption('Kismet')
    clock = pg.time.Clock()

    # Declare Maps.
    Starting_Area = Level_Start()

    # Declare character sprites.
    Fursa = Fursa_sprite()
    character_sprites = pg.sprite.Group()
    character_sprites.add(Fursa)

    enemy_images = enemy_frames()
    skeleton_01 = skeleton(enemy_images)
    character_sprites.add(skeleton_01)

    # Declare particle sprites.
    blast_particle_frames = blast_frames()
    blast_images = blast_particle_frames.blast_images
    blast_particle = Fursa_blast(blast_images)
    particle_sprites = pg.sprite.Group()
    particle_sprites.add(blast_particle)

    # Game Loop
    while True:

        # Surfaces are blit and updated in order of back to front on screen.

        # Layer 1-------- Screen background back surface refresh.
        screen.blit(Starting_Area.map.back_surface, (0,0))

        # Layer 2-------- Particle sprites update.
        particle_sprites.update(Fursa, particle_sprites)
        particle_sprites.draw(screen)

        # Layer 3-------- Character sprites update.
        character_sprites.update(Starting_Area.map.blockers)
        character_sprites.draw(screen)

        # Layer 4-------- Screen background front surface refresh.
        screen.blit(Starting_Area.map.front_surface, (0,0))

        clock.tick(90) # Framerate.
        print(clock)

        pg.display.flip()

if __name__ == '__main__':
    main()
