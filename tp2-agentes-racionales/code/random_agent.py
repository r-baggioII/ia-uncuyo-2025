import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_agent import BaseAgent

class AlfredAgent(BaseAgent):
    def __init__(self, server_url="http://localhost:5000", **kwargs):
        super().__init__(server_url, "AlfredAgent", **kwargs)
        self.action_map = {
            0: self.up,
            1: self.down,
            2: self.left,
            3: self.right,
        }

    def get_strategy_description(self):
        # Updated description reflecting the new logic
        return "If a spot is dirty, there's a 50% chance I'll clean it. Otherwise, I'll move randomly."

    def _move_randomly(self):
        """Helper method to choose and perform a random move."""
        random_key = random.randint(0, 3)
        action_to_perform = self.action_map[random_key]
        return action_to_perform()

    def think(self):
        if not self.is_connected():
            return False

        perception = self.get_perception()
        if not perception or perception.get('is_finished', True):
            return False

        # --- Updated Logic ---
        if perception.get('is_dirty', False):
            # The spot is dirty. Let's make a choice: 0 for clean, 1 for move.
            choice = random.randint(0, 1)

            if choice == 0:
                # We chose to clean.
                return self.suck()
            else:
                # We chose to ignore the dirt and move instead.
                return self._move_randomly()
        else:
            # The spot is already clean, so we just move.
            return self._move_randomly()