# AI/minmax_alphabeta.py
import time
from PrologRules.ia_helper import switch_player

INF = 10**9

class MinMaxAlphaBeta:
    def __init__(self, manager, evaluator, engine, max_depth=3, time_limit=None):
        self.m = manager
        self.evaluator = evaluator
        self.max_depth = max_depth
        self.engine = engine
        self.time_limit = time_limit
        
        # Variables d'état pour la recherche
        self.root_player = None
        self.transpo = {} 
        self.start_time = None
        self.node_count = 0

   # -------------------------------------------------------------
    # WRAPPER : Iterative deepening 
    # -------------------------------------------------------------
    def compute(self, state, player):
        self.start_time = time.perf_counter()
        self.node_count = 0
        self.root_player = player
        self.transpo = {}
        
        best_move = None
        best_score = -INF

        # 1. Coup tactique 
        center = 12
        if state[center] == 'e' and ("placement", center) in self.m.get_legal_moves(state, player):
            return 99999, ("placement", center)

        # 2. Iterative deepening
        for depth in range(1, self.max_depth + 1):
            
            # Si on a déjà dépassé le temps avant même de commencer la profondeur
            if self._timeout():
                print(f"[TIMEOUT] Pas le temps de démarrer la prof {depth}")
                break

            # On tente de récupérer le score et le coup de cette profondeur
            val, move = self._alphabeta_root(state, player, depth)

            # --- SÉCURITÉ TIMEOUT ---
            # Si _alphabeta_root renvoie None (indiquant une coupure), 
            # on N'UPDATE PAS best_move. On garde celui de la profondeur d'avant.
            if val is None or move is None:
                print(f"[TIMEOUT] Calcul interrompu à la profondeur {depth}. On garde le coup de prof {depth-1}.")
                break
            
            # Si la profondeur est complète, on met à jour le "vrai" meilleur coup
            best_move = move
            best_score = val
            
            print(f"[ID] Profondeur={depth} | Score={best_score} | Best={best_move}")
            
            # Victoire trouvée, inutile d'aller plus loin
            if best_score >= 9000:
                break

        return best_score, best_move

    # -------------------------------------------------------------
    # RACINE
    # -------------------------------------------------------------
    def _alphabeta_root(self, state, player, depth):
        alpha = -INF
        beta = INF
        current_best_score = -INF
        current_best_move = None

        moves = self.m.get_legal_moves(state, player)
        if not moves:
            return -INF, None

        # Move ordering
        ordered = []
        for mv in moves:
            sim = self.engine.simulate_move(state, player, mv)
            if self.m.winner(sim) == player: return 100000, mv
            score = self.evaluator.evaluate(sim, self.root_player)
            ordered.append((score, mv))
        ordered.sort(key=lambda x: x[0], reverse=True)
        ordered_moves = [mv for _, mv in ordered]

        for mv in ordered_moves:
            # CHECK TIMEOUT
            if self._timeout():
                # On renvoie None pour signaler à compute() que ce résultat est pourri
                return None, None 

            child = self.engine.simulate_move(state, player, mv)
            val = self._alphabeta(child, switch_player(player), depth-1, alpha, beta, False)

            if val is None: # Timeout remonté des enfants
                return None, None

            if val > current_best_score:
                current_best_score = val
                current_best_move = mv

            alpha = max(alpha, val)

        return current_best_score, current_best_move

    # -------------------------------------------------------------
    # ALPHABETA RECURSIF
    # -------------------------------------------------------------
    def _alphabeta(self, state, player, depth, alpha, beta, maximizing):
        if self._timeout():
            return None

        self.node_count += 1
        
        # Transposition Table Lookup
        # La clé inclut 'maximizing' pour différencier les nœuds Min et Max
        key = (tuple(state), depth, maximizing)
        if key in self.transpo:
            return self.transpo[key]

        # --- Cas Terminal ---
        if depth == 0 or self.m.is_terminal(state):
            # On évalue toujours par rapport au root_player (l'IA)
            # Si le plateau est bon pour root_player -> positif
            # Si le plateau est mauvais pour root_player -> négatif
            val = self.evaluator.evaluate(state, self.root_player)
            self.transpo[key] = val
            return val

        moves = self.m.get_legal_moves(state, player)
        if not moves:
            # Pas de coups possibles (ne devrait pas arriver si non terminal, mais sécurité)
            val = -INF if maximizing else INF
            return val

        # --- Move Ordering Interne ---
        ordered = []
        for mv in moves:
            sim = self.engine.simulate_move(state, player, mv)
            # Optimisation: on évalue toujours pour root_player pour le tri
            s = self.evaluator.evaluate(sim, self.root_player)
            ordered.append((s, mv))
        
        # Si Maximizing (IA): on veut voir les scores élevés en premier (Reverse=True)
        # Si Minimizing (Opponent): on veut voir les scores faibles en premier (Reverse=False)
        # (Car un score faible pour l'IA est un score fort pour l'adversaire)
        ordered.sort(key=lambda x: x[0], reverse=maximizing)
        ordered_moves = [mv for _, mv in ordered]

        # --- MAX NODE (Tour de l'IA) ---
        if maximizing:
            value = -INF
            for mv in ordered_moves:
                child = self.engine.simulate_move(state, player, mv)
                result = self._alphabeta(child, switch_player(player), depth-1, alpha, beta, False)
                
                if result is None: return None
                
                value = max(value, result)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break # Beta Cutoff
            
            self.transpo[key] = value
            return value

        # --- MIN NODE (Tour de l'Adversaire) ---
        else:
            value = INF
            for mv in ordered_moves:
                child = self.engine.simulate_move(state, player, mv)
                result = self._alphabeta(child, switch_player(player), depth-1, alpha, beta, True)
                
                if result is None: return None
                
                value = min(value, result)
                beta = min(beta, value)
                if beta <= alpha:
                    break # Alpha Cutoff
            
            self.transpo[key] = value
            return value

    def _timeout(self):
        return (self.time_limit and (time.perf_counter() - self.start_time) > self.time_limit)