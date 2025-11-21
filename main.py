import pygame
import config
from games.game import Game
from gui.menu import Menu



def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption(" Teeko ")  
    clock = pygame.time.Clock()

    menu = Menu(screen)
    game = None
    state = "menu"

    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == "menu":
                action = menu.handle_event(event)
                if isinstance(action, dict):  # paramètres renvoyés
                    game = Game(screen,
                        mode=action["mode"],
                        difficulty=action["difficulty"],
                        player1_name=action["player1_name"],
                        player2_name=action["player2_name"])
                    state = "game"

            elif state == "game":
             if event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)

        # Mise à jour et affichage
        if state == "menu":
            menu.draw()
        elif state == "game":
            game.update()
            game.draw()

        pygame.display.flip()
        clock.tick(config.FPS)

pygame.quit()


#if __name__ == "__main__":
 #   main()
