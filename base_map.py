import pygame as pg


# Contains all parameters that all map classes contain. Serves as a parent class.
class base_map():
    def __init__(self, package):

        # States.
        self.cutscene = False
        self.first_cutscene = True
        self.battle = False
        self.event = 0
        self.map_first_time = True

        # Refresh rects and sounds to end when map is terminated.
        self.refresh_rects = []
        self.ui = []
        self.end_sounds = []

        # Portal parameters.
        self.p_index = 0
        self.portal_start = False
        self.portal_blast_start = True
        self.portal_aura_start = True
        self.portal_rect = pg.Rect(1115, 660, 160, 160)
        self.portal_images = package['portal'][0]
        self.portal_blast = package['portal'][1]
        self.portal_blast.set_volume(0.50)
        self.portal_aura = package['portal'][2]
        self.portal_aura.set_volume(0.40)

