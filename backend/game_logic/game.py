import random
from backend import config
import logging

game_logger = logging.getLogger('gamelogic')

class GameState:
    def __init__(self):
        # Game mode
        self.mode = 'Human Player'  # Alternatively 'AI Agent'
        self.game_over = False
        # Score and time
        self.score = 0
        self.time = 0

        # Initialize ball position in center
        self.ball_x_grid = config.GRID_WIDTH // 2
        self.ball_y_grid = config.GRID_HEIGHT // 2

        # Ball initial direction is chosen at random from specified choices
        self.ball_dx_grid = random.choice(config.INITIAL_DX_CHOICES)
        self.ball_dy_grid = config.BALL_INITIAL_DY_GRID

        # Paddle
        self.paddle_x_grid = (config.GRID_WIDTH // 2) - (config.PADDLE_WIDTH_GRID // 2)
        self.paddle_dx_grid = config.PADDLE_INITIAL_DX_GRID

        # Bricks
        self.bricks = []
        for row in range(config.NUM_BRICK_ROWS):
            for col in range(config.GRID_WIDTH // config.BRICK_WIDTH_GRID):
                brick = {
                    'x_grid': col * config.BRICK_WIDTH_GRID,
                    'y_grid': row * config.BRICK_HEIGHT_GRID,
                    'width_grid': config.BRICK_WIDTH_GRID,
                    'height_grid': config.BRICK_HEIGHT_GRID,
                    'was_hit': False,
                    'row': row,
                }
                self.bricks.append(brick)

        game_logger.info(f"Game started!")

    def get_speed(self):
        """Returns the current speed of the ball based on the game mode."""
        if self.mode == 'AI Agent':
            return config.BALL_SPEED_AI_AGENT
        else:
            return config.BALL_SPEED_HUMAN_PLAYER

    def get_reward(self):
        """Returns the reward for the current state, i.e. -1 for each timestep."""
        return -self.time

    def from_state(self, state):
        """Sets the current GameState's attributes from a dict"""
        self.ball_x_grid = state.get('ball_x_grid', self.ball_x_grid)
        self.ball_y_grid = state.get('ball_y_grid', self.ball_y_grid)
        self.paddle_x_grid = state.get('paddle_x_grid', self.paddle_x_grid)
        self.ball_dx_grid = state.get('ball_dx_grid', self.ball_dx_grid)
        self.ball_dy_grid = state.get('ball_dy_grid', self.ball_dy_grid)

        return self
        
    def update(self):
        """Updates the game state for one timestep, using GRID UNITS."""
        if self.game_over:
            return
        speed = self.get_speed()
        # Increase time
        self.time += 1

        # Update Ball Position
        self.ball_x_grid += self.ball_dx_grid * speed
        self.ball_y_grid += self.ball_dy_grid * speed

        # Bouncing off walls
        if self.ball_x_grid < 0 or self.ball_x_grid + config.BALL_SIZE_GRID > config.GRID_WIDTH:
            self.ball_dx_grid *= -1
            game_logger.debug(f"Ball hit wall at ({self.ball_x_grid}, {self.ball_y_grid})")
        
        # Collision with top border
        if self.ball_y_grid < 0:
            self.ball_dy_grid *= -1
            if self.ball_dx_grid == 0: # random direction to avoid getting stuck
                self.ball_dx_grid = random.choice(config.INITIAL_DX_CHOICES)

        # Collision with paddle
        paddle_top = (config.GRID_HEIGHT - config.PADDLE_HEIGHT_GRID)
        if (
            self.ball_y_grid + config.BALL_SIZE_GRID >= paddle_top and
            self.ball_x_grid + config.BALL_SIZE_GRID >= self.paddle_x_grid and
            self.ball_x_grid <= self.paddle_x_grid + config.PADDLE_WIDTH_GRID
        ):
            self.ball_dy_grid *= -1
            self.ball_y_grid = paddle_top - config.BALL_SIZE_GRID
        
        # Ball misses paddle
        if self.ball_y_grid + config.BALL_SIZE_GRID > config.GRID_HEIGHT:
            self._reset_game_after_miss()
            return

        # Ball collision with bricks
        collided_bricks = []
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
                collided_bricks.append(brick)

        # Pick one at random; ensures that each time no more than a single brick is removed
        if collided_bricks: 
            if self.ball_dy_grid > 0:
                target_row = max(brick['row'] for brick in collided_bricks)
            else:
                target_row = min(brick['row'] for brick in collided_bricks)
            target_bricks = [b for b in collided_bricks if b['row'] == target_row]
            brick = random.choice(target_bricks)
            brick['was_hit'] = True
            game_logger.info(f"Brick eliminated")
            if brick['row'] == 0:
                self.score += 7
            elif brick['row'] == 1:
                self.score += 5
            elif brick['row'] == 2:
                self.score += 3

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

            # Determine collision direction
            vertical_overlap = min(ball_bottom, brick_bottom) - max(ball_top, brick_top)
            horizontal_overlap = min(ball_right, brick_right) - max(ball_left, brick_left)
            if vertical_overlap < horizontal_overlap:
                # Ball hits bottom of brick
                self.ball_dy_grid *= -1
                if self.ball_dx_grid == 0: # random direction to avoid getting stuck
                    self.ball_dx_grid = random.choice(config.INITIAL_DX_CHOICES)
            else:
                # Ball hits side of brick
                self.ball_dx_grid *= -1
                if self.ball_dx_grid == 0: # random direction to avoid getting stuck
                    self.ball_dx_grid = random.choice(config.INITIAL_DX_CHOICES)
        
        if all(brick['was_hit'] for brick in self.bricks):
            self.game_over = True
            game_logger.info(f"You Won! All bricks eliminated. Final Score: {self.score}. Final Reward: {-self.time}")

    
    def apply_action(self, action):
        """Applies the provided action to move the paddle."""
        self.paddle_dx_grid = action
        self.paddle_x_grid += self.paddle_dx_grid
        self.paddle_x_grid = max(0, min(self.paddle_x_grid, config.GRID_WIDTH - config.PADDLE_WIDTH_GRID))

    def _reset_game_after_miss(self):
        """Resets game state if ball misses the paddle (as per PDF)."""
        # Reset score
        self.score = 0
        # Place paddle back in center with speed 0
        self.paddle_x_grid = (config.GRID_WIDTH // 2) - (config.PADDLE_WIDTH_GRID // 2)
        self.paddle_dx_grid = 0
        # Shoot ball randomly from center
        self.ball_x_grid = config.GRID_WIDTH // 2
        self.ball_y_grid = config.GRID_HEIGHT // 2
        self.ball_dx_grid = random.choice(config.INITIAL_DX_CHOICES)
        self.ball_dy_grid = config.BALL_INITIAL_DY_GRID # Still moves vertically
        game_logger.info(f"Game Over! Ball hit bottom. Final Score: {self.score}")
        # Make all bricks reappear
        for brick in self.bricks:
            brick['was_hit'] = False

    def get_state_for_display(self):
        """
        Differentiates between hit bricks and non-hit bricks.
        Returns a dict with pixel coordinates suitable for JSON serialization to the frontend.
        All grid unit values are multiplied by GRID_UNIT_SIZE for display.
        """
        return {
            'ball': {
                'x': self.ball_x_grid * config.GRID_UNIT_SIZE + config.BALL_RADIUS_PIXELS, # Center of ball for circle
                'y': self.ball_y_grid * config.GRID_UNIT_SIZE + config.BALL_RADIUS_PIXELS,
                'radius': config.BALL_RADIUS_PIXELS
            },
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
            'score': self.score,
            'time': self.time,
            'game_over': self.game_over,
            'screen': {
                'width': config.GRID_WIDTH * config.GRID_UNIT_SIZE,
                'height': config.GRID_HEIGHT * config.GRID_UNIT_SIZE
            }
        }