# --- Game Grid Dimensions ---
GRID_WIDTH = 15  # e.g., 15 units wide 
GRID_HEIGHT = 10 # e.g., 10 units high 

# --- UI Scaling Factor ---
# Pixels per abstract grid unit.
GRID_UNIT_SIZE = 40 # For 15x10 grid, 40 pixels/unit gives 600x400 screen

# --- GUI Screen Dimensions ---
SCREEN_WIDTH = GRID_WIDTH * GRID_UNIT_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_UNIT_SIZE

# -- BRICK LAYOUT ---
NUM_BRICKS_PER_ROW = 5
NUM_ROWS = 3 
BRICK_WIDTH_GRID = GRID_WIDTH // NUM_BRICKS_PER_ROW # Bricks are 3x1 
BRICK_HEIGHT_GRID = 1

# --- Element Dimensions (in GRID UNITS) ---
BALL_SIZE_GRID = 1 # Ball is 1x1
PADDLE_WIDTH_GRID = 5 # Paddle is 5x1 
PADDLE_HEIGHT_GRID = 1 # Paddle is 5x1 

# Derived element dimensions (in PIXELS) for frontend
BALL_RADIUS_PIXELS = BALL_SIZE_GRID * GRID_UNIT_SIZE // 2
PADDLE_WIDTH_PIXELS = PADDLE_WIDTH_GRID * GRID_UNIT_SIZE
PADDLE_HEIGHT_PIXELS = PADDLE_HEIGHT_GRID * GRID_UNIT_SIZE
BRICK_WIDTH_PIXELS = BRICK_WIDTH_GRID * GRID_UNIT_SIZE
BRICK_HEIGHT_PIXELS = BRICK_HEIGHT_GRID * GRID_UNIT_SIZE

# --- Movement Speeds (in GRID UNITS per step) ---
# Ball has constant speed of 1 in vertical direction and between -2 and 2 in horizontal direction
BALL_INITIAL_DX_GRID = 1
BALL_INITIAL_DY_GRID = 1 

# Paddle speed changes by +1, -1, or 0 grid units per step
PADDLE_MAX_SPEED_GRID = 2
PADDLE_INITIAL_DX_GRID = 0

# Initial speed for the *demo visualization brick*
# This is a separate moving element just for the initial demo, not a game brick.
BRICK_INITIAL_DX_GRID = 3

# --- Reinforcement Learning Hyperparameters ---
EPSILON = 0.1  # For epsilon-greedy policy
DISCOUNT_FACTOR = 0.99
LEARNING_RATE = 0.1 # Alpha for Q-value updates
NUM_EPISODES = 10000