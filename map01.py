import pygame as pg
from TiledMap import TiledMap
from npc import Masir_sprite
from base_map import BaseMap


# Starting area.
class Map01(BaseMap):
    def __init__(self, package, sprites, fi):
        super().__init__(package)
        self.fi = fi

        # Map graphics and music.
        self.fi.cd('Maps Map_01')
        self.map = TiledMap(self.fi.path('Map_01_1920x1080.tmx'))
        self.map.make_map()
        self.blockers = self.map.blockers
        self.music = pg.mixer.music.load(self.fi.path('296 - The Tea Garden (Loop).mp3'))
        pg.mixer.music.play(loops=-1, start=0.0)

        # Declare npcs.
        self.Masir = Masir_sprite(800, 600, self.fi)
        self.Masir_dead = False
        sprites['npc'].add(self.Masir)

        # The script is labeled using self.event. Each dialogue references a list containing two strings.
        # The first is the actual dialogue while the second is the speaker.
        self.script = {  0: ["Where am I?",   'Boy'],
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

    def update(self, fursa, sprites, screen):
        self.cutscene_event(fursa, screen)
