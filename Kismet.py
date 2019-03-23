import pygame as pg
import pygame.freetype
import pytmx
from pytmx.util_pygame import load_pygame
import sys
import os
from time import sleep
import random

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

# ----------------------------------------------------PLAYERS-------------------------------------------------------------------
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
        self.rect = pg.Rect((200, 0), (128, 102)) # Spawn point and collision size.
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
        self.hit = False
        self.hp = 3

        # Load sound effects.
        os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Fursa")
        self.jump_noise = pg.mixer.Sound("jump_02.wav")
        self.attack_noise = pg.mixer.Sound("Electro_Current_Magic_Spell.wav")
        self.attack_charge = pg.mixer.Sound("charge_up.wav")

    # Function that uploads and stores all possible frames Fursa may use. Is called in __init__.
    # Created separately for organizational purposes.
    def upload_frames(self):
        idle_images = []
        walk_images = []
        run_images = []
        attack_images = []
        shield_images = []
        hit_images = []
        death_images = []

        # State IDs
        #-----------------------0------------1------------2------------3--------------4--------------5-----------6-------#
        self.all_images = [idle_images, walk_images, run_images, attack_images, shield_images, death_images, hit_images]

        directories =      ["C:/Users/Andrew/Desktop/Python_Projects/Kismet/Fursa/Idle"          # Idle animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Fursa/Walk"          # Walking animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Fursa/Run"           # Run animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Fursa/Attack_01"     # Attack animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Fursa/Attack_02"     # Shield animation.
                           ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Fursa/Death"]        # Hit & Death animation.

        # Create a list containing lists with all animation frames. Each list is referenceable by the state ID shown above.
        for i, directory in enumerate(directories):
            os.chdir(directory)
            for file in os.listdir(directory):
                self.all_images[i].append(pg.transform.scale(load_image(file), (128, 128)))

        self.all_images[6] = (self.all_images[5][0:7])

        # Create a list of number of frames for each animation.
        self.frame_maxes = [len(images) for images in self.all_images]

    # Function that changes Fursa's animation depending on the action performed.
    # Continuously called in self.update().
    def change_state(self):

        # Each frame list has a state ID that can be found outlined in self.upload_frames().
        # Each animation type has its own fps.
        if self.hit:
            self.state = 6
            self.frame_speed = 25
        elif self.attack:
            self.state = 3
            self.frame_speed = 75
        elif self.key_pressed and self.shift:
            self.state = 2
            self.frame_speed = 100
        elif self.key_pressed:
            self.state = 1
            self.frame_speed = 150
        else:
            self.state = 0
            self.frame_speed = 200

        self.current_images = self.all_images[self.state]

    """
        Function that handles Fursa's key inputs. Called in update().
        Split into two sections:
        1. Monitoring held down keys and combinations.
        2. Monitoring single key press events.
        Due to the nature of pygame, both have to be used in tandem to
        create fluid game controls.
    """

    def handle_keys(self, time, cutscene):
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

                if event.key == pg.K_ESCAPE:
                     pg.quit()
                     sys.exit()

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
            if (time - self.jump_dt) >= 60:
                self.jump_dt = time
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
    # Must be fed the blockers of the current map.
    def update(self, blockers, time, enemy_sprites, cutscene):

        # Disallow any key input if cutscene is in progress.
        if cutscene is False:
            self.handle_keys(time, cutscene)
            self.change_state()
        else:
            self.state = 0
            self.frame_speed = 200
            self.current_images = self.all_images[self.state]

        """
            Cycle through frames depending on self.frame_speed that is set in self.change_state().
            Flip the frame image vertically depending on which direction Fursa is facing.
            Self.frame_override is a boolean representing the previous state of self.facing_right.
            If the direction that Fursa is facing has changed before a frame can be refreshed,
            bypasses frame timer and resets the to avoid Fursa momentarily moving facing the wrong direction.
        """


        if (time - self.frame_dt) >= self.frame_speed or self.facing_right != self.frame_override:
            self.frame_dt = time

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
                self.hit = False
                self.frame_index = 0

            # Play attack noise at the correct frame.
            if self.attack == True and self.frame_index == 8:
                self.attack_noise.play()

        for enemy in enemy_sprites:
            if enemy.attack and enemy.frame_index == 7:
                if self.rect.collidepoint(enemy.rect.x + 50, enemy.rect.centery + 20):
                    self.frame_index = 0
                    self.hp -= 1
                    self.hit = True

            # elif self.flow_right is False:
            #     if self.rect.collidepoint(enemy.rect.x + 20, enemy.rect.centery + 20):
            #         self.particle_hit = True

        # Gravity emulation with current map blockers.
        for block in blockers:
            # Checks to see if Fursa is in contact with the ground.
            if self.rect.colliderect(block):
                pass
            else:
                # If not in contact with the ground, accelerates falling down every 20 ms.
                # Gravity is disabled when a jump animation is in progress.
                if (time - self.gravity_dt) >= 20 and self.jump is False:
                    self.gravity_dt = time
                    self.fall_rate *= 1.1 # Acceleration rate.
                    for i in range(int(self.fall_rate)):
                        self.rect.y += 1
                        # Halts falling when Fursa lands on a block.
                        if self.rect.colliderect(block):
                            self.fall_rate = 1
                            break

# Class simply containing projectile frames of various attacks.
# Created to avoid having to load from the hard drive every time a projectile is created.
class blast_frames():
    def __init__(self):

        # Fursa's attack blast properly separated into frames into a list from a spritesheet.
        os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Fursa")
        coordinates = [(128 * i, 0, 128, 128) for i in range(0,8)]
        blast_image_ss = spritesheet('EnergyBall.png')
        blast_images_separate = blast_image_ss.images_at(coordinates, colorkey = (0, 0, 0))
        self.blast_images_r = [pg.transform.scale(blast_images_separate[i], (48, 48)) for i in range(0, len(blast_images_separate))]
        self.blast_images_l = [pg.transform.flip(self.blast_images_r[i], True, False) for i in range(0, len(self.blast_images_r))]

        # Impact frames.
        coordinates = [(0, 128 * i, 128, 128) for i in range(0,8)]
        impact_images_ss = spritesheet('energyBallImpact.png')
        impact_images_separate = impact_images_ss.images_at(coordinates, colorkey = (0, 0, 0))
        self.impact_images_r = [pg.transform.scale(impact_images_separate[i], (48, 48)) for i in range(0, len(impact_images_separate))]
        self.impact_images_l = [pg.transform.flip(self.impact_images_r[i], True, False) for i in range(0, len(self.impact_images_r))]

# Fursa's blast projectile sprite.
class Fursa_blast(pg.sprite.Sprite):
    def __init__(self, blast_images_r, blast_images_l, impact_images_r, impact_images_l):
        super().__init__()
        self.blast_images_r = blast_images_r
        self.blast_images_l = blast_images_l
        self.impact_images_r = impact_images_r
        self.impact_images_l = impact_images_l
        self.images = blast_images_r
        self.impact = impact_images_r
        self.image = blast_images_r[0]
        self.rect = pg.Rect(-100, 0, 64, 64) # Random spawn location off map just for initialization.
        self.spawn = False
        self.i = 0
        self.e = 0
        self.already_spawned = False
        self.flow_right = True
        self.particle_hit = False

    def update(self, Fursa, particle_sprites, enemy_sprites):

        # At the proper frame during Fursa's attack animation, place blast coming out of Fursa's hand.
        if Fursa.attack == True and Fursa.frame_index == 8:

            # Self.already_spawned is initially set to False. Once Fursa summons the blast it is set to True,
            # so that existing blasts aren't affected by additional attacks in the future.
            if self.already_spawned == False:

                if Fursa.facing_right:
                    self.flow_right = True
                else:
                    self.flow_right = False

                if self.flow_right:
                    self.rect.x = Fursa.rect.x + 70
                    self.rect.y = Fursa.rect.y + 52
                    self.images = self.blast_images_r
                    self.impact = self.impact_images_r

                    self.image = self.images[0]
                    self.spawn = True
                    self.already_spawned = True
                    # Creates another blast sprite and stores it in sprite group ready for Fursa.
                    sleep(0.05) # Waits 50 ms to allow frame index to change so two blasts are not spawned.
                    particle_sprites.add(Fursa_blast(self.blast_images_r, self.blast_images_l, self.impact_images_r, self.impact_images_l))


                else:
                    self.rect.x = Fursa.rect.x + 20
                    self.rect.y = Fursa.rect.y + 52
                    self.images = self.blast_images_l
                    self.impact = self.impact_images_l

                    self.image = self.images[0]
                    self.spawn = True
                    self.already_spawned = True
                    # Creates another blast sprite and stores it in sprite group ready for Fursa.
                    sleep(0.05) # Waits 50 ms to allow frame index to change so two blasts are not spawned.
                    particle_sprites.add(Fursa_blast(self.blast_images_r, self.blast_images_l, self.impact_images_r, self.impact_images_l))

        # Once blast is spawned by Fursa, will keep traveling across map until it hits the
        # right of left edge of the map in which case the sprite will be killed.
        if self.spawn and self.particle_hit is False:
            if self.images == self.blast_images_r:
                self.rect.x += 3
            else:
                self.rect.x -= 3

            self.image = self.images[self.i] # Frame changing.
            self.i += 1
            if self.i == 8:
                self.i = 0

            if self.rect.right > 1280 or self.rect.left < 0:
                self.spawn = False
                self.kill()

        elif self.spawn and self.particle_hit:

            self.images = self.impact
            self.image = self.images[self.e] # Frame changing.
            self.e += 1
            if self.e == 8:
                self.kill()
                self.particle_hit = False

        for enemy in enemy_sprites:
            if self.flow_right:
                if self.rect.collidepoint(enemy.rect.x + 50, enemy.rect.centery + 20):
                    self.particle_hit = True
            elif self.flow_right is False:
                if self.rect.collidepoint(enemy.rect.x + 20, enemy.rect.centery + 20):
                    self.particle_hit = True

# ----------------------------------------------------ENEMIES-------------------------------------------------------------------
class skeleton(pg.sprite.Sprite):
    def __init__(self, frames):
        super().__init__()
        self.frames = frames.skeleton_frames
        self.frame_maxes = frames.skeleton_frame_maxes
        self.current_images = self.frames[0] # Idle
        self.image = self.current_images[0]
        self.prev_state = 0
        self.state = 0
        self.rect = pg.Rect(1200, 400, 72, 96)
        self.frame_index = 0
        self.frame_dt = 0
        self.frame_speed = 100
        self.facing_right = True
        self.frame_override = True
        self.gravity_dt = 0
        self.fall_rate = 1
        self.jump = False
        self.aggroed = False
        self.reaction_done = False
        self.chase = False
        self.attack = False
        self.pre_engaged_dt = 0
        self.one_shot = True
        self.change_state = False
        self.pstate = 0
        self.cstate = 0
        self.hit = False
        self.hp = 3

    # Skeleton AI.
    def AI(self, blockers, time, character, particle_sprites):

        self.prev_state = self.state

        if self.hit is False:
            # When not aggroed, pace back and forth spawn location.
            if not self.aggroed:
                if (time - self.pre_engaged_dt) >= 2500:
                    self.pre_engaged_dt = time
                    self.state ^= 1
                    if self.state == 0: # Idle
                        pass
                    if self.state == 1:
                        self.facing_right = not self.facing_right
                    self.frame_index = 0
                if self.state == 1:
                    if self.facing_right:
                        self.rect.x += 1
                    else:
                        self.rect.x -= 1

            # for block in blockers:
            #     if self.rect.left <= block.left or self.rect.right >= block.right:
            #         self.state == 0

            # If within aggro range, switch animation to react.
            if abs(self.rect.centerx - character.rect.centerx) < 200 and not self.aggroed:
                self.frame_speed = 400
                self.state = 2
                self.aggroed = True
                self.frame_index = 0

            # Allow for reaction frames to finish.
            if self.state == 2 and self.frame_index == 4:
                self.chase = True
                self.frame_index = 0

            # When aggroed and reaction is done, move towards the player.
            if self.attack == False:
                if self.aggroed and self.chase:
                    self.state = 1
                    self.frame_speed = 100
                    if (self.rect.centerx - character.rect.centerx) > 0:
                        self.facing_right = False
                        self.rect.x -= 1
                    else:
                        self.facing_right = True
                        self.rect.x += 1

            # Start attack animation.
            if abs(self.rect.centerx - character.rect.centerx) < 100 and self.chase:
                self.attack = True
                self.frame_speed = 150
                self.state = 3

            for particle in particle_sprites:
                if particle.particle_hit is True:
                    self.chase = True
                    self.aggroed = True
                    self.hit = True
                    self.frame_speed = 150
                    self.state = 4
                    self.hp -= 1

        if self.hp <= 0:
            self.state = 5

        if self.prev_state != self.state:
            self.change_state = True
            self.pstate = self.prev_state
            self.cstate = self.state

    def change_rect_by_state(self, old_state, new_state, self_facing):
        self.frame_index = 0
        sizes = [(72,96), (66,99), (66,96), (129,111), (90,96), (99,96)]
        old_size_x = sizes[old_state][0]
        new_size_x = sizes[new_state][0]
        old_size_y = sizes[old_state][1]
        new_size_y = sizes[new_state][1]
        x_dt = new_size_x - old_size_x
        y_dt = new_size_y - old_size_y
        self.rect.width = old_size_x + x_dt
        self.rect.height = old_size_y + y_dt
        self.rect.y -= y_dt
        if self.facing_right is not True and new_state != 4: self.rect.x -= x_dt

    def update(self, blockers, time, character, particle_sprites):

        self.AI(blockers, time, character, particle_sprites)

        # Frame update and flipping.

        if (time - self.frame_dt) >= self.frame_speed or self.facing_right != self.frame_override:
            self.frame_dt = time

            self.current_images = self.frames[self.state]

            if self.change_state is True:
                self.change_rect_by_state(self.pstate, self.cstate, self.facing_right)
                self.change_state = False

            if self.facing_right:
                self.image = self.current_images[self.frame_index]
                self.frame_index += 1
                self.frame_override = True
            else:
                self.image = pg.transform.flip(self.current_images[self.frame_index], True, False)
                self.frame_index += 1
                self.frame_override = False

            if self.frame_index == self.frame_maxes[self.state]:
                if self.state == 2:
                    pass
                elif self.state == 5:
                    self.kill()
                else:
                    self.attack = False
                    self.hit = False
                    self.frame_index = 0


        # Gravity emulation with current map blockers.
        # Same as Fursa. Additional comments can be found there.
        for block in blockers:
            if self.rect.colliderect(block):
                pass
            else:
                if (time - self.gravity_dt) >= 20 and self.jump is False:
                    self.gravity_dt = time
                    self.fall_rate *= 1.1
                    for i in range(int(self.fall_rate)):
                        self.rect.y += 1
                        if self.rect.colliderect(block):
                            self.fall_rate = 1
                            break

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
                        ,[(30 * i, 0, 30, 32) for i in range(0, 8 )]       # Hit--------------------4
                        ,[(33 * i, 0, 33, 32) for i in range(0, 15)]       # Death------------------5
                      ]

        sizes = [(72,96), (66,99), (66,96), (129,111), (90,96), (99,96)]

        self.skeleton_frame_maxes = [len(frame_amount) for frame_amount in coordinates]

        spritesheets = [spritesheet(file) for file in os.listdir(directory)]
        spritesheets_separate = [spritesheet.images_at(coordinates[i], colorkey = (0, 0, 0)) for i, spritesheet in enumerate(spritesheets)]

        for i, ss_sep in enumerate(spritesheets_separate):
            scaled_frames = [pg.transform.scale(ss_sep[e], sizes[i]) for e in range(0, len(ss_sep))]
            self.skeleton_frames.append(scaled_frames)

