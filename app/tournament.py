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
        self.match_count = self.player_count - 1
        self.is_four_player = is_four_player
        self.matches = []
        self.unassigned_players: list[str] = []
        self.winner: str = None
        self.gamestate = gamestate
        print("Tournament created with {} players".format(self.player_count))

    def get_match_count(self):
        return self.match_count

    def get_match(self, index: int):
        if index < 0 or index >= len(self.matches):
            return None
        return self.matches[index]

    def start_tournament(self):
        if self.player_count < 2:
            print("Not enough players to create a tournament (minimum 2 players)")
            return
        if not self.is_four_player:
            self._create_two_player_tournament()
        else:
            pass  # TODO: Implement four player tournament

    def _create_two_player_tournament(self):
        players = self.players
        shuffle(players)
        first_round_match_count = self.player_count // 2

        for _ in range(self.match_count):
            self.matches.append(Match())

        for i in range(first_round_match_count):
            offset = i * 2
            match = self.matches[i]
            match.players.append(players[offset])
            match.players.append(players[offset + 1])

    def assign_player_positions(self, gs: "GameState", match_index: int):
        """Assigns players to a match based on the match index in the gamestate"""
        required_player_count = 4 if self.is_four_player else 2
        if match_index < 0 or match_index >= len(self.matches):
            print("Invalid match index")
            return
        match = self.matches[match_index]
        if len(match.players) != required_player_count:
            print("Match has invalid number of players")
            return
        gs.players[match.players[0]] = gs.left
        gs.players[match.players[1]] = gs.right
        if required_player_count == 4:
            gs.players[match.players[2]] = gs.top
            gs.players[match.players[3]] = gs.bottom

    def set_match_winner(self, match_index: int, winner: str):
        if match_index < 0 or match_index >= len(self.matches):
            print("Invalid match index")
            return
        if winner not in self.matches[match_index].players:
            print("Invalid winner for match")
            return
        if self.matches[match_index].winner is not None:
            print("Match already has a winner")
            return
        self.matches[match_index].winner = winner
        self.unassigned_players.append(winner)
        self._assign_future_matches(match_index)

    def _assign_future_matches(self, match_index: int):
        required_player_count = 4 if self.is_four_player else 2
        if match_index < 0 or match_index >= self.match_count:
            print("Invalid match index")
            return
        if match_index == self.match_count - 1:
            self.winner = self.unassigned_players.pop()
            print("Winner of the tournament is {}".format(self.winner))
            return
        if len(self.unassigned_players) < 1:
            print("No players to assign, this should not happen!")
            return
        for i in range(match_index + 1, self.match_count):
            match = self.matches[i]
            if len(match.players) < required_player_count:
                match.players.append(self.unassigned_players.pop())
                return
        print("No matches to assign players to")
