from .game.game import GameState
from .game.game import Player
from random import shuffle

# Create a tournament class that will create a tournament
# based on the number of players in the lobby
# and the number of players per match

# Inputs: GameState initially when creating object, and:
#   - Winner of each match after it is played (to be recorded in Tournament?)
# Outputs: Tournament initially on object creation, and:
#   - Number of matches to be played to determine the champion before the any matches are played
#   - Assign players to matches by modifying the GameState object before a match starts


class Match:
    def __init__(self):
        self.players: list[str] = []
        self.winner: Player = None


class Tournament:
    def __init__(self, gamestate: "GameState", player_name_list, is_four_player):
        self.players: list[str] = player_name_list
        self.player_count = len(player_name_list)
        self.match_count = None
        self.is_four_player: bool = is_four_player
        self.matches = []
        self.unassigned_players: list[str] = []
        self.winner: str = None
        self.gamestate = gamestate # <-- not used? t. Noel

    def get_match_count(self):
        if self.match_count is not None:
            return self.match_count
        if not self.is_four_player:
            self.match_count = self.player_count - 1
            return self.match_count
        # Code below calculates the number of matches required for a 4 player tournament
        # it is valid only for player counts that are powers of 4 (4, 16, 64, 256, etc.)
        total: int = 0
        rolling: int = self.player_count
        while rolling > 1:
            rolling = rolling // 4
            total += rolling
        self.match_count = total
        return self.match_count

    def get_match(self, index: int):
        if index < 0 or index >= len(self.matches):
            return None
        return self.matches[index]

    def start_tournament(self):
        required_player_count = 4 if self.is_four_player else 2
        if self.player_count < required_player_count:
            return
        players = self.players
        shuffle(players)
        first_round_match_count = self.player_count // required_player_count
        for _ in range(self.match_count):
            self.matches.append(Match())
        for i in range(first_round_match_count):
            offset = i * required_player_count
            match = self.matches[i]
            for n in range(required_player_count):
                match.players.append(players[offset + n])

    def assign_player_positions(self, gs: "GameState", match_index: int):
        """Assigns players in a match to their positions in the gamestate object"""
        required_player_count = 4 if self.is_four_player else 2
        if match_index < 0 or match_index >= len(self.matches):
            return
        match = self.matches[match_index]
        if len(match.players) != required_player_count:
            return
        gs.players[match.players[0]] = gs.left
        gs.players[match.players[1]] = gs.right
        if required_player_count == 4:
            gs.players[match.players[2]] = gs.top
            gs.players[match.players[3]] = gs.bottom

    def set_match_winner(self, match_index: int, winner: str):
        if match_index < 0 or match_index >= len(self.matches):
            return
        if winner not in self.matches[match_index].players:
            return
        if self.matches[match_index].winner is not None:
            return
        self.matches[match_index].winner = winner
        self.unassigned_players.append(winner)
        self._assign_future_matches(match_index)

    def _assign_future_matches(self, match_index: int):
        required_player_count = 4 if self.is_four_player else 2
        if match_index < 0 or match_index >= self.match_count:
            return
        if match_index == self.match_count - 1:
            self.winner = self.unassigned_players.pop()
            return
        if len(self.unassigned_players) < 1:
            return
        for i in range(match_index + 1, self.match_count):
            match = self.matches[i]
            if len(match.players) < required_player_count:
                match.players.append(self.unassigned_players.pop())
                return
