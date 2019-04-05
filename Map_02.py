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
        coordinates = []

        # Battle Scene.
        self.battle_map = TiledMap('battle_scene.tmx')
        self.battle_map.make_map()
        self.battle_spawn_pos = self.battle_map.battle_spawns
        file.cd('UI\Combat')
        self.combat_box = pg.image.load('Combat UI Box.png').convert_alpha()
        self.combat_box = pg.transform.scale(self.combat_box, (960,300))

        # Declare enemys.
        skeleton_01 = skeleton(enemy_frames, 600, 500)
        enemy_sprites.add(skeleton_01)

        # Dialog dictionary.
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

    def battle_event(self, character, screen):
        self.map = self.battle_map
        screen.blit(self.combat_box, (0,780))
        screen.blit(self.combat_box, (960,780))


        # Allow exiting the game during a cutscene.
        for event in pg.event.get():
            # Allow to quit game. Included in this portion to be able to keep only one event loop.
            if event.type == pg.KEYDOWN:
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
