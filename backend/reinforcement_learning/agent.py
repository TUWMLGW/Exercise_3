from backend.game_logic.game import GameState
from backend import config
from backend.reinforcement_learning.setup import discretize_state, choose_action_epsilon_greedy
import random

class MLAgent:
    """Implements the Monte Carlo Control algorithm."""
    def __init__(self):
        self.q_table = {}  # Q(s, a) values
        self.returns_sum = {} # Sum of returns for each (s,a) pair
        self.returns_count = {} # Count of visits for each (s,a) pair
        self.possible_actions = [-1, 0, 1] # Paddle speed change: left, stay, right

    def train_episode(self):
        """Runs a single episode of the game for training."""
        game_state = GameState() # Initialize a new game
        episode_history = [] # Store (state, action, reward) tuples

        # You would run the game loop here:
        # while not game_state.is_game_over():
        #     discrete_state = discretize_state(game_state)
        #     action = choose_action_epsilon_greedy(self.q_table, discrete_state, self.possible_actions)
        #     game_state.apply_action(action) # Needs to be implemented in game.py
        #     reward = game_state.get_reward() # Needs to be implemented in game.py
        #     episode_history.append((discrete_state, action, reward))
        #     game_state.update() # Update ball/brick etc.

        # After episode ends (all bricks cleared or ball missed):
        # Calculate returns and update Q-table (Monte Carlo specific logic)
        # ... your Monte Carlo updates here ...

    def choose_action(self, game_state):
        """
        Picks an optimal action based on the provided game state (breaks ties randomly).
        """
        return 1
        discrete_state = discretize_state(game_state)
        # Choose greedy action (epsilon=0 for exploitation)
        # You'll need a non-exploratory version of choose_action_epsilon_greedy, or set epsilon=0
        q_values = {action: self.q_table.get((discrete_state, action), 0.0) for action in self.possible_actions}
        if not q_values: # Pick randomly
             return random.choice(self.possible_actions)
        max_q = max(q_values.values())
        best_actions = [action for action, q in q_values.items() if q == max_q]
        return random.choice(best_actions)