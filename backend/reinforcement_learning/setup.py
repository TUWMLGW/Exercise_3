from backend import config
from backend.game_logic.game import GameState
import random

def discretize_state(game_state_object):
    """
    Converts a continuous game state into a discrete, hashable state for the RL agent.
    This is critical for Q-learning/Monte Carlo with a Q-table.

    Example (very simplified):
    - ball_x_bin = int(game_state_object.ball_x / (config.SCREEN_WIDTH / 10))
    - ball_y_bin = int(game_state_object.ball_y / (config.SCREEN_HEIGHT / 10))
    - paddle_x_bin = int(game_state_object.paddle_x / (config.SCREEN_WIDTH / 5))
    - ball_dx_sign = 1 if game_state_object.ball_dx > 0 else -1
    - ball_dy_sign = 1 if game_state_object.ball_dy > 0 else -1

    Returns a tuple, e.g., (ball_x_bin, ball_y_bin, paddle_x_bin, ball_dx_sign, ball_dy_sign)
    """
    # ... your discretization logic here ...
    pass

def choose_action_epsilon_greedy(q_table, state, possible_actions):
    """
    Chooses an action based on the epsilon-greedy policy.
    """
    if random.uniform(0, 1) < config.EPSILON:
        return random.choice(possible_actions) # Explore
    else:
        # Exploit: Choose action with highest Q-value for the current state
        # (You'll need to handle states not yet in Q-table)
        q_values = {action: q_table.get((state, action), 0.0) for action in possible_actions}
        max_q = max(q_values.values())
        best_actions = [action for action, q in q_values.items() if q == max_q]
        return random.choice(best_actions)