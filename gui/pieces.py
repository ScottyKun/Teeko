#on definit notre pion par id de so joueur et sa position

class Piece:
    def __init__(self, position, player_id):
        self.position = position  # (x, y)
        self.player_id = player_id  # 1 ou 2