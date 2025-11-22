import pygame
import config
from gui.pieces import Piece
from PrologRules.prolog_manager import PrologManager

class Board:
    def __init__(self, surface):
        self.surface = surface
        self.points = []
        self.player1_pieces = []
        self.player2_pieces = []
        self.occupied_positions = []
        self.phase = "placement"

        self.manager = PrologManager()
        # === coordonnées logiques : 0..4 ===
        for row in range(config.BOARD_ROWS):
            for col in range(config.BOARD_ROWS):
                self.points.append((row, col))

    #
    def to_prolog_state(self):
        state = ["e"]*25
        for p in self.player1_pieces:
            r,c = p.position
            state[r*5+c] = "n"
        for p in self.player2_pieces:
            r,c = p.position
            state[r*5+c] = "b"
        return state
    

    #
    def update_from_prolog_state(self, state):
        self.player1_pieces.clear()
        self.player2_pieces.clear()
        self.occupied_positions.clear()

        for idx,val in enumerate(state):
            r = idx//5
            c = idx%5
            if val=="n":
                self.player1_pieces.append(Piece((r,c),1))
                self.occupied_positions.append((r,c))
                
            elif val=="b":
                self.player2_pieces.append(Piece((r,c),2))
                self.occupied_positions.append((r,c))
            
    
    #
    def update_phase_from_prolog(self):
        phase = self.manager.get_phase(self.to_prolog_state())
        if phase:
            self.phase = phase

    # Convertit (x,y) logique → position pixel
    def logical_to_pixel(self, pos):
        col, row = pos
        x = config.MARGIN + row * config.CELL_SIZE
        y = config.MARGIN + col * config.CELL_SIZE
        return (x, y)

    # Placer un pion
    def place_piece(self, pos, current_player):
        if pos not in self.occupied_positions:
            piece = Piece(pos, current_player)  # pos logique
            if current_player == 1:
                self.player1_pieces.append(piece)
            else:
                self.player2_pieces.append(piece)

            self.occupied_positions.append(pos)

            if len(self.player1_pieces) + len(self.player2_pieces) == 8:
                self.phase = "deplacement"

    #
    def pixel_to_logical(self, pos):
        x, y = pos
        row = round((x - config.MARGIN) / config.CELL_SIZE)
        col = round((y - config.MARGIN) / config.CELL_SIZE)
        if 0 <= col < config.BOARD_ROWS and 0 <= row < config.BOARD_ROWS:
            return (col, row)
        return None

    def draw(self):
        self.surface.fill(config.BANNER_BG)

        # grille
        for row in range(config.BOARD_ROWS):
            for col in range(config.BOARD_ROWS):
                x = config.MARGIN + col * config.CELL_SIZE
                y = config.MARGIN + row * config.CELL_SIZE

                if col < config.BOARD_ROWS - 1:
                    pygame.draw.line(
                        self.surface, config.BLACK,
                        (x, y), (x + config.CELL_SIZE, y),
                        config.GRID_LINE_WIDTH
                    )

                if row < config.BOARD_ROWS - 1:
                    pygame.draw.line(
                        self.surface, config.BLACK,
                        (x, y), (x, y + config.CELL_SIZE),
                        config.GRID_LINE_WIDTH
                    )

        # POINTS (convertir logique → pixel)
        for (lx, ly) in self.points:
            px, py = self.logical_to_pixel((lx, ly))
            pygame.draw.circle(self.surface, config.BLACK, (px, py), config.POINT_RADIUS+2, 1)
            pygame.draw.circle(self.surface, config.BLACK, (px, py), config.POINT_RADIUS)

        # PIECES
        for piece in self.player1_pieces:
            px, py = self.logical_to_pixel(piece.position)
            pygame.draw.circle(self.surface, config.RED, (px, py), config.POINT_RADIUS+3, 1)
            pygame.draw.circle(self.surface, config.RED, (px, py), config.POINT_RADIUS)

        for piece in self.player2_pieces:
            px, py = self.logical_to_pixel(piece.position)
            pygame.draw.circle(self.surface, config.BLUE, (px, py), config.POINT_RADIUS+3, 1)
            pygame.draw.circle(self.surface, config.BLUE, (px, py), config.POINT_RADIUS)
