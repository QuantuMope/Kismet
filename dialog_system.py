import pygame as pg
import pathlib


# Takes care of the dialog system in map classes.
# Serves as one of the sibling parent class for base_map.
class DialogSystem:
    def __init__(self, package):

        # Dialog parameters.
        self.black_edge1 = pg.Rect((0, 0), (1920, 200))
        self.black_edge2 = pg.Rect((0, 880), (1920, 200))
        self.dialog_start = True
        self.dialog_box = package['dialogBox']
        self.dialog_font = package['dialogFont']
        self.dialog_noise = package['dialogNoise']
        self.dialog_1_final = ''
        self.dialog_2_final = ''
        self.dialog_name_final = ''
        self.dialog_length = ''
        self.e = 0
        self.a = 0
        self.i = 0

    @staticmethod
    def black_edges(screen):
        # Blackout the bottom and top of the screen during dialogue.
        black = (0, 0, 0)
        pg.draw.rect(screen, black, (0, 0, 1920, 200))
        pg.draw.rect(screen, black, (0, 880, 1920, 200))

    def dialog(self, text, name, screen):
        # Function to render and blit dialogue.
        self.black_edges(screen)
        screen.blit(self.dialog_box, (550, 880))
        if self.dialog_start:
            self.dialog_noise.play()
            self.e = 0
            self.a = 0
            self.dialog_length = len(text)
            # If text is long, wrap the text. Otherwise, simply print.
            if len(text) > 50:
                self.i = 50
                # Properly wrap text in the dialogue box by detecting spaces.
                # Text will only ever be two lines.
                # Algorithm is coded so that dialogue is "typed".
                while text[self.i] != ' ':
                    self.i += 1
                if self.i > 52:
                    self.i = 50
                    while text[self.i] != ' ':
                        self.i -= 1

        # Render text one by one until length is reached for single or double line dialog.
        if self.e != (len(text) + 1):
            if self.a == 0 or self.a != self.dialog_length:
                if len(text) > 50:
                    new_text = [text[0:self.i], text[self.i+1:]]
                    load_text_1 = new_text[0][0:self.e]
                    load_text_2 = new_text[1][0:self.a]
                    dialog_text_1, rect_1 = self.dialog_font.render(load_text_1)
                    dialog_text_2, rect_2 = self.dialog_font.render(load_text_2)
                    screen.blit(dialog_text_1, (600, 955))
                    screen.blit(dialog_text_2, (600, 1005))
                    self.e += 1
                    if self.e >= self.i:
                        self.a += 1

                    # Print the speaker's name.
                    name_text, rect_3 = self.dialog_font.render(name)
                    screen.blit(name_text, (600, 905))

                    # Store completed rendered text.
                    self.dialog_1_final = dialog_text_1
                    self.dialog_2_final = dialog_text_2
                    self.dialog_name_final = name_text

                else:
                    load_text_1 = text[0:self.e]
                    dialog_text_1, rect_1 = self.dialog_font.render(load_text_1)
                    screen.blit(dialog_text_1, (600, 955))
                    self.e += 1

                    dialog_text_2, rect_2 = self.dialog_font.render('')

                    # Print the speaker's name.
                    name_text, rect_3 = self.dialog_font.render(name)
                    screen.blit(name_text, (600, 905))

                    # Store completed rendered text.
                    self.dialog_1_final = dialog_text_1
                    self.dialog_2_final = dialog_text_2
                    self.dialog_name_final = name_text

        # If line by line render is done, simply blit the final text so avoid needless rendering.
        else:
            screen.blit(self.dialog_1_final, (600, 955))
            screen.blit(self.dialog_2_final, (600, 1005))
            screen.blit(self.dialog_name_final, (600, 905))
