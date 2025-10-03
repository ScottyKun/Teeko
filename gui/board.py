# gui/board.py
import pygame
from config import *
from typing import Optional, Tuple

class Board:
    """
    Classe qui dessine le plateau, calcule les positions de case et gère hover/selection.
    """

    def __init__(self, rows=BOARD_ROWS, cols=BOARD_COLS,
                 screen_size=(WINDOW_WIDTH, WINDOW_HEIGHT), margin=BOARD_MARGIN):
        self.rows = rows
        self.cols = cols
        self.screen_w, self.screen_h = screen_size
        self.margin = margin

        # calcul d'une zone carrée pour le plateau, centrée
        self.size = int(min(self.screen_w - 2 * self.margin,
                            self.screen_h - 2 * self.margin))
        self.cell_size = self.size / max(self.rows, self.cols)

        # coordonnées top-left du plateau (entier pour pygame.Rect)
        self.x = int((self.screen_w - self.size) // 2)
        self.y = int((self.screen_h - self.size) // 2)
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        # état visuel (pas encore l'état du jeu logique)
        self.hover: Optional[Tuple[int,int]] = None
        self.selected: Optional[Tuple[int,int]] = None

    def get_cell_at_pos(self, pos) -> Optional[Tuple[int,int]]:
        """Retourne (row, col) si pos est dans le plateau, sinon None."""
        px, py = pos
        if not self.rect.collidepoint(px, py):
            return None
        rel_x = px - self.x
        rel_y = py - self.y
        col = int(rel_x // self.cell_size)
        row = int(rel_y // self.cell_size)
        # bornes de sécurité
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return (row, col)
        return None

    def draw(self, surface: pygame.Surface):
        """Dessine le plateau sur la surface fournie."""
        # --- ombre portée (sur surface avec alpha) pour un rendu moderne ---
        shadow = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 70))
        surface.blit(shadow, (self.x + 6, self.y + 6))

        # arrière-plan du plateau (rectangle arrondi)
        pygame.draw.rect(surface, COLOR_BOARD, self.rect, border_radius=BOARD_BORDER_RADIUS)

        # lignes de la grille (horizontales + verticales)
        for i in range(self.rows + 1):
            y = self.y + int(i * self.cell_size)
            pygame.draw.line(surface, COLOR_GRID, (self.x, y), (self.x + self.size, y), GRID_LINE_WIDTH)
        for j in range(self.cols + 1):
            x = self.x + int(j * self.cell_size)
            pygame.draw.line(surface, COLOR_GRID, (x, self.y), (x, self.y + self.size), GRID_LINE_WIDTH)

        # emplacements circulaires (visuels) — centre de chaque case
        radius = int(self.cell_size * 0.28)
        for r in range(self.rows):
            for c in range(self.cols):
                cx = int(self.x + c * self.cell_size + self.cell_size / 2)
                cy = int(self.y + r * self.cell_size + self.cell_size / 2)
                pygame.draw.circle(surface, COLOR_CELL, (cx, cy), radius)

        # survol (hover) : rectangle légèrement coloré derrière la case
        if self.hover is not None:
            hr, hc = self.hover
            rx = int(self.x + hc * self.cell_size + CELL_PADDING)
            ry = int(self.y + hr * self.cell_size + CELL_PADDING)
            size = int(self.cell_size - 2 * CELL_PADDING)
            hover_rect = pygame.Rect(rx, ry, size, size)
            pygame.draw.rect(surface, COLOR_HOVER, hover_rect, border_radius=12)

        # sélection : rectangle plus marqué (au-dessus du hover)
        if self.selected is not None:
            sr, sc = self.selected
            sx = int(self.x + sc * self.cell_size + CELL_PADDING + 4)
            sy = int(self.y + sr * self.cell_size + CELL_PADDING + 4)
            ssize = int(self.cell_size - 2 * CELL_PADDING - 8)
            sel_rect = pygame.Rect(sx, sy, ssize, ssize)
            pygame.draw.rect(surface, COLOR_SELECTED, sel_rect, border_radius=10)
