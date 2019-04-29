from directory_change import files
import pygame as pg
from Fursa_projectiles import SPIRIT_BLAST, blast_frames


# Fursa sprite. The main character of the game
# Contains the pygame eventloop for non-cutscenes and non-battles.
class Fursa_sprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        file = files()
        # Initialize frame parameters. Frames are uploaded once using upload_frames.
        self.upload_frames(file)
        self.current_frames = self.all_frames[0]
        self.image = self.current_frames[0]
        self.facing_right = True
        self.frame_override = True
        self.frame_speed = 200
        self.frame_index = 0
        # Projectile animation frames.
        fursa_projectile = blast_frames()
        self.projectile_frames = fursa_projectile.frames

        # Sprite rect init.
        self.rect = pg.Rect((200, 20), (128, 128))

        # States.
        self.prev_state = 0
        self.state = 0
        self.key_pressed = False
        self.jump = False
        self.attack = False
        self.hit = False
        self.cutscene_enter = False
        self.map_forward = False
        self.battle_forward = False
        self.walking = False
        self.running = False
        self.on_ground = False
        self.fall_rate = 1
        self.jump_rate = 20
        self.jump_index = 0
        # @pixel/frame. At approx 80 fps --> 80 pixel/sec
        self.move = 1

        # Time recorders.
        self.gravity_dt = 0
        self.frame_dt = 0
        self.jump_dt = 0

        # Load sound effects.
        file.cd('Players\Fursa')
        self.jump_noise = pg.mixer.Sound("jump_02.wav")
        self.attack_noise = pg.mixer.Sound("Electro_Current_Magic_Spell.wav")
        self.attack_charge = pg.mixer.Sound("charge_up.wav")
        self.walk_dirt = pg.mixer.Sound("stepdirt_7.wav")
        self.walk_dirt.set_volume(0.15)
        self.teleport_noise = pg.mixer.Sound('teleport.wav')
        self.battle_sword_aftersound = pg.mixer.Sound('battle_sword_aftersound.wav')
        self.battle_impact_noise = pg.mixer.Sound('battle_start.wav')
        self.battle_impact_noise.set_volume(0.50)

        # Battle Transition Screen.
        resolution = width, height = 1920, 1080
        black = (0, 0, 0)
        self.battle_transition = pg.Surface(resolution)
        self.battle_transition.fill(black)

        # Character attributes and battle states.
        self.level = 1
        self.exp = 0
        self.current_hp = 10
        self.current_mp = 10
        self.max_hp = 10
        self.max_mp = 10
        self.party_spawn = 2
        self.speed = 3
        self.spell = False
        self.turn = False
        self.turn_determiner = [self.party_spawn, self.speed]

        # Combat move and selection descriptions.
        self.slot_labels = {1: ['ATTACK', 'SPIRIT BLAST'],
                            2: ['BAG', '---'],
                            3: ['RUN', '---'],
                            4: ['SPELL', '---']
                            }

        self.combat_descriptions = {1: ['Attack the enemy with a basic attack. Low damage but free of resources.',
                                        'A concentrated blast of spiritual energy. Low damage and mana cost.'],

                                    2: ['Use an item in your bag to heal or temporarily boost your attributes.',
                                        ''],

                                    3: ['Attempt to run away from combat. Has a chance of failing. No experience awarded if successful.',
                                        ''],

                                    4: ['Attack the enemy with a spell of your choice. Spells require mana to cast.',
                                        '']
                                    }

    def upload_frames(self, file):

        """ Function that uploads and stores all frames for Fursa during init.
            Created separately for organizational purposes. """

        idle_images = []
        walk_images = []
        run_images = []
        attack_images = []
        shield_images = []
        hit_images = []
        death_images = []

        # State IDs. Used as an identifier when changing self.state.
        # -----------------------0------------1------------2------------3--------------4--------------5-----------6-------#
        self.all_frames = [idle_images, walk_images, run_images, attack_images, shield_images, death_images, hit_images]

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
                self.all_frames[i].append(pg.transform.scale(pg.image.load(img_file).convert_alpha(), (128, 128)))
        # Hit animation is simply the first couple of frames from the death animation.
        self.all_frames[6] = (self.all_frames[5][0:7])

        # Create a list of number of frames for each animation. Used to know when frame_index should be reset.
        self.frame_maxes = [len(images) for images in self.all_frames]

    def change_state_keys(self):

        """ Function that changes Fursa's animation depending on keyboard input.
            Is continuously called during non-cutscenes and non-battles.
            Animations are ordered in priority.
            Each animation type has its own fps. """

        self.prev_state = self.state

        # HIT animation.
        if self.hit:
            self.state = 6
            self.frame_speed = 25
            self.walking = self.running = False

        # ATTACK animation.
        elif self.attack:
            self.state = 3
            self.frame_speed = 75
            self.walking = self.running = False

        # RUN animation.
        elif self.key_pressed and self.shift:
            self.state = 2
            self.frame_speed = 100
            self.walking = False
            self.running = True

        # WALK animation.
        elif self.key_pressed:
            self.state = 1
            self.frame_speed = 125
            self.walking = True
            self.running = False

        # IDLE animation.
        else:
            self.state = 0
            self.frame_speed = 200
            self.walking = self.running = False

        # Reset frame_index if state change is detected.
        if self.prev_state != self.state:
            self.frame_index = 0

    def handle_keys(self, time, dt, map):

        """ Function that handles Fursa's key inputs and translates them into actions.
            Is called continuously during non-cutscenes and non-battles.
            Split into two sections:
                1. Monitoring held down keys and combinations.
                2. Monitoring single key press events in pygame event loop.
            Due to the nature of pygame, both have to be used in tandem to create fluid game controls.
            WARNING -> Pygame event loops transfer over to Map.py files during cutscenes and battles. """

        # Monitor held down keys. (movement)
        # If an attack animation is not in progress, move in the direction of the pressed key.
        if self.attack is False:
            keys = pg.key.get_pressed()
            if keys[pg.K_d]:
                self.rect.x += self.move
                self.key_pressed = True
            elif keys[pg.K_a]:
                self.rect.x -= self.move
                self.key_pressed = True
            # Speed is doubled when shift is held down. (RUN animation)
            if keys[pg.K_LSHIFT]:
                self.shift = True
                self.move = 2 * dt
            else:
                self.shift = False
                self.move = 1 * dt

        # Pygame event loop.
        for event in pg.event.get():

            # Monitor single key presses.
            # If a key is pressed and an attack animation is not in progress, register the key press.
            if event.type == pg.KEYDOWN and self.attack is False:

                # Reset frame_index whenever a key is pressed.
                self.key_pressed = True
                self.frame_index = 0

                # Registers which way Fursa should be facing.
                if event.key == pg.K_d:
                    self.facing_right = True
                elif event.key == pg.K_a:
                    self.facing_right = False

                # Enables attack animation.
                elif event.key == pg.K_r:
                    self.attack = True

                # Jump input. self.jump is fed into jump code located below.
                elif event.key == pg.K_SPACE:
                    self.jump_noise.play()
                    self.jump = True

                # If Fursa is in contact with a portal, allow transition to next map.
                elif event.key == pg.K_w:
                    if self.rect.collidepoint(map.portal_rect.centerx, map.portal_rect.centery):
                        # Cancel any and all sounds in previous map upon exit.
                        for sound in map.end_sounds:
                            sound.stop()
                        self.teleport_noise.play()
                        self.map_forward = True

                # Allow closing the game.
                elif event.key == pg.K_ESCAPE:
                    pg.quit()

            # Frame reset when key is no longer held down. self.key_pressed set to false changes state back to idle.
            elif event.type == pg.KEYUP and self.attack is False:
                self.frame_index = 0
                self.key_pressed = False

        # Jump code is placed outside event loop so that the animation can carry out properly.
        # Jump up decelerates every 60ms by 20% until jump_index reaches 5.
        if self.jump is True:
            if (time - self.jump_dt) >= 60:
                self.jump_dt = time
                self.jump_rate *= 0.8
                self.jump_index += 1
                for i in range(int(self.jump_rate)):
                    self.rect.y -= 1
                    if self.jump_index == 5:
                        self.jump = False
                        self.jump_rate = 20
                        self.jump_index = 0
                        break

    def change_state_battle(self, state_id):

        """ Function that changes Fursa's animation depending on battle state.
            Is continuously called during battles.
            Matches change_state_keys. """

        # WALK animation.
        if state_id == 1:
            self.state = 1
            self.frame_speed = 125
            self.walking = True
            self.running = False
        # RUN animation.
        elif state_id == 2:
            self.state = 2
            self.frame_speed = 100
            self.walking = False
            self.running = True
        # ATTACK animation.
        elif state_id == 3:
            self.state = 3
            self.frame_speed = 75
            self.walking = self.running = False
        # IDLE animation.
        elif state_id == 0:
            self.state = 0
            self.frame_speed = 200
            self.walking = self.running = False

        self.current_frames = self.all_frames[self.state]

    def battle_controls(self, map):

        """ Function that handles Fursa's battle inputs and translates them into actions.
            Battle commands are selected in the pygame eventloop located in Map.py files.
            Is called continuously during battles. """

        self.prev_state = self.state

        # If it is Fursa's turn, allow action.
        if map.current_turn == self.party_spawn:
            # Melee attack.
            if map.battle_command == 1:
                map.animation_complete = False
                # Run up to enemy position and perform attack animation.
                if self.rect.right <= map.battle_spawn_pos[4].left:
                    self.change_state_battle(2)
                    self.rect.x += 2
                else:
                    self.attack = True
                    self.change_state_battle(3)

            # Spell animation.
            elif map.battle_command == 2:
                map.animation_complete = False
                # Run to the middle platform and perform spell animation.
                if self.rect.centerx <= map.battle_spawn_pos[6].centerx:
                    self.change_state_battle(2)
                    self.rect.x += 2
                else:
                    self.spell = True
                    self.change_state_battle(3)

            # Return to position.
            # map.battle_command is set to 0 when self.attack or self.attack becomes false.
            elif map.battle_command == 0:
                if self.rect.centerx >= map.battle_spawn_pos[self.party_spawn].centerx:
                    self.facing_right = False
                    self.change_state_battle(2)
                    self.rect.x -= 2
                else:
                    # When action is completed and Fursa is back in position, turn is over.
                    self.facing_right = True
                    self.change_state_battle(0)
                    map.animation_complete = True

        if self.prev_state != self.state:
            self.frame_index = 0

    def update(self, time, dt, map, screen, character_sprites, enemy_sprites, particle_sprites, file):

        """ Main update function. Continuously called at all times in game loop main()
            Updates Fursa's frame and hitbox. Monitors platform interaction.
            Monitors whether open world, cutscene, or battle controls should be enabled. """

        # Hitbox and refresh rect updates.
        if self.facing_right:
            self.hitbox_rect = pg.Rect((self.rect.x + 52, self.rect.y + 36), (18, 64))
        else:
            self.hitbox_rect = pg.Rect((self.rect.x + 58, self.rect.y + 36), (18, 64))

        self.refresh_rect = pg.Rect((self.rect.x - 64, self.rect.y - 64), (256, 256))

        # Enable different code segments depending on game state.
        if map.cutscene is False and map.battle is False:
            self.handle_keys(time, dt, map)
            self.change_state_keys()
            self.cutscene_enter = False
        elif map.battle is True:
            self.battle_controls(map)
        # Disallow any key input if cutscene is in progress. Revert Fursa to an idle state.
        elif map.cutscene is True:
            self.state = 0
            self.frame_speed = 200
            self.walking = self.running = False
            self.current_frames = self.all_frames[self.state]
            if self.cutscene_enter is False:
                self.frame_index = 0
                self.cutscene_enter = True

        """
            Cycle through frames depending on the self.frame_speed for the specific state Fursa is in.
            Flip the frame image vertically depending on which direction Fursa is facing.
            self.frame_override is a boolean representing the previous state of self.facing_right where true is right.
            If the direction that Fursa is facing has changed before a frame can be refreshed,
            bypasses frame timer in order to avoid Fursa momentarily moving facing the wrong direction.
        """

        if (time - self.frame_dt) >= self.frame_speed or self.facing_right != self.frame_override:
            self.frame_dt = time

            self.current_frames = self.all_frames[self.state]

            # Resets frame index if the max for a certain animation is reached.
            # Sets attack, spell, and hit to false to indicate completion.
            if self.frame_index == self.frame_maxes[self.state]:
                if self.attack or self.spell:
                    # Initiates walkback during battles.
                    map.battle_command = 0
                self.attack = False
                self.spell = False
                self.hit = False
                self.frame_index = 0

            if self.facing_right is True:
                self.image = self.current_frames[self.frame_index]
                self.frame_index += 1
                self.frame_override = True
            else:
                self.image = pg.transform.flip(self.current_frames[self.frame_index], True, False)
                self.frame_index += 1
                self.frame_override = False

            # Play dirt crunch noise at the correct frame.
            if self.walking and self.on_ground:
                if self.frame_index == 2 or self.frame_index == 8:
                    self.walk_dirt.play()
            elif self.running and self.on_ground:
                if self.frame_index == 4 or self.frame_index == 11:
                    self.walk_dirt.play()

            # Play attack noise at correct frames.
            elif self.attack is True:
                if self.frame_index == 1:
                    self.attack_charge.play()
                elif self.frame_index == 8:
                    self.attack_noise.play()
            # Create a blast particle for spells.
            elif self.spell is True:
                if self.frame_index == 1:
                    self.attack_charge.play()
                elif self.frame_index == 8:
                    self.attack_noise.play()
                    blast = SPIRIT_BLAST(self)
                    particle_sprites.add(blast)

        # Gravity emulation using map platforms.
        for block in map.blockers:
            # Checks to see if Fursa is in contact with the ground.
            if self.hitbox_rect.colliderect(block):
                self.on_ground = True
                break
            else:
                self.on_ground = False

        if self.on_ground is False:
            # If not in contact with the ground, accelerates falling down every 20 ms by 10%.
            # Gravity is disabled when a jump animation is in progress.
            if (time - self.gravity_dt) >= 20 and self.jump is False:
                self.gravity_dt = time
                self.fall_rate *= 1.1
                start_fall = self.rect.y
                for i in range(int(self.fall_rate)):
                    self.rect.y += 1
                    self.hitbox_rect.y += 1
                    end_fall = self.rect.y
                    if (end_fall - start_fall) > 256:
                        pg.display.update(self.refresh_rect)
                    # Halts falling when Fursa lands on a block.
                    for block in map.blockers:
                        if self.hitbox_rect.colliderect(block):
                            self.fall_rate = 1
                            self.on_ground = True
                            break
                    if self.on_ground is True:
                        break

        """ Enemy collision detection. Transition to battle mode. (turn-based combat)
            All code pertaining to transitioning into combat mode is located here.
            Once transition is completed, pygame event loop moves to Map.py file.
            Transition includes setting spawn locations and changing map surfaces. """

        # If not already in a battle, and hit by an enemy's attack, transition to battle mode.
        if map.battle is False:
            for enemy in enemy_sprites:
                if enemy.attack:
                    if self.hitbox_rect.colliderect(enemy.rect) and enemy.frame_index == 8:

                        # Set frame to a hit frame.
                        self.image = self.all_frames[6][2]

                        # Pause impact frame for 1s.
                        self.battle_impact_noise.play()
                        pg.mixer.music.stop()
                        enemy_sprites.draw(screen)
                        character_sprites.draw(screen)
                        screen.blit(map.map.front_surface, (0, 0))
                        pg.display.flip()
                        pg.time.wait(1000)
                        # Clear background to black for 1s.
                        screen.blit(self.battle_transition, (0, 0))
                        enemy_sprites.draw(screen)
                        character_sprites.draw(screen)
                        pg.display.flip()
                        self.battle_sword_aftersound.play()
                        pg.time.wait(1000)

                        # Initiate music.
                        file.cd('Maps\Map_02')
                        battle_music = pg.mixer.music.load('300-B - Blood of Lilith (Loop, MP3).mp3')
                        pg.mixer.music.play(loops=-1, start=0.0)

                        # Initialize states.
                        self.state = 0
                        self.frame_index = 0
                        self.facing_right = True
                        enemy.facing_right = False
                        self.jump = False
                        self.battle_forward = True
                        map.battle = True

                        # Spawn locations.
                        self.rect.centerx = map.battle_spawn_pos[self.party_spawn].centerx
                        self.rect.centery = map.battle_spawn_pos[self.party_spawn].centery
                        enemy.rect.centerx = map.battle_spawn_pos[enemy.party_spawn].centerx
                        enemy.rect.centery = map.battle_spawn_pos[enemy.party_spawn].centery


            """ Battle Platform Layout.
                                                      Midpoint for Ranged Attacks
                                          Ally                       |                  Enemies

    Spawn Location Indexes    ------0---------1-----------2----------6-----------4---------5--------6------"""
