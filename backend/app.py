import os
from flask import Flask, render_template, jsonify, request # type: ignore
from flask_cors import CORS # type: ignore

from backend import config
from backend.game_logic.game import GameState

from backend.reinforcement_learning.agent import MLAgent


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
rl_agent = MLAgent()

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
    if request.method == 'POST':
        data = request.get_json()
        mode = data.get('mode', 'Human Player')
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

if __name__ == '__main__':
    print("Starting Flask development server...")
    print(f"Visit the GUI in your browser: http://127.0.0.1:5000/")
    app.run(debug=True)