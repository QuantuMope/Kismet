import pygame as pg
for event in pg.event.get():
    if event.type == pg.KEYDOWN:
        if self.current_turn <= 2:

            if self.current_slot == 1:
                if event.key == pg.K_s:
                    self.new_slot = 4
                elif event.key == pg.K_d:
                    self.new_slot = 2
                elif event.key == pg.K_r:
                    self.battle_command = 1

            elif self.current_slot == 4:
                if event.key == pg.K_r:
                    self.action_select = True
                    self.new_slot = 1
                elif event.key == pg.K_w:
                    self.new_slot = 1
                elif event.key == pg.K_d:
                    self.current_slot = 3

            elif self.current_slot == 2:
                if event.key == pg.K_a:
                    self.new_slot = 1
                elif event.key == pg.K_s:
                    self.new_slot = 3
                    
            elif self.current_slot == 3:
                if event.key == pg.K_a:
                    self.new_slot = 4
                elif event.key == pg.K_w:
                    self.new_slot = 2

            if self.new_slot != self.current_slot:
                self.combat_selector[self.current_slot] = black
                self.combat_selector[self.new_slot] = white
                self.current_slot = self.new_slot
                self.dialog_noise.play()
