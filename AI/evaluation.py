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

        #positions centrales
        self.center_indices = {6, 7, 8, 11, 12, 13, 16, 17, 18}

        #heatmap
        self.heatmap= [
            1,  1,  2,  2, 3,
            2,  4,  6,  4, 2,
            2,  6, 10,  6, 2,
            2,  4,  6,  4, 2,
            1,  2,  2,  2, 1
        ]

        #positions gagnantes
        self.winning_patterns = self.m.get_winning_positions()
    
    def evaluate(self,state,player):

        #victoire
        if self.m.winner(state)==player:
            return 10000
        
        if self.m.winner(state)==switch_player(player):
            return -10000
        
        score=0

        #alignements
        score += self.score_alignements(state,player)*10

        #controle du centre
        score += self.score_center(state,player)*3

        #mobilite
        score += self.score_mobility(state,player)

        #menaces
        score += self.score_threats(state, player) * 25

        #carres potentiels
        score += self.score_square_potential(state, player) * 12

        #heatmap
        score += self.score_heatmap(state, player) * 4

        return score

    def score_alignements(self,state,player):
        #le score est base sur la proximite des pions

        positions=self.m.get_player_positions(state,player)
        if len(positions)<=1:
            return 0
        
        score=0
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                d = abs(positions[i] - positions[j])

                # voisins directs
                if d in (1, 5, 6, 4):
                    score += 3
                # voisins diagonaux un peu éloignés
                elif d in (2, 10):
                    score += 1

        return score
    
    def score_center(self,state,player):
        positions = self.m.get_player_positions(state, player)
        return sum(1 for pos in positions if pos in self.center_indices)
    
    def score_mobility(self, state, player):
        moves = self.m.get_legal_moves(state, player)
        return len(moves)
    
    def score_heatmap(self,state,player):
        positions = self.m.get_player_positions(state, player)
        return sum(self.heatmap[pos] for pos in positions)
    
    def score_square_potential(self,state,player):
        positions = set(self.m.get_player_positions(state, player))
        if len(positions) < 3:
            return 0

        score = 0

        # Liste des 9 carrés possibles sur un plateau 5x5
        squares = [
            [0, 1, 5, 6], [1, 2, 6, 7], [2, 3, 7, 8],
            [5, 6, 10,11],[6, 7, 11,12],[7, 8, 12,13],
            [10,11,15,16],[11,12,16,17],[12,13,17,18]
        ]

        for sq in squares:
            cnt = sum(1 for p in sq if p in positions)

            if cnt == 3:
                score += 6     
            elif cnt == 4:
                score += 25   

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