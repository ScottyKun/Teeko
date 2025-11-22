import pygame
import config
import os

class Menu:
    def __init__(self, surface):
        self.surface = surface
        self.font_title = pygame.font.Font(None, 72)
        self.font_text = pygame.font.Font(None, 38)
        self.font_small = pygame.font.Font(None, 32)

        # Image de fond
        bg_path = os.path.join("assets", "bg.png")
        if os.path.exists(bg_path):
            self.background = pygame.image.load(bg_path).convert()
        else:
            self.background = None

        # Données du menu
        self.modes = ["PvsP", "PvsIA", "IAvsIA"]
        self.mode_index = 0
        self.mode = self.modes[self.mode_index]

        self.difficulties = ["Débutant", "Intermédiaire", "Expert"]
        self.diff_index = 0
        self.difficulty = self.difficulties[self.diff_index]

        self.show_difficulty = False

        self.player1_name = ""
        self.player2_name = ""
        self.active_input = None
        self.cursor_visible = True
        self.cursor_timer = pygame.time.get_ticks()

        # Rectangles interactifs
        self.start_button = pygame.Rect(config.WINDOW_WIDTH//2 - 120, 700, 240, 60)
        self.input_player1 = pygame.Rect(config.WINDOW_WIDTH//2 - 150, 400, 300, 40)
        self.input_player2 = pygame.Rect(config.WINDOW_WIDTH//2 - 150, 460, 300, 40)
        self.mode_rect = pygame.Rect(config.WINDOW_WIDTH//2 - 150, 300, 300, 40)
        self.diff_rect = pygame.Rect(config.WINDOW_WIDTH//2 - 150, 350, 300, 40)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.collidepoint(event.pos):
                # Renvoie tous les paramètres du menu
                return {
                    "mode": self.mode,
                    "difficulty": self.difficulty,
                    "player1_name": self.player1_name or "Player 1",
                    "player2_name": self.player2_name or "Player 2"
                }

            # Champs de texte
            if self.mode in ["PvsP", "PvsIA"]:
                if self.input_player1.collidepoint(event.pos):
                    self.active_input = "p1"
                elif self.mode == "PvsP" and self.input_player2.collidepoint(event.pos):
                    self.active_input = "p2"
                else:
                    self.active_input = None

            # Changement de mode
            if self.mode_rect.collidepoint(event.pos):
                self.mode_index = (self.mode_index + 1) % len(self.modes)
                self.mode = self.modes[self.mode_index]

                # Ajuster les champs selon le mode
                if self.mode == "PvsP":
                    self.show_difficulty = False
                    self.player1_name = ""
                    self.player2_name = ""
                elif self.mode == "PvsIA":
                    self.show_difficulty = True
                    self.player1_name = ""
                    self.player2_name = "IA"
                else:  # IA vs IA
                    self.show_difficulty = True
                    self.player1_name = "IA 1"
                    self.player2_name = "IA 2"

            # Changement de difficulté
            if self.show_difficulty and self.diff_rect.collidepoint(event.pos):
                self.diff_index = (self.diff_index + 1) % len(self.difficulties)
                self.difficulty = self.difficulties[self.diff_index]

        elif event.type == pygame.KEYDOWN:
            if self.active_input:
                if event.key == pygame.K_BACKSPACE:
                    if self.active_input == "p1":
                        self.player1_name = self.player1_name[:-1]
                    else:
                        self.player2_name = self.player2_name[:-1]
                else:
                    char = event.unicode
                    if char.isprintable():
                        if self.active_input == "p1" and len(self.player1_name) < 15:
                            self.player1_name += char
                        elif self.active_input == "p2" and len(self.player2_name) < 15:
                            self.player2_name += char
        return None

    def update_cursor(self):
        now = pygame.time.get_ticks()
        if now - self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = now
    
    def write(self, text):
        if text=="PvsP":
            return "Joueur vs Joueur"
        
        if text=="PvsIA":
            return "Joueur vs IA"
        
        if text=="IAvsIA":
            return "IA vs IA"

    def draw(self):
        # Fond
        if self.background:
            bg_scaled = pygame.transform.scale(self.background, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
            self.surface.blit(bg_scaled, (0, 0))
        else:
            self.surface.fill((25, 25, 45))

        # Titre
        title_surface = self.font_title.render("Jeu de Teeko", True, (0, 0, 0))
        title_rect = title_surface.get_rect(center=(config.WINDOW_WIDTH//2, 120))
        self.surface.blit(title_surface, title_rect)

        # Mode
        pygame.draw.rect(self.surface, (80, 80, 120), self.mode_rect, border_radius=8)
        mode_text = self.font_text.render(self.write(self.mode), True, (255, 255, 255))
        self.surface.blit(mode_text, (self.mode_rect.x + 10, self.mode_rect.y + 5))

        # Difficulté
        if self.show_difficulty:
            pygame.draw.rect(self.surface, (80, 80, 120), self.diff_rect, border_radius=8)
            diff_text = self.font_small.render(f"Difficulté : {self.difficulty}", True, (255, 255, 255))
            self.surface.blit(diff_text, (self.diff_rect.x + 10, self.diff_rect.y + 5))

        # Inputs
        if self.mode in ["PvsP", "PvsIA"]:
            self.draw_input(self.input_player1, self.player1_name, "Nom Joueur 1" if self.mode == "PvsP" else "Nom Joueur")
            if self.mode == "PvsP":
                self.draw_input(self.input_player2, self.player2_name, "Nom Joueur 2")

        # Bouton start
        pygame.draw.rect(self.surface, (0, 150, 0), self.start_button, border_radius=12)
        start_text = self.font_text.render("Commencer", True, (255, 255, 255))
        self.surface.blit(start_text, (self.start_button.x + (self.start_button.width - start_text.get_width())//2,
                                       self.start_button.y + (self.start_button.height - start_text.get_height())//2))

    def draw_input(self, rect, text, placeholder):
        pygame.draw.rect(self.surface, (255, 255, 255), rect, 2, border_radius=6)
        display_text = text if text else placeholder
        color = (255, 255, 255) if text else (180, 180, 180)
        txt_surface = self.font_small.render(display_text, True, color)
        self.surface.blit(txt_surface, (rect.x + 10, rect.y + 6))

        self.update_cursor()
        if self.cursor_visible and self.active_input:
            if (self.active_input == "p1" and rect == self.input_player1) or \
               (self.active_input == "p2" and rect == self.input_player2):
                cursor_x = rect.x + 10 + self.font_small.size(text)[0] + 2
                pygame.draw.line(self.surface, (255, 255, 255), (cursor_x, rect.y + 8), (cursor_x, rect.y + 32), 2)
