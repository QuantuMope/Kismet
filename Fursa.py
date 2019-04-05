from spritesheet import spritesheet
from directory_change import files
import pygame as pg

# Fursa sprite. The main character of the game.
class Fursa_sprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        file = files()
        self.frame_index = 0
        self.upload_frames(file) # Uploads all frames. Function found below.
        self.current_images = self.all_images[0]
        self.image = self.current_images[0]
        self.prev_state = 0
        self.state = 0
        self.facing_right = True
        self.frame_override = True
        self.rect = pg.Rect((200, 20), (128, 128)) # Spawn point and collision size.
        self.hitbox_rect = pg.Rect((self.rect.x + 52 , self.rect.y + 36), (18, 64))
        self.refresh_rect = pg.Rect((self.rect.x - 64, self.rect.y - 64), (256, 256))

        # States
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
        self.cutscene_enter = False
        self.map_forward = False
        self.battle_forward = False
        self.battle = False
        self.walking = False
        self.running = False
        self.on_ground = False

        # Load sound effects.
        file.cd('Players\Fursa')
        self.jump_noise = pg.mixer.Sound("jump_02.wav")
        self.attack_noise = pg.mixer.Sound("Electro_Current_Magic_Spell.wav")
        self.attack_charge = pg.mixer.Sound("charge_up.wav")
        self.walk_dirt = pg.mixer.Sound("stepdirt_7.wav")
        self.walk_dirt.set_volume(0.15)
        self.teleport_noise = pg.mixer.Sound('teleport.wav')
        # Battle Transition Sounds.
        self.battle_sword_aftersound = pg.mixer.Sound('battle_sword_aftersound.wav')
        self.battle_impact_noise = pg.mixer.Sound('battle_start.wav')
        self.battle_impact_noise.set_volume(0.50)

        # Battle Transition Screen.
        resolution = width, height = 1920,1080
        black = (0,0,0)
        self.battle_transition = pg.Surface(resolution)
        self.battle_transition.fill(black)

    # Function that uploads and stores all possible frames Fursa may use. Is called in __init__.
    # Created separately for organizational purposes.
    def upload_frames(self, file):

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

        directories =      ["Players\Fursa\Idle"          # Idle animation.
                           ,"Players\Fursa\Walk"          # Walking animation.
                           ,"Players\Fursa\Run"           # Run animation.
                           ,"Players\Fursa\Attack_01"     # Attack animation.
                           ,"Players\Fursa\Attack_02"     # Shield animation.
                           ,"Players\Fursa\Death"]        # Hit & Death animation.

        # Create a list containing lists with all animation frames. Each list is referenceable by the state ID shown above.
        for i, directory in enumerate(directories):
            file.cd(directory)
            for img_file in file.file_list():
                self.all_images[i].append(pg.transform.scale(pg.image.load(img_file).convert_alpha(), (128, 128)))

        self.all_images[6] = (self.all_images[5][0:7])

        # Create a list of number of frames for each animation.
        self.frame_maxes = [len(images) for images in self.all_images]

    # Function that changes Fursa's animation depending on the action performed.
    # Continuously called in self.update().
    def change_state_keys(self):

        # Each frame list has a state ID that can be found outlined in self.upload_frames().
        # Each animation type has its own fps.
        self.prev_state = self.state

        if self.hit:
            self.state = 6
            self.frame_speed = 25
            self.walking = False
            self.running = False
        elif self.attack:
            self.state = 3
            self.frame_speed = 75
            self.walking = False
            self.running = False
        elif self.key_pressed and self.shift:
            self.state = 2
            self.frame_speed = 100
            self.walking = False
            self.running = True
        elif self.key_pressed:
            self.state = 1
            self.frame_speed = 125
            self.walking = True
            self.running = False
        else:
            self.state = 0
            self.frame_speed = 200
            self.walking = False
            self.running = False

        self.current_images = self.all_images[self.state]

        if self.prev_state != self.state:
            self.frame_index = 0

    """
        Function that handles Fursa's key inputs. Called in update().
        Split into two sections:
        1. Monitoring held down keys and combinations.
        2. Monitoring single key press events.
        Due to the nature of pygame, both have to be used in tandem to
        create fluid game controls.
    """

    def handle_keys(self, time, dt, map):

        # Monitor held down keys. (movement)
        # If attack animation is not in progress, move in the direction of the pressed key.
        if self.attack == False:
            keys = pg.key.get_pressed()
            if keys[pg.K_d]:
                self.rect.x += self.speed
                self.key_pressed = True  # Self.key_pressed() is fed back to change_state(). Found several times throughout handle_keys().
            elif keys[pg.K_a]:
                self.rect.x -= self.speed
                self.key_pressed = True
            # Running changes speed by holding down shift.
            # Self.shift is fed back to change_state().
            if keys[pg.K_LSHIFT]:
                self.shift = True
                self.speed = 2 * dt
            else:
                self.shift = False
                self.speed = 1 * dt

        # Pygame event loop.
        for event in pg.event.get():

            # Monitor single key presses. (actions)
            # If a key is pressed and an attack animation is not in progress, register the key press.
            if event.type == pg.KEYDOWN and self.attack == False:

                self.key_pressed = True
                self.frame_index = 0 # Frame reset when key is pressed.

                # Registers which way Fursa should be facing. Fed to self.update().
                if event.key == pg.K_d:
                    self.facing_right = True
                    self.walking = True
                elif event.key == pg.K_a:
                    self.facing_right = False
                    self.walking = True

                # Enables attack animation.
                # Self.attack set to True prevents other key inputs to be registered until the animation is completed.
                elif event.key == pg.K_r:
                    self.attack = True
                    self.attack_charge.play()

                # Jump input.
                elif event.key == pg.K_SPACE:
                    self.jump_noise.play()
                    self.jump = True    # ----------------> Jump starts.

                elif event.key == pg.K_w:
                    if self.rect.collidepoint(map.portal_rect.centerx, map.portal_rect.centery):
                        for sound in map.end_sounds:
                            sound.stop()
                        self.teleport_noise.play()
                        self.map_forward = True

                elif event.key == pg.K_ESCAPE:
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

    def change_state_battle(self):
        pass

    def battle_controls(self):
        pass

    # Function that updates Fursa's frames and positioning. Called continuously in game loop main().
    # Must be fed the blockers of the current map.
    def update(self, blockers, time, dt, cutscene, screen, map, map_travel, battle_travel,
                character_sprites, enemy_sprites, particle_sprites, particle_frames, file):

        normalized_dt = round(dt / 11)

        if self.facing_right:
            self.hitbox_rect = pg.Rect((self.rect.x + 52 , self.rect.y + 36), (18, 64))
        else:
            self.hitbox_rect = pg.Rect((self.rect.x + 58 , self.rect.y + 36), (18, 64))

        self.refresh_rect = pg.Rect((self.rect.x - 64, self.rect.y - 64), (256, 256))

        # Disallow any key input if cutscene is in progress. Revert Fursa into a idle state.
        if map.battle is True:
            self.state = 0
            self.change_state_battle()
            self.battle_controls()
            if battle_travel:
                self.battle_forward = False
        elif cutscene is False:
            self.handle_keys(time, normalized_dt, map)
            self.change_state_keys()
            self.cutscene_enter = False
            if map_travel:
                self.map_forward = False
        elif cutscene:
            self.state = 0
            self.frame_speed = 200
            self.walking = False
            self.running = False
            self.current_images = self.all_images[self.state]
            if self.cutscene_enter is False:
                self.frame_index = 0
                self.cutscene_enter = True

        """
            Cycle through frames depending on self.frame_speed that is set in self.change_state().
            Flip the frame image vertically depending on which direction Fursa is facing.
            Self.frame_override is a boolean representing the previous state of self.facing_right.
            If the direction that Fursa is facing has changed before a frame can be refreshed,
            bypasses frame timer and resets the to avoid Fursa momentarily moving facing the wrong direction.
        """

        if (time - self.frame_dt) >= self.frame_speed or self.facing_right != self.frame_override:
            self.frame_dt = time

            # Resets frame index if the max for a certain animation is reached.
            # Also, sets attack animation back to False in case the action was an attack.
            if self.frame_index == self.frame_maxes[self.state]:
                self.attack = False
                self.hit = False
                self.frame_index = 0

            if self.facing_right:
                self.image = self.current_images[self.frame_index]
                self.frame_index += 1
                self.frame_override = True
            else:
                self.image = pg.transform.flip(self.current_images[self.frame_index], True, False)
                self.frame_index += 1
                self.frame_override = False

            # Play attack noise at the correct frame.
            if self.walking and self.on_ground:
                if self.frame_index == 2 or self.frame_index == 8:
                    self.walk_dirt.play()

            elif self.running and self.on_ground:
                if self.frame_index == 4 or self.frame_index == 11:
                    self.walk_dirt.play()

            elif self.attack == True and self.frame_index == 8:
                self.attack_noise.play()
                blast = Fursa_blast(particle_frames, self.facing_right, self.rect.x, self.rect.y)
                particle_sprites.add(blast)


        """ ----------------------SKIP POS 1 ----------------------------------------
         |  Enemy collision detection. Transition to turn-based combat.
         |  All code pertaining to transitioning into combat mode is located here.
         |  Each individual sprite's combat behavior is located in its own respective class.
        """
        for enemy in enemy_sprites:
            if enemy.attack:
                if self.hitbox_rect.colliderect(enemy.rect) and enemy.frame_index == 8:

                    self.image = self.all_images[6][2]

                    # Transition screen.
                    self.battle_impact_noise.play()
                    pg.mixer.music.stop()
                    enemy_sprites.draw(screen)
                    character_sprites.draw(screen)
                    screen.blit(map.map.front_surface, (0,0))
                    pg.display.flip()
                    pg.time.wait(1000)
                    screen.blit(self.battle_transition, (0,0))
                    enemy_sprites.draw(screen)
                    character_sprites.draw(screen)
                    pg.display.flip()
                    self.battle_sword_aftersound.play()
                    pg.time.wait(1000)

                    # Spawn and music start.
                    self.facing_right = True
                    enemy.facing_right = False
                    file.cd('Maps\Map_02')
                    battle_music = pg.mixer.music.load('300-B - Blood of Lilith (Loop, MP3).mp3')
                    pg.mixer.music.play(loops = -1, start = 0.0)
                    self.rect.centerx = map.battle_spawn_pos[1].centerx
                    self.rect.centery = map.battle_spawn_pos[1].centery
                    enemy.rect.centerx = map.battle_spawn_pos[3].centerx
                    enemy.rect.centery = map.battle_spawn_pos[3].centery
                    self.frame_index = 0
                    self.hp -= 1
                    self.hit = True
                    self.jump = False
                    self.battle = True
                    self.battle_forward = True
                    self.state = 0


        """ ---------------------------- END OF BATTLE CODE -------------------------------"""

        # Gravity emulation with current map blockers.
        for block in blockers:
            # Checks to see if Fursa is in contact with the ground.
            if self.hitbox_rect.colliderect(block):
                self.on_ground = True
                break
            else:
                self.on_ground = False

        if self.on_ground is False:
            # If not in contact with the ground, accelerates falling down every 20 ms.
            # Gravity is disabled when a jump animation is in progress.
            if (time - self.gravity_dt) >= 20 and self.jump is False:
                self.gravity_dt = time
                self.fall_rate *= 1.1 # Acceleration rate.
                start_fall = self.rect.y
                for i in range(int(self.fall_rate)):
                    self.rect.y += 1
                    self.hitbox_rect.y += 1
                    end_fall = self.rect.y
                    if (end_fall - start_fall) > 256:
                        pg.display.update(self.refresh_rect)
                    # Halts falling when Fursa lands on a block.
                    for block in blockers:
                        if self.hitbox_rect.colliderect(block):
                            self.fall_rate = 1
                            self.on_ground = True
                            break
                    if self.on_ground is True:
                        break

