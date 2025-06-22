from backend import config
import random
import logging

game_logger = logging.getLogger('gamelogic')

def discretize_state(game_state):
    """Returns a tuple containing the state of the game"""
    ball_x_bin = int(game_state.ball_x_grid // 2)
    ball_y_bin = int(game_state.ball_y_grid // 2)
    paddle_x_bin = int(game_state.paddle_x_grid // 2)

    ball_dx_sign = 1 if game_state.ball_dx_grid > 0 else -1
    ball_dy_sign = 1 if game_state.ball_dy_grid > 0 else -1

    return (ball_x_bin, ball_y_bin, paddle_x_bin, ball_dx_sign, ball_dy_sign)

def choose_action_epsilon_greedy(q_table, state, possible_actions):
    """Chooses an action based on the epsilon-greedy policy."""
    if random.uniform(0, 1) < config.EPSILON: # Explore
        return random.choice(possible_actions) 
    else: # Exploit
        q_values = {action: q_table.get((state, action), 0.0) for action in possible_actions}
        max_q = max(q_values.values())
        best_actions = [action for action, q in q_values.items() if q == max_q]
        return random.choice(best_actions)
    
def count_state_action_pairs():
    """Computing the amount of possible (state, action) pairs."""
    ball_x_bins = (config.GRID_WIDTH // 2) + 1
    ball_y_bins = (config.GRID_HEIGHT // 2) + 1
    paddle_x_bins = ((config.GRID_WIDTH - config.PADDLE_WIDTH_GRID) // 2) + 1
    ball_dx_signs = 2 
    ball_dy_signs = 2  
    num_actions = 3   

    num_states = ball_x_bins * ball_y_bins * paddle_x_bins * ball_dx_signs * ball_dy_signs
    num_state_action_pairs = num_states * num_actions

    game_logger.info(f"Possible states: {num_states}")
    game_logger.info(f"Possible (state, action) pairs: {num_state_action_pairs}")
    return num_state_action_pairs