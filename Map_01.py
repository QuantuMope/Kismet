import pygame as pg
from directory_change import files
from spritesheet import spritesheet
from TiledMap import TiledMap
from npc import Masir_sprite


# Starting area.
class Map_01():
    def __init__(self, dialog_package, npc_sprites):
        file = files()

        # Map graphics and music.
        file.cd('Maps\Map_01')
        self.map = TiledMap('Map_01_1920x1080.tmx')
        self.map.make_map()
        self.blockers = self.map.blockers
        self.music = pg.mixer.music.load('296 - The Tea Garden (Loop).mp3')
        pg.mixer.music.play(loops=-1, start=0.0)

        # States.
        self.cutscene = False
        self.first_cutscene = True
        self.battle = False
        self.event = 0
        self.Masir_dead = False
        self.map_first_time = True

        # Portal animation.
        coordinates = []
        for i in range(0,7):
            coordinates.extend([(100 * e, 100 * i, 100, 100) for e in range(0, 8)])
        coordinates.extend([(100 * e, 700, 100, 100) for e in range(0, 5)])
        portal_images_ss = spritesheet('12_nebula_spritesheet.png')
        portal_images_separate = portal_images_ss.images_at(coordinates, colorkey=(0, 0, 0))
        self.portal_images = [pg.transform.scale(portal_images_separate[i], (160, 160)) for i in range(0, len(portal_images_separate))]
        self.p_index = 0
        self.portal_start = False
        self.portal_blast = pg.mixer.Sound('portal_noise.wav')
        self.portal_blast.set_volume(0.50)
        self.portal_aura = pg.mixer.Sound('portal_aura_noise.wav')
        self.portal_aura.set_volume(0.40)
        self.portal_blast_start = True
        self.portal_aura_start = True
        self.portal_rect = pg.Rect(1115, 660, 160, 160)

        # Refresh rects and sounds to end when map is terminated.
        self.ui = []
        self.refresh_rects = [self.portal_rect]
        self.end_sounds = [self.portal_aura]

        # Declare npcs.
        self.Masir = Masir_sprite(800, 600)
        npc_sprites.add(self.Masir)

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
        self.i = 0
        # The script is labeled using self.event. Each dialogue references a list containing two strings.
        # The first is the actual dialgoue while the second is the speaker.
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

            # Activate secondary dialogue when approaching Masir.
            if abs(fursa.rect.centerx - self.Masir.rect.centerx) < 150 and self.Masir_dead is False:
                self.cutscene = True

        # CUTSCENE MODE.
        if self.cutscene:
            self.refresh_rects = [self.portal_rect, self.black_edge1, self.black_edge2]

            if self.event < 7:
                # Print dialogue based on self.event.
                self.dialog(self.script[self.event][0], self.script[self.event][1], screen)
                self.dialog_start = False
            elif self.event == 7:
                # Masir portal creation scene.
                self.Masir.attack = True
                self.event += 1
                self.black_edges(screen)
            elif self.Masir.attack is False and self.event < 12:
                # After portal is created, further dialogue.
                self.dialog(self.script[self.event][0], self.script[self.event][1], screen)
                self.dialog_start = False
            elif self.event >= 12:
                # Once dialogue is completed, Masir approaches the portal.
                self.Masir.walking = True
                self.Masir.rect.x += 1
                self.black_edges(screen)
            else:
                self.black_edges(screen)

            # Create the portal during Masir's cutscene.
            if self.Masir.attack is True:
                if self.Masir.frame_index == 16:
                    self.portal_start = True
                    if self.portal_aura_start:
                        self.portal_aura.play(loops=-1)
                        self.portal_aura_start = False
                elif self.Masir.frame_index == 3 and self.portal_blast_start:
                    self.portal_blast.play()
                    self.portal_blast_start = False

            # Once Masir is in contact with the portal, kill the sprite and end the cutscene.
            if self.Masir.rect.centerx == self.portal_rect.centerx:
                self.Masir.kill()
                self.cutscene = False
                self.Masir_dead = True

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
                    if self.event == 2:
                        self.cutscene = False

        else:
            self.refresh_rects = [self.portal_rect]

        # Portal frame change and frame index reset.
        if self.portal_start is True:
            screen.blit(self.portal_images[self.p_index], (1115, 660))
            self.p_index += 1
            if self.p_index == len(self.portal_images):
                self.p_index = 0

    def update(self, fursa, enemy_sprites, screen):
        self.cutscene_event(fursa, screen)
