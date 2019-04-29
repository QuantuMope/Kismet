import pygame as pg
from directory_change import files


class skeleton(pg.sprite.Sprite):
    def __init__(self, frames, spawnx, spawny):
        super().__init__()
        file = files()

        # Initialize frame parameters.
        self.frames = frames.skeleton_frames
        self.frame_maxes = frames.skeleton_frame_maxes
        self.current_frames = self.frames[0]
        self.image = self.current_frames[0]
        self.facing_right = True
        self.frame_override = True
        self.frame_speed = 100
        self.frame_index = 0

        # Sprite rect init.
        self.rect = pg.Rect(spawnx, spawny, 72, 96)

        # States.
        self.prev_state = 0
        self.state = 0
        self.fall_rate = 1
        self.aggroed = False
        self.reaction_done = False
        self.chase = False
        self.attack = False
        self.hit = False
        self.on_ground = False
        self.pstate = 0
        self.cstate = 0
        self.change_state_check = False

        # Time recorders.
        self.gravity_dt = 0
        self.frame_dt = 0
        self.pre_engaged_dt = 0

        # Combat attributes.
        self.current_hp = 10
        self.current_mp = 10
        self.max_hp = 10
        self.max_mp = 10
        self.party_spawn = 4
        self.speed = 1
        self.turn = False
        self.first_attack = True
        self.hit_done = False
        self.turn_determiner = [self.party_spawn, self.speed]

        # Load sound effects.
        file.cd("Enemies\Skeleton")
        self.swing_sound = pg.mixer.Sound('swing.wav')

    # Skeleton AI.
    def AI(self, time, dt, fursa, particle_sprites):

        """ Skeleton's AI behavior during non-battles.
            Reacts accordingly to Fursa.
            Is called continuously during non-battles. """

        self.prev_state = self.state

        if self.hit is False:
            # When not aggroed, pace back and forth around the spawn location.
            if not self.aggroed:
                if (time - self.pre_engaged_dt) >= 2500:
                    self.pre_engaged_dt = time
                    self.state ^= 1
                    if self.state == 0:
                        pass
                    if self.state == 1:
                        self.facing_right = not self.facing_right
                    self.frame_index = 0
                if self.state == 1:
                    if self.facing_right:
                        self.rect.x += 1 * dt
                    else:
                        self.rect.x -= 1 * dt

            # If within aggro range, switch animation to reaction.
            if abs(self.rect.centerx - fursa.rect.centerx) < 200 and not self.aggroed:
                self.change_state(2)
                self.aggroed = True
                self.frame_index = 0

            # Allow for reaction frames to finish.
            if self.state == 2 and self.frame_index == 4:
                self.chase = True
                self.frame_index = 0

            # When aggroed and reaction is done, move towards the player. (chase)
            if self.attack is False:
                if self.aggroed and self.chase:
                    self.change_state(1)
                    if (self.rect.centerx - fursa.rect.centerx) > 0:
                        self.facing_right = False
                        self.rect.x -= 1 * dt
                    else:
                        self.facing_right = True
                        self.rect.x += 1 * dt

            # Start attack animation when close enough to Fursa.
            if abs(self.rect.centerx - fursa.rect.centerx) < 100 and self.chase:
                self.attack = True
                self.change_state(3)

            for particle in particle_sprites:
                if particle.particle_hit is True:
                    self.change_state(4)
                    self.chase = True
                    self.aggroed = True
                    self.hit = True
                    self.current_hp -= 1

        if self.current_hp <= 0:
            self.state = 5

        # Monitor state changes to change rect appropriately.
        if self.prev_state != self.state:
            self.change_state_check = True
            self.pstate = self.prev_state
            self.cstate = self.state

    def change_state(self, state_id):
        # Simple function to change states.
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

        """ Function used to appropriately change the rect of the skeleton when a state change is detected.
            Necessary due to the varying rect sizes of the frames between different actions.
            Called in self.update() during state changes. """

        self.frame_index = 0
        sizes = [(72, 96), (66, 99), (66, 96), (129, 111), (85, 96), (99, 96)]
        old_size_x = sizes[old_state][0]
        new_size_x = sizes[new_state][0]
        old_size_y = sizes[old_state][1]
        new_size_y = sizes[new_state][1]
        x_dt = new_size_x - old_size_x
        y_dt = new_size_y - old_size_y
        self.rect.width = old_size_x + x_dt
        self.rect.height = old_size_y + y_dt
        self.rect.y -= y_dt
        if self.facing_right is not True and new_state != 4:
            self.rect.x -= x_dt + 10

    def battle(self, map, fursa, particle_sprites):

        """ Skeleton's AI behavior during battles.
            Is called continuously during battles. """

        self.prev_state = self.state

        # Reacts to particles collisions.
        for particle in particle_sprites:
            if particle.hitbox_rect.collidepoint((self.hitbox_rect.x + self.hitbox_rect.width/2),
                                                 (self.hitbox_rect.y + self.hitbox_rect.height/2)):
                self.change_state(4)
                self.frame_index = 0

        # Reacts to Fursa's melee attack.
        if fursa.attack is True:
            if fursa.rect.colliderect(self.hitbox_rect) and fursa.frame_index == 8:
                self.change_state(4)
                self.frame_index = 0

        # Idle when it is not skeleton's current turn and a hit reaction is not underway.
        if map.current_turn != self.party_spawn and self.hit_done is True:
            self.change_state(0)

        # When it is skeleton's turn, go up for a melee attack.
        # self.first_attack serves as a one shot.
        if map.current_turn == self.party_spawn and self.first_attack:
            map.battle_command = 1
            self.first_attack = False

        if map.current_turn == self.party_spawn and self.hit_done is True:
            map.animation_complete = False
            if map.battle_command == 1:
                # Run up to player position and perform attack animation.
                if self.rect.left >= map.battle_spawn_pos[2].right + 40:
                    self.change_state(1)
                    self.rect.x -= 2
                else:
                    self.change_state(3)
                    self.attack = True

            # Return to position.
            # map.battle_command is set to 0 when self.attack or self.attack becomes false.
            elif map.battle_command == 0:
                if self.rect.centerx <= map.battle_spawn_pos[self.party_spawn].centerx:
                    self.facing_right = True
                    self.change_state(1)
                    self.rect.x += 2
                else:
                    self.facing_right = False
                    self.change_state(0)
                    map.animation_complete = True
                    self.first_attack = True
                    self.hit_done = False

        # Monitor state changes to change rect appropriately.
        if self.prev_state != self.state:
            self.change_state_check = True
            self.pstate = self.prev_state
            self.cstate = self.state


    def update(self, time, dt, map, fursa, particle_sprites):

        """ Main update function. Continuously called at all times in game loop main()
            Updates skeleton's frame and hitbox. Monitors platform interaction.
            Monitors whether open world, cutscene, or battle controls should be enabled. """

        # Hitbox and refresh rect updates.
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

        self.refresh_rect = pg.Rect((self.rect.x - 128, self.rect.y - 64), (256, 256))

        # Enable different code segments depending on game state.
        if map.battle is False:
            self.AI(time, dt, fursa, particle_sprites)
        else:
            self.battle(map, fursa, particle_sprites)

        # Frame update and flipping.
        if (time - self.frame_dt) >= self.frame_speed or self.facing_right != self.frame_override:
            self.frame_dt = time

            self.current_frames = self.frames[self.state]

            # Changes rect when a state change is detected.
            if self.change_state_check is True:
                self.change_rect_by_state(self.pstate, self.cstate, self.facing_right)
                self.change_state_check = False

            # Resets frame index if the max for a certain animation is reached.
            # Sets attack and hit to false to indicate completion.
            if self.frame_index == self.frame_maxes[self.state]:
                if self.state == 2:
                    pass
                elif self.state == 5:
                    self.kill()
                # Allows reaction to finish before attack starts.
                elif self.state == 4:
                    self.hit_done = True
                    self.frame_index = 0
                else:
                    if self.attack:
                        # Initiates walkback during battles.
                        map.battle_command = 0
                    self.attack = False
                    self.frame_index = 0

            if self.facing_right:
                self.image = self.current_frames[self.frame_index]
                self.frame_index += 1
                self.frame_override = True
                # Displaces skeleton when turning due to position difference when frame is flipped.
                if self.turn is True:
                    self.rect.x += 50
                    self.turn = False
            else:
                self.image = pg.transform.flip(self.current_frames[self.frame_index], True, False)
                self.frame_index += 1
                self.frame_override = False
                if self.turn is False:
                    self.rect.x -= 20
                    self.turn = True

            # Play attack noise at correct frame.
            if self.state == 3 and self.frame_index == 7:
                self.swing_sound.play()

        # If skeleton connects an attack on Fursa in open world, revert back to idle in preparation for battle mode.
        if map.battle is False:
            if self.attack:
                if fursa.hitbox_rect.colliderect(self.rect) and self.frame_index == 8:
                    self.state = 0
                    self.rect.width = 72
                    self.rect.height = 96

        # Gravity emulation with current map blockers.
        for block in map.blockers:
            # Checks to see if skeleton is in contact with the ground.
            if self.rect.colliderect(block):
                self.on_ground = True
                break
            else:
                self.on_ground = False

        if self.on_ground is False:
            # If not in contact with the ground, accelerates falling down every 20 ms by 10%.
            if (time - self.gravity_dt) >= 20:
                self.gravity_dt = time
                self.fall_rate *= 1.1
                start_fall = self.rect.y
                for i in range(int(self.fall_rate)):
                    self.rect.y += 1
                    self.hitbox_rect.y += 1
                    end_fall = self.rect.y
                    if (end_fall - start_fall) > 256:
                        pg.display.update(self.refresh_rect)
                    # Halts falling when skeleton lands on a block.
                    for block in map.blockers:
                        if self.rect.colliderect(block):
                            self.fall_rate = 1
                            self.on_ground = True
                            break
                    if self.on_ground is True:
                        break
