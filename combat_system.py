import pygame as pg
from operator import itemgetter


# Takes care of the combat system in map classes. Serves as a parent class.
class combat_system():
    def __init__(self, package):

        self.status_box = package['statusBox']
        self.combat_box = package['combatBox']
        self.combat_box_rect = pg.Rect((720, 750), (690, 300))
        self.description_box = package['descriptionBox']
        self.description_rect = pg.Rect((1410, 750), (460, 300))
        self.pointer = package['pointer']
        self.point_rect = self.pointer.get_rect()
        self.combat_font = package['combatFont']
        self.hpmp_font = package['hpmpFont']
        self.battle_sword_aftersound = package['battleNoises'][0]
        self.battle_impact_noise = package['battleNoises'][1]
        self.battle_impact_noise.set_volume(0.50)

        # Battle Transition Screen.
        resolution = width, height = 1920, 1080
        black = (0, 0, 0)
        self.battle_transition_screen = pg.Surface(resolution)
        self.battle_transition_screen.fill(black)

        # States.
        self.battle_init = True
        self.turn_order = []
        self.turn_i = 0
        self.battle_command = 0
        self.action_select = False
        self.animation_complete = True
        self.returned = True
        self.change_turn = False
        self.pointer_frame = 0

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

    def battle_transition(self, screen, sprites, fursa, current_enemy):

        # Set frame to a hit frame.
        fursa.image = fursa.all_frames[6][2]

        # Pause impact frame for 1s.
        self.battle_impact_noise.play()
        pg.mixer.music.stop()
        sprites['enemy'].draw(screen)
        sprites['character'].draw(screen)
        screen.blit(self.map.front_surface, (0, 0))
        pg.display.flip()
        pg.time.wait(1000)
        # Clear background to black for 1s.
        screen.blit(self.battle_transition_screen, (0, 0))
        sprites['enemy'].draw(screen)
        sprites['character'].draw(screen)
        pg.display.flip()
        self.battle_sword_aftersound.play()
        pg.time.wait(1000)

        # Initiate music.
        self.fi.cd('Maps\Map_02')
        battle_music = pg.mixer.music.load('300-B - Blood of Lilith (Loop, MP3).mp3')
        pg.mixer.music.play(loops=-1, start=0.0)

        # Initialize states.
        fursa.state = 0
        fursa.frame_index = 0
        fursa.facing_right = True
        current_enemy.facing_right = False
        fursa.jump = False
        fursa.battle_forward = True
        self.battle = True

        # Spawn locations.
        fursa.rect.centerx = self.battle_spawn_pos[fursa.party_spawn].centerx
        fursa.rect.centery = self.battle_spawn_pos[fursa.party_spawn].centery
        current_enemy.rect.centerx = self.battle_spawn_pos[current_enemy.party_spawn].centerx
        current_enemy.rect.centery = self.battle_spawn_pos[current_enemy.party_spawn].centery

    """ Battle Platform Layout.
                                              Midpoint for Ranged Attacks
                                  Ally                       |                  Enemies

Spawn Location Indexes    ------0---------1-----------2----------6-----------4---------5--------6------"""


    def battle_event(self, fursa, enemy_sprites, screen):

        """ Start battle events when certain criteria are met.
            During a battle, the pygame event loop is used in this function.
            The main one located in Fursa.py is disabled. """

        # Set slot labels.
        self.slot_labels = fursa.slot_labels
        self.combat_descriptions = fursa.combat_descriptions

        # Update refresh rects to include turn pointer.
        self.refresh_rects = [pg.Rect((spawn.centerx - 30, spawn.y + 80), (60, 60)) for spawn in
                              self.battle_spawn_pos]

        # Initiate Fursa's UI text and print.
        white = (255, 255, 255)
        black = (0, 0, 0)
        fursa_name, rect = self.dialog_font.render('FURSA', fgcolor=black, size=36)
        fursa_lvl, rect = self.dialog_font.render('Lvl.%x' % fursa.level, fgcolor=black, size=18)
        fursa_HP, rect = self.dialog_font.render('HP:', fgcolor=(139, 0, 0), size=30)
        fursa_MP, rect = self.dialog_font.render('MP:', fgcolor=(0, 0, 139), size=30)
        fursa_hpnum, rect = self.hpmp_font.render('%s/%s' % (str(fursa.current_hp), str(fursa.max_hp)),
                                                  fgcolor=black, size=48)
        fursa_mpnum, rect = self.hpmp_font.render('%s/%s' % (str(fursa.current_mp), str(fursa.max_mp)),
                                                  fgcolor=black, size=48)
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
            slot_button, rect = self.dialog_font.render(self.slot_labels[slot][self.action_select],
                                                        fgcolor=self.combat_selector[slot], size=36)
            coordinates = [(850 - int((rect.width - 150) / 2), 830), (1150 - int((rect.width - 150) / 2), 830),
                           (1150 - int((rect.width - 150) / 2), 930), (850 - int((rect.width - 150) / 2), 930)]
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
                screen.blit(self.pointer,
                            (self.battle_spawn_pos[self.current_turn].centerx - self.point_rect.width / 2,
                             self.battle_spawn_pos[self.current_turn].centery + 80))
            # Create a bobbing up and down effect.
            elif self.pointer_frame <= 60:
                self.pointer_frame += 1
                screen.blit(self.pointer,
                            (self.battle_spawn_pos[self.current_turn].centerx - self.point_rect.width / 2,
                             self.battle_spawn_pos[self.current_turn].centery + 90))
            else:
                self.pointer_frame = 0
                screen.blit(self.pointer,
                            (self.battle_spawn_pos[self.current_turn].centerx - self.point_rect.width / 2,
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
