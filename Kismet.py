import pygame as pg
import pygame.freetype
import sys
from time import sleep
import random

# Import Modules
from directory_change import files
from Fursa import Fursa_sprite, blast_frames, Fursa_blast
from enemies import enemy_frames
from Map_01 import Map_01
from Map_02 import Map_02

# Game Start.
def main():
    fi = files()
    # Game parameters.
    pg.mixer.pre_init(44100, -16, 2, 1024)
    pg.init()
    pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.MOUSEBUTTONDOWN])
    resolution = width, height = 1920,1080
    flags = pg.FULLSCREEN | pg.HWSURFACE | pg.DOUBLEBUF
    screen = pg.display.set_mode(resolution, flags)
    screen.set_alpha(None)
    pg.display.set_caption('Kismet')
    clock = pg.time.Clock()
    fi.cd('UI\Dialog')
    dialog_box = pg.image.load('dialogue_box.png').convert_alpha()
    dialog_box = pg.transform.scale(dialog_box, (795, 195))
    dialog_font = pg.freetype.Font('eight-bit-dragon.otf', size = 24)
    dialog_noise = pg.mixer.Sound('chat_noise.wav')
    dialog_package = [dialog_box, dialog_font, dialog_noise]
    fi.cd('UI\Fonts')
    fps_font = pg.freetype.Font('digital-7.ttf', size = 48)


    # Declare character sprites.
    Fursa = Fursa_sprite()
    character_sprites = pg.sprite.GroupSingle()
    character_sprites.add(Fursa)

    # Declare npc sprites.
    npc_sprites = pg.sprite.Group()

    # Declare enemy sprites.
    enemy_images = enemy_frames()
    enemy_sprites = pg.sprite.Group()

    # Declare particle sprites.
    blast_particle_frames = blast_frames()
    particle_sprites = pg.sprite.Group()

    # Declare Initial Map.

    #Test
    current_map = Tutorial_Area = Map_02(npc_sprites, dialog_package, enemy_images, enemy_sprites)

    # #Normal
    # Starting_Area = Map_01(npc_sprites, dialog_package)
    # current_map = Starting_Area

    map_index = 0
    map_travel = False
    battle_travel =  False
    black = (255,255,255)
    old_rects = [pg.Rect((0,0),(0,0))]
    fps_rect = [pg.Rect((1860,10),(50,50))]
    ui_refresh = 0
    ui_frames = []

    # Game Loop
    while True:

        pg.event.pump()

        time = pg.time.get_ticks()
        dt = clock.tick(97) # Framerate.

        # Surfaces are blit and updated in order of back to front on screen.

        # Layer 1---------------------------------------------------------------------------------------- Screen background back surface refresh.

        if current_map.map_first_time:
            screen.blit(current_map.map.back_surface, (0,0))
        else:
            for rect in active_rects:
                screen.blit(current_map.map.back_surface, rect, rect)

        # Layer 2------------------------------------------------------------------------------------------- Particle sprites update.

        particle_sprites.update(Fursa, dt, particle_sprites, enemy_sprites)
        particle_sprites.draw(screen)
        particle_rects = [particle.refresh_rect for particle in particle_sprites.sprites()]

        # Layer 3----------------------------------------------------------------------------------------------------- Enemy sprites update

        enemy_sprites.update(current_map.map.blockers, time, Fursa, particle_sprites)
        enemy_sprites.draw(screen)
        enemy_rects = [enemy.refresh_rect for enemy in enemy_sprites.sprites()]

        # Layer 4--------------------------------------------------------------------------------------------------- Character sprites update.

        character_sprites.update(current_map.map.blockers, time, dt, current_map.cutscene, screen,
                                 current_map, map_travel, battle_travel, character_sprites, enemy_sprites, particle_sprites, blast_particle_frames.frames, fi)
        #pg.draw.rect(screen, black, Fursa.refresh_rect)
        character_sprites.draw(screen)
        character_rects = [Fursa.refresh_rect]

        # Layer 5--------------------------------------------------------------------------------------------------------- NPC sprites update.

        npc_sprites.update(current_map.map.blockers, time)
        npc_sprites.draw(screen)
        npc_rects = [npc.rect for npc in npc_sprites.sprites()]

        # Layer 6----------------------------------------------------------------------------------------------- Screen background front surface refresh.

        if current_map.map_first_time:
            screen.blit(current_map.map.front_surface, (0,0))
        else:
            for rect in active_rects:
                screen.blit(current_map.map.front_surface, rect, rect)

        # Layer 7----------------------------------------------------------------------------------------------- Cutscene animations and fps.

        current_map.update(Fursa, enemy_sprites, screen)
        fps_text, rect = fps_font.render(str(int(round(clock.get_fps()))))
        screen.blit(fps_text, (1860, 10))

        #TEST
        # if current_map.map_first_time:
        #     pass
        # else:
        #     for rect in active_rects:
        #         pg.draw.rect(screen, black, rect)

        rects = character_rects + particle_rects + npc_rects + enemy_rects + fps_rect + current_map.refresh_rects
        active_rects = rects + old_rects + current_map.ui

        if current_map.map_first_time:
            pg.display.flip()
        else:
            pg.display.update(active_rects)

        old_rects = rects
        current_map.map_first_time = False


        # Handle transitioning to and from different maps.
        """ Map Index -------------------- Map ----------------Combat_Area(Y/N)------------
           |   00                      Starting_Area                   N              |
           |   01                      Tutorial_Area                   Y              |
         ------------------------------------------------------------------------------ """

        if Fursa.map_forward is True:
            map_index += 1
            if map_index == 1:
                current_map = Tutorial_Area = Map_02(npc_sprites, dialog_package, enemy_images, enemy_sprites)
            Fursa.rect.x = current_map.spawnx
            Fursa.rect.y = current_map.spawny
            map_travel = True
        else:
            map_travel = False

        if Fursa.battle_forward is True:
            current_map.map_first_time = True
            battle_travel = True
        else:
            battle_travel =  False


if __name__ == '__main__':
    main()
