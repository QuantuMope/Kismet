import pygame as pg
from spritesheet import SpriteSheet


class EnemySpriteFrames:
    def __init__(self, fi):
        self.fi = fi
        self.skeleton_frames = []
        self.skeleton_frames_func()

    def skeleton_frames_func(self):
        self.fi.cd('Enemies Skeleton Sprite_Sheets')

        # Spritesheet coordinates.                                                               Indexes
        coordinates = [[(24 * i, 0, 24, 32) for i in range(0, 11)],      # Idle. -----------------0
                       [(22 * i, 0, 22, 33) for i in range(0, 13)],      # Walking----------------1
                       [(22 * i, 0, 22, 32) for i in range(0, 4 )],      # React------------------2
                       [(43 * i, 0, 43, 37) for i in range(0, 18)],      # Attacking--------------3
                       [(30 * i, 0, 30, 32) for i in range(0, 8 )],      # Hit--------------------4
                       [(33 * i, 0, 33, 32) for i in range(0, 15)]]      # Death------------------5

        sizes = [(72,96), (66,99), (66,96), (129,111), (90,96), (99,96)]

        self.skeleton_frame_maxes = [len(frame_amount) for frame_amount in coordinates]

        spritesheets = [SpriteSheet(self.fi.path(ss)) for ss in self.fi.file_list()]
        ss_sep = [ss.images_at(coordinates[i], colorkey=(0, 0, 0)) for i, ss in enumerate(spritesheets)]

        for i, ss_sep in enumerate(ss_sep):
            scaled_frames = [pg.transform.scale(ss_sep[e], sizes[i]) for e in range(0, len(ss_sep))]
            self.skeleton_frames.append(scaled_frames)
