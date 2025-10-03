import pygame
import config

class Board:
    def __init__(self, surface):
        self.surface = surface
        self.points = []

        # calculer positions des points
        for row in range(config.BOARD_ROWS):
            for col in range(config.BOARD_ROWS):
                x = config.MARGIN + col * config.CELL_SIZE
                y = config.MARGIN + row * config.CELL_SIZE
                self.points.append((x, y))

    def draw(self):
        # fond
        self.surface.fill(config.BANNER_BG)

        # dessiner les lignes
        for row in range(config.BOARD_ROWS):
            for col in range(config.BOARD_ROWS):
                x = config.MARGIN + col * config.CELL_SIZE
                y = config.MARGIN + row * config.CELL_SIZE

                # horizontal
                if col < config.BOARD_ROWS - 1:
                    pygame.draw.line(
                        self.surface, config.BLACK,
                        (x, y), (x + config.CELL_SIZE, y),
                        config.GRID_LINE_WIDTH
                    )

                # vertical
                if row < config.BOARD_ROWS - 1:
                    pygame.draw.line(
                        self.surface, config.BLACK,
                        (x, y), (x, y + config.CELL_SIZE),
                        config.GRID_LINE_WIDTH
                    )

                # diagonales (optionnel)
                if col < config.BOARD_ROWS - 1 and row < config.BOARD_ROWS - 1:
                    pygame.draw.line(
                        self.surface, config.DARK_GREY,
                        (x, y), (x + config.CELL_SIZE, y + config.CELL_SIZE),
                        1
                    )
                    pygame.draw.line(
                        self.surface, config.DARK_GREY,
                        (x + config.CELL_SIZE, y), (x, y + config.CELL_SIZE),
                        1
                    )

        # dessiner les points
        for (x, y) in self.points:
            # Cercle extérieur discret (semi-transparent si on gère alpha)
            pygame.draw.circle(self.surface, config.BLACK, (x, y), config.POINT_RADIUS+2, 1)
            # Cercle intérieur
            pygame.draw.circle(self.surface, config.BLACK, (x, y), config.POINT_RADIUS)
