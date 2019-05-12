import pygame as pg
from TiledMap import TiledMap
from enemies import skeleton
from base_map import base_map


# Area 2
class Map_02(base_map):
    def __init__(self, package, sprites, enemy_frames, fi):
        super().__init__(package)
        self.fi = fi

        # Map graphics and music.
        self.fi.cd('Maps\Map_02')
        self.map = TiledMap('Map_02.tmx')
        self.map.make_map()
        self.blockers = self.map.blockers

        # Fursa spawn location.
        self.spawnx = 100
        self.spawny = 500

        # BATTLE MODE.
        # Battle map, spawn locations, turn order, and states.
        self.battle_map = TiledMap('battle_scene.tmx')
        self.battle_map.make_map()
        self.battle_spawn_pos = self.battle_map.battle_spawns

        # Add the combat boxes to the battle map front surface. Greatly improves fps due to alpha pixels.
        self.battle_map.front_surface.blit(self.status_box, (50, 750))
        self.battle_map.front_surface.blit(self.combat_box, (720, 750))
        self.battle_map.front_surface.blit(self.description_box, (1410, 750))

        # Declare enemys.
        skeleton_01 = skeleton(enemy_frames, 600, 500, self.fi)
        sprites['enemy'].add(skeleton_01)

        # The script is labeled using self.event. Each dialogue references a list containing two strings.
        # The first is the actual dialogue while the second is the speaker.
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

    def update(self, fursa, sprites, screen):

        # If not already in a battle, and hit by an enemy's attack, transition to battle mode.
        if self.battle is False:
            for enemy in sprites['enemy']:
                if enemy.attack:
                    if fursa.hitbox_rect.colliderect(enemy.rect) and enemy.frame_index == 8:
                        current_enemy = enemy
                        self.battle_transition(screen, sprites, fursa, current_enemy)

        if self.battle is False:
            self.cutscene_event(fursa, screen)
        else:
            self.battle_event(fursa, sprites['enemy'], screen)
