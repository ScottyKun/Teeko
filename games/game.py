import pygame
import config
from games.board import Board
from gui.banner import Banner
from AI.ai_engine import AIEngine

class Game:
    def __init__(self, surface, mode, difficulty, player1_name, player2_name):
        self.surface = surface
        self.board = Board(surface)
        self.banner = Banner(surface, player1_name, player2_name)
        self.current_player = 1
        self.selected_piece = None  # pour la phase de déplacement
        self.selected_from = None # pour le shift
        self.phase_message = ""
        self.message_timer = 0
        self.engine=AIEngine()
        ##
        self.mode = mode
        self.difficulty = difficulty
        self.p1=player1_name
        self.p2=player2_name
        if self.board.phase == "placement":
            self.show_message("Phase de placement", duration=1500)

    #
    def player_to_prolog(self,player):
        return 'n' if player == 1 else 'b'
    
    #
    def opponent(self,player):
        return 2 if player == 1 else 1
    
    # gestion du mode
    def is_ai(self,player):
        if self.mode == "PvsP":
            return False
        if self.mode == "PvsIA" and player == 2:
            return True
        if self.mode == "IAvsIA":
            return True
        return False
    
    #
    def coords_to_index(self,row, col):
        return row * 5 + col

    def handle_click(self, pos):
        # récupérer le point le plus proche d'un clic
        nearest = self.get_nearest_point(pos)
        if not nearest:
            return

        x, y = nearest

        # conversion pour avoir index
        index = self.coords_to_index(x, y)

        # joueur format prolog
        prolog_player = self.player_to_prolog(self.current_player)

        # determiner phase du jeu
        self.board.phase = self.engine.get_phase(self.board.to_prolog_state())

        new_state = None 

        if self.board.phase == "placement":
            move = ('placement', index)

            if not self.engine.validate_move(self.board.to_prolog_state(), prolog_player, move):
                self.show_message("Coup invalide !")
                return
            
            # On applique le coup
            new_state = self.engine.apply_move(self.board.to_prolog_state(), prolog_player, move)

        else:
            # Phase de déplacement
            if self.selected_from is None:
                state = self.board.to_prolog_state()
                # Vérifier que la case appartient bien au joueur courant
                if state[index] != prolog_player:
                    print("Tu dois sélectionner un de TES pions.")
                    return
                
                self.selected_from = index
                print(f"FROM sélectionné: {index}")
                return
            
            else:
                self.selected_piece = index
                print(f"TO sélectionné: {index}")

                # on est donc dans le cas du deplacement
                move = ('shift', self.selected_from, self.selected_piece)

                if not self.engine.validate_move(self.board.to_prolog_state(), prolog_player, move):
                    self.show_message("Coup invalide !")
                    # On reset la sélection si le coup est invalide pour permettre de rechoisir
                    self.selected_from = None 
                    return
            
                new_state = self.engine.apply_move(self.board.to_prolog_state(), prolog_player, move)
                self.selected_from = None

        # --- Mise à jour du plateau seulement si le nouvel état est valide ---
        if new_state:
            self.board.update_from_prolog_state(new_state)
        else:
            print("Erreur: Prolog n'a pas renvoyé de nouvel état.")
            return

        # check winner
        winner = self.engine.get_winner(new_state)
        if winner  in ('b', 'n'):
            if winner == 'n':
                self.show_message(f"{self.p1} a gagné la partie !", duration=2000)
            else:
                self.show_message(f"{self.p2} a gagné la partie !", duration=2000)
            # On peut ajouter un return ici pour arrêter de jouer si gagné
            return 

        # changement de player
        self.current_player = self.opponent(self.current_player)
        print(self.current_player)
        
        # Si on est en mode vs IA
        if self.is_ai(self.current_player):
            # Petit délai pour voir le coup du joueur avant que l'IA joue (optionnel mais sympa)
            pygame.time.set_timer(pygame.USEREVENT+1, 300)
            #self.ai_play()


    # tour de IA
    def ai_play(self):
        prolog_player = self.player_to_prolog(self.current_player)

        ai_move = self.engine.get_best_move(self.board.to_prolog_state(), prolog_player)

        if ai_move:
            new_state = self.engine.apply_move(self.board.to_prolog_state(), prolog_player, ai_move)
            
            if new_state:
                self.board.update_from_prolog_state(new_state)
            else:
                print("Erreur critique : L'IA a généré un coup que Prolog n'arrive pas à appliquer.")
        else:
            print("L'IA ne trouve pas de coup valide (Match nul ou bloqué ?)")

        winner = self.engine.get_winner(self.board.to_prolog_state())
        if winner in ('b', 'n'):
            if winner == 'n':
                self.show_message(f"{self.p1} a gagné la partie !", duration=5000)
            else:
                self.show_message(f"{self.p2} a gagné la partie !", duration=5000)
            return

        # changement de player
        self.current_player = self.opponent(self.current_player)
        print(self.current_player)

    #
    def affiche_phase(self):
        if self.board.phase == "placement":
            return None
        elif self.board.phase == "deplacement":
            self.show_message("Phase de déplacement", duration=1500)

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
