import os
from flask import Flask, render_template, jsonify # type: ignore
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
    Serves the main HTML page for the Breakout GUI.
    """
    return render_template('index.html')

@app.route('/game_state')
def get_game_state():
    """
    API endpoint to provide the current game state to the frontend.
    This endpoint will be called repeatedly by the JavaScript to update the visualization.
    """
    current_game_state.update()

    return jsonify(current_game_state.get_state_for_display())

if __name__ == '__main__':
    print("Starting Flask development server...")
    print(f"Visit the GUI in your browser: http://127.0.0.1:5000/")
    app.run(debug=True)