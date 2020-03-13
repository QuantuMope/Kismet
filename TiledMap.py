import pygame as pg
import pytmx
from pytmx.util_pygame import load_pygame

# TiledMap class to properly render Tiled maps by layer to surfaces.
class TiledMap:
    def __init__(self, filename):
        tm = load_pygame(filename)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tm = tm
        self.blockers = []
        self.battle_spawns = []

    # Renders two surfaces. back_surface is the surface that sprites appear in front of. top_surface vice versa.
    def render(self, back_surface, top_surface):
        first_time = True
        ti = self.tm.get_tile_image_by_gid
        self.last_layer = 0
        self.layer_counter = 0
        # Determine last tile layer.
        for layer in self.tm.visible_tile_layers:
            self.last_layer += 1
        for layer in self.tm.visible_layers:
            self.layer_counter += 1

            # Create a surface of tiles for back and front surfaces.
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = ti(gid)
                    if tile:
                        if self.layer_counter != self.last_layer:
                            back_surface.blit(tile, (x * self.tm.tilewidth, y * self.tm.tileheight))
                        else:
                            top_surface.blit(tile, (x * self.tm.tilewidth, y * self.tm.tileheight))

            # Create a list of platforms and walls by rect.
            elif isinstance(layer, pytmx.TiledObjectGroup) and first_time:
                for object in layer:
                    new_rect = pg.Rect(object.x, object.y, object.width, object.height)
                    self.blockers.append(new_rect)
                first_time = False

            # Create a list of spawn locations by rect for battle maps.
            elif isinstance(layer, pytmx.TiledObjectGroup):
                for object in layer:
                    new_rect = pg.Rect(object.x, object.y, object.width, object.height)
                    self.battle_spawns.append(new_rect)

    def make_map(self):
        self.back_surface = pg.Surface((self.width, self.height)).convert()
        self.front_surface = pg.Surface((self.width, self.height), pg.SRCALPHA, 32).convert_alpha()
        self.render(self.back_surface, self.front_surface)
        return self.back_surface, self.front_surface
