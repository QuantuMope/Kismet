import pygame as pg
from directory_change import files


class Masir_sprite(pg.sprite.Sprite):
    def __init__(self, spawnx, spawny):
        super().__init__()
        file = files()
        # Initialize frame parameters. Frames are uploaded once using upload_frames.
        self.upload_frames(file)
        self.current_frames = self.all_frames[0]
        self.image = self.current_frames[0]
        self.facing_right = True
        self.frame_override = True
        self.frame_speed = 300
        self.frame_index = 0

        # Sprite rect init.
        self.rect = pg.Rect((spawnx, spawny), (256, 198))

        # States
        self.state = 0
        self.fall_rate = 1
        self.attack = False
        self.walking = False
        self.on_ground = False

        # Time recorders.
        self.gravity_dt = 0
        self.frame_dt = 0

    def upload_frames(self, file):

        """ Function that uploads and stores all frames for Masir during init.
            Created separately for organizational purposes. """

        idle_images = []
        walk_images = []
        action_images = []

        # State IDs. Used as an identifier when changing self.state.
        # -----------------------0-------------1------------2----------
        self.all_frames = [idle_images, walk_images, action_images]

        directories =           ["NPCs\Masir\Idle_Png"       # Idle animation.
                                ,"NPCs\Masir\Walk_Png"       # Walk animation.
                                ,"NPCs\Masir\Action_Png"]    # Action animation.


        # Create a list containing lists with all animation frames. Each list is referenceable by the state ID shown above.
        for i, directory in enumerate(directories):
            file.cd(directory)
            for img_file in file.file_list():
                self.all_frames[i].append(pg.transform.scale(pg.image.load(img_file).convert_alpha(), (256, 256)))

        # Create a list of number of frames for each animation. Used to know when frame_index should be reset.
        self.frame_maxes = [len(images) for images in self.all_frames]

    def change_state(self):

        """ Function that changes Masir's animation depending on cutscene output.
            Is continuously called during non-cutscenes and non-battles.
            Animations are ordered in priority.
            Each animation type has its own fps. """

        # ATTACK animation.
        if self.attack:
            self.state = 2
            self.frame_speed = 125

        # WALK animation.
        elif self.walking:
            self.state = 1
            self.frame_speed = 200

        # IDLE animation.
        else:
            self.state = 0
            self.frame_speed = 300

    def update(self, time, dt, map):

        """ Main update function. Continuously called at all times in game loop main()
            Updates Masir's frame and hitbox. Monitors platform interaction. """

        self.change_state()

        if (time - self.frame_dt) >= self.frame_speed or self.facing_right != self.frame_override:
            self.frame_dt = time

            self.current_frames = self.all_frames[self.state]

            if self.facing_right:
                self.image = self.current_frames[self.frame_index]
                self.frame_index += 1
                self.frame_override = True
            else:
                self.image = pg.transform.flip(self.current_frames[self.frame_index], True, False)
                self.frame_index += 1
                self.frame_override = False

            if self.frame_index == self.frame_maxes[self.state]:
                self.attack = False
                self.frame_index = 0

        # Gravity emulation with current map blockers.
        for block in map.blockers:
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
                    for block in map.blockers:
                        if self.rect.colliderect(block):
                            self.fall_rate = 1
                            self.on_ground = True
                            break
                    if self.on_ground is True:
                        break
