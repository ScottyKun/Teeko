"""
Fichier central de notre architecture. Il est responsable de la communication entre toutes les parties

"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from PrologRules.prolog_manager import PrologManager
from evaluation import Evaluation
from minmax import MinMax

class AIEngine:
    def __init__(self, prolog_file="teeko_rules.pl", max_depth=3):
        # Manager pour communiquer avec Prolog
        self.manager = PrologManager(prolog_file)

        # Fonction d'évaluation
        self.evaluator = Evaluation(self.manager)

        # Algorithme MinMax
        self.minmax = MinMax(self.manager, self.evaluator, max_depth)

    def get_best_move(self,state,player):
        score, move = self.minmax.compute(state, player)
        return move
    
if __name__ == "__main__":
    prolog_manager = PrologManager("teeko_rules.pl")
    evaluator = Evaluation(prolog_manager)
    ai = MinMax(prolog_manager, evaluator, max_depth=2)

    # État initial vide
    initial_state = ['e']*25
    player = 'b'


    score, move = ai.compute(initial_state, player)
    print(f"Meilleur score: {score}, Meilleur coup: {move}")