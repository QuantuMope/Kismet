import pygame as pg


# Contains all parameters that all map classes contain. Serves as a parent class.
class base_map():
    def __init__(self):

        # States.
        self.cutscene = False
        self.first_cutscene = True
        self.battle = False
        self.event = 0
        self.map_first_time = True
        self.battle_init = True

        # Refresh rects and sounds to end when map is terminated.
        self.refresh_rects = []
        self.ui = []
        self.end_sounds = []