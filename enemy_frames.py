import pygame as pg
from spritesheet import spritesheet

class enemy_sprite_frames():
    def __init__(self, fi):
        self.fi = fi
        self.skeleton_frames = []
        self.skeleton_frames_func()

    def skeleton_frames_func(self):
        self.fi.cd('Enemies Skeleton Sprite_Sheets')

        # Spritesheet coordinates.                                                               Indexes
        coordinates = [
                         [(24 * i, 0, 24, 32) for i in range(0, 11)]       # Idle. -----------------0
                        ,[(22 * i, 0, 22, 33) for i in range(0, 13)]       # Walking----------------1
                        ,[(22 * i, 0, 22, 32) for i in range(0, 4 )]       # React------------------2
                        ,[(43 * i, 0, 43, 37) for i in range(0, 18)]       # Attacking--------------3
                        ,[(30 * i, 0, 30, 32) for i in range(0, 8 )]       # Hit--------------------4
                        ,[(33 * i, 0, 33, 32) for i in range(0, 15)]       # Death------------------5
                      ]

        sizes = [(72,96), (66,99), (66,96), (129,111), (90,96), (99,96)]

        self.skeleton_frame_maxes = [len(frame_amount) for frame_amount in coordinates]

        spritesheets = [spritesheet(self.fi.path(sprite_sheet)) for sprite_sheet in self.fi.file_list()]
        spritesheets_separate = [spritesheet.images_at(coordinates[i], colorkey=(0, 0, 0)) for i, spritesheet in enumerate(spritesheets)]

        for i, ss_sep in enumerate(spritesheets_separate):
            scaled_frames = [pg.transform.scale(ss_sep[e], sizes[i]) for e in range(0, len(ss_sep))]
            self.skeleton_frames.append(scaled_frames)
