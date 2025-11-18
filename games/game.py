import pygame
import config
from games.board import Board
from gui.banner import Banner

class Game:
    def __init__(self, surface, mode, difficulty, player1_name, player2_name):
        self.surface = surface
        self.board = Board(surface)
        self.banner = Banner(surface, player1_name, player2_name)
        self.current_player = 1
        self.selected_piece = None  # pour la phase de déplacement
        self.phase_message = ""
        self.message_timer = 0
        ##
        self.mode = mode
        self.difficulty = difficulty
        self.p1=player1_name
        self.p2=player2_name

    def handle_click(self, pos):
        # récupérer le point le plus proche d'un clic
        nearest = self.get_nearest_point(pos)
        if not nearest:
            return

        # Phase de placement
        if self.board.phase == "placement":
            if nearest not in self.board.occupied_positions:
                self.board.place_piece(nearest, self.current_player)
                if self.current_player == 1:
                    print(f"Phase de placement → {self.p1} a placé un pion à {nearest}")
                else:
                    print(f"Phase de placement → {self.p2} a placé un pion à {nearest}")    

                # Si on atteint la phase de déplacement
                if self.board.phase == "deplacement":
                   self.show_message("Phase de déplacement commencée !")
                # changer de joueur
                self.current_player = 2 if self.current_player == 1 else 1

        # Phase de déplacement
        elif self.board.phase == "deplacement":
            # Sélection du pion à déplacer
            if not self.selected_piece:
                # On cherche si le joueur clique sur un de ses pions
                pieces = self.board.player1_pieces if self.current_player == 1 else self.board.player2_pieces
                for piece in pieces:
                    if self.distance(piece.position, nearest) < config.POINT_RADIUS * 2:
                        self.selected_piece = piece
                        if self.current_player == 1:
                            print(f"Phase de placement → {self.p1} a sélectionné un pion à {piece.position}")
                        else:
                            print(f"Phase de placement → {self.p2} a sélectionné un pion à {piece.position}") 
                        return
            else:
                # Déplacement du pion
                if nearest not in self.board.occupied_positions:
                    print(f"Joueur {self.current_player} déplace un pion de {self.selected_piece.position} vers {nearest}")
                    self.board.occupied_positions.remove(self.selected_piece.position)
                    self.selected_piece.position = nearest
                    self.board.occupied_positions.append(nearest)
                    self.selected_piece = None
                    self.current_player = 2 if self.current_player == 1 else 1

    # determiner le point le plus proche d'un clic
    def get_nearest_point(self, pos):
     return self.board.pixel_to_logical(pos)


    # calculer la distance entre deux points
    def distance(self, p1, p2):
        return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5
    
    def show_message(self, message, duration=2000):
        self.phase_message = message
        self.message_timer = pygame.time.get_ticks() + duration

    def update(self):
        if self.phase_message and pygame.time.get_ticks() > self.message_timer:
            self.phase_message = ""

    def draw(self):
        self.board.draw()
        self.banner.draw(current_player=self.current_player)

        # === Affichage du message temporaire ===
        if self.phase_message:
            font = pygame.font.SysFont("Arial", 36, bold=True)
            text_surf = font.render(self.phase_message, True, config.WHITE)
            text_rect = text_surf.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
            pygame.draw.rect(self.surface, (0, 0, 0, 100), text_rect.inflate(40, 20), border_radius=12)
            self.surface.blit(text_surf, text_rect)
