import random
from backend import config

class GameState:
    def __init__(self):
        # Initialize positions in GRID UNITS
        self.ball_x_grid = config.GRID_WIDTH // 2
        self.ball_y_grid = config.GRID_HEIGHT // 2
        # Ball initial direction is chosen at random from specified choices
        initial_dx_choices = [-2, -1, 0, 1, 2] 
        self.ball_dx_grid = random.choice(initial_dx_choices)
        self.ball_dy_grid = config.BALL_INITIAL_DY_GRID # Constant speed of 1 in vertical 

        # Paddle
        self.paddle_x_grid = (config.GRID_WIDTH // 2) - (config.PADDLE_WIDTH_GRID // 2)
        self.paddle_dx_grid = config.PADDLE_INITIAL_DX_GRID

        # Bricks
        self.bricks = []
        for row in range(config.NUM_ROWS):
            for col in range(config.NUM_BRICKS_PER_ROW):
                brick = {
                    'x_grid': col * config.BRICK_WIDTH_GRID,
                    'y_grid': row * config.BRICK_HEIGHT_GRID,
                    'width_grid': config.BRICK_WIDTH_GRID,
                    'height_grid': config.BRICK_HEIGHT_GRID,
                    'was_hit': False,
                    'row': row,
                }
                self.bricks.append(brick)
        
    def update(self):
        """Updates the game state for one timestep, using GRID UNITS."""
        # Update Ball Position
        self.ball_x_grid += self.ball_dx_grid
        self.ball_y_grid += self.ball_dy_grid

        # Bouncing off walls
        if self.ball_x_grid < 0 or self.ball_x_grid + config.BALL_SIZE_GRID > config.GRID_WIDTH:
            self.ball_dx_grid *= -1
        
        # Collision with top border
        if self.ball_y_grid < 0:
            self.ball_dy_grid *= -1

        # Collision with paddle
        paddle_top = (config.GRID_HEIGHT - config.PADDLE_HEIGHT_GRID)
        if (
            self.ball_y_grid + config.BALL_SIZE_GRID >= paddle_top and
            self.ball_x_grid + config.BALL_SIZE_GRID >= self.paddle_x_grid and
            self.ball_x_grid <= self.paddle_x_grid + config.PADDLE_WIDTH_GRID
        ):
            self.ball_dy_grid *= -1
        
        # Ball misses paddle
        if self.ball_y_grid + config.BALL_SIZE_GRID > config.GRID_HEIGHT:
            self._reset_game_after_miss()
            return

        # Ball collision with bricks
        for brick in self.bricks:
            if brick['was_hit']:
                continue
            bx, by = brick['x_grid'], brick['y_grid']
            bw, bh = brick['width_grid'], brick['height_grid']

            ball_left = self.ball_x_grid
            ball_right = self.ball_x_grid + config.BALL_SIZE_GRID
            ball_top = self.ball_y_grid
            ball_bottom = self.ball_y_grid + config.BALL_SIZE_GRID

            brick_left = bx
            brick_right = bx + bw
            brick_top = by
            brick_bottom = by + bh

            if (
                ball_right > brick_left and
                ball_left < brick_right and
                ball_bottom > brick_top and
                ball_top < brick_bottom
            ):
                brick['was_hit'] = True

                # Determine collision direction
                if (ball_left < brick_right and ball_right > brick_left):
                    # Horizontal collision
                    self.ball_dx_grid *= -1
                else:
                    # Vertical collision
                    self.ball_dy_grid *= -1
                break

    def _reset_game_after_miss(self):
        """Resets game state if ball misses the paddle (as per PDF)."""
        self.paddle_x_grid = (config.GRID_WIDTH // 2) - (config.PADDLE_WIDTH_GRID // 2)
        self.paddle_dx_grid = 0
        self.ball_x_grid = config.GRID_WIDTH // 2
        self.ball_y_grid = config.GRID_HEIGHT // 2
        initial_dx_choices = [-2, -1, 0, 1, 2]
        self.ball_dx_grid = random.choice(initial_dx_choices)
        self.ball_dy_grid = config.BALL_INITIAL_DY_GRID # Still moves vertically
        for brick in self.bricks:
            brick['was_hit'] = False

    def get_state_for_display(self):
        """
        Returns a dictionary with PIXEL coordinates suitable for JSON serialization to the frontend.
        All grid unit values are multiplied by GRID_UNIT_SIZE for display.
        """
        return {
            'ball': {
                'x': self.ball_x_grid * config.GRID_UNIT_SIZE + config.BALL_RADIUS_PIXELS, # Center of ball for circle
                'y': self.ball_y_grid * config.GRID_UNIT_SIZE + config.BALL_RADIUS_PIXELS,
                'radius': config.BALL_RADIUS_PIXELS
            },
            # For the demo brick, we'll send it as a 'brick' type, but it's your paddle visual
            'paddle': {
                'x': self.paddle_x_grid * config.GRID_UNIT_SIZE,
                'y': (config.GRID_HEIGHT - config.PADDLE_HEIGHT_GRID) * config.GRID_UNIT_SIZE, # Place paddle at bottom of grid
                'width': config.PADDLE_WIDTH_PIXELS,
                'height': config.PADDLE_HEIGHT_PIXELS
            },
            'bricks': [
                {
                    'x': brick['x_grid'] * config.GRID_UNIT_SIZE,
                    'y': brick['y_grid'] * config.GRID_UNIT_SIZE,
                    'width': config.BRICK_WIDTH_PIXELS,
                    'height': config.BRICK_HEIGHT_PIXELS,
                    'was_hit': brick['was_hit'],
                    'row': brick['row']
                } for brick in self.bricks if not brick['was_hit']
            ],
            'screen': {
                'width': config.SCREEN_WIDTH,
                'height': config.SCREEN_HEIGHT
            }
        }