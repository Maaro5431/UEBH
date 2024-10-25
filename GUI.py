import pygame
import sys
import datetime
import fileinput

import pygame


def update_window():
    pygame.display.flip()


def close_win():
    pygame.display.flip()
    pygame.quit()


def get_input():
    user_text = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:

                # Check for backspace
                if event.key == pygame.K_0:
                    return 0

                elif event.key == pygame.K_1:
                    return 1

                elif event.key == pygame.K_2:
                    return 2


class Storyline:
    def __init__(self):
        self.f = open("Storyline.txt", "a")
        self.current_time = datetime.datetime.now()
        self.f.write("\n*************" + str(self.current_time) + "*************")

    def write_line(self, lines):
        self.f.write('\n' + str(lines))

    def close(self):
        self.f.close()


class Win():

    def __init__(self, switch):
        self.switch = switch
        if switch:
            pygame.init()
            pygame.font.init()
            self.font = pygame.font.SysFont("Arial", 15)
            self.window_width = 1542  # / 1.5
            self.window_height = 899  # / 1.5
            self.window = pygame.display.set_mode((self.window_width, self.window_height))
            bg_image = pygame.image.load("C:/Users/Maaro/Desktop/Hons Project/UEBH/Board.png")

            self.window.blit(bg_image, (0, 0))

    def reset(self):
        if self.switch:
            self.window = pygame.display.set_mode((self.window_width, self.window_height))
            bg_image = pygame.image.load("C:/Users/Maaro/Desktop/Hons Project/UEBH/Board.png")
            self.window.blit(bg_image, (0, 0))

    def mark(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                print(f'Mouse clicked at {x}, {y}')
                self.check_box((x, y), "/////////////////////////////////", "red")
                pygame.display.update()

    def check_box(self, coordinates, value, colour):
        if self.switch:
            txt = self.font.render(value, True, colour)
            self.window.blit(txt, (coordinates[0], coordinates[1]))
            pygame.display.flip()

    def input_number_box(self):
        initial_text = ''
        rect = pygame.Rect(45, 860, 140, 32)
        color = pygame.Color('grey')

        text = initial_text
        active = False

        # Create a clock object to control the frame rate
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if len(text) > 0:
                            return text  # Return the input when Enter is pressed
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]  # Remove the last character
                    elif event.unicode.isdigit() or event.unicode == '.':
                        text += event.unicode  # Allow digits and decimal points only

            # Render the current text
            txt_surface = self.font.render(text, True, pygame.Color('black'))

            # Adjust the text box width to fit the text
            width = max(200, txt_surface.get_width() + 10)
            rect.w = width

            # Draw the text box and text
            pygame.draw.rect(self.window, color, rect)
            self.window.blit(txt_surface, (rect.x + 5, rect.y + 5))

            # Update the display
            pygame.display.flip()

            # Control the frame rate
            clock.tick(30)
