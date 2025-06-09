from backend import config
from backend.game_logic.game import GameState
import random

def discretize_state(game_state):
    """Returns a tuple containing the state of the game"""
    ball_x_bin = int(game_state.ball_x_grid)
    ball_y_bin = int(game_state.ball_y_grid)
    paddle_x_bin = int(game_state.paddle_x_grid)
    paddle_y_bin = int(config.GRID_HEIGHT - config.PADDLE_HEIGHT_GRID)

    ball_dx_sign = 1 if game_state.ball_dx_grid > 0 else -1
    ball_dy_sign = 1 if game_state.ball_dy_grid > 0 else -1

    return (ball_x_bin, ball_y_bin, paddle_x_bin, paddle_y_bin, ball_dx_sign, ball_dy_sign)

def choose_action_epsilon_greedy(q_table, state, possible_actions):
    """Chooses an action based on the epsilon-greedy policy."""
    if random.uniform(0, 1) < config.EPSILON: # Explore
        return random.choice(possible_actions) 
    else: # Exploit
        q_values = {action: q_table.get((state, action), 0.0) for action in possible_actions}
        max_q = max(q_values.values())
        best_actions = [action for action, q in q_values.items() if q == max_q]
        return random.choice(best_actions)