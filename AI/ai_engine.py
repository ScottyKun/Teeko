"""
Fichier central de notre architecture. Il est responsable de la communication entre toutes les parties

"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from PrologRules.prolog_manager import PrologManager
from PrologRules.ia_helper import python_to_move_tuple
from AI.evaluation import Evaluation
from AI.minmax import MinMax
from AI.minmax_op import MinMaxOp

class AIEngine:
    def __init__(self, prolog_file="teeko_rules.pl", max_depth=3):
        # Manager pour communiquer avec Prolog
        self.manager = PrologManager(prolog_file)

        # Fonction d'évaluation
        self.evaluator = Evaluation(self.manager)

        # Algorithme MinMax
        self.minmax = MinMaxOp(self.manager, self.evaluator,self, max_depth)

    def get_best_move(self,state,player):
        score, move = self.minmax.compute(state, player)
        if move:
            return python_to_move_tuple(move)
        return None

    #valide un coup
    def validate_move(self, state, player, move):
        return self.manager.validate_move(state,player,move)
        
    
    # Appliquer un coup et renvoyer le nouvel état
    def apply_move(self, state, player,move):
        new_state = self.manager.apply_move(state, player, move)
        return new_state

    # Obtenir la phase courante pour informer la GUI
    def get_phase(self, state):
        return self.manager.get_phase(state)
    
    #retourne winner
    def get_winner(self, state):
        return self.manager.winner(state)
    
    #simuler
    def simulate_move(self, state, player, move):
        new_state = list(state)

        # Si placement
        if move[0] == "placement":
            dst = move[1]
            new_state[dst] = player
            return new_state

        # Si déplacement
        if move[0] == "move":
            src, dst = move[1]
            new_state[src] = 'e'
            new_state[dst] = player
            return new_state

        return new_state


"""
#test de AIEngine

if __name__ == "__main__":
    prolog_manager = PrologManager("teeko_rules.pl")
    evaluator = Evaluation(prolog_manager)
    ai = MinMax(prolog_manager, evaluator, max_depth=2)

    # État initial vide
    initial_state = [
        'e','e','e','e','e',
        'e','b','b','n','e',
        'e','b','n','e','e',
        'e','e','n','n','e',
        'e','e','e','e','e'
    ]
    player = 'b'


    score, move = ai.compute(initial_state, player)
    print(f"Meilleur score: {score}, Meilleur coup: {move}")
"""