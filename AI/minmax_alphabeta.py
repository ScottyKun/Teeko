# AI/minmax_alphabeta.py
import time
import random
from PrologRules.ia_helper import switch_player

INF = 10**9

class MinMaxAlphaBeta:
    def __init__(self, manager, evaluator, engine, max_depth=4, time_limit=None, mode=None):
        self.m = manager
        self.evaluator = evaluator
        self.max_depth = max_depth
        self.engine = engine
        self.time_limit = time_limit

        self.mode = mode  # "IAvsIA" ou "PvsIA"
        self.state_history = []
        self.max_cycle_repeats = 2          # combien de répétitions avant random
        self.max_cycle_full_repeats = 4     # combien avant draw
        
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

        # Coup tactique : centre
        center = 12
        if state[center] == 'e' and ("placement", center) in self.m.get_legal_moves(state, player):
            return 99999, ("placement", center)

        # ID Deepening
        for depth in range(1, self.max_depth + 1):

            if self._timeout():
                break

            val, move = self._alphabeta_root(state, player, depth)

            if val is None or move is None:
                break
            
            best_move = move
            best_score = val

            print(f"[ID] Profondeur={depth} | Score={best_score} | Best={best_move}")

            if best_score >= 9000:
                break

        return best_score, best_move

    # -------------------------------------------------------------
    # ALPHABETA RACINE
    # -------------------------------------------------------------
    def _alphabeta_root(self, state, player, depth):
        alpha = -INF
        beta = INF
        scored_moves = []

        moves = self.m.get_legal_moves(state, player)
        if not moves:
            return -INF, None

        # ====================
        # 1. DÉTECTION CYCLE 
        # ======================
        cycle_status = self.detect_cycle(state)

        # Match nul uniquement en IAvsIA
        if cycle_status == "full" and self.mode == "IAvsIA":
            print("[CYCLE] Match nul détecté (IAvsIA).")
            return 0, None

        # ======================================================
        # 2. MOVE ORDERING 
        # ======================================================
        ordered = []
        for mv in moves:
            sim = self.engine.simulate_move(state, player, mv)

            # Coup gagnant immédiat → joue direct
            if self.m.winner(sim) == player:
                return 100000, mv

            score = self.evaluator.evaluate(sim, self.root_player)
            ordered.append((score, mv))

        ordered.sort(key=lambda x: x[0], reverse=True)
        ordered_moves = [mv for _, mv in ordered]

        # ================================
        # 3. PHASE DE PLACEMENT → RANDOM
        # =================================
        is_placement_phase = (state.count('e') > 17)
        if is_placement_phase:
            k = min(3, len(ordered_moves))
            candidates = ordered_moves[:k]
            random.shuffle(candidates)
            ordered_moves = candidates

        # ============================
        # 4. ANTI-CYCLE 
        # ============================
        if cycle_status == "minor":
            # IA vs IA → random safe seulement si aucun coup gagnant immédiat
            if self.mode == "IAvsIA":
                print("[CYCLE] Cycle détecté, random safe activé (IAvsIA)")
                best = self.safe_random_move(state, player, ordered_moves)
                return self.evaluator.evaluate(self.engine.simulate_move(state, player, best), self.root_player), best

            # PvsIA → réordonne simplement les coups cycliques à la fin
            else:
                non_cyclic = []
                cyclic = []

                for mv in ordered_moves:
                    sim = self.engine.simulate_move(state, player, mv)
                    if tuple(sim) in self.state_history:
                        cyclic.append(mv)
                    else:
                        non_cyclic.append(mv)

                # Priorité aux coups non cycliques
                ordered_moves = non_cyclic + cyclic

        # ===========================
        # 5. BOUCLE ALPHA-BETA 
        # ===========================
        best_score = -INF
        best_move = None

        for mv in ordered_moves:
            child = self.engine.simulate_move(state, player, mv)
            next_player = switch_player(player)

            maximizing = (next_player == self.root_player)

            val = self._alphabeta(child, next_player, depth-1, alpha, beta, maximizing)

            if val is None:
                return None, None

            scored_moves.append((val, mv))

            if val > best_score:
                best_score = val
                best_move = mv

            alpha = max(alpha, val)

        return best_score, best_move



    # -------------------------------------------------------------
    # RECURSIVE ALPHA-BETA
    # -------------------------------------------------------------
    def _alphabeta(self, state, player, depth, alpha, beta, maximizing):

        if self._timeout():
            return None

        self.node_count += 1

        # -------------------------------------------------
        # clé de transposition 
        # -------------------------------------------------
        key = (tuple(state), depth, player, maximizing, self.root_player)
        # -------------------------------------------------
        if key in self.transpo:
            return self.transpo[key]

        # Terminal node
        if depth == 0 or self.m.is_terminal(state):
            val = self.evaluator.evaluate(state, self.root_player)
            self.transpo[key] = val
            return val

        moves = self.m.get_legal_moves(state, player)
        if not moves:
            val = -INF if maximizing else INF
            self.transpo[key] = val
            return val

        # Move ordering
        ordered = []
        for mv in moves:
            sim = self.engine.simulate_move(state, player, mv)
            s = self.evaluator.evaluate(sim, self.root_player)
            ordered.append((s, mv))

        ordered.sort(key=lambda x: x[0], reverse=maximizing)
        ordered_moves = [mv for _, mv in ordered]

        # ------------------------
        # MAX PLAYER (root_player)
        # ------------------------
        if maximizing:
            value = -INF
            for mv in ordered_moves:
                child = self.engine.simulate_move(state, player, mv)

                next_player = switch_player(player)
                next_max = (next_player == self.root_player)   # FIX 3
                result = self._alphabeta(child, next_player, depth-1, alpha, beta, next_max)

                if result is None:
                    return None

                value = max(value, result)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break

            self.transpo[key] = value
            return value

        # ------------------------
        # MIN PLAYER (adversaire)
        # ------------------------
        else:
            value = INF
            for mv in ordered_moves:
                child = self.engine.simulate_move(state, player, mv)

                next_player = switch_player(player)
                next_max = (next_player == self.root_player)   # FIX 4
                result = self._alphabeta(child, next_player, depth-1, alpha, beta, next_max)

                if result is None:
                    return None

                value = min(value, result)
                beta = min(beta, value)
                if beta <= alpha:
                    break

            self.transpo[key] = value
            return value

    def _timeout(self):
        return (self.time_limit and (time.perf_counter() - self.start_time) > self.time_limit)
    
    # ------------------------
    # Détecttion des boucles dans le jeu
    # ------------------------
    def detect_cycle(self, state):
        """
        Retourne :
            - "none"  → pas de cycle
            - "minor" → cycle léger détecté (on déclenche un random contrôlé)
            - "full"  → cycle trop long → match nul (IA vs IA uniquement)
        """
        s = tuple(state)
        self.state_history.append(s)

        # On ne garde que les 12 derniers
        if len(self.state_history) > 12:
            self.state_history.pop(0)

        repeats = self.state_history.count(s)

        if repeats >= self.max_cycle_full_repeats:
            return "full"

        if repeats >= self.max_cycle_repeats:
            return "minor"

        return "none"
    
    # ------------------------
    # Gestion des boucles de jeu
    # ------------------------
    
    def safe_random_move(self, state, player, moves):
        """
        Choisir un coup aléatoire parmi les moves qui sont tactiquement sûrs 
        et donner la priorité aux coups de blocage immédiats.
        """
        safe_moves = []

        # 1. DÉTECTION DES MENACES DE L'ADVERSAIRE (Étape préliminaire)
        threat_moves = []
        current_opponent_moves = self.m.get_legal_moves(state, switch_player(player))
        for cm in current_opponent_moves:
            sim_threat = self.engine.simulate_move(state, switch_player(player), cm)
            if self.m.winner(sim_threat) == switch_player(player):
                threat_moves.append(cm)
                
        # 2. ANALYSE DES COUPS CANDIDATS
        # On mélange les coups au début pour que le premier coup de blocage trouvé soit aléatoire
        random.shuffle(moves) 
        
        for mv in moves:
            sim = self.engine.simulate_move(state, player, mv)

            # A. FILTRE NÉGATIF 1: Éviter la défaite immédiate
            if self.m.winner(sim) == switch_player(player):
                continue

            # B. FILTRE NÉGATIF 2: Éviter la double menace (Fourchette)
            danger_count = 0
            next_moves = self.m.get_legal_moves(sim, switch_player(player))
            for nm in next_moves:
                sim2 = self.engine.simulate_move(sim, switch_player(player), nm)
                if self.m.winner(sim2) == switch_player(player):
                    danger_count += 1
            
            if danger_count >= 2:
                continue
                
            # C. FILTRE POSITIF (Priorité de la Défense)
            if threat_moves:
                # Vérifier si ce coup (mv) élimine toutes les menaces
                blocks_all_threats = True
                next_opponent_moves = self.m.get_legal_moves(sim, switch_player(player))
                
                for nom in next_opponent_moves:
                    sim_after_block = self.engine.simulate_move(sim, switch_player(player), nom)
                    # Si l'adversaire peut encore gagner après mon coup, le blocage a échoué.
                    if self.m.winner(sim_after_block) == switch_player(player):
                        blocks_all_threats = False 
                        break

                if blocks_all_threats:
                    # C'est un coup de blocage réussi -> PRIORITY RETURN
                    return mv 

            # Si le coup passe tous les filtres sans être un blocage prioritaire, il est sûr
            safe_moves.append(mv)

        # 3. CONCLUSION
        if safe_moves:
            # Retourner un coup VRAIMENT aléatoire parmi les coups sûrs restants
            return random.choice(safe_moves)

        # Aucun coup n'est 'safe' (la partie est perdue)
        return moves[0]


