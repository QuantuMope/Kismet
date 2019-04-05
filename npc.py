import pygame as pg
from directory_change import files

class Masir_sprite(pg.sprite.Sprite):
    def __init__(self, spawnx, spawny):
        super().__init__()
        file = files()
        self.frame_index = 0
        self.upload_frames(file)
        self.current_images = self.all_images[0]
        self.image = self.current_images[0]
        self.state = 0
        self.facing_right = True
        self.frame_override = True
        self.frame_dt = 0
        self.frame_speed = 300
        self.gravity_dt = 0
        self.fall_rate = 1
        self.rect = pg.Rect((spawnx, spawny), (256, 198)) # Spawn point and collision size.
        self.attack = False
        self.walk = False
        self.on_ground = False


    def upload_frames(self, file):
        idle_images = []
        walk_images = []
        action_images = []

        # State IDs
        #-----------------------0-------------1------------2----------
        self.all_images = [idle_images, walk_images, action_images]

        directories =           ["NPCs\Masir\Idle_Png"       # Idle animation.
                                ,"NPCs\Masir\Walk_Png"       # Walk animation.
                                ,"NPCs\Masir\Action_Png"]    # Action animation.


        # Create a list containing lists with all animation frames. Each list is referenceable by the state ID shown above.
        for i, directory in enumerate(directories):
            file.cd(directory)
            for img_file in file.file_list():
                self.all_images[i].append(pg.transform.scale(pg.image.load(img_file).convert_alpha(), (256, 256)))

        # Create a list of number of frames for each animation.
        self.frame_maxes = [len(images) for images in self.all_images]

    def change_state(self):
        if self.attack:
            self.state = 2
            self.frame_speed = 125
        elif self.walk:
            self.state = 1
            self.frame_speed = 200
        else:
            self.state = 0
            self.frame_speed = 300

        self.current_images = self.all_images[self.state]

    def update(self, blockers, time):
        self.change_state()
        if (time - self.frame_dt) >= self.frame_speed or self.facing_right != self.frame_override:
            self.frame_dt = time

            if self.facing_right:
                self.image = self.current_images[self.frame_index]
                self.frame_index += 1
                self.frame_override = True
            else:
                self.image = pg.transform.flip(self.current_images[self.frame_index], True, False)
                self.frame_index += 1
                self.frame_override = False

            if self.frame_index == self.frame_maxes[self.state]:
                self.attack = False
                self.frame_index = 0

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
                for i in range(int(self.fall_rate)):
                    self.rect.y += 1
                    # Halts falling when Fursa lands on a block.
                    for block in blockers:
                        if self.rect.colliderect(block):
                            self.fall_rate = 1
                            self.on_ground = True
                            break
                    if self.on_ground is True:
                        break
