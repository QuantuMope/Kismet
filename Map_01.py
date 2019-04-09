import pygame as pg
from directory_change import files
from spritesheet import spritesheet
from TiledMap import TiledMap
from npc import Masir_sprite

# Starting area.
class Map_01():
    def __init__(self, npc_sprites, dialog_package):
        file = files()

        # Map graphics and music.
        file.cd('Maps\Map_01')
        self.map = TiledMap('Map_01_1920x1080.tmx')
        self.music = pg.mixer.music.load('296 - The Tea Garden (Loop).mp3')
        pg.mixer.music.play(loops = -1, start = 0.0)
        self.map.make_map()
        self.cutscene = False
        self.first_stage = True
        self.battle = False
        self.event = 0
        self.Masir_dead = False
        self.map_first_time = True
        coordinates = []

        # Portal animation.
        for i in range(0,7):
            coordinates.extend([(100 * e, 100 * i, 100, 100) for e in range(0, 8)])
        coordinates.extend([(100 * e, 700, 100, 100) for e in range(0, 5)])

        portal_images_ss = spritesheet('12_nebula_spritesheet.png')
        portal_images_separate = portal_images_ss.images_at(coordinates, colorkey = (0, 0, 0))
        self.portal_images = [pg.transform.scale(portal_images_separate[i], (160, 160)) for i in range(0, len(portal_images_separate))]
        self.p_index = 0
        self.portal_start = False
        self.portal_blast = pg.mixer.Sound('portal_noise.wav')
        self.portal_blast.set_volume(0.50)
        self.portal_aura = pg.mixer.Sound('portal_aura_noise.wav')
        self.portal_aura.set_volume(0.40)
        self.portal_blast_start = True
        self.portal_aura_start = True
        self.portal_rect = pg.Rect(1115,660,160,160)

        self.refresh_rects = [self.portal_rect]
        self.ui = []

        self.end_sounds = [self.portal_aura]

        # Declare npcs.
        self.Masir = Masir_sprite(800, 600)
        npc_sprites.add(self.Masir)

        # Dialog dictionary.
        self.black_edge1 = pg.Rect((0,0), (1920,200))
        self.black_edge2 = pg.Rect((0,880), (1920,200))
        self.dialog_start = True
        self.dialog_box = dialog_package[0]
        self.dialog_font = dialog_package[1]
        self.dialog_noise = dialog_package[2]
        self.e = 0
        self.a = 0
        self.script = {                0: ["Where am I?",   'Boy'],
                                       1: ["... Who am I?", 'Boy'],
                                       2: ["So you\'ve awakened, my child.", '???'],
                                       3: ["... Do you know me?", 'Boy'],
                                       4: ["... It seems you\'ve lost more of your memory than I would have liked.", '???'],
                                       5: ["Please explain. I'm so confused. Who am I?", 'Boy'],
                                       6: ["Your name is Fursa. You are the son of Chaos.", '???'],
                                      #7 is Masir portal scene.
                                       8: ["In the ancient tongue, your name means... chance.", '???'],
                                       9: ["Please follow me, as we have much to accomplish.", '???'],
                                       10:["Wait. What is your name?", 'Fursa'],
                                       11:["You may call me Masir, little one.", 'Masir']}


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

            if abs(character.rect.centerx - self.Masir.rect.centerx) < 150:
                if self.Masir_dead is False:
                    self.cutscene = True

        if self.cutscene:
            self.refresh_rects = [self.portal_rect, self.black_edge1, self.black_edge2]

            if self.event < 7:
                self.dialog(self.script[self.event][0], self.script[self.event][1], screen)
                self.dialog_start = False
            elif self.event == 7:
                self.Masir.attack = True
                self.event += 1
                self.black_edges(screen)
            elif self.Masir.attack is False and self.event < 12:
                self.dialog(self.script[self.event][0], self.script[self.event][1], screen)
                self.dialog_start = False
            elif self.event >= 12:
                self.Masir.walk = True
                self.Masir.rect.x += 1
                self.black_edges(screen)
            else:
                self.black_edges(screen)

            if self.Masir.attack is True:
                if self.Masir.frame_index == 16:
                    self.portal_start = True
                    if self.portal_aura_start:
                        self.portal_aura.play(loops = -1)
                        self.portal_aura_start = False
                elif self.Masir.frame_index == 3 and self.portal_blast_start:
                    self.portal_blast.play()
                    self.portal_blast_start = False

            if self.Masir.rect.centerx == self.portal_rect.centerx:
                self.Masir.kill()
                self.cutscene = False
                self.Masir_dead = True

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
                    if self.event == 2:
                        self.cutscene = False

        else:
            self.refresh_rects = [self.portal_rect]

        if self.portal_start is True:
            screen.blit(self.portal_images[self.p_index], (1115,660))
            self.p_index += 1
            if self.p_index == len(self.portal_images):
                self.p_index = 0


    def update(self, character, enemy_sprites, screen):
        self.cutscene_event(character, screen)
