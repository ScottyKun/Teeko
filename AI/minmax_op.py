from PrologRules.ia_helper import switch_player

class MinMaxOp:
    def __init__(self, manager, evaluator, engine, max_depth=2):
        self.m = manager
        self.evaluator = evaluator
        self.max_depth = max_depth
        self.transpo = {}
        self.engine = engine 
    
    def compute(self, state, player):
        """
        Retourne le meilleur coup pour player sous forme :
            (best_score, best_move)
        """
        score, move = self.minmax(state, player, self.max_depth, True)

        # Affichage du choix final pour debug
        print(f"[MinMax] Meilleur coup choisi pour '{player}' : {move} avec score {score}")

        return score, move

    
    def minmax(self, state, player, depth, maximizing):

        key = (tuple(state), player, depth, maximizing)
        if key in self.transpo:
            print(f"[CACHE HIT] → état déjà connu pour {player} / depth={depth}")
            return self.transpo[key]
        

        # État terminal ou profondeur atteinte -> évaluation statique
        if depth == 0 or self.m.is_terminal(state):
            score = self.evaluator.evaluate(state, player)
            return score, None

        legal_moves = self.m.get_legal_moves(state, player)

        if not legal_moves:
            # Si aucun coup -> très mauvais
            return -9999 if maximizing else 9999, None

        best_move = None

        # maximizing player
        if maximizing:
            best_score = -999999

            for move in legal_moves:
                new_state = self.engine.simulate_move(state, player, move)
                score, _ = self.minmax(new_state, switch_player(player), depth - 1, False)

                if score > best_score:
                    best_score = score
                    best_move = move

            self.transpo[key] = (best_score, best_move)
            return best_score, best_move

        #minimizing player
        else:
            best_score = 999999

            for move in legal_moves:
                new_state = self.engine.simulate_move(state, player, move)
                score, _ = self.minmax(new_state, switch_player(player), depth - 1, True)

                if score < best_score:
                    best_score = score
                    best_move = move
            
            self.transpo[key] = (best_score, best_move)
            return best_score, best_move