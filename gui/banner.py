import pygame
import config

class Banner:
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.SysFont("Arial", 24, bold=True)  # police réduite
        self.player1_name = "Player 1"
        self.player2_name = "Player 2"

    def draw(self, current_player=1):
        banner_rect = pygame.Rect(0, 0, config.WINDOW_WIDTH, 70)
        pygame.draw.rect(self.surface, config.BANNER_BG, banner_rect, border_radius=10)

        # Player 1
        text1 = self.font.render(self.player1_name, True, config.WHITE)
        self.surface.blit(text1, (100, 20))
        pygame.draw.circle(self.surface, config.RED, (60, 35), 12)
        pygame.draw.circle(self.surface, config.RED, (60, 35), 20, 3)

        # Player 2
        text2 = self.font.render(self.player2_name, True, config.WHITE)
        self.surface.blit(text2, (config.WINDOW_WIDTH - 200, 20))
        pygame.draw.circle(self.surface, config.BLUE, (config.WINDOW_WIDTH - 60, 35), 12)
        pygame.draw.circle(self.surface, config.BLUE, (config.WINDOW_WIDTH - 60, 35), 20, 3)

        # Indication joueur actif (rectangle discret)
        if current_player == 1:
            pygame.draw.rect(self.surface, config.RED, (90, 15, 160, 40), 2, border_radius=8)
        else:
            pygame.draw.rect(self.surface, config.BLUE, (config.WINDOW_WIDTH - 255, 15, 160, 40), 2, border_radius=8)