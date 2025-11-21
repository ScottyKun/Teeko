#Appels prolog pour simplifier la communication avec IA et GUI
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from pyswip import Prolog, Functor, Variable, Query, Atom
from PrologRules.ia_helper import move_to_python,python_list_to_prolog

class PrologManager:
    def __init__(self, prolog_file="teeko_rules.pl"):
        self.prolog = Prolog()
        print(f"[PrologManager] Chargement de {prolog_file} ...")

        path = os.path.join("PrologRules", "teeko_rules.pl")
        self.prolog.consult(path)
        
        print("[PrologManager] OK")

    
    #phase de jeu (placement ou deplacement)
    def get_phase(self, state):
        state = python_list_to_prolog(state)

        query = f"phase({state}, Phase)"
        res = list(self.prolog.query(query))

        if res:
            return res[0]["Phase"]

        return None
    
    #coups valides
    def get_legal_moves(self, state, player):
        result = []

        state = python_list_to_prolog(state)

        if(player=='b'):
            query_str = f"legal_moves({state}, b, Moves)"
        else:
            query_str = f"legal_moves({state}, n, Moves)"


        solutions = list(self.prolog.query(f"{query_str}"))
        
        for sol in solutions:
            moves = sol["Moves"]
           
            try:
                for m in moves:
                    result.append(move_to_python(m))
            except TypeError:
                result.append(move_to_python(moves))

        return result


    #appliquer un coup (retourne le nouvel etat avec un move en python)
    def apply_move(self, state, player, move):
        state = python_list_to_prolog(state)

        # convertir le move Python en Prolog
        if move[0] == "placement":
            move_term = f"placement({move[1]})"
        else:
            move_term = f"shift({move[1]}, {move[2]})"

        query = f"apply_move({state}, {player}, {move_term}, NewState)"

        res = list(self.prolog.query(query))
        if res:
            return res[0]["NewState"]

        return None
    
    #verifier fin de partie
    def is_terminal(self, state):
        state = python_list_to_prolog(state)
        res = list(self.prolog.query(f"is_terminal({state})"))
        return len(res) > 0
    
    #renvoie gagnant (b ou n ou none)
    def winner(self, state):
        state = python_list_to_prolog(state)
        res = list(self.prolog.query(f"game_over({state}, W)"))

        if res:
            return res[0]["W"]

        return None
    
    #nb pions du joueur
    def count_pieces(self, state, player):
        state = python_list_to_prolog(state)
        res = list(self.prolog.query(f"count_pieces({state}, {player}, N)"))

        if res:
            return int(res[0]["N"])

        return 0
    
    #index des pions
    def get_index(self, x, y):
        res = list(self.prolog.query(f"index({x}, {y}, I)"))

        if res:
            return int(res[0]["I"])

        return None
    
    #empty positions(indices)
    def get_empty_positions(self, state):
        state = python_list_to_prolog(state)
        res = list(self.prolog.query(f"empty_positions({state}, Pos)"))

        if res:
            return [int(x) for x in res[0]["Pos"]]

        return []

    
    #postions du joueur(indices)
    def get_player_positions(self, state, player):
        state = python_list_to_prolog(state)
        res = list(self.prolog.query(f"player_positions({state}, {player}, Pos)"))

        if res:
            return [int(x) for x in res[0]["Pos"]]

        return []
    
    #winning positions
    def get_winning_positions(self):
        res = list(self.prolog.query("winning_positions(Pos)"))

        if res:
            raw = res[0]["Pos"]
            return [[int(i) for i in combo] for combo in raw]

        return []
