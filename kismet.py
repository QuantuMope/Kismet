import pygame as pg
import pygame.freetype
import os
from spritesheet import SpriteSheet

# Import Game Modules
from fursa import Fursa
from enemy_frames import EnemySpriteFrames
from map01 import Map01
from map02 import Map02


# Files class is in Kismet.py because a single file object is declared
# locally that assigns the main base directory. The file object is then
# passed down to other classes.
class FileNavigator:
    def __init__(self):
        base_path = os.path.dirname(os.path.realpath(__file__))
        self.main_directory = base_path
        self.current_directory = base_path

    def cd(self, path):
        characters = list(path)
        for i, letter in enumerate(characters):
            if letter == ' ':
                characters[i] = '/'
        new_path = '/' + ''.join(characters)

        final_path = self.main_directory + new_path
        # os.chdir(final_path)
        self.current_directory = final_path

    def file_list(self):
        files = os.listdir(self.current_directory)
        files.sort()
        return files

    def path(self, file_name):
        return self.current_directory + '/' + file_name


def main():
    fi = FileNavigator()
    # Initiate pygame parameters.
    pg.mixer.pre_init(44100, -16, 2, 1024)
    pg.init()
    pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.MOUSEBUTTONDOWN])
    resolution = width, height = 1920, 1080
    flags = pg.HWSURFACE | pg.DOUBLEBUF # | pg.FULLSCREEN
    screen = pg.display.set_mode(resolution, flags)
    screen.set_alpha(None)
    pg.display.set_caption('Kismet')
    clock = pg.time.Clock()

    """ Loads many graphical parameters here so that all data can be initialized once,
        cached, and reused by all classes. """

    # Dialog Initialization.
    fi.cd('UI Dialog')
    dialog_box = pg.image.load(fi.path('dialogue_box.png')).convert_alpha()
    dialog_box = pg.transform.scale(dialog_box, (795, 195))
    dialog_font = pg.freetype.Font(fi.path('eight-bit-dragon.otf'), size=24)
    dialog_noise = pg.mixer.Sound(fi.path('chat_noise.wav'))

    # User interface boxes. There is a combat, status, and description box.
    fi.cd('UI Combat')
    base_box = pg.image.load(fi.path('Combat UI Box transparent.png')).convert_alpha()
    status_box = pg.transform.scale(base_box, (670, 300))
    combat_box = pg.transform.scale(base_box, (690, 300))
    description_box = pg.transform.scale(base_box, (460, 300))
    # Pointer indicating whose turn it is during a battle.
    pointer = pg.image.load(fi.path('black_triangle.png')).convert_alpha()
    pointer = pg.transform.scale(pointer, (60, 42))
    battle_sword_aftersound = pg.mixer.Sound(fi.path('battle_sword_aftersound.wav'))
    battle_impact_noise = pg.mixer.Sound(fi.path('battle_start.wav'))
    fi.cd('UI Fonts')
    combat_font = pg.freetype.Font(fi.path('ferrum.otf'), size=24)
    hpmp_font = pg.freetype.Font(fi.path('DisposableDroidBB_ital.ttf'), size=24)
    fps_font = pg.freetype.Font(fi.path('digital-7.ttf'), size=48)

    # Portal animation.
    fi.cd('Maps')
    coordinates = []
    for i in range(0, 7):
        coordinates.extend([(100 * e, 100 * i, 100, 100) for e in range(0, 8)])
    coordinates.extend([(100 * e, 700, 100, 100) for e in range(0, 5)])
    portal_images_ss = SpriteSheet(fi.path('12_nebula_spritesheet.png'))
    portal_images_separate = portal_images_ss.images_at(coordinates, colorkey=(0, 0, 0))
    portal_images = [pg.transform.scale(portal_images_separate[i], (160, 160))
                     for i in range(0, len(portal_images_separate))]
    portal_blast = pg.mixer.Sound(fi.path('portal_noise.wav'))
    portal_aura = pg.mixer.Sound(fi.path('portal_aura_noise.wav'))

    package = {"dialogBox": dialog_box,
               "dialogFont": dialog_font,
               "dialogNoise": dialog_noise,
               "statusBox": status_box,
               "combatBox": combat_box,
               "descriptionBox": description_box,
               "pointer": pointer,
               "combatFont": combat_font,
               "hpmpFont": hpmp_font,
               "battleNoises": [battle_sword_aftersound, battle_impact_noise],
               "portal": [portal_images, portal_blast, portal_aura]}

    """ Sprite group initialization done below. """

    fursa = Fursa(fi)
    character_sprites = pg.sprite.GroupSingle()
    character_sprites.add(fursa)
    npc_sprites = pg.sprite.Group()
    enemy_images = EnemySpriteFrames(fi)
    enemy_sprites = pg.sprite.Group()
    particle_sprites = pg.sprite.Group()

    # Sprite dictionary for easy reference.
    sprites = {"character": character_sprites,
               "npc": npc_sprites,
               "enemy": enemy_sprites,
               "particles": particle_sprites}

    # Declare Initial Map.
    # Test
    # current_map = Tutorial_Area = Map02(package, sprites, enemy_images, fi)

    #Normal
    Starting_Area = Map01(package, sprites, fi)
    current_map = Starting_Area

    # Declare internal variables.
    map_index = 0
    black = (0, 0, 0)
    old_rects = [pg.Rect((0, 0), (0, 0))]
    fps_rect = [pg.Rect((1860, 10), (50, 50))]
    running = True

    # Game Loop
    while running:

        pg.event.pump()

        # Get time between frames. Set fpx max to 97.
        time = pg.time.get_ticks()
        dt = clock.tick(97)
        dt = round(dt / 11)

        # Surfaces are blit and updated in order of back to front on screen.

        # Layer 1: Screen background back surface refresh.

        if current_map.map_first_time:
            screen.blit(current_map.map.back_surface, (0, 0))
        else:
            for rect in active_rects:
                screen.blit(current_map.map.back_surface, rect, rect)

        # Layer 2: Enemy sprites update.

        enemy_sprites.update(time, dt, current_map, fursa, particle_sprites)
        # for enemy in enemy_sprites:
        #     pg.draw.rect(screen, black, enemy.hitbox_rect)
        enemy_sprites.draw(screen)
        enemy_rects = [enemy.refresh_rect for enemy in enemy_sprites.sprites()]

        # Layer 3: Character sprites update.

        character_sprites.update(time, dt, current_map, screen, sprites, fi)
        # pg.draw.rect(screen, black, fursa.refresh_rect)
        character_sprites.draw(screen)
        character_rects = [fursa.refresh_rect]

        # Layer 4: NPC sprites update.

        npc_sprites.update(time, dt, current_map)
        npc_sprites.draw(screen)
        npc_rects = [npc.rect for npc in npc_sprites.sprites()]

        # Layer 5: Particle sprites update.

        particle_sprites.update(dt, enemy_sprites)
        # for particle in particle_sprites:
        #     pg.draw.rect(screen, black, particle.hitbox_rect)
        particle_sprites.draw(screen)
        particle_rects = [particle.refresh_rect for particle in particle_sprites.sprites()]

        # Layer 6: Screen background front surface refresh.

        if current_map.map_first_time:
            screen.blit(current_map.map.front_surface, (0, 0))
        else:
            for rect in active_rects:
                screen.blit(current_map.map.front_surface, rect, rect)

        # Layer 7: Cutscene animations and fps.

        current_map.update(fursa, sprites, screen)
        fps_text, rect = fps_font.render(str(int(round(clock.get_fps()))))
        screen.blit(fps_text, (1860, 10))

        #TEST
        # if current_map.map_first_time:
        #     pass
        # else:
        #     for rect in current_map.refresh_rects:
        #         pg.draw.rect(screen, black, rect)

        rects = character_rects + particle_rects + npc_rects + enemy_rects + fps_rect + current_map.refresh_rects
        active_rects = rects + old_rects + current_map.ui

        if current_map.map_first_time:
            pg.display.flip()
        else:
            pg.display.update(active_rects)

        old_rects = rects
        current_map.map_first_time = False

        """ Handle transitioning to and from different maps.
        
            Map Index -------------------- Map ----------------Combat_Area(Y/N)------------
           |   00                      Starting_Area                   N              |
           |   01                      Tutorial_Area                   Y              |
         ------------------------------------------------------------------------------ """

        if fursa.map_forward is True:
            # Cancel any and all sounds in previous map upon exit. (such as portal noise)
            for sound in current_map.end_sounds:
                sound.stop()
            map_index += 1
            if map_index == 1:
                # Initializes new map and spawns Fursa appropriately.
                current_map = Tutorial_Area = Map02(package, sprites, enemy_images, fi)
                fursa.rect.x = current_map.spawnx
                fursa.rect.y = current_map.spawny
            fursa.map_forward = False

        if fursa.battle_forward is True:
            current_map.map_first_time = True
            fursa.battle_forward = False


if __name__ == '__main__':
    main()
