from pathlib import Path
import json

class GameStats :
    """ Track statistics for Alien Invasion. """
    
    def __init__(self, ai_game) :
        """ Initialize statistics. """
        self.settings = ai_game.settings
        self.reset_stats()
        
        # High score should never be reset
        path = Path("json_files/high_score.json")
        
        # Reads the json formated data from high_score.json into the variable 'self.high_score'
        contents = path.read_text()
        self.high_score = json.loads(contents)
    
    def reset_stats(self) :
        """ Initialize statistics that can change during the game. """
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1