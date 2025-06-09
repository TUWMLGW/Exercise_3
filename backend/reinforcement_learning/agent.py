from backend.game_logic.game import GameState
from backend import config
from backend.reinforcement_learning.setup import discretize_state, choose_action_epsilon_greedy
import random
import numpy as np
import pickle
import os

class RLAgent:
    """Implements the Monte Carlo Control with Exploring Starts algorithm."""
    def __init__(self):
        self.q_table = {}  # Q(s, a) values = action-value function
        self.returns = {} # Reward sum for each (s,a)
        self.returns_count = {} # Visit count for each (s,a)
        self.policies = {} # Policy for each state s
        self.possible_actions = [-1, 0, 1] # Paddle movement

    def train_episode(self):
        """Runs a single episode of the game for training."""
        start_state = self.random_start_state()
        start_action = random.choice(self.possible_actions)
        game_state = GameState()
        game_state.from_state(start_state)
        episode_history = []

        game_state.apply_action(start_action)
        discrete_state = discretize_state(game_state)
        reward = game_state.get_reward()
        episode_history.append((discrete_state, start_action, reward))
        game_state.update()

        while not game_state.game_over:
            discrete_state = discretize_state(game_state)
            action = choose_action_epsilon_greedy(self.q_table, discrete_state, self.possible_actions)
            game_state.apply_action(action)
            reward = game_state.get_reward()
            episode_history.append((discrete_state, action, reward))
            game_state.update()

        G = 0
        visited = set()
        for t in reversed(range(len(episode_history))):
            state, action, reward = episode_history[t]
            G = config.DISCOUNT_FACTOR * G + reward
            if (state, action) not in visited:
                visited.add((state, action))
                if (state, action) not in self.returns:
                    self.returns[(state, action)] = []
                self.returns[(state, action)].append(G)
                self.q_table[(state, action)] = np.mean(self.returns[(state, action)])

                q_values = [self.q_table.get((state, action), 0.0) for action in self.possible_actions]
                best_action = self.possible_actions[np.argmax(q_values)]
                self.policies[state] = best_action

    def choose_action(self, game_state):
        """Picks an optimal action based on the provided game state (breaks ties randomly)."""
        discrete_state = discretize_state(game_state)

        if discrete_state in self.policies:
            return self.policies[discrete_state]

        print("State not found")
        q_values = {action: self.q_table.get((discrete_state, action), 0.0) for action in self.possible_actions}
        if not q_values:
            print("No optimal values found, gonna play randomly")
            return random.choice(self.possible_actions)

        max_q = max(q_values.values())
        best_actions = [action for action, q in q_values.items() if q == max_q]
        return random.choice(best_actions)

    def random_start_state(self):
        """Returns a random start state (ball motion angle) for exploring starts."""
        state = {
            'ball_x_grid': config.GRID_WIDTH // 2,
            'ball_y_grid': config.GRID_HEIGHT // 2,
            'paddle_x_grid': (config.GRID_WIDTH // 2) - (config.PADDLE_WIDTH_GRID // 2),
            'ball_dx_grid': random.choice(config.INITIAL_DX_CHOICES),
            'ball_dy_grid': config.BALL_INITIAL_DY_GRID
        }

        return state

    def save(self, grid_dimension, directory="saved"):
        """
        Saves the agent's learned parameters to a file.
        """
        grid_width, grid_height = grid_dimension
        save_dir = os.path.join(directory, f"W{grid_width}_H{grid_height}")
        filename = os.path.join(save_dir, "rl_agent.pkl")

        if os.path.exists(filename):
            print(f"Agent already exists, skipping save.")
            return

        os.makedirs(save_dir, exist_ok=True)
        agent_data = {
            'q_table': self.q_table,
            'policies': self.policies,
            'returns': self.returns,
            'game_dimensions': {'width': grid_width, 'height': grid_height},
        }
        try:
            with open(filename, 'wb') as f:
                pickle.dump(agent_data, f)
            print(f"Agent successfully saved to {filename}")
        except Exception as e:
            print(f"Error saving agent to {filename}: {e}")

    @classmethod
    def load_agent(cls, grid_dimension, directory="saved"):
        """
        Loads an agent's learned parameters. 
        """
        grid_width, grid_height = grid_dimension
        save_dir = os.path.join(directory, f"W{grid_width}_H{grid_height}")
        filename = os.path.join(save_dir, "rl_agent.pkl")
        try:
            with open(filename, 'rb') as f:
                agent_data = pickle.load(f)
                
            loaded_agent = cls()

            loaded_agent.q_table = agent_data.get('q_table', {})
            loaded_agent.policies = agent_data.get('policies', {})
            loaded_agent.returns = agent_data.get('returns', {})
            
            print(f"Agent successfully loaded from {filename}")
            return loaded_agent

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found. Returning a new, untrained agent.")
            return cls()

        except Exception as e:
            print(f"Error loading agent from {filename}: {e}. Returning a new, untrained agent.")
            return cls()