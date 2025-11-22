#on va essayer de rendre nos structures prolog friendly avec python et vice versa

import re
#conversion d'un etat
def list_to_state(list):
    return list.copy()

def state_to_list(state):
    return state.copy()

#manipulation des actions
#conversion d'un move prolog en coup python "placement(12)" -> ("placement", 12)//"shift(3,7)" -> ("shift", 3, 7)
def move_to_python(move_str):
    # Extraction du nom de functor et des arguments
    match = re.match(r"(\w+)\((.*?)\)", move_str)
    if not match:
        raise ValueError(f"Format de coup Prolog invalide : {move_str}")

    functor = match.group(1)
    raw_args = match.group(2)

    # si pas d'arguments
    if raw_args.strip() == "":
        return (functor,)

    # convertir chaque argument en int
    args = [int(x.strip()) for x in raw_args.split(",")]

    return (functor, *args)


#coup python en un dict pour les algos
def python_to_move_tuple(m):
    # Si c'est déjà un tuple : OK
    if isinstance(m, tuple):
        return m

    # Si c'est un dict : convertir proprement
    if isinstance(m, dict):
        if m.get("type") == "placement":
            return ("placement", m["index"])
        if m.get("type") == "shift":
            return ("shift", m["from"], m["to"])
    
    raise ValueError("Format de move inconnu: " + str(m))
    
#conversion liste imbriquee prolog en liste python
def flatten(results):
    flat = []
    for r in results:
        if isinstance(r, list):
            flat.extend(r)
        else:
            flat.append(r)
    return flat

#copie profonde d'un etat
def deep_copy_state(state):
    return [x for x in state]

#changement de joueur
def switch_player(player):
    return 'n' if player == 'b' else 'b'

#debug
def debug_state(state):
    for i in range(0, 25, 5):
        print(state[i:i+5])
    print()

def python_list_to_prolog(lst):
    # Convertir chaque élément en Prolog (b, n, e)
    prolog_elems = [str(x).strip() for x in lst]
    # Joindre avec des virgules et entourer de []
    return "[" + ",".join(prolog_elems) + "]"
