# Teeko

> Implémentation Python du jeu Teeko — moteur, IA et intégration Prolog.

## Description

Ce dépôt contient une version de Teeko écrite en Python, conçue pour expérimenter des stratégies de jeu et des algorithmes d'intelligence artificielle. L'implémentation sépare clairement :

- la logique du plateau et des règles (`games/`),
- la couche IA (`AI/`) (Minimax / Alpha-Beta, évaluation),
- l'intégration Prolog pour la logique formelle et la génération/validation des coups (`PrologRules/`),
- l'interface utilisateur (GUI simple via `pygame`) dans `gui/`.

## Structure importante

- `main.py` : point d'entrée, initialise la fenêtre, le menu et crée l'instance `Game` avec les paramètres choisis.
- `config.py` : constantes globales (taille de fenêtre, couleurs, grille, etc.).
- `games/game.py` : classe `Game` — orchestration de la partie (entrées utilisateur, tour IA, interaction avec l'engine).
- `games/board.py` : classe `Board` — représentation du plateau côté Python, conversion vers/depuis l'état Prolog.
- `AI/ai_engine.py` : `AIEngine` — centralise la communication Prolog/IA, gère l'évaluation et le MinMax.
- `AI/minmax_alphabeta.py` et `AI/minmax.py` : algorithmes de recherche (Minimax, Alpha-Beta).
- `PrologRules/prolog_manager.py` : wrapper autour de `pyswip.Prolog` — appelle les règles Prolog (`teeko_rules.pl`).
- `PrologRules/teeko_rules.pl` : règles Prolog définissant les mouvements légaux, application des coups et conditions de victoire.

## Prérequis

- Python 3.8+
- Les dépendances principales se trouvent dans `requirements.txt` (ex. `pyswip` pour l'intégration Prolog, `pygame` pour la GUI).

## Installation (Windows / PowerShell)

1. Créez et activez un environnement virtuel :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Installez les dépendances :

```powershell
pip install -r requirements.txt
```

Remarque : pour `pyswip` vous devrez également avoir SWI-Prolog installé sur votre machine.

## Exécution

Lancer l'application depuis la racine du dépôt :

```powershell
python main.py
```

Le menu vous permet de choisir `mode` (PvsP, PvsIA, IAvsIA), la `difficulty` et les noms des joueurs : ces paramètres sont passés au constructeur de `Game` (voir section suivante).

## Détails techniques (composants clés)

Classe `Game` (`games/game.py`)
- Constructeur : `Game(surface, mode, difficulty, player1_name, player2_name)`
	- `surface` : surface `pygame` où dessiner.
	- `mode` : chaîne parmi `"PvsP"`, `"PvsIA"`, `"IAvsIA"`.
	- `difficulty` : chaîne indiquant la difficulté (influence les paramètres de l'IA).
	- `player1_name`, `player2_name` : noms affichés dans la bannière.
- Initialisation : crée un `Board`, une `Banner` et une `AIEngine` (avec la difficulté et le mode).
- Gestion des tours :
	- `handle_click(pos)` : gère les clics souris côté humain. Convertit la position pixel en coordonnée logique via `Board.pixel_to_logical`, construit un move Python et demande à l'`AIEngine`/Prolog de le valider et d'appliquer (`validate_move`, `apply_move`). Si le nouvel état est retourné par Prolog, il met à jour le plateau via `Board.update_from_prolog_state`.
	- `ai_play()` : appelé pour le tour de l'IA ; récupère `get_best_move` depuis `AIEngine`, applique le move via `apply_move` et met à jour le plateau.
- Conversion joueur Python → Prolog : méthode `player_to_prolog(player)` qui renvoie `'n'` si `player==1` sinon `'b'`.
- Phase de jeu : la classe interroge `AIEngine.get_phase(state)` pour connaître `placement` ou `deplacement`.

Classe `Board` (`games/board.py`)
- Représente l'état local (côté GUI) : listes `player1_pieces`, `player2_pieces`, `occupied_positions`.
- Initialisation : construit la liste des points logiques (5x5), initialise un `PrologManager()` pour certaines requêtes directes.
- Conversion état Python → Prolog : `to_prolog_state()` retourne une liste de 25 éléments `['e','e',...,'n','b',...]` où `n`=joueur1, `b`=joueur2 et `e`=empty.
- Mise à jour depuis Prolog : `update_from_prolog_state(state)` vide les listes de pièces et reconstruit `Piece((r,c), owner)` pour chaque cellule non vide selon l'état renvoyé par Prolog.
- Placement et déplacements :
	- `place_piece(pos, current_player)` : place localement un pion si la position est libre et bascule la `phase` sur `deplacement` quand 8 pions ont été posés.
	- `pixel_to_logical(pos)` / `logical_to_pixel(pos)` : conversion entre coordonnées écran et grille logique.
- Rôle Prolog/Python pour le plateau : la logique (règles de validité, application de coups, détection de fin) est déléguée à Prolog via `PrologManager`. Python maintient la représentation graphique et appelle Prolog pour obtenir le nouvel état quand un coup est appliqué.

Classe `AIEngine` (`AI/ai_engine.py`)
- Rôle : point central entre la GUI, la logique Prolog et les algorithmes d'IA.
	- Initialise un `PrologManager` pour exécuter les requêtes Prolog.
	- Crée un `Evaluation` (fonction d'évaluation heuristique) et construit l'algorithme `MinMaxAlphaBeta` avec des paramètres dépendant de la `difficulty`.
	- Méthodes principales :
		- `get_best_move(state, player)` : demande au MinMax le meilleur coup pour `player`, renvoie un move Python convertible pour `Game`.
		- `validate_move(state, player, move)` : passe la validation à `PrologManager`.
		- `apply_move(state, player, move)` : délègue l'application du coup à Prolog et retourne le nouvel état si valide.
		- `get_phase(state)` et `get_winner(state)` : wrappers autour des requêtes Prolog correspondantes.
	- `simulate_move(...)` : utilitaire local pour simuler un coup (utile en recherche sans appeler Prolog).

Classe `PrologManager` (`PrologRules/prolog_manager.py`) — résumé
- Utilise `pyswip` pour charger `teeko_rules.pl` et exposer des fonctions :
	- `get_phase`, `get_legal_moves`, `apply_move`, `validate_move`, `is_terminal`, `winner`, etc.
- Conversion entre structures Python et termes Prolog (via `ia_helper`) :
	- Python envoie l'état du plateau sous forme de liste (`['e','n','b',...]`). `PrologManager` transforme cette liste en terme Prolog attendu et effectue les requêtes.
	- Pour appliquer un coup, `AIEngine` ou `Game` crée un tuple Python (`('placement', index)` ou `('shift', src, dst)`), `PrologManager.apply_move` transforme ce tuple en terme Prolog (`placement(Index)` / `shift(From,To)`) et exécute `apply_move(State, Player, Move, NewState)` dans Prolog.

Fichier `main.py`
- Initialise `pygame`, crée la fenêtre et le `Menu`.
- Le menu renvoie un `dict` d'options lorsque l'utilisateur lance une partie : `{"mode":..., "difficulty":..., "player1_name":..., "player2_name":...}` — ces paramètres sont passés au constructeur de `Game`.
- Boucle principale :
	- Écoute les événements `MOUSEBUTTONDOWN` pour transmettre les clics à `Game.handle_click`.
	- Gère un timer (`pygame.USEREVENT+1`) pour exécuter `Game.ai_play()` lorsque l'IA doit jouer (petit délai visuel entre coups).

## Fichiers les plus importants (vue rapide)
- `main.py` — bootstrap / boucle principale.
- `games/game.py` — logique de partie, gestion des tours et conversion des entrées.
- `games/board.py` — état du plateau côté GUI, conversion vers/depuis Prolog.
- `AI/ai_engine.py` — interface IA ↔ Prolog, gestion des paramètres de recherche.
- `AI/minmax_alphabeta.py` — moteur de recherche principal (MinMax + alpha-beta, limites de profondeur/temps).
- `PrologRules/prolog_manager.py` — wrapper Prolog, point d'appel pour règles et validation.
- `PrologRules/teeko_rules.pl` — règles formelles du jeu (mouvements, application, victoire).

## requirements.txt
Les dépendances minimales (exemple) sont listées dans `requirements.txt`. Installez-les avec `pip install -r requirements.txt`.

## Licence

Ce projet est distribué sous licence MIT. Le fichier `LICENSE` à la racine contient le texte complet.

---

## Schéma de déroulement d'une partie

Cette section décrit, pas à pas, comment une partie se déroule au niveau des fichiers et fonctions principales, le format des moves, la validation et l'application des coups pour les trois modes de jeu.

Format des états et des moves
- État du plateau : une liste Python de 25 éléments (indices 0..24) où chaque cellule vaut `'e'` (empty), `'n'` (joueur 1) ou `'b'` (joueur 2). `Board.to_prolog_state()` produit cet état.
- Mapping index <-> coordonnées : l'index est calculé par `index = row * 5 + col` (0-based). Les fonctions de conversion dans `Board` sont `pixel_to_logical(pos)` et `logical_to_pixel(pos)`. Attention aux conventions de tuple `(row, col)` vs `(col, row)` — le code appelle `coords_to_index(row, col)` pour obtenir l'index.
- Format d'un move Python :
	- Placement : `('placement', index)` (index en 0..24)
	- Déplacement (shift) : `('shift', src_index, dst_index)`

Validation et application (rôle des fichiers)
- `games/game.py` : orchestre la partie, récupère les entrées utilisateur (clics) et déclenche l'IA via timer.
- `games/board.py` : représente l'état côté GUI, conversions pixel/logique et méthodes d'affichage. Met à jour l'état local via `update_from_prolog_state(new_state)` après application d'un coup.
- `AI/ai_engine.py` : point central pour l'IA ; possède les méthodes `validate_move(state, player, move)`, `apply_move(state, player, move)`, `get_phase(state)` et `get_best_move(state, player)`.
- `PrologRules/prolog_manager.py` : wrapper autour de `pyswip.Prolog`. Transforme états/moves Python en termes Prolog et exécute les prédicats Prolog :
	- Validation : `valid_placement/3` et `valid_shift/4` (appelées via `validate_move`).
	- Application : `apply_move(State, Player, Move, NewState)` (renvoie `NewState`).
	- Phase / winner / legal moves : `phase/2`, `game_over/2`, `legal_moves/3`, etc.

Flux général (toutes phases)
1. L'état courant est obtenu via `Board.to_prolog_state()` (liste de 25 éléments).
2. Lorsqu'un joueur humain clique, `Game.handle_click(pos)` :
	 - conversion pixel → logique (`Board.pixel_to_logical`), calcul de l'index (`coords_to_index`), construction du move Python (`('placement', index)` ou `('shift', frm, to')`).
	 - validation via `AIEngine.validate_move(state, prolog_player, move)` → appelle `PrologManager.validate_move` qui exécute le prédicat Prolog approprié.
	 - si valide : application via `AIEngine.apply_move` → `PrologManager.apply_move` qui exécute `apply_move(...)` dans Prolog et retourne `NewState` (structure Prolog convertie en liste Python par `pyswip`).
	 - mise à jour côté GUI via `Board.update_from_prolog_state(new_state)`.
	 - vérification du gagnant via `AIEngine.get_winner(state)` (wrapper Prolog).

3. Lorsqu'une IA joue :
	 - `Game` appelle `AIEngine.get_best_move(state, prolog_player)` (souvent depuis `Game.ai_play()` déclenchée par un timer). Cette méthode :
		 - récupère la phase (`get_phase`), règle les limites de temps/profondeur,
		 - lance `MinMaxAlphaBeta.compute(state, player)` (algorithme MinMax/Alpha-Beta),
		 - convertit le résultat en tuple Python via `python_to_move_tuple`.
	 - le coup retourné est appliqué via `AIEngine.apply_move(...)` comme décrit ci‑dessus, puis le plateau est mis à jour.

Comportement par mode

PvsP (Joueur vs Joueur)
- Flux :
	1. `main.py` crée `Game` avec `mode='PvsP'`.
	2. Chaque clic déclenche `Game.handle_click`, validation et application via Prolog.
	3. Après application, `Game` bascule `current_player` et attend la saisie suivante.
- Particularités : pas d'appel à l'IA ; la logique Prolog est utilisée uniquement pour valider et appliquer les coups.

PvsIA (Joueur vs IA)
- Flux :
	1. Le joueur humain joue par clic → `Game.handle_click` → validation + application.
	2. Après le coup humain, `Game` met en place un timer (`pygame.time.set_timer(pygame.USEREVENT+1, 300)`) pour laisser un court délai visuel.
	3. Quand le timer se déclenche, `Game.ai_play()` est appelé : il invoque `AIEngine.get_best_move`, applique le move via Prolog et met à jour le plateau.
	4. Le tour revient au joueur humain, et ainsi de suite.
- Particularités : l'IA décide de son coup via le moteur `MinMaxAlphaBeta`, mais la validation et l'application restent centralisées dans Prolog (via `PrologManager`).

IAvsIA (IA vs IA)
- Flux :
	1. `Game` est créé avec `mode='IAvsIA'` et dès l'initialisation un timer périodique est défini (`pygame.time.set_timer(pygame.USEREVENT+1, 300)`).
	2. À chaque événement timer, `Game.ai_play()` est appelé : l'IA courante calcule son meilleur coup (`AIEngine.get_best_move`) et l'applique via Prolog.
	3. Après application et mise à jour du plateau, `current_player` change et, si le nouveau joueur est aussi une IA, le timer est relancé pour le prochain coup.
- Particularités : utile pour tester les moteurs IA en mode autonome ; surveillez le temps alloué dans `AIEngine.get_difficulty_params` car les deux IA s'enchaînent rapidement.

Notes d'implémentation et points d'attention
- SWI-Prolog : `pyswip` transmet les structures Prolog en objets Python — `PrologManager` convertit ces objets en listes/entiers via `ia_helper`.
- Cohérence des coordonnées : le code emploie plusieurs fonctions de conversion (attention à l'ordre des tuples). Toujours utiliser `Board.pixel_to_logical` / `Board.logical_to_pixel` et `coords_to_index` pour obtenir l'index du coup.
- Tests & debugging : pour tracer un coup complet, inspectez :
	- l'état initial renvoyé par `Board.to_prolog_state()` ;
	- l'appel à `PrologManager.validate_move(...)` ;
	- l'appel à `PrologManager.apply_move(...)` et la valeur `NewState` renvoyée ;
	- la mise à jour par `Board.update_from_prolog_state(NewState)`.

*** Fin du schéma de déroulement ***


