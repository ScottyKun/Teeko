%index vers position
%coord(Index,X,Y)
coord(0,0,0).  coord(1,1,0).  coord(2,2,0).  coord(3,3,0).  coord(4,4,0).
coord(5,0,1).  coord(6,1,1).  coord(7,2,1).  coord(8,3,1).  coord(9,4,1).
coord(10,0,2). coord(11,1,2). coord(12,2,2). coord(13,3,2). coord(14,4,2).
coord(15,0,3). coord(16,1,3). coord(17,2,3). coord(18,3,3). coord(19,4,3).
coord(20,0,4). coord(21,1,4). coord(22,2,4). coord(23,3,4). coord(24,4,4).

%position vers index
index(X,Y,Index):-coord(Index,X,Y).

%verifie que pos est dans plateau
in_bounds(X,Y):-X>=0,X=<4,Y>=0,Y=<4.

%condition de deplacement de un pion
adjacent(I1,I2):-coord(I1,X1,Y1), coord(I2,X2,Y2), DX is abs(X1-X2), DY is abs(Y1-Y2), DX=<1, DY=<1, (DX+DY)>0.

%definition des joueurs(symbole)
player_symbol(b).
player_symbol(n).

%adversaire
opponent(b,n).
opponent(n,b).


%compte nb pions
count_pieces(State,Player,Count):-include(=(Player),State,Filtered),length(Filtered, Count),!.

%liste case vides (e)
empty_positions(State,Indices):-findall(I,nth0(I,State,e),Indices).

%positions occupees par un joueur
player_positions(State,Player,Indices):-findall(I,nth0(I,State,Player),Indices).

%phase de jeu
phase(State,placement):-count_pieces(State,b,CountB), count_pieces(State,n,CountN), Total is CountB+CountN, Total<8.

phase(State,deplacement):-count_pieces(State,b,CountB), count_pieces(State,n,CountN), Total is CountB+CountN, Total>=8.


%combinaisons gagnantes avec index
%winning_positions(List)
winning_positions([
    % Horizontales
    [0,1,2,3],   [1,2,3,4],
    [5,6,7,8],   [6,7,8,9],
    [10,11,12,13],[11,12,13,14],
    [15,16,17,18],[16,17,18,19],
    [20,21,22,23],[21,22,23,24],

    % Verticales
    [0,5,10,15], [5,10,15,20],
    [1,6,11,16], [6,11,16,21],
    [2,7,12,17], [7,12,17,22],
    [3,8,13,18], [8,13,18,23],
    [4,9,14,19], [9,14,19,24],

    % Diagonales
    [0,6,12,18], [6,12,18,24], [1, 7, 13, 19], [5, 11, 17, 23],
    [4,8,12,16], [8,12,16,20], [3, 7, 11, 15], [9, 13, 17, 21],

    % Carrés 2x2
    [0,1,5,6],   [1,2,6,7],   [2,3,7,8],   [3,4,8,9],
    [5,6,10,11], [6,7,11,12], [7,8,12,13], [8,9,13,14],
    [10,11,15,16], [11,12,16,17], [12,13,17,18], [13,14,18,19],
    [15,16,20,21], [16,17,21,22], [17,18,22,23], [18,19,23,24]
]).

%joueur est sur une position gagnante
all_positions_owned(State,Player,List):-forall(member(I,List),nth0(I,State,Player)).

%victoire deun joueur
win(State,Player):-winning_positions(All),member(L,All),all_positions_owned(State,Player,L),!.

%fin de partie
is_terminal(State):-win(State,b); win(State,n).

%renvoie le gagnant
game_over(State,b):-win(State,b),!.
game_over(State,n):-win(State,n),!.
game_over(_,none).


%verifier si on peut placer un pion
valid_placement(State,Player,Index):-phase(State,placement), nth0(Index,State,e).

%verifier deplacement de un pion
valid_shift(State,Player,From,To):-phase(State,deplacement),nth0(From, State, Player), nth0(To,State,e), adjacent(From,To).

%verifier coup valide(placement ou deplacement)
legal_move(State,Player,placement(Index)):-valid_placement(State,Player,Index).

legal_move(State,Player,shift(From,To)):-valid_shift(State,Player,From,To).

%lister tous les coups valides
legal_moves(State,Player,Moves):-findall(Move,legal_move(State,Player,Move),Moves).

%appliquer un coup et renvoie nouvel etat (on retire puis on place)
apply_move(State,Player,placement(Index),NewState):-nth0(Index,State,e,Temp), nth0(Index,NewState,Player,Temp).

apply_move(State,Player,shift(From,To),NewState):-replace(State,From,e,Temp), replace(Temp,To,Player,NewState).

replace([_|T],0,Elem,[Elem|T]).
replace([H|T],Index,Elem,[H|R]):-Index>0, Index1 is Index -1, replace(T,Index1, Elem, R).

%nouvel etat avec joueur
generate_new_state(State,Player,Move,NewState):-apply_move(State,Player,Move,NewState).