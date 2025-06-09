import os
from flask import Flask, render_template, jsonify, request # type: ignore
from flask_cors import CORS # type: ignore
from tqdm import tqdm

from backend import config
from backend.game_logic.game import GameState

from backend.reinforcement_learning.agent import RLAgent


# --- Flask App Initialization ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(basedir, '..', 'frontend', 'templates'),
    static_folder=os.path.join(basedir, '..', 'frontend', 'static')
)
CORS(app)

# --- Game Instance ---
current_game_state = GameState()
rl_agent = RLAgent()

# --- FLask Routes ---
@app.route('/')
def index():
    """
    Renders the HTML page.
    """
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
                return jsonify({
                    "error": f"Board width {board_width} must be a multiple of {config.BRICK_WIDTH_GRID}."
                }), 400
            config.GRID_WIDTH = int(board_width)
            config.GRID_HEIGHT = int(board_height)
            current_game_state = GameState()

        current_game_state.mode = mode
        # AI Agent Mode
        if mode == 'AI Agent':
            action = rl_agent.choose_action(current_game_state)
            current_game_state.apply_action(action)
        # Human Player Mode
        else:
            action = data.get('action', 0)
            current_game_state.apply_action(action)

        current_game_state.update()
        
        return jsonify(current_game_state.get_state_for_display())
    else:
        return jsonify(current_game_state.get_state_for_display())

@app.route('/reset_game', methods=['POST'])
def reset_game():
    """Resets the game"""
    global current_game_state
    current_game_state = GameState()
    return jsonify({ 'status': 'reset' })

@app.route('/train_agent', methods=['POST'])
def train_agent():
    """Trains the RL Agent on the instantiated game"""
    data = request.get_json()
    board_width = data.get('boardWidth')
    board_height = data.get('boardHeight')
    print(board_width, board_height)

    save_dir = os.path.join("backend/reinforcement_learning/saved", f"W{board_width}_H{board_height}")
    filename = os.path.join(save_dir, "rl_agent.pkl")
    grid_dimension = (board_width, board_height)
    global rl_agent
    if os.path.exists(filename):
        rl_agent = RLAgent.load_agent(grid_dimension)
    else:
        rl_agent = RLAgent()
        for episode in tqdm(range(config.NUM_EPISODES)):
            rl_agent.train_episode()
        rl_agent.save(grid_dimension)
    return jsonify({'status': 'trained'})

if __name__ == '__main__':
    print("Starting Flask development server...")
    print(f"Visit the GUI in your browser: http://127.0.0.1:5000/")
    app.run(debug=True)