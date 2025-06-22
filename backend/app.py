import os
from flask import Flask, render_template, jsonify, request # type: ignore
from flask_cors import CORS # type: ignore
from tqdm import tqdm
import logging
import time
import csv
from flask import Response
import io
import matplotlib.pyplot as plt
from flask import send_file

from backend import config
from backend.game_logic.game import GameState
from backend.reinforcement_learning.agent import RLAgent
from backend.logging_config import setup_logging


# --- Flask App Initialization ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(basedir, '..', 'frontend', 'templates'),
    static_folder=os.path.join(basedir, '..', 'frontend', 'static')
)
CORS(app)
# --- App Logger ---
app_logger = logging.getLogger("app")

# --- Game Instance ---
current_game_state = GameState()
rl_agent = RLAgent()

# --- FLask Routes ---
@app.route('/')
def index():
    """Renders the HTML page."""
    app_logger.info("Accessing index page.")
    return render_template('index.html')

@app.route('/game_state', methods=['GET', 'POST'])
def get_game_state():
    """
    Provides current game state to the frontend and identifies game mode.
    This endpoint will be called repeatedly by the JavaScript to update the visualization.
    """
    global current_game_state
    global rl_agent
    if request.method == 'POST':
        data = request.get_json()
        mode = data.get('mode', 'Human Player')
        board_width = data.get('boardWidth')
        board_height = data.get('boardHeight')

        if board_width and board_height:
            if int(board_width) % config.BRICK_WIDTH_GRID != 0:
                app_logger.info(f"Board width {board_width} is not a multiple of {config.BRICK_WIDTH_GRID}.")
                return jsonify({
                    "error": f"Board width {board_width} must be a multiple of {config.BRICK_WIDTH_GRID}."
                }), 400
            if int(board_width) < config.PADDLE_WIDTH_GRID:
                app_logger.info(f"Board width {board_width} is less than {config.PADDLE_WIDTH_GRID}.")
                return jsonify({
                    "error": f"Board width {board_width} must be at least {config.PADDLE_WIDTH_GRID}."
                }), 400
            config.GRID_WIDTH = int(board_width)
            config.GRID_HEIGHT = int(board_height)
            current_game_state = GameState()

            save_dir = os.path.join("backend/reinforcement_learning/saved", f"W{config.GRID_WIDTH}_H{config.GRID_HEIGHT}")
            filename = os.path.join(save_dir, "rl_agent.pkl")
            grid_dimension = (config.GRID_WIDTH, config.GRID_HEIGHT)
            if os.path.exists(filename):
                rl_agent = RLAgent.load_agent(grid_dimension)
            else:
                rl_agent = RLAgent()

        current_game_state.mode = mode
        # AI Agent Mode
        if mode == 'AI Agent':
            if not rl_agent.policy:
                return jsonify({"error": "AI Agent is not trained for this board."}), 400
            action = rl_agent.choose_action(current_game_state)
            current_game_state.apply_action(action)
            app_logger.debug(f"AI Agent chose action: {action}")

        # Human Player Mode
        else:
            action = data.get('action', 0)
            current_game_state.apply_action(action)
            app_logger.debug(f"Human Player chose action: {action}")
        current_game_state.update()
        
        return jsonify(current_game_state.get_state_for_display())
    else:
        return jsonify(current_game_state.get_state_for_display())

@app.route('/reset_game', methods=['POST'])
def reset_game():
    """Resets the game"""
    global current_game_state
    current_game_state = GameState()
    app_logger.info(f"Game was reset successfully.")
    return jsonify({ 'status': 'reset' })

@app.route('/train_agent', methods=['POST'])
def train_agent():
    """Trains the RL Agent on the instantiated game"""
    data = request.get_json()
    board_width = data.get('boardWidth')
    board_height = data.get('boardHeight')
    app_logger.info(f"Training request received for dimensions: {board_width}x{board_height}.")

    config.GRID_WIDTH = board_width
    config.GRID_HEIGHT = board_height

    save_dir = os.path.join("backend/reinforcement_learning/saved", f"W{board_width}_H{board_height}")
    filename = os.path.join(save_dir, "rl_agent.pkl")
    grid_dimension = (board_width, board_height)
    global rl_agent
    if os.path.exists(filename):
        rl_agent = RLAgent.load_agent(grid_dimension)
        app_logger.info(f"Agent for {board_width}x{board_height} found on disk and successfully loaded for training. Agent's policy is as follows: {rl_agent.policy}")
    else:
        app_logger.info(f"No agent found for {board_width}x{board_height}. Creating a new one for training.")
        rl_agent = RLAgent()
        for episode in tqdm(range(config.NUM_EPISODES)):
            rl_agent.train_episode()
        rl_agent.save(grid_dimension)
        app_logger.info(f"Training completed and agent saved for {board_width}x{board_height} dimensions.")
        trajectory = rl_agent.record_trajectory()
        rl_agent.plot_trajectory(trajectory)
    return jsonify({'status': 'trained'})

@app.route('/download_trajectory', methods=['GET'])
def download_trajectory():
    """Downloads the a plot of the trajectory of the current game"""
    trajectory = current_game_state.get_trajectory()
    if not trajectory:
        return jsonify({'error': 'No trajectory data available.'}), 400
    
    ball_x = [entry['ball'][0] for entry in trajectory]
    ball_y = [entry['ball'][1] for entry in trajectory]
    paddle_x = [entry['paddle'] for entry in trajectory]
    steps = list(range(len(trajectory)))

    fig, axs = plt.subplots(2, 1, figsize=(10, 5))
    axs[0].plot(ball_x, ball_y, marker='o')
    axs[0].set_title("Ball Trajectory (Grid Units)")
    axs[0].set_xlabel("Ball X")
    axs[0].set_ylabel("Ball Y")
    axs[0].invert_yaxis()

    axs[1].plot(steps, paddle_x, marker='x')
    axs[1].set_title("Paddle X Position Over Time")
    axs[1].set_xlabel("Timestep")
    axs[1].set_ylabel("Paddle X")

    plt.tight_layout() 
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    plt.close(fig)
    img_bytes.seek(0)
    return send_file(img_bytes, mimetype='image/png', as_attachment=True, download_name='trajectory.png')

if __name__ == '__main__':
    setup_logging()
    app_logger.info("Starting Flask development server...")
    app_logger.info(f"Visit the GUI in your browser: http://127.0.0.1:5000/")
    app.run(debug=True)