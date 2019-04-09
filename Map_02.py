import pygame as pg
from directory_change import files
from spritesheet import spritesheet
from TiledMap import TiledMap
from enemies import skeleton, enemy_frames

# Area 2
class Map_02():
    def __init__(self, npc_sprites, dialog_package, enemy_frames, enemy_sprites):
        file = files()

        # Map graphics and music.
        file.cd('Maps\Map_02')
        self.map = TiledMap('Map_02.tmx')
        self.map.make_map()
        self.cutscene = False
        self.first_stage = True
        self.battle = False
        self.event = 0
        self.spawnx = 100
        self.spawny = 500
        self.map_first_time = True
        coordinates = []
        self.refresh_rects = []
        self.ui = []

        # Battle Scene.
        self.battle_map = TiledMap('battle_scene.tmx')
        self.battle_map.make_map()
        self.battle_spawn_pos = self.battle_map.battle_spawns
        file.cd('UI\Combat')
        self.combat_box = pg.image.load('Combat UI Box transparent.png').convert_alpha()
        self.status_box = pg.transform.scale(self.combat_box, (670,300))
        self.combat_box = pg.transform.scale(self.combat_box, (690,300))
        self.combat_box_rect = pg.Rect((720, 750), (690, 300))
        self.description_box = pg.transform.scale(self.combat_box, (460,300))
        self.description_rect = pg.Rect((1410, 750), (460, 300))
        self.pointer = pg.image.load('black_triangle.png').convert_alpha()
        self.pointer = pg.transform.scale(self.pointer, (60,42))
        self.point_rect = self.pointer.get_rect()
        file.cd('UI\Fonts')
        self.combat_font = pg.freetype.Font('ferrum.otf', size = 24)
        self.hpmp_font = pg.freetype.Font('DisposableDroidBB_ital.ttf', size = 24)

        self.battle_map.front_surface.blit(self.status_box, (50,750))
        self.battle_map.front_surface.blit(self.combat_box, (720,750))
        self.battle_map.front_surface.blit(self.description_box, (1410,750))

        self.battle_init = True

        white = (255,255,255)
        black = (0,0,0)
        self.current_slot = 1
        self.action_select = False
        self.pointer_frame = 0
        self.battle_command = 0
        attack_select = white
        bag_select = black
        run_select = black
        spell_select = black
        self.combat_selector = { 1: attack_select,
                                 2: bag_select,
                                 3: run_select,
                                 4: spell_select }

        # Declare enemys.
        skeleton_01 = skeleton(enemy_frames, 600, 500)
        enemy_sprites.add(skeleton_01)

        # Dialog dictionary.
        self.black_edge1 = pg.Rect((0,0), (1920,200))
        self.black_edge2 = pg.Rect((0,880), (1920,200))
        self.dialog_start = True
        self.dialog_box = dialog_package[0]
        self.dialog_font = dialog_package[1]
        self.dialog_noise = dialog_package[2]
        self.e = 0
        self.a = 0
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
        black = (0,0,0)
        pg.draw.rect(screen, black, (0,0,1920,200))
        pg.draw.rect(screen, black, (0,880,1920,200))

    # Function to render and blit dialog.
    def dialog(self, text, name, screen):
        self.black_edges(screen)
        screen.blit(self.dialog_box, (550,880))
        load_text = ''
        if self.dialog_start:
            self.dialog_noise.play()
            self.e = 0
            self.a = 0

        if len(text) > 50:
            i = 50
            while text[i] != ' ':
                i += 1
            if i > 52:
                i = 50
                while text[i] != ' ':
                    i -= 1

            new_text = [text[0:i], text[i+1:]]
            load_text_1 = new_text[0][0:self.e]
            load_text_2 = new_text[1][0:self.a]
            dialog_text_1, rect_1 = self.dialog_font.render(load_text_1)
            dialog_text_2, rect_2 = self.dialog_font.render(load_text_2)
            screen.blit(dialog_text_1, (600, 955))
            screen.blit(dialog_text_2, (600, 1005))
            self.e += 1
            if self.e >= i:
                self.a += 1

        else:
            load_text_1 = text[0:self.e]
            dialog_text_1, rect_1 = self.dialog_font.render(load_text_1)
            screen.blit(dialog_text_1, (600,955))
            self.e += 1

        name_text, rect_3 = self.dialog_font.render(name)
        screen.blit(name_text, (600,905))

    def cutscene_event(self, character, screen):
        if self.cutscene is False:
            if self.first_stage and character.state != 0:
                self.cutscene = True
                self.first_stage = False

        if self.cutscene:
            self.refresh_rects = [self.black_edge1, self.black_edge2]

            if self.event < 5:
                self.dialog(self.script[self.event][0], self.script[self.event][1], screen)
                self.dialog_start = False
            else:
                self.black_edges(screen)

            # Allow exiting the game during a cutscene.
            for event in pg.event.get():
                # Allow to quit game. Included in this portion to be able to keep only one event loop.
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                         pg.quit()
                         sys.exit()

                # Navigating cutscenes.
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.dialog_start = True
                    self.event += 1
                    if self.event == 5:
                        self.cutscene = False

        else:
            self.refresh_rects = []

    def combat_descrip(self, text, screen):
        load_text = ''
        rep = 0
        new_text = []
        e = 0
        i = 0
        old_i = 0
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

    def battle_event(self, character, enemy_sprites, screen):
        self.slot_labels = character.slot_labels
        self.combat_descriptions = character.combat_descriptions
        white = (255,255,255)
        black = (0,0,0)
        self.map = self.battle_map

        # Fursa UI.
        Fursa_name, rect = self.dialog_font.render('FURSA', fgcolor = black, size = 36)
        Fursa_lvl, rect = self.dialog_font.render('Lvl.%x' % character.level, fgcolor = black, size = 18)
        Fursa_HP, rect = self.dialog_font.render('HP:', fgcolor = (139,0,0), size = 30)
        Fursa_MP, rect = self.dialog_font.render('MP:', fgcolor = (0,0,139), size = 30)
        Fursa_hpnum, rect = self.hpmp_font.render('%s/%s' % (str(character.current_hp), str(character.max_hp)), fgcolor = black, size = 48)
        Fursa_mpnum, rect = self.hpmp_font.render('%s/%s' % (str(character.current_mp), str(character.max_mp)), fgcolor = black, size = 48)
        screen.blit(Fursa_name, (80, 800))
        screen.blit(Fursa_lvl, (210, 815))
        screen.blit(Fursa_HP, (300, 805))
        screen.blit(Fursa_hpnum, (370, 805))
        screen.blit(Fursa_MP, (500, 805))
        screen.blit(Fursa_mpnum, (570, 805))

        # Combat UI.
        for slot in range(1, 5):
            slot_button, rect = self.dialog_font.render(self.slot_labels[slot][self.action_select], fgcolor = self.combat_selector[slot], size = 36)
            coordinates = [(850 - int((rect.width - 150)/2), 830), (1150 - int((rect.width - 150)/2), 830),
                           (1150 - int((rect.width - 150)/2), 930), (850 - int((rect.width - 150)/2), 930)]
            screen.blit(slot_button, coordinates[slot - 1])


        self.refresh_rects = []
        self.ui = [self.combat_box_rect, self.description_rect]
        self.combat_descrip(self.combat_descriptions[self.current_slot][self.action_select], screen)

        # Initializing battle parameters.
        if self.battle_init:
            self.turn_i = 0
            # Turn order based on speed. *WARNING Very preliminary. Rough code for simple functionality.
            # Will have to completely revamp once additional sprites are added.
            for enemy in enemy_sprites:
                if character.speed > enemy.speed:
                    self.turn_order = [character.party_spawn, enemy.party_spawn]
                else:
                    self.turn_order = [enemy.party_spawn, character.party_spawn]
            self.battle_init = False


        # Turn and enemy selection pointer.
        if self.pointer_frame <= 30:
            self.pointer_frame += 1
            screen.blit(self.pointer, (self.battle_spawn_pos[self.turn_order[self.turn_i]].centerx - self.point_rect.width / 2,
                                       self.battle_spawn_pos[self.turn_order[self.turn_i]].centery + 80))
        elif self.pointer_frame <= 60:
            self.pointer_frame += 1
            screen.blit(self.pointer, (self.battle_spawn_pos[self.turn_order[self.turn_i]].centerx - self.point_rect.width / 2,
                                       self.battle_spawn_pos[self.turn_order[self.turn_i]].centery + 90))
        else:
            self.pointer_frame = 0
            screen.blit(self.pointer, (self.battle_spawn_pos[self.turn_order[self.turn_i]].centerx - self.point_rect.width / 2,
                                       self.battle_spawn_pos[self.turn_order[self.turn_i]].centery + 80))


        """ 1 : Action | 2 : Bag      Action UI Selector goes by clockwise slots increasing state IDs.
            -----------------------
            4 : Spell  | 3 : Run    """


        # Allow exiting the game during a cutscene.
        for event in pg.event.get():
            # Allow to quit game. Included in this portion to be able to keep only one event loop.
            if event.type == pg.KEYDOWN:
                if self.action_select is True:
                    if event.key == pg.K_e:
                        self.action_select = False
                        self.combat_selector[self.current_slot] = black
                        self.current_slot = 1
                        self.combat_selector[self.current_slot] = white
                        self.dialog_noise.play()

                else:

                    if self.current_slot == 1:
                        if event.key == pg.K_s and self.slot_labels[slot][self.action_select] != '---':
                            self.combat_selector[self.current_slot] = black
                            self.current_slot = 4
                            self.combat_selector[self.current_slot] = white
                            self.dialog_noise.play()
                        elif event.key == pg.K_d and self.slot_labels[slot][self.action_select] != '---':
                            self.combat_selector[self.current_slot] = black
                            self.current_slot = 2
                            self.combat_selector[self.current_slot] = white
                            self.dialog_noise.play()
                        elif event.key == pg.K_r:
                            self.battle_command = 1
                            self.dialog_noise.play()
                    elif self.current_slot == 4:
                        if event.key == pg.K_r and self.slot_labels[slot][self.action_select] != '---':
                            self.action_select = True
                            self.combat_selector[self.current_slot] = black
                            self.current_slot = 1
                            self.combat_selector[self.current_slot] = white
                            self.dialog_noise.play()
                        elif event.key == pg.K_w and self.slot_labels[slot][self.action_select] != '---':
                            self.combat_selector[self.current_slot] = black
                            self.current_slot = 1
                            self.combat_selector[self.current_slot] = white
                            self.dialog_noise.play()
                        elif event.key == pg.K_d and self.slot_labels[slot][self.action_select] != '---':
                            self.combat_selector[self.current_slot] = black
                            self.current_slot = 3
                            self.combat_selector[self.current_slot] = white
                            self.dialog_noise.play()
                    elif self.current_slot == 2:
                        if event.key == pg.K_a and self.slot_labels[slot][self.action_select] != '---':
                            self.combat_selector[self.current_slot] = black
                            self.current_slot = 1
                            self.combat_selector[self.current_slot] = white
                            self.dialog_noise.play()
                        elif event.key == pg.K_s and self.slot_labels[slot][self.action_select] != '---':
                            self.combat_selector[self.current_slot] = black
                            self.current_slot = 3
                            self.combat_selector[self.current_slot] = white
                            self.dialog_noise.play()
                    elif self.current_slot == 3:
                        if event.key == pg.K_a and self.slot_labels[slot][self.action_select] != '---':
                            self.combat_selector[self.current_slot] = black
                            self.current_slot = 4
                            self.combat_selector[self.current_slot] = white
                            self.dialog_noise.play()
                        elif event.key == pg.K_w and self.slot_labels[slot][self.action_select] != '---':
                            self.combat_selector[self.current_slot] = black
                            self.current_slot = 2
                            self.combat_selector[self.current_slot] = white
                            self.dialog_noise.play()

                if event.key == pg.K_ESCAPE:
                     pg.quit()
                     sys.exit()

            # Navigating cutscenes.
            elif event.type == pg.MOUSEBUTTONDOWN:
                pass


    def update(self, character, enemy_sprites, screen):
        if character.battle is False:
            self.battle = False
            self.cutscene_event(character, screen)
        else:
            self.battle = True
            self.battle_event(character, enemy_sprites, screen)