# -------------------------------------------------------NPCS-------------------------------------------------------------------
class Masir_sprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frame_index = 0
        self.upload_frames()
        self.current_images = self.all_images[0]
        self.image = self.current_images[0]
        self.state = 0
        self.facing_right = True
        self.frame_override = True
        self.frame_dt = 0
        self.frame_speed = 300
        self.gravity_dt = 0
        self.fall_rate = 1


        self.rect = pg.Rect((800, 0), (256, 198)) # Spawn point and collision size.


    def upload_frames(self):
        idle_images = []
        walk_images = []
        action_images = []

        # State IDs
        #-----------------------0-------------1------------2----------
        self.all_images = [idle_images, walk_images, action_images]

        directories =           ["C:/Users/Andrew/Desktop/Python_Projects/Kismet/Masir/Idle_Png"       # Idle animation.
                                ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Masir/Walk_Png"       # Walk animation.
                                ,"C:/Users/Andrew/Desktop/Python_Projects/Kismet/Masir/Action_Png"]    # Action animation.


        # Create a list containing lists with all animation frames. Each list is referenceable by the state ID shown above.
        for i, directory in enumerate(directories):
            os.chdir(directory)
            for file in os.listdir(directory):
                self.all_images[i].append(pg.transform.scale(load_image(file), (256, 256)))

        # Create a list of number of frames for each animation.
        self.frame_maxes = [len(images) for images in self.all_images]

    def change_state(self):
        self.current_images = self.all_images[self.state]
        return

    def update(self, blockers, time):
        if (time - self.frame_dt) >= self.frame_speed or self.facing_right != self.frame_override:
            self.frame_dt = time

            if self.facing_right:
                self.image = self.current_images[self.frame_index]
                self.frame_index += 1
                self.frame_override = True
            else:
                self.image = pg.transform.flip(self.current_images[self.frame_index], True, False)
                self.frame_index += 1
                self.frame_override = False

            if self.frame_index == self.frame_maxes[self.state]:
                self.frame_index = 0

        for block in blockers:
        # Checks to see if Fursa is in contact with the ground.
            if self.rect.colliderect(block):
                pass
            else:
                # If not in contact with the ground, accelerates falling down every 20 ms.
                # Gravity is disabled when a jump animation is in progress.
                if (time - self.gravity_dt) >= 20:
                    self.gravity_dt = time
                    self.fall_rate *= 1.1 # Acceleration rate.
                    for i in range(int(self.fall_rate)):
                        self.rect.y += 1
                        # Halts falling when Fursa lands on a block.
                        if self.rect.colliderect(block):
                            self.fall_rate = 1
                            break


