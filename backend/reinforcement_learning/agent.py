from backend.game_logic.game import GameState
from backend import config
from backend.reinforcement_learning.setup import discretize_state, choose_action_epsilon_greedy
import random
import numpy as np
import pickle
import os
import logging

rl_agent_logger = logging.getLogger('rlagent')

class RLAgent:
    """Implements the Monte Carlo Control with Exploring Starts algorithm."""
    def __init__(self):
        self.q_table = {}  # Q(s, a) values = action-value function
        self.returns = {} # Reward sum for each (s,a)
        self.policy = {} # Policy for each state s
        self.possible_actions = [-1, 0, 1] # Paddle movement
        rl_agent_logger.info("RLAgent instance created.")

        self.episode_rewards = [] # List to store total reward per episode (will store final reward)
        self.q_value_changes = [] # List to store magnitude of Q-value changes
        self.policy_changes_count = [] # List to store how many policy entries changed per episode
        self.unique_states_visited = set() # To track unique states visited across episodes
        self.unique_state_action_pairs_visited = set() # To track unique (s,a) pairs visited

    def train_episode(self):
        """Runs a single episode of the game for training."""
        rl_agent_logger.info("Training agent on single episode")
        start_state = self.random_start_state()
        start_action = random.choice(self.possible_actions)
        game_state = GameState()
        game_state.from_state(start_state)
        episode_history = []
        final_episode_reward = 0

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
        
        if episode_history: 
            final_episode_reward = episode_history[-1][2] # Reward from the last (state, action, reward) tuple

        self.episode_rewards.append(final_episode_reward)

        G = 0
        visited = set()
        current_episode_policy_changes = 0

        for t in reversed(range(len(episode_history))):
            state, action, reward = episode_history[t]
            G = config.DISCOUNT_FACTOR * G + reward
            self.unique_states_visited.add(state)
            self.unique_state_action_pairs_visited.add((state, action))
            if (state, action) not in visited:
                visited.add((state, action))
                if (state, action) not in self.returns:
                    self.returns[(state, action)] = []
                self.returns[(state, action)].append(G)
                self.q_table[(state, action)] = int(np.mean(self.returns[(state, action)]))

                q_values = [self.q_table.get((state, action), 0.0) for action in self.possible_actions]
                best_action = self.possible_actions[np.argmax(q_values)]
                old_policy_action = self.policy.get(state)
                if old_policy_action is None or old_policy_action != best_action:
                    self.policy[state] = best_action
                    current_episode_policy_changes += 1 
        self.policy_changes_count.append(current_episode_policy_changes)
        rl_agent_logger.info(f"Episode finished. Final Game Reward: {final_episode_reward}, Policy Changes: {current_episode_policy_changes}")
        rl_agent_logger.info(f"Total Unique States Visited: {len(self.unique_states_visited)}, Total Unique State-Action Pairs: {len(self.unique_state_action_pairs_visited)}")
        

    def choose_action(self, game_state):
        """Picks an optimal action based on the provided game state (breaks ties randomly)."""
        discrete_state = discretize_state(game_state)
        rl_agent_logger.info(f"Choosing best action based on policy: {self.policy}")
        if discrete_state in self.policy:
            return self.policy[discrete_state]

        rl_agent_logger.warning(f"Inference: State {discrete_state} not found in policy. Falling back to Q-table/random.")
        q_values = {action: self.q_table.get((discrete_state, action), 0.0) for action in self.possible_actions}
        if not q_values:
            rl_agent_logger.warning("No optimal values found, gonna play randomly")
            return random.choice(self.possible_actions)

        max_q = max(q_values.values())
        best_actions = [action for action, q in q_values.items() if q == max_q]
        action = random.choice(best_actions)
        rl_agent_logger.info(f"Inference: State={discrete_state}, Action={action})")
        return action

    def random_start_state(self):
        """Returns a random start state (ball motion angle) for exploring starts."""
        state = {
            'ball_x_grid': config.GRID_WIDTH // 2,
            'ball_y_grid': config.GRID_HEIGHT // 2,
            'paddle_x_grid': (config.GRID_WIDTH // 2) - (config.PADDLE_WIDTH_GRID // 2),
            'ball_dx_grid': random.choice(config.INITIAL_DX_CHOICES),
            'ball_dy_grid': config.BALL_INITIAL_DY_GRID
        }
        rl_agent_logger.debug(f"Generated random start state: {state}")
        return state

    def save(self, grid_dimension, directory="backend/reinforcement_learning/saved"):
        """
        Saves the agent's learned parameters to a file.
        """
        grid_width, grid_height = grid_dimension
        save_dir = os.path.join(directory, f"W{grid_width}_H{grid_height}")
        filename = os.path.join(save_dir, "rl_agent.pkl")

        if os.path.exists(filename):
            rl_agent_logger.info(f"Agent already exists at {filename}, skipping save.")
            return

        os.makedirs(save_dir, exist_ok=True)
        agent_data = {
            'q_table': self.q_table,
            'policy': self.policy,
            'returns': self.returns,
            'game_dimensions': {'width': grid_width, 'height': grid_height},
        }
        try:
            with open(filename, 'wb') as f:
                pickle.dump(agent_data, f)
            rl_agent_logger.info(f"Agent successfully saved to {filename}")
        except Exception as e:
            rl_agent_logger.error(f"Error saving agent to {filename}: {e}", exc_info=True)

    @classmethod
    def load_agent(cls, grid_dimension, directory="backend/reinforcement_learning/saved"):
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
            loaded_agent.policy = agent_data.get('policy', {})
            loaded_agent.returns = agent_data.get('returns', {})
            
            rl_agent_logger.info(f"Agent successfully loaded from {filename}")
            return loaded_agent

        except FileNotFoundError:
            rl_agent_logger.error(f"File '{filename}' not found. Returning a new, untrained agent.")
            return cls()

        except Exception as e:
            rl_agent_logger.error(f"Error loading agent from {filename}: {e}. Returning a new, untrained agent.")
            return cls()