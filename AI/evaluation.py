"""
On va definir notre fonction d'evaluation qu'on va utiliser dans nos algos de recherche
Il va retourner un score selon que l'etat soit favorable ou defavorable

Pour donner un score, on se basera sur
- victoire ou defaite
-proximite de victoire (nombre de pions alignes, carres)
-controle du centre
-mobilite (nombre de coups possibles)


Score global = somme pondérée :
            +10 000 si player gagne
            -10 000 si player perd
            + alignements
            + contrôle du centre
            + mobilité
            +menaces proches de victoire

"""

from PrologRules.ia_helper import switch_player

class Evaluation:
    def __init__(self, manager):
        self.m=manager


        #positions gagnantes
        self.winning_patterns = self.m.get_winning_positions()
    
    def evaluate(self,state,player):

        #victoire
        if self.m.winner(state)==player:
            return 10000
        
        if self.m.winner(state)==switch_player(player):
            return -10000
        
        score=0

        opponent = switch_player(player)
        player_pos = self.m.get_player_positions(state, player)
        opp_pos = self.m.get_player_positions(state, opponent)

        score = 0

        # --- 1) HEATMAP (améliorée) ---
        HEATMAP = [
            5,  8, 12,  8,  5,
            8, 15, 22, 15,  8,
            12, 22, 30, 22, 12,
            8, 15, 22, 15,  8,
            5,  8, 12,  8,  5
        ]
        for p in player_pos:
            score += HEATMAP[p]
        for o in opp_pos:
            score -= HEATMAP[o]

        # --- 2) GROUPING (adjacency improved) ---
        # Encourage IA à REGROUPER ses pions
        # Pénalise adversaire groupé : équivalent défensif
        def neighbors(i):
            x, y = i % 5, i // 5
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    if dx==0 and dy==0: continue
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < 5 and 0 <= ny < 5:
                        yield ny*5 + nx
        
        group_bonus = 0
        for p in player_pos:
            for nb in neighbors(p):
                if nb in player_pos:
                    group_bonus += 12   # bonus plus fort qu’avant
        score += group_bonus

        group_penalty = 0
        for o in opp_pos:
            for nb in neighbors(o):
                if nb in opp_pos:
                    group_penalty += 10  # défense (un peu moins fort)
        score -= group_penalty

        # --- 3) ALIGNEMENTS / PATTERNS (attaque + défense) ---
        # Très important pour Teeko
        for pattern in self.winning_patterns:
            pcount = sum(1 for pos in pattern if pos in player_pos)
            ocount = sum(1 for pos in pattern if pos in opp_pos)
            empty = 4 - pcount - ocount

            # Si j'ai 3 + 1 vide -> énorme chance de gagner
            if pcount == 3 and empty == 1:
                score += 350

            # Si l'adversaire a 3 + 1 vide -> gros danger
            if ocount == 3 and empty == 1:
                score -= 420

            # Alignement partiel (positif)
            if pcount == 2 and empty == 2:
                score += 35
            if ocount == 2 and empty == 2:
                score -= 45

        # --- 4) THREATS (ta fonction existante, on l'utilise !) ---
        score += self.score_threats(state, player)

        # --- 5) MOBILITY (faible mais utile en phase shift) ---
        if len(player_pos) == 4:
            my_moves = len(self.m.get_legal_moves(state, player))
            op_moves = len(self.m.get_legal_moves(state, opponent))
            score += (my_moves - op_moves) * 2

        return score
    
    def score_threats(self,state,player):
        player_pos = set(self.m.get_player_positions(state, player))
        opp_pos = set(self.m.get_player_positions(state, switch_player(player)))

        score = 0

        for pattern in self.winning_patterns:

            # Compter les pions de chaque joueur dans ce pattern
            player_count = sum(1 for pos in pattern if pos in player_pos)
            opp_count = sum(1 for pos in pattern if pos in opp_pos)

            
            # Menaces du joueur (attaque)
            if opp_count == 0:
                if player_count == 2:
                    score += 1
                elif player_count == 3:
                    score += 4

            # Menaces de l’adversaire (défense)
            if player_count == 0:
                if opp_count == 2:
                    score -= 2    # menace modérée
                elif opp_count == 3:
                    score -= 6    # menace forte 

        return score