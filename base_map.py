import pygame as pg
from combat_system import CombatSystem
from dialog_system import DialogSystem


# Contains all parameters and methods that all map classes contain.
# Serves as parent class to map classes.
class BaseMap(CombatSystem, DialogSystem):
    def __init__(self, package):
        CombatSystem.__init__(self, package)
        DialogSystem.__init__(self, package)

        # States.
        self.cutscene = False
        self.first_cutscene = True
        self.battle = False
        self.event = 0
        self.map_first_time = True

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

        # Refresh rects and sounds to end when map is terminated.
        self.refresh_rects = []
        self.ui = []
        self.end_sounds = [self.portal_aura]

