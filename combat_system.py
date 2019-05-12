import pygame as pg


# Takes care of the combat system in map classes. Serves as a parent class.
class combat_system():
    def __init__(self, package):

        self.status_box = package['statusBox']
        self.combat_box = package['combatBox'][0]
        self.combat_box_rect = package['combatBox'][1]
        self.description_box = package['descriptionBox'][0]
        self.description_rect = package['descriptionBox'][1]
        self.combat_font = package['combatFont']
        self.hpmp_font = package['hpmpFont']
