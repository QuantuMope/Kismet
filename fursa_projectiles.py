from spritesheet import SpriteSheet
import pygame as pg


class BlastFrames:

    """ Class simply containing projectile frames of various attacks.
        Created to avoid having to load from the hard drive every time a projectile is created.
        Is used in Fursa's init. """

    def __init__(self, fi):
        self.fi = fi
        # Fursa's attack blast properly separated into frames into a list from a spritesheet.
        self.fi.cd("Players Fursa")
        coordinates = [(128 * i, 0, 128, 128) for i in range(0, 8)]
        blast_image_ss = SpriteSheet(self.fi.path('EnergyBall.png'))
        blast_images_separate = blast_image_ss.images_at(coordinates, colorkey=(0, 0, 0))
        self.blast_frames_r = [pg.transform.scale(blast_images_separate[i], (64, 64)) for i in range(0, len(blast_images_separate))]
        self.blast_frames_l = [pg.transform.flip(self.blast_frames_r[i], True, False) for i in range(0, len(self.blast_frames_r))]

        # Impact frames.
        coordinates = [(0, 128 * i, 128, 128) for i in range(0, 8)]
        impact_images_ss = SpriteSheet(self.fi.path('energyBallImpact.png'))
        impact_images_separate = impact_images_ss.images_at(coordinates, colorkey=(0, 0, 0))
        self.impact_frames_r = [pg.transform.scale(impact_images_separate[i], (64, 64)) for i in range(0, len(impact_images_separate))]
        self.impact_frames_l = [pg.transform.flip(self.impact_frames_r[i], True, False) for i in range(0, len(self.impact_frames_r))]

        self.frames = [self.blast_frames_r, self.blast_frames_l, self.impact_frames_r, self.impact_frames_l]


# Fursa's SPIRIT BLAST projectile sprite.
class SpiritBlast(pg.sprite.Sprite):
    def __init__(self, fursa):
        super().__init__()
        # Store projectile frames.
        frames = fursa.projectile_frames
        self.blast_frames_r = frames[0]
        self.blast_frames_l = frames[1]
        self.impact_frames_r = frames[2]
        self.impact_frames_l = frames[3]

        # Match projectile's direction and spawn location depending on Fursa.
        self.flowing_right = True if fursa.facing_right else False
        if self.flowing_right:
            self.rect = pg.Rect(fursa.rect.x + 70, fursa.rect.y + 44, 64, 64)
            self.frames = self.blast_frames_r
            self.impact = self.impact_frames_r
        else:
            self.rect = pg.Rect(fursa.rect.x + 20, fursa.rect.y + 44, 64, 64)
            self.frames = self.blast_frames_l
            self.impact = self.impact_frames_l

        # Initialize frame parameters.
        self.image = self.frames[0]
        self.i = 0
        self.e = 0
        self.hit = False

    def update(self, dt, enemy_sprites):
        # Update hitbox and refresh rect.
        self.refresh_rect = pg.Rect((self.rect.x - 16, self.rect.y - 16), (96, 96))
        self.hitbox_rect = pg.Rect((self.rect.x + 10, self.rect.y + 20), (48, 20))

        # Once blast is spawned by Fursa, will keep traveling across map until it hits the
        # right of left edge of the map in which case the sprite will be killed.
        if not self.hit and self.flowing_right:
            self.rect.x += 3 * dt
        elif not self.hit:
            self.rect.x -= 3 * dt

        if self.rect.right > 1920 or self.rect.left < 0:
            self.spawn = False
            self.kill()
        elif self.hit:
            self.frames = self.impact
            self.image = self.frames[self.e] # Frame changing.
            self.e += 1
            if self.e == 8:
                self.kill()

        # Frame update and reset.
        self.image = self.frames[self.i]
        self.i += 1
        if self.i == 8:
            self.i = 0

        # Detect collision with enemy.
        for enemy in enemy_sprites:
            if self.hitbox_rect.collidepoint((enemy.hitbox_rect.x + enemy.hitbox_rect.width/2),
                                             (enemy.hitbox_rect.y + enemy.hitbox_rect.height/2)):
                self.hit = True
