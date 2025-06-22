# --- Game Grid Dimensions ---
GRID_WIDTH = 15  # e.g., 15 units wide 
GRID_HEIGHT = 10 # e.g., 10 units high 

# --- UI Scaling Factor ---
# Pixels per abstract grid unit.
GRID_UNIT_SIZE = 40 # For 15x10 grid, 40 pixels/unit gives 600x400 screen

# -- BRICK LAYOUT ---
BRICK_WIDTH_GRID = 3 # Bricks are 3x1 
BRICK_HEIGHT_GRID = 1
NUM_BRICK_ROWS = 3 

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
# Ball speed varies by player mode
BALL_INITIAL_DX_GRID = 1
BALL_INITIAL_DY_GRID = 1
INITIAL_DX_CHOICES = [-2, -1, 0, 1, 2] 
BALL_SPEED_HUMAN_PLAYER = 0.1 
BALL_SPEED_AI_AGENT =  0.1

# Paddle speed changes by +1, -1, or 0 grid units per step
PADDLE_INITIAL_DX_GRID = 0

# --- Reinforcement Learning Hyperparameters ---
EPSILON = 0.1 
DISCOUNT_FACTOR = 0.99
NUM_EPISODES = 100