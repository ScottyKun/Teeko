# main.py
import pygame
from config import *
from gui.board import Board

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Teeko - Interface (prototype)")
    clock = pygame.time.Clock()

    board = Board(screen_size=(WINDOW_WIDTH, WINDOW_HEIGHT))
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 22)

    running = True
    status_text = "Survoler et cliquer sur une case"

    while running:
        # --- événements ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEMOTION:
                board.hover = board.get_cell_at_pos(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # clic gauche
                    cell = board.get_cell_at_pos(event.pos)
                    if cell:
                        board.selected = cell
                        status_text = f"Sélection : ligne {cell[0]} — colonne {cell[1]}"

        # --- rendu ---
        screen.fill(COLOR_BG)

        # Titre / info dans la zone supérieure
        title_surf = font.render("Teeko — Prototype UI", True, (230, 230, 230))
        screen.blit(title_surf, (20, 16))
        info_surf = small_font.render(status_text, True, (200, 200, 200))
        screen.blit(info_surf, (20, 56))

        # Dessiner le plateau (board s'occupe de hover/selection)
        board.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
