from .game.game import GameState
from .game.game import Player
from random import shuffle
import logging

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
        self.players = []
        self.winner = None

# alive_players = await self.get_alive_players()
# alive_player_names = list(map(lambda player: player.name, alive_players))

class Tournament:
    logger = logging.getLogger(__name__)
    
    def __init__(self, gamestate: 'GameState', player_name_list, is_four_player):
        self.players = player_name_list
        self.player_count = len(player_name_list)
        self.match_count = self.player_count - 1
        self.is_four_player = is_four_player
        self.matches = []
        self.winner = None
        self.gamestate = gamestate
        self.logger.debug("Tournament created with {} players".format(self.player_count))

    def get_match_count(self):
        return self.match_count

    def get_match(self, index: int):
        if index < 0 or index >= len(self.matches):
            return None
        return self.matches[index]

    def start_tournament(self):
        if self.player_count < 2:
            self.logger.error("Not enough players to create a tournament (minimum 2 players)")
            return
        if not self.is_four_player:
            self._create_two_player_tournament()
        else:
            pass # TODO: Implement four player tournament
            
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

    def assign_players(self, gamestate: 'GameState', match_index: int):
        """Assigns players to a match based on the match index in the gamestate"""
        if not self.is_four_player:
            self._assign_two_player_match(gamestate, match_index)
        else:
            pass # TODO: Implement four player tournament match assignment
    
    def _assign_two_player_match(self, gs: 'GameState', match_index: int):
        if match_index < 0 or match_index >= len(self.matches):
            self.logger.error("Invalid match index")
            return
        match = self.matches[match_index]
        if len(match.players) == 2:
            gs.players[match.players[0]] = gs.left
            gs.players[match.players[1]] = gs.right
        else:
            self.logger.error("Match has invalid number of players")
        
    def set_match_winner(self, match_index: int, winner: 'Player'):
        if match_index < 0 or match_index >= len(self.matches):
            self.logger.error("Invalid match index")
            return
        if winner not in self.matches[match_index].players:
            self.logger.error("Invalid winner for match")
            return
        if self.matches[match_index].winner is not None:
            self.logger.error("Match already has a winner")
            return
        self.matches[match_index].winner = winner
            