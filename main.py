import pygame
import sys
import config
from gui.board import Board
from gui.banner import Banner

def get_nearest_point(pos, board):
    x, y = pos
    for px, py in board.points:
        dist = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
        if dist < config.POINT_RADIUS * 2:  # tolérance
            return (px, py)
    return None


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption(" Teeko ")  
    clock = pygame.time.Clock()

    board = Board(screen)
    banner = Banner(screen)
    current_player = 1

    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = pygame.mouse.get_pos()
                nearest = get_nearest_point(click_pos, board)
                if nearest:
                    print("Intersection cliquée :", nearest)
                    # Alternance du joueur actif
                    current_player = 2 if current_player == 1 else 1

        board.draw()
        banner.draw(current_player=current_player)
        pygame.display.flip()
        clock.tick(config.FPS)


if __name__ == "__main__":
    main()
