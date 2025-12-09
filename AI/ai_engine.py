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

from AI.minmax_alphabeta import MinMaxAlphaBeta

class AIEngine:
    def __init__(self, prolog_file="teeko_rules.pl", difficulty=None, mode=None):
        # Manager pour communiquer avec Prolog
        self.manager = PrologManager(prolog_file)

        # Fonction d'évaluation
        self.evaluator = Evaluation(self.manager)

        # Mode de jeu (PvsP, PvsIA, IAvsIA)
        self.mode = mode

        # Définition des paramètres selon difficulté
        self.difficulty = difficulty
        self.difficulty_params = self.get_difficulty_params(difficulty)

        # Algorithme MinMax
        self.minmax = MinMaxAlphaBeta(
            manager=self.manager,
            evaluator=self.evaluator,
            engine=self,
            max_depth=self.difficulty_params["max_depth"],
            time_limit=self.difficulty_params["placement_time"],
            mode=self.mode  
        )

    def get_best_move(self,state,player):
        phase = self.get_phase(state)
        self.set_time_limit(phase)

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
        if move[0] == "shift":
            src, dst = move[1], move[2]
            new_state[src] = 'e'
            new_state[dst] = player
            return new_state

        return new_state
    
    # Paramètres selon difficulté
    def get_difficulty_params(self, difficulty):
        if difficulty == "Débutant":
            return {"max_depth": 3, "placement_time": 2.0, "shift_time": 5.0}
        elif difficulty == "Intermediaire":
            return {"max_depth": 4, "placement_time": 2.5, "shift_time": 6.5}
        elif difficulty == "Expert":
            return {"max_depth": 5, "placement_time": 3.0, "shift_time": 7.5}
        else:
            return {"max_depth": 3, "placement_time": 2.5, "shift_time": 5.0}

    # Ajuste le temps limite selon la phase
    def set_time_limit(self, phase):
        if phase == "placement":
            self.minmax.time_limit = self.difficulty_params["placement_time"]
        else:
            self.minmax.time_limit = self.difficulty_params["shift_time"]
    
    

"""
#test de AIEngine

if __name__ == "__main__":
    prolog_manager = PrologManager("teeko_rules.pl")
    evaluator = Evaluation(prolog_manager)
    engine=AIEngine()
    ai = MinMaxAlphaBeta(prolog_manager, evaluator, engine, max_depth=3)

    # État initial vide
    initial_state = [
        'e','e','e','e','e',
        'e','b','n','n','e',
        'e','b','b','e','e',
        'e','n','b','n','e',
        'e','e','e','e','e'
    ]
    player = 'b'


    score, move = ai.compute(initial_state, player)

    print(f"Meilleur score: {score}, Meilleur coup: {move}")
"""