# -------------------------------------------------------MAPS-------------------------------------------------------------------
# Starting area. Stores map and music data.
class Map_01:
    def __init__(self, npc_sprites):
        # Map graphics and music.
        os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Level Start")
        self.map = TiledMap('Starting_Area.tmx')
        self.music = pg.mixer.music.load('301 - Good Memories.mp3')
        #pg.mixer.music.play(loops = -1, start = 0.0)
        self.map.make_map()
        self.cutscene = False

        # Declare npcs.
        self.Masir = Masir_sprite()
        npc_sprites.add(self.Masir)


    def cutscene_event(self, character):
        if abs(character.rect.centerx - self.Masir.rect.centerx) < 200:
            self.cutscene = True

        # Pygame event loop.
        for event in pg.event.get():
            # Allow to quit game. Included in this portion to be able to keep only one event loop.
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                     pg.quit()
                     sys.exit()


    def update(self, character):
        self.cutscene_event(character)
        print(self.Masir.rect.centerx)


    



# Game Start.
def main():

    # Game parameters.
    pg.mixer.pre_init(44100, -16, 2, 512)
    pg.init()
    os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet")
    size = width, height = 1920, 1200
    screen = pg.display.set_mode(size, pg.FULLSCREEN)
    pg.display.set_caption('Kismet')
    clock = pg.time.Clock()
    os.chdir("C:/Users/Andrew/Desktop/Python_Projects/Kismet/Dialog")
    dialog_box = load_image('dialogue_box.png')
    dialog_box = pg.transform.scale(dialog_box, (795, 195))
    dialog_font = pg.freetype.Font('NEOTERICc - Bold DEMO VERSION.ttf', size = 36)

    dialog_text, rect = dialog_font.render('Hello, young one. I\'ve been expecting you for so long.')

    # Declare character sprites.
    Fursa = Fursa_sprite()
    character_sprites = pg.sprite.Group()
    character_sprites.add(Fursa)

    # Declare npc sprites.
    npc_sprites = pg.sprite.Group()

    # Declare enemy sprites.
    enemy_images = enemy_frames()
    enemy_sprites = pg.sprite.Group()
    skeleton_01 = skeleton(enemy_images)
    enemy_sprites.add(skeleton_01)

    # Declare particle sprites.
    blast_particle_frames = blast_frames()
    blast_images_r = blast_particle_frames.blast_images_r
    blast_images_l = blast_particle_frames.blast_images_l
    impact_images_r = blast_particle_frames.impact_images_r
    impact_images_l = blast_particle_frames.impact_images_l
    blast_particle = Fursa_blast(blast_images_r, blast_images_l, impact_images_r, impact_images_l)
    particle_sprites = pg.sprite.Group()
    particle_sprites.add(blast_particle)

    # Declare Maps.
    Starting_Area = Map_01(npc_sprites)
    maps = [Starting_Area]
    current_map = maps[0]

    # Game Loop
    while True:

        time = pg.time.get_ticks()
        # Surfaces are blit and updated in order of back to front on screen.

        # Layer 1-------- Screen background back surface refresh.
        screen.blit(current_map.map.back_surface, (0,0))

        # Layer 2-------- Particle sprites update.
        particle_sprites.update(Fursa, particle_sprites, enemy_sprites)
        particle_sprites.draw(screen)

        # Layer 3-------- Character sprites update.
        character_sprites.update(current_map.map.blockers, time, enemy_sprites, current_map.cutscene)
        character_sprites.draw(screen)

        npc_sprites.update(current_map.map.blockers, time)
        npc_sprites.draw(screen)

        # Layer 4-------- Enemy sprites update.
        #enemy_sprites.update(current_map.map.blockers, time, Fursa, particle_sprites)
        #enemy_sprites.draw(screen)

        # Layer 5-------- Screen background front surface refresh.
        screen.blit(current_map.map.front_surface, (0,0))

        screen.blit(dialog_box, (200,100))
        screen.blit(dialog_text, (300,150))

        current_map.update(Fursa)


        clock.tick(90) # Framerate.
        #print(clock)

        pg.display.flip()

if __name__ == '__main__':
    main()
