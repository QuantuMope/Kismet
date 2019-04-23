import pygame as pg
from directory_change import files
from spritesheet import spritesheet

class skeleton(pg.sprite.Sprite):
    def __init__(self, frames, spawnx, spawny):
        super().__init__()
        file = files()
        self.frames = frames.skeleton_frames
        self.frame_maxes = frames.skeleton_frame_maxes
        self.current_images = self.frames[0] # Idle
        self.image = self.current_images[0]
        self.prev_state = 0
        self.state = 0
        self.rect = pg.Rect(spawnx, spawny, 72, 96)
        self.hitbox_rect = pg.Rect((self.rect.x + 30, self.rect.y - 30), (72, 96))
        self.refresh_rect = pg.Rect((self.rect.x - 30, self.rect.y), (128, 128))

        # States
        self.frame_index = 0
        self.frame_dt = 0
        self.frame_speed = 100
        self.facing_right = True
        self.frame_override = True
        self.gravity_dt = 0
        self.fall_rate = 1
        self.jump = False
        self.aggroed = False
        self.reaction_done = False
        self.chase = False
        self.attack = False
        self.pre_engaged_dt = 0
        self.one_shot = True
        self.change_state = False
        self.pstate = 0
        self.cstate = 0
        self.hit = False
        self.hp = 3
        self.on_ground = False
        self.turn = False

        # Combat attributes.
        self.speed = 1
        self.party_spawn = 4
        self.turn = False
        self.first_attack = True
        self.hit_done = False
        self.first_hit = False

        self.turn_determiner = [self.party_spawn, self.speed]

        file.cd("Enemies\Skeleton")
        self.swing_sound = pg.mixer.Sound('swing.wav')

    # Skeleton AI.
    def AI(self, blockers, time, character, particle_sprites):

        self.prev_state = self.state

        if self.hit is False:
            # When not aggroed, pace back and forth spawn location.
            if not self.aggroed:
                if (time - self.pre_engaged_dt) >= 2500:
                    self.pre_engaged_dt = time
                    self.state ^= 1
                    if self.state == 0: # Idle
                        pass
                    if self.state == 1:
                        self.facing_right = not self.facing_right
                    self.frame_index = 0
                if self.state == 1:
                    if self.facing_right:
                        self.rect.x += 1
                    else:
                        self.rect.x -= 1

            # If within aggro range, switch animation to react.
            if abs(self.rect.centerx - character.rect.centerx) < 200 and not self.aggroed:
                self.change_state_battle(2)
                self.aggroed = True
                self.frame_index = 0

            # Allow for reaction frames to finish.
            if self.state == 2 and self.frame_index == 4:
                self.chase = True
                self.frame_index = 0

            # When aggroed and reaction is done, move towards the player.
            if self.attack == False:
                if self.aggroed and self.chase:
                    self.change_state_battle(1)
                    if (self.rect.centerx - character.rect.centerx) > 0:
                        self.facing_right = False
                        self.rect.x -= 1
                    else:
                        self.facing_right = True
                        self.rect.x += 1

            # Start attack animation.
            if abs(self.rect.centerx - character.rect.centerx) < 100 and self.chase:
                self.attack = True
                self.change_state_battle(3)

            for particle in particle_sprites:
                if particle.particle_hit is True:
                    self.change_state_battle(4)
                    self.chase = True
                    self.aggroed = True
                    self.hit = True
                    self.hp -= 1

        if self.hp <= 0:
            self.state = 5

        if self.prev_state != self.state:
            self.change_state = True
            self.pstate = self.prev_state
            self.cstate = self.state

    def change_state_battle(self, state_id):
        if state_id == 0:
            self.state = 0
            self.frame_speed = 100
        elif state_id == 1:
            self.state = 1
            self.frame_speed = 100
        elif state_id == 2:
            self.state = 2
            self.frame_speed = 400
        elif state_id == 3:
            self.state = 3
            self.frame_speed = 100
        elif state_id == 4:
            self.state = 4
            self.frame_speed = 125
        elif state_id == 5:
            self.state = 5
            self.frame_speed = 150

    def change_rect_by_state(self, old_state, new_state, self_facing):
        self.frame_index = 0
        sizes = [(72,96), (66,99), (66,96), (129,111), (85,96), (99,96)]
        old_size_x = sizes[old_state][0]
        new_size_x = sizes[new_state][0]
        old_size_y = sizes[old_state][1]
        new_size_y = sizes[new_state][1]
        x_dt = new_size_x - old_size_x
        y_dt = new_size_y - old_size_y
        self.rect.width = old_size_x + x_dt
        self.rect.height = old_size_y + y_dt
        self.rect.y -= y_dt
        if self.facing_right is not True and new_state != 4: self.rect.x -= x_dt + 10


    def battle(self, map, character, particle_sprites):
        self.prev_state = self.state

        for particle in particle_sprites:
            if particle.hitbox_rect.collidepoint((self.hitbox_rect.x + self.hitbox_rect.width/2),(self.hitbox_rect.y + self.hitbox_rect.height/2)):
                self.change_state_battle(4)
                self.frame_index = 0

        if character.attack is True and self.first_hit is False:
            if character.rect.colliderect(self.hitbox_rect) and character.frame_index == 8:
                self.change_state_battle(4)
                self.frame_index = 0
                self.first_hit = True

        if map.current_turn != self.party_spawn and self.hit_done is True:
            self.change_state_battle(0)

        if map.current_turn == self.party_spawn and self.first_attack:
            map.battle_command = 1
            self.first_attack = False

        if map.current_turn == self.party_spawn and self.hit_done is True:
            map.animation_complete = False
            if map.battle_command == 1:
                if self.rect.left >= map.battle_spawn_pos[2].right + 40:
                    self.change_state_battle(1)
                    self.rect.x -= 2
                else:
                    self.change_state_battle(3)
                    self.attack = True

            elif map.battle_command == 0:
                if self.rect.centerx <= map.battle_spawn_pos[self.party_spawn].centerx:
                    self.facing_right = True
                    self.change_state_battle(1)
                    self.rect.x += 2
                else:
                    self.facing_right = False
                    self.change_state_battle(0)
                    map.animation_complete = True
                    self.first_attack = True
                    self.hit_done = False
                    self.first_hit = False

        if self.prev_state != self.state:
            self.change_state = True
            self.pstate = self.prev_state
            self.cstate = self.state


    def update(self, blockers, time, map, character, particle_sprites):

        self.refresh_rect = pg.Rect((self.rect.x - 128, self.rect.y - 64), (256, 256))

        if self.facing_right:
            if self.state == 3:
                self.hitbox_rect = pg.Rect((self.rect.x, self.rect.y + 40), (52, 72))
            else:
                self.hitbox_rect = pg.Rect((self.rect.x, self.rect.y + 25), (52, 72))
        else:
            if self.state == 3:
                self.hitbox_rect = pg.Rect((self.rect.x + 70, self.rect.y + 40), (52, 72))
            else:
                self.hitbox_rect = pg.Rect((self.rect.x + 20, self.rect.y + 25), (52, 72))

        if character.battle is False:
            self.AI(blockers, time, character, particle_sprites)
        else:
            self.battle(map, character, particle_sprites)

        # Frame update and flipping.

        if (time - self.frame_dt) >= self.frame_speed or self.facing_right != self.frame_override:
            self.frame_dt = time

            self.current_images = self.frames[self.state]

            if self.change_state is True:
                self.change_rect_by_state(self.pstate, self.cstate, self.facing_right)
                self.change_state = False

            if self.facing_right:
                self.image = self.current_images[self.frame_index]
                self.frame_index += 1
                self.frame_override = True
                if self.turn is True:
                    self.rect.x += 50
                    self.turn = False
            else:
                self.image = pg.transform.flip(self.current_images[self.frame_index], True, False)
                self.frame_index += 1
                self.frame_override = False
                if self.turn is False:
                    self.rect.x -= 20
                    self.turn = True

            if self.state == 3 and self.frame_index == 7:
                self.swing_sound.play()

            if self.frame_index == self.frame_maxes[self.state]:
                if self.state == 2:
                    pass
                elif self.state == 5:
                    self.kill()
                elif self.state == 4:
                    self.hit_done = True
                    self.frame_index = 0
                else:
                    if self.attack:
                        map.battle_command = 0
                    self.attack = False
                    self.frame_index = 0

        if map.battle is False:
            if self.attack:
                if character.hitbox_rect.colliderect(self.rect) and self.frame_index == 8:
                    self.state = 0
                    self.rect.width = 72
                    self.rect.height = 96


        # Gravity emulation with current map blockers.
        for block in blockers:
            # Checks to see if Fursa is in contact with the ground.
            if self.rect.colliderect(block):
                self.on_ground = True
                break
            else:
                self.on_ground = False

        if self.on_ground is False:
            # If not in contact with the ground, accelerates falling down every 20 ms.
            # Gravity is disabled when a jump animation is in progress.
            if (time - self.gravity_dt) >= 20:
                self.gravity_dt = time
                self.fall_rate *= 1.1 # Acceleration rate.
                start_fall = self.rect.y
                for i in range(int(self.fall_rate)):
                    self.rect.y += 1
                    self.hitbox_rect.y += 1
                    # end_fall = self.rect.y
                    # if (end_fall - start_fall) > 256:
                    #     pg.display.update(self.refresh_rect)
                    # Halts falling when Fursa lands on a block.
                    for block in blockers:
                        if self.rect.colliderect(block):
                            self.fall_rate = 1
                            self.on_ground = True
                            break
                    if self.on_ground is True:
                        break
class enemy_frames():
    def __init__(self):
        file = files()
        self.skeleton_frames = []
        self.skeleton_frames_func(file)

    def skeleton_frames_func(self, file):
        directory = file.cd('Enemies\Skeleton\Sprite Sheets')

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

        spritesheets = [spritesheet(sprite_sheet) for sprite_sheet in file.file_list()]
        spritesheets_separate = [spritesheet.images_at(coordinates[i], colorkey = (0, 0, 0)) for i, spritesheet in enumerate(spritesheets)]

        for i, ss_sep in enumerate(spritesheets_separate):
            scaled_frames = [pg.transform.scale(ss_sep[e], sizes[i]) for e in range(0, len(ss_sep))]
            self.skeleton_frames.append(scaled_frames)
