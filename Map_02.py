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
        self.pointer = pg.image.load('black_triangle.png').convert_alpha()
        self.pointer = pg.transform.scale(self.pointer, (40,25))
        file.cd('UI\Fonts')
        self.combat_font = pg.freetype.Font('ferrum.otf', size = 24)
        self.hpmp_font = pg.freetype.Font('DisposableDroidBB_ital.ttf', size = 24)

        white = (255,255,255)
        black = (0,0,0)
        self.current_select = 1
        attack_select = white
        bag_select = black
        run_select = black
        spell_select = black
        self.combat_selector = { 1: attack_select,
                                 2: bag_select,
                                 3: run_select,
                                 4: spell_select }

        self.refresh_rects = []

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

    def battle_event(self, character, screen):
        self.refresh_rects = [self.combat_box_rect]
        white = (255,255,255)
        black = (0,0,0)
        self.map = self.battle_map
        screen.blit(self.status_box, (50,750))
        screen.blit(self.combat_box, (720,750))
        screen.blit(self.description_box, (1410,750))
        Fursa_name, rect = self.dialog_font.render('FURSA', fgcolor = black, size = 36)
        Fursa_lvl, rect = self.dialog_font.render('Lvl.1', fgcolor = black, size = 18)
        Fursa_HP, rect = self.dialog_font.render('HP:', fgcolor = (139,0,0), size = 30)
        Fursa_MP, rect = self.dialog_font.render('MP:', fgcolor = (0,0,139), size = 30)
        Fursa_hpnum, rect = self.hpmp_font.render('10/10', fgcolor = black, size = 48)
        Fursa_mpnum, rect = self.hpmp_font.render('10/10', fgcolor = black, size = 48)
        screen.blit(Fursa_name, (80, 800))
        screen.blit(Fursa_lvl, (210, 815))
        screen.blit(Fursa_HP, (300, 805))
        screen.blit(Fursa_hpnum, (370, 805))
        screen.blit(Fursa_MP, (500, 805))
        screen.blit(Fursa_mpnum, (570, 805))

        attack_button, rect = self.dialog_font.render('ATTACK', fgcolor = self.combat_selector[1], size = 36)
        spell_button, rect = self.dialog_font.render('SPELL', fgcolor = self.combat_selector[4], size = 36)
        bag_button, rect = self.dialog_font.render('BAG', fgcolor = self.combat_selector[2], size = 36)
        run_button, rect = self.dialog_font.render('RUN', fgcolor = self.combat_selector[3], size = 36)
        screen.blit(attack_button, (850, 830))
        screen.blit(spell_button, (850, 930))
        screen.blit(bag_button, (1150, 830))
        screen.blit(run_button, (1150, 930))


        screen.blit(self.pointer, (self.battle_spawn_pos[1].x, self.battle_spawn_pos[1].y))


        """ 1 : Action | 2 : Bag      Action UI Selector goes by clockwise increasing state IDs.
            -----------------------
            4 : Spell  | 3 : Run    """


        # Allow exiting the game during a cutscene.
        for event in pg.event.get():
            # Allow to quit game. Included in this portion to be able to keep only one event loop.
            if event.type == pg.KEYDOWN:
                if self.current_select == 1:
                    if event.key == pg.K_s:
                        self.combat_selector[self.current_select] = black
                        self.current_select = 4
                        self.combat_selector[self.current_select] = white
                        self.dialog_noise.play()
                    elif event.key == pg.K_d:
                        self.combat_selector[self.current_select] = black
                        self.current_select = 2
                        self.combat_selector[self.current_select] = white
                        self.dialog_noise.play()
                elif self.current_select == 2:
                    if event.key == pg.K_a:
                        self.combat_selector[self.current_select] = black
                        self.current_select = 1
                        self.combat_selector[self.current_select] = white
                        self.dialog_noise.play()
                    elif event.key == pg.K_s:
                        self.combat_selector[self.current_select] = black
                        self.current_select = 3
                        self.combat_selector[self.current_select] = white
                        self.dialog_noise.play()
                elif self.current_select == 3:
                    if event.key == pg.K_a:
                        self.combat_selector[self.current_select] = black
                        self.current_select = 4
                        self.combat_selector[self.current_select] = white
                        self.dialog_noise.play()
                    elif event.key == pg.K_w:
                        self.combat_selector[self.current_select] = black
                        self.current_select = 2
                        self.combat_selector[self.current_select] = white
                        self.dialog_noise.play()
                elif self.current_select == 4:
                    if event.key == pg.K_w:
                        self.combat_selector[self.current_select] = black
                        self.current_select = 1
                        self.combat_selector[self.current_select] = white
                        self.dialog_noise.play()
                    elif event.key == pg.K_d:
                        self.combat_selector[self.current_select] = black
                        self.current_select = 3
                        self.combat_selector[self.current_select] = white
                        self.dialog_noise.play()

                if event.key == pg.K_ESCAPE:
                     pg.quit()
                     sys.exit()

            # Navigating cutscenes.
            elif event.type == pg.MOUSEBUTTONDOWN:
                pass


    def update(self, character, screen):
        if character.battle is False:
            self.battle = False
            self.cutscene_event(character, screen)
        else:
            self.battle = True
            self.battle_event(character, screen)