# Class simply containing projectile frames of various attacks.
# Created to avoid having to load from the hard drive every time a projectile is created.
class blast_frames():
    def __init__(self):
        file = files()
        # Fursa's attack blast properly separated into frames into a list from a spritesheet.
        file.cd("Players\Fursa")
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

        self.frames = [self.blast_images_r, self.blast_images_l, self.impact_images_r, self.impact_images_l]

# Fursa's blast projectile sprite.
class Fursa_blast(pg.sprite.Sprite):
    def __init__(self, frames, Fursa_facing_right, Fursa_x, Fursa_y):
        super().__init__()
        self.blast_images_r = frames[0]
        self.blast_images_l = frames[1]
        self.impact_images_r = frames[2]
        self.impact_images_l = frames[3]

        self.flowing_right = True if Fursa_facing_right else False

        if self.flowing_right:
            self.rect = pg.Rect(Fursa_x + 70, Fursa_y + 52, 64, 64)
            self.images = self.blast_images_r
            self.impact = self.impact_images_r
        else:
            self.rect = pg.Rect(Fursa_x + 20, Fursa_y + 52, 64, 64)
            self.images = self.blast_images_l
            self.impact = self.impact_images_l

        self.image = self.images[0]
        self.refresh_rect = pg.Rect((self.rect.x - 16, self.rect.y - 16), (96, 96))
        self.spawn = True
        self.i = 0
        self.e = 0
        #self.already_spawned = False
        self.flow_right = True
        self.particle_hit = False

    def update(self, Fursa, dt, particle_sprites, enemy_sprites):

        normalized_dt = round(dt / 11)
        dt = normalized_dt

        self.refresh_rect = pg.Rect((self.rect.x - 16, self.rect.y - 16), (96, 96))

        # Once blast is spawned by Fursa, will keep traveling across map until it hits the
        # right of left edge of the map in which case the sprite will be killed.
        if self.particle_hit is False and self.flowing_right:
            self.rect.x += 4 * dt
        else:
            self.rect.x -= 4 * dt

        self.image = self.images[self.i] # Frame changing.
        self.i += 1
        if self.i == 8: self.i = 0

        if self.rect.right > 1920 or self.rect.left < 0:
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
