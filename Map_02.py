import pygame as pg
from directory_change import files
from TiledMap import TiledMap
from enemies import skeleton
from operator import itemgetter


# Area 2
class Map_02():
    def __init__(self, dialog_package, npc_sprites, enemy_frames, enemy_sprites):
        file = files()

        # Map graphics and music.
        file.cd('Maps\Map_02')
        self.map = TiledMap('Map_02.tmx')
        self.map.make_map()
        self.blockers = self.map.blockers

        # States.
        self.cutscene = False
        self.first_cutscene = True
        self.battle = False
        self.event = 0
        self.map_first_time = True
        self.battle_init = True

        # Fursa spawn location.
        self.spawnx = 100
        self.spawny = 500

        # Refresh rects and sounds to end when map is terminated.
        self.refresh_rects = []
        self.ui = []
        self.end_sounds = []

        # BATTLE MODE.
        # Battle map, spawn locations, turn order, and states.
        self.battle_map = TiledMap('battle_scene.tmx')
        self.battle_map.make_map()
        self.battle_spawn_pos = self.battle_map.battle_spawns
        self.turn_order = []
        self.turn_i = 0
        self.battle_command = 0
        self.action_select = False
        self.animation_complete = True
        self.returned = True
        self.change_turn = False

        # User interface boxes. There is a combat, status, and description box.
        file.cd('UI\Combat')
        self.combat_box = pg.image.load('Combat UI Box transparent.png').convert_alpha()
        self.status_box = pg.transform.scale(self.combat_box, (670, 300))
        self.combat_box = pg.transform.scale(self.combat_box, (690, 300))
        self.combat_box_rect = pg.Rect((720, 750), (690, 300))
        self.description_box = pg.transform.scale(self.combat_box, (460, 300))
        self.description_rect = pg.Rect((1410, 750), (460, 300))

        # Move selection highlighter.
        self.current_slot = 1
        white = (255, 255, 255)
        black = (0, 0, 0)
        attack_select = white
        bag_select = black
        run_select = black
        spell_select = black
        self.combat_selector = {1: attack_select,
                                2: bag_select,
                                3: run_select,
                                4: spell_select
                                }

        # Pointer indicating whose turn it is during a battle.
        self.pointer = pg.image.load('black_triangle.png').convert_alpha()
        self.pointer = pg.transform.scale(self.pointer, (60, 42))
        self.point_rect = self.pointer.get_rect()
        self.pointer_frame = 0

        # Initiate fonts.
        file.cd('UI\Fonts')
        self.combat_font = pg.freetype.Font('ferrum.otf', size=24)
        self.hpmp_font = pg.freetype.Font('DisposableDroidBB_ital.ttf', size=24)

        # Add the combat boxes to the battle map front surface. Greatly improves fps due to alpha pixels.
        self.battle_map.front_surface.blit(self.status_box, (50, 750))
        self.battle_map.front_surface.blit(self.combat_box, (720, 750))
        self.battle_map.front_surface.blit(self.description_box, (1410, 750))

        # Declare enemys.
        skeleton_01 = skeleton(enemy_frames, 600, 500)
        enemy_sprites.add(skeleton_01)

        # Dialog system.
        self.black_edge1 = pg.Rect((0, 0), (1920, 200))
        self.black_edge2 = pg.Rect((0, 880), (1920, 200))
        self.dialog_start = True
        self.dialog_box = dialog_package[0]
        self.dialog_font = dialog_package[1]
        self.dialog_noise = dialog_package[2]
        self.dialog_1_final = ''
        self.dialog_2_final = ''
        self.dialog_name_final = ''
        self.dialog_length = ''
        self.e = 0
        self.a = 0
        # The script is labeled using self.event. Each dialogue references a list containing two strings.
        # The first is the actual dialgoue while the second is the speaker.
        self.script = {                0: ["Where'd you go?",   'Fursa'],
                                       1: ["*A voice starts to sound in Fursa's mind.*", ''],
                                       2: ["I am watching from afar, my child.", 'Masir'],
                                       3: ["I am afraid I must limit my aid. You must learn how to use your powers again.", 'Masir'],
                                       4: ["An evil enemy is up ahead. Go and vanquish it.", 'Masir']
                                      #  5  exits dialogue.

                                      #  6: ["Your name is Fursa. You are the son of Chaos.", '???'],
                                      # #7 is Masir portal scene.
                                      #  8: ["In the ancient tongue, your name means... chance.", '???'],
                                      #  9: ["Please follow me, as we have much to accomplish.", '???'],
                                      #  10:["Wait. What is your name?", 'Fursa'],
                                      #  11:["You may call me Masir, little one.", 'Masir']
                                      }

    def black_edges(self, screen):
        # Blackout the bottom and top of the screen during dialogue.
        black = (0, 0, 0)
        pg.draw.rect(screen, black, (0, 0, 1920, 200))
        pg.draw.rect(screen, black, (0, 880, 1920, 200))

    def dialog(self, text, name, screen):
        # Function to render and blit dialogue.
        self.black_edges(screen)
        screen.blit(self.dialog_box, (550, 880))
        if self.dialog_start:
            self.dialog_noise.play()
            self.e = 0
            self.a = 0
            self.dialog_length = len(text)
            # If text is long, wrap the text. Otherwise, simply print.
            if len(text) > 50:
                self.i = 50
                # Properly wrap text in the dialogue box by detecting spaces.
                # Text will only ever be two lines.
                # Algorithm is coded so that dialogue is "typed".
                while text[self.i] != ' ':
                    self.i += 1
                if self.i > 52:
                    self.i = 50
                    while text[self.i] != ' ':
                        self.i -= 1

        # Render text one by one until length is reached for single or double line dialog.
        if self.e != (len(text) + 1):
            if self.a == 0 or self.a != self.dialog_length:
                if len(text) > 50:
                    new_text = [text[0:self.i], text[self.i+1:]]
                    load_text_1 = new_text[0][0:self.e]
                    load_text_2 = new_text[1][0:self.a]
                    dialog_text_1, rect_1 = self.dialog_font.render(load_text_1)
                    dialog_text_2, rect_2 = self.dialog_font.render(load_text_2)
                    screen.blit(dialog_text_1, (600, 955))
                    screen.blit(dialog_text_2, (600, 1005))
                    self.e += 1
                    if self.e >= self.i:
                        self.a += 1

                    # Print the speaker's name.
                    name_text, rect_3 = self.dialog_font.render(name)
                    screen.blit(name_text, (600, 905))

                    # Store completed rendered text.
                    self.dialog_1_final = dialog_text_1
                    self.dialog_2_final = dialog_text_2
                    self.dialog_name_final = name_text

                else:
                    load_text_1 = text[0:self.e]
                    dialog_text_1, rect_1 = self.dialog_font.render(load_text_1)
                    screen.blit(dialog_text_1, (600, 955))
                    self.e += 1

                    dialog_text_2, rect_2 = self.dialog_font.render('')

                    # Print the speaker's name.
                    name_text, rect_3 = self.dialog_font.render(name)
                    screen.blit(name_text, (600, 905))

                    # Store completed rendered text.
                    self.dialog_1_final = dialog_text_1
                    self.dialog_2_final = dialog_text_2
                    self.dialog_name_final = name_text

        # If line by line render is done, simply blit the final text so avoid needless rendering.
        else:
            screen.blit(self.dialog_1_final, (600, 955))
            screen.blit(self.dialog_2_final, (600, 1005))
            screen.blit(self.dialog_name_final, (600, 905))

    def cutscene_event(self, fursa, screen):

        """ Start cutscene events when certain criteria are met.
            During a cutscene, the pygame event loop is used in this function.
            The main one located in Fursa.py is disabled. """

        if self.cutscene is False:
            # Activate dialogue upon first movement.
            if self.first_cutscene and fursa.state != 0:
                self.cutscene = True
                self.first_cutscene = False

        # CUTSCENE MODE.
        if self.cutscene:
            self.refresh_rects = [self.black_edge1, self.black_edge2]

            if self.event < 5:
                # Print dialogue based on self.event.
                self.dialog(self.script[self.event][0], self.script[self.event][1], screen)
                self.dialog_start = False
            else:
                self.black_edges(screen)

            # Pygame event loop activates ONLY during cutscenes.
            for event in pg.event.get():

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()

                # Cutscenes are navigated using mouse clicks.
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.dialog_start = True
                    self.event += 1
                    # Exit cutscenes at certain self.events.
                    if self.event == 5:
                        self.cutscene = False

        else:
            self.refresh_rects = []

    def combat_descrip(self, text, screen):
        # Function to render and blit combat move descriptions.
        rep = 0
        new_text = []
        e = 0
        i = 0
        old_i = 0
        # Wrap text multiple times. Shown as a short paragraph.
        # Algorithm is coded to show text immediately.
        while i <= len(text):
            i = old_i + 25
            if i <= len(text):
                while text[i] != ' ':
                    i += 1
                    if i > old_i + 30:
                        while text[i] != ' ':
                            i -= 1
                        break
                new_text.append(text[e:i])
                combat_text = new_text[rep]
                combat_descrip, rect = self.dialog_font.render(combat_text)
                screen.blit(combat_descrip, (1430, 800 + 50 * rep))
                rep += 1
                old_i = i
                e = i + 1
            else:
                new_text.append(text[e:i])
                combat_text = new_text[rep]
                combat_descrip, rect = self.dialog_font.render(combat_text)
                screen.blit(combat_descrip, (1430, 800 + 50 * rep))

    def battle_event(self, fursa, enemy_sprites, screen):

        """ Start battle events when certain criteria are met.
            During a battle, the pygame event loop is used in this function.
            The main one located in Fursa.py is disabled. """

        # Set slot labels.
        self.slot_labels = fursa.slot_labels
        self.combat_descriptions = fursa.combat_descriptions

        # Update refresh rects to include turn pointer.
        self.refresh_rects = [pg.Rect((spawn.centerx - 30, spawn.y + 80), (60, 60)) for spawn in self.battle_spawn_pos]

        # Initiate Fursa's UI text and print.
        white = (255, 255, 255)
        black = (0, 0, 0)
        fursa_name, rect = self.dialog_font.render('FURSA', fgcolor=black, size=36)
        fursa_lvl, rect = self.dialog_font.render('Lvl.%x' % fursa.level, fgcolor=black, size=18)
        fursa_HP, rect = self.dialog_font.render('HP:', fgcolor=(139, 0, 0), size=30)
        fursa_MP, rect = self.dialog_font.render('MP:', fgcolor=(0, 0, 139), size=30)
        fursa_hpnum, rect = self.hpmp_font.render('%s/%s' % (str(fursa.current_hp), str(fursa.max_hp)), fgcolor=black, size=48)
        fursa_mpnum, rect = self.hpmp_font.render('%s/%s' % (str(fursa.current_mp), str(fursa.max_mp)), fgcolor=black, size=48)
        screen.blit(fursa_name, (80, 800))
        screen.blit(fursa_lvl, (210, 815))
        screen.blit(fursa_HP, (300, 805))
        screen.blit(fursa_hpnum, (370, 805))
        screen.blit(fursa_MP, (500, 805))
        screen.blit(fursa_mpnum, (570, 805))

        # Print combat button labels in combat UI box.
        # self.action_select as a bool is used to determine whether the general actions or spell actions should be printed.
        # self.combat_selector determines the color.
        for slot in range(1, 5):
            slot_button, rect = self.dialog_font.render(self.slot_labels[slot][self.action_select], fgcolor=self.combat_selector[slot], size=36)
            coordinates = [(850 - int((rect.width - 150)/2), 830), (1150 - int((rect.width - 150)/2), 830),
                           (1150 - int((rect.width - 150)/2), 930), (850 - int((rect.width - 150)/2), 930)]
            screen.blit(slot_button, coordinates[slot - 1])

        self.ui = [self.combat_box_rect, self.description_rect]
        # Print the combat description of the current highlighted move in the description box.
        self.combat_descrip(self.combat_descriptions[self.current_slot][self.action_select], screen)

        """ Initialize battle parameters at the start of battle once.
            Determines the turn order by comparing characters' and enemies' turn_determiners,
            where turn_determiner = [spawn location, speed].
            The speed is used to order the turn_determiners into self.turn_order from high to low.
            As the self.current_turn is updated by an increasing self.turn_i, the corresponding
            spawn location of the selected turn_determiner is then used to identify which sprite is
            the one that is allowed to perform an action. """

        if self.battle_init:
            # Switch map and blockers to battle map.
            self.map = self.battle_map
            self.blockers = self.map.blockers
            for enemy in enemy_sprites:
                self.turn_order.append(enemy.turn_determiner)
            self.turn_order.append(fursa.turn_determiner)
            self.turn_order = sorted(self.turn_order, key=itemgetter(1), reverse=True)
            self.current_turn = self.turn_order[self.turn_i][0]
            self.battle_init = False

        # Turn changer code & Turn and enemy selection pointer.
        # Only show the pointer while choosing a move.
        if self.animation_complete is True and self.change_turn is False:
            if self.pointer_frame <= 30:
                self.pointer_frame += 1
                # Display the pointer above the sprite using its battle_spawn_pos if it is the correct current_turn.
                screen.blit(self.pointer, (self.battle_spawn_pos[self.current_turn].centerx - self.point_rect.width / 2,
                                           self.battle_spawn_pos[self.current_turn].centery + 80))
            # Create a bobbing up and down effect.
            elif self.pointer_frame <= 60:
                self.pointer_frame += 1
                screen.blit(self.pointer, (self.battle_spawn_pos[self.current_turn].centerx - self.point_rect.width / 2,
                                           self.battle_spawn_pos[self.current_turn].centery + 90))
            else:
                self.pointer_frame = 0
                screen.blit(self.pointer, (self.battle_spawn_pos[self.current_turn].centerx - self.point_rect.width / 2,
                                           self.battle_spawn_pos[self.current_turn].centery + 80))
        # Hide during animations. Uses self.change_turn as a one shot.
        elif self.animation_complete is False and self.change_turn is False:
            # Increase turn_i in preparation of the next turn.
            self.turn_i += 1
            self.change_turn = True
            if self.turn_i == len(self.turn_order):
                self.turn_i = 0
        # Once animation is complete and sprite has changed battle_command back to 0, change the current_turn.
        elif self.animation_complete is True and self.battle_command == 0:
            self.change_turn = False
            self.current_turn = (self.turn_order[self.turn_i])[0]

        """ 1 : Attack | 2 : Bag      Action UI Selector goes by clockwise slots increasing state IDs.
            -----------------------
            4 : Spell  | 3 : Run

            There are up to three stages of selecting a combat move:
                1. Choosing between the general actions show above.
                2. Choosing a certain spell or item if selector 2 or 4 is selected.
                3. Selecting the target of the spell, attack, or item.

            self.action_select is a bool used to distinguish between the general actions(false) and spell actions(true).
            self.current_select acts as an index for self.combat_selector that determines which action is highlighted white.
            The key r is used to move forward while key e is used to navigate backwards. """

        # Pygame event loop activates ONLY during battles.
        for event in pg.event.get():

            if event.type == pg.KEYDOWN:

                # If it is an ally or Fursa's turn, allow keyboard input.
                # The number 2 represents spawn_pos 0, 1, 2.
                if self.current_turn <= 2:

                    # Spell selector screen.
                    if self.action_select is True:
                        if event.key == pg.K_e:
                            # Navigate backwards.
                            self.action_select = False
                            self.new_slot = 1
                            self.dialog_noise.play()
                        elif self.current_slot == 1:
                            if event.key == pg.K_r:
                                # Create a spell in character sprite.
                                self.battle_command = 2
                                self.action_select = False
                                self.new_slot = 1
                                self.dialog_noise.play()
                            # Disallow key input if no valid move exists in the attempted key input.
                            elif event.key == pg.K_s and self.slot_labels[4][1] != '---':
                                self.new_slot = 4
                            elif event.key == pg.K_d and self.slot_labels[2][1] != '---':
                                self.new_slot = 2
                    # General actions selector.
                    else:
                        # Attack selection.
                        if self.current_slot == 1:
                            if event.key == pg.K_s:
                                self.new_slot = 4
                            elif event.key == pg.K_d:
                                self.new_slot = 2
                            # Attack command.
                            elif event.key == pg.K_r:
                                self.battle_command = 1
                        # Spell selection.
                        elif self.current_slot == 4:
                            # Spell command. Changes slot labels to spells.
                            if event.key == pg.K_r:
                                self.action_select = True
                                self.new_slot = 1
                            elif event.key == pg.K_w:
                                self.new_slot = 1
                            elif event.key == pg.K_d:
                                self.new_slot = 3
                        # Bag selection.
                        elif self.current_slot == 2:
                            if event.key == pg.K_a:
                                self.new_slot = 1
                            elif event.key == pg.K_s:
                                self.new_slot = 3
                        # Run selection.
                        elif self.current_slot == 3:
                            if event.key == pg.K_a:
                                self.new_slot = 4
                            elif event.key == pg.K_w:
                                self.new_slot = 2

                    # If a change has been made, update selector colors.
                    if self.new_slot != self.current_slot:
                        self.combat_selector[self.current_slot] = black
                        self.combat_selector[self.new_slot] = white
                        self.current_slot = self.new_slot
                        self.dialog_noise.play()

                if event.key == pg.K_ESCAPE:
                    pg.quit()

            elif event.type == pg.MOUSEBUTTONDOWN:
                pass

    def update(self, fursa, enemy_sprites, screen):
        if self.battle is False:
            self.cutscene_event(fursa, screen)
        else:
            self.battle_event(fursa, enemy_sprites, screen)
