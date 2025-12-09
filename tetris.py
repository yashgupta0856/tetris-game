"""
Tetris Game - A complete implementation with modern features
Features: Ghost piece, hold piece, next piece preview, scoring, levels
"""

import random
from typing import List, Tuple, Optional

import pygame

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
GRID_X = 250
GRID_Y = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Tetromino shapes and colors
SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
}

COLORS = {
    "I": CYAN,
    "O": YELLOW,
    "T": PURPLE,
    "S": GREEN,
    "Z": RED,
    "J": BLUE,
    "L": ORANGE,
}


class GameState:
    """Base class for game states"""

    def handle_input(self, event, game):
        """Handle input events for this state"""

    def update(self, delta_time, game):
        """Update game logic for this state"""

    def draw(self, game):
        """Draw additional state-specific elements"""


class PlayingState(GameState):
    """Active gameplay state"""

    def handle_input(self, event, game):
        """Handle input during active gameplay"""
        if event.key == pygame.K_LEFT:
            game.move_piece(-1, 0)
        elif event.key == pygame.K_RIGHT:
            game.move_piece(1, 0)
        elif event.key == pygame.K_DOWN:
            if game.move_piece(0, 1):
                game.score += 1  # Bonus for soft drop
        elif event.key == pygame.K_UP:
            game.rotate_piece()
        elif event.key == pygame.K_SPACE:
            game.hard_drop()
        elif event.key == pygame.K_c:
            game.hold_current_piece()
        elif event.key == pygame.K_g:
            game.show_ghost = not game.show_ghost
        elif event.key == pygame.K_p:
            game.state = PausedState()

    def update(self, delta_time, game):
        """Update active gameplay"""
        # Auto-fall
        game.fall_time += delta_time
        if game.fall_time >= game.fall_speed:
            game.fall_time = 0
            if not game.move_piece(0, 1):
                game.lock_piece()

    def draw(self, game):
        """No additional drawing needed for playing state"""


class PausedState(GameState):
    """Game paused state"""

    def handle_input(self, event, game):
        """Handle input while paused"""
        if event.key == pygame.K_p:
            game.state = PlayingState()

    def update(self, delta_time, game):
        """No updates while paused"""

    def draw(self, game):
        """Draw pause overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        game.screen.blit(overlay, (0, 0))

        pause_text = game.font.render("PAUSED", True, WHITE)
        continue_text = game.small_font.render("Press P to Continue", True, WHITE)

        game.screen.blit(
            pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 250)
        )
        game.screen.blit(
            continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 320)
        )


class LineClearingState(GameState):
    """Line clearing animation state"""

    def handle_input(self, event, game):
        """No input handling during line clearing"""

    def update(self, delta_time, game):
        """Update line clearing animation"""
        game.clear_animation_time += delta_time
        if game.clear_animation_time >= game.clear_animation_duration:
            game.finish_clearing_animation()
            game.state = PlayingState()

    def draw(self, game):
        """No additional drawing needed - animation handled in draw_grid"""


class GameOverState(GameState):
    """Game over state"""

    def handle_input(self, event, game):
        """Handle input in game over state"""
        if event.key == pygame.K_r:
            game.reset_game()
            game.state = PlayingState()

    def update(self, delta_time, game):
        """No updates in game over state"""

    def draw(self, game):
        """Draw game over overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        game.screen.blit(overlay, (0, 0))

        game_over_text = game.font.render("GAME OVER", True, RED)
        score_text = game.font.render(f"Final Score: {game.score}", True, WHITE)
        restart_text = game.small_font.render("Press R to Restart", True, WHITE)

        game.screen.blit(
            game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 250)
        )
        game.screen.blit(
            score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 320)
        )
        game.screen.blit(
            restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400)
        )


class Tetromino:
    """Represents a Tetris piece"""

    def __init__(self, shape_type: str):
        self.type = shape_type
        self.shape = [row[:] for row in SHAPES[shape_type]]
        self.color = COLORS[shape_type]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate_clockwise(self):
        """Rotate the piece 90 degrees clockwise"""
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def rotate_counterclockwise(self):
        """Rotate the piece 90 degrees counterclockwise"""
        self.shape = [list(row) for row in zip(*self.shape)][::-1]

    def get_blocks(self) -> List[Tuple[int, int]]:
        """Get list of block positions for this piece"""
        blocks = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    blocks.append((self.x + x, self.y + y))
        return blocks

    def copy(self):
        """Create a copy of this tetromino"""
        new_piece = Tetromino(self.type)
        new_piece.shape = [row[:] for row in self.shape]
        new_piece.x = self.x
        new_piece.y = self.y
        return new_piece


class TetrisGame:
    """Main game class"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris - Ultimate Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Game state
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece: Optional[Tetromino] = None
        self.next_piece: Optional[Tetromino] = None
        self.hold_piece: Optional[Tetromino] = None
        self.can_hold = True
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False

        # Timing
        self.fall_time = 0
        self.fall_speed = 1000  # milliseconds

        # Animation state
        self.clearing_lines = []
        self.clear_animation_time = 0
        self.clear_animation_duration = 500  # milliseconds

        # Settings
        self.show_ghost = True

        # State pattern
        self.state: GameState = PlayingState()

        # Initialize first pieces
        self.next_piece = self.get_random_piece()
        self.spawn_new_piece()

    def get_random_piece(self) -> Tetromino:
        """Get a random tetromino"""
        return Tetromino(random.choice(list(SHAPES.keys())))

    def spawn_new_piece(self):
        """Spawn a new piece at the top"""
        self.current_piece = self.next_piece
        self.next_piece = self.get_random_piece()
        self.can_hold = True

        # Check if game over
        if not self.is_valid_position(self.current_piece):
            self.game_over = True
            self.state = GameOverState()

    def is_valid_position(self, piece: Tetromino, offset_x=0, offset_y=0) -> bool:
        """Check if a piece position is valid"""
        for x, y in piece.get_blocks():
            new_x = x + offset_x
            new_y = y + offset_y

            # Check boundaries
            if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                return False

            # Check collision with placed blocks
            if new_y >= 0 and self.grid[new_y][new_x] is not None:
                return False

        return True

    def move_piece(self, dx: int, dy: int) -> bool:
        """Try to move the piece by dx, dy"""
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate_piece(self):
        """Try to rotate the piece with wall kicks"""
        original_shape = [row[:] for row in self.current_piece.shape]
        self.current_piece.rotate_clockwise()

        # Try wall kicks
        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1)]
        for dx, dy in kicks:
            if self.is_valid_position(self.current_piece, dx, dy):
                self.current_piece.x += dx
                self.current_piece.y += dy
                return

        # Rotation failed, restore original shape
        self.current_piece.shape = original_shape

    def hard_drop(self):
        """Drop the piece instantly to the bottom"""
        drop_distance = 0
        while self.move_piece(0, 1):
            drop_distance += 1

        self.score += drop_distance * 2  # Bonus points for hard drop
        self.lock_piece()

    def get_ghost_piece(self) -> Tetromino:
        """Get the ghost piece showing where the current piece will land"""
        ghost = self.current_piece.copy()
        while self.is_valid_position(ghost, 0, 1):
            ghost.y += 1
        return ghost

    def lock_piece(self):
        """Lock the current piece into the grid"""
        for x, y in self.current_piece.get_blocks():
            if y >= 0:
                self.grid[y][x] = self.current_piece.color

        self.clear_lines()
        if not self.clearing_lines:
            self.spawn_new_piece()

    def clear_lines(self):
        """Clear completed lines and update score"""
        lines_to_clear = []

        for y in range(GRID_HEIGHT):
            if all(self.grid[y][x] is not None for x in range(GRID_WIDTH)):
                lines_to_clear.append(y)

        if lines_to_clear:
            # Start animation
            self.clearing_lines = lines_to_clear[:]
            self.clear_animation_time = 0

            # Update score and level
            num_lines = len(lines_to_clear)
            self.lines_cleared += num_lines

            # Scoring: 100, 300, 500, 800 for 1, 2, 3, 4 lines
            line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += line_scores.get(num_lines, 0) * self.level

            # Level up every 10 lines
            new_level = self.lines_cleared // 10 + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_speed = max(100, 1000 - (self.level - 1) * 100)

            # Transition to line clearing state
            self.state = LineClearingState()

    def finish_clearing_animation(self):
        """Complete the line clearing animation and remove lines"""
        if self.clearing_lines:
            for y in reversed(self.clearing_lines):
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
            self.clearing_lines = []
            self.spawn_new_piece()

    def hold_current_piece(self):
        """Hold the current piece for later"""
        if not self.can_hold:
            return

        if self.hold_piece is None:
            self.hold_piece = Tetromino(self.current_piece.type)
            self.spawn_new_piece()
        else:
            # Swap current and hold piece
            temp_type = self.current_piece.type
            self.current_piece = Tetromino(self.hold_piece.type)
            self.hold_piece = Tetromino(temp_type)

        self.can_hold = False

    def draw_grid(self):
        """Draw the game grid"""
        # Draw background
        grid_rect = pygame.Rect(
            GRID_X, GRID_Y, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE
        )
        pygame.draw.rect(self.screen, DARK_GRAY, grid_rect)

        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                self.screen,
                GRAY,
                (GRID_X + x * BLOCK_SIZE, GRID_Y),
                (GRID_X + x * BLOCK_SIZE, GRID_Y + GRID_HEIGHT * BLOCK_SIZE),
            )

        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                self.screen,
                GRAY,
                (GRID_X, GRID_Y + y * BLOCK_SIZE),
                (GRID_X + GRID_WIDTH * BLOCK_SIZE, GRID_Y + y * BLOCK_SIZE),
            )

        # Draw placed blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] is not None:
                    self.draw_block(x, y, self.grid[y][x])

        # Draw clearing animation
        if self.clearing_lines:
            progress = self.clear_animation_time / self.clear_animation_duration
            alpha = int(255 * (1 - progress))

            for y in self.clearing_lines:
                for x in range(GRID_WIDTH):
                    rect = pygame.Rect(
                        GRID_X + x * BLOCK_SIZE + 1,
                        GRID_Y + y * BLOCK_SIZE + 1,
                        BLOCK_SIZE - 2,
                        BLOCK_SIZE - 2,
                    )
                    # Create a surface with alpha for fade effect
                    surf = pygame.Surface((BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                    surf.set_alpha(alpha)
                    surf.fill(WHITE)
                    self.screen.blit(surf, (rect.x, rect.y))

        # Draw ghost piece
        if self.current_piece and self.show_ghost and not self.clearing_lines:
            ghost = self.get_ghost_piece()
            for x, y in ghost.get_blocks():
                if y >= 0:
                    rect = pygame.Rect(
                        GRID_X + x * BLOCK_SIZE + 2,
                        GRID_Y + y * BLOCK_SIZE + 2,
                        BLOCK_SIZE - 4,
                        BLOCK_SIZE - 4,
                    )
                    pygame.draw.rect(self.screen, self.current_piece.color, rect, 2)

        # Draw current piece
        if self.current_piece:
            for x, y in self.current_piece.get_blocks():
                if y >= 0:
                    self.draw_block(x, y, self.current_piece.color)

    def draw_block(self, x: int, y: int, color: Tuple[int, int, int]):
        """Draw a single block"""
        rect = pygame.Rect(
            GRID_X + x * BLOCK_SIZE + 1,
            GRID_Y + y * BLOCK_SIZE + 1,
            BLOCK_SIZE - 2,
            BLOCK_SIZE - 2,
        )
        pygame.draw.rect(self.screen, color, rect)

        # Add highlight for 3D effect
        highlight = tuple(min(c + 40, 255) for c in color)
        pygame.draw.line(
            self.screen, highlight, (rect.left, rect.top), (rect.right, rect.top), 2
        )
        pygame.draw.line(
            self.screen, highlight, (rect.left, rect.top), (rect.left, rect.bottom), 2
        )

    def draw_piece_preview(self, piece: Tetromino, x: int, y: int, title: str):
        """Draw a piece preview box"""
        # Draw title
        title_text = self.small_font.render(title, True, WHITE)
        self.screen.blit(title_text, (x, y - 30))

        # Draw box
        box_rect = pygame.Rect(x, y, 120, 100)
        pygame.draw.rect(self.screen, DARK_GRAY, box_rect)
        pygame.draw.rect(self.screen, WHITE, box_rect, 2)

        # Draw piece centered in box
        if piece:
            offset_x = x + 60 - len(piece.shape[0]) * BLOCK_SIZE // 2
            offset_y = y + 50 - len(piece.shape) * BLOCK_SIZE // 2

            for row_idx, row in enumerate(piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            offset_x + col_idx * BLOCK_SIZE,
                            offset_y + row_idx * BLOCK_SIZE,
                            BLOCK_SIZE - 2,
                            BLOCK_SIZE - 2,
                        )
                        pygame.draw.rect(self.screen, piece.color, rect)

    def draw_ui(self):
        """Draw the user interface"""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (50, 100))

        # Level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (50, 150))

        # Lines
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (50, 200))

        # Next piece
        self.draw_piece_preview(self.next_piece, 580, 100, "NEXT")

        # Hold piece
        self.draw_piece_preview(self.hold_piece, 580, 250, "HOLD")

        # Controls
        controls = [
            "Controls:",
            "Left/Right: Move",
            "Down: Soft Drop",
            "Up: Rotate",
            "SPACE: Hard Drop",
            "C: Hold",
            "P: Pause",
            "G: Toggle Ghost",
            "ESC: Quit",
        ]

        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, WHITE)
            self.screen.blit(control_text, (50, 400 + i * 30))

    def reset_game(self):
        """Reset the game to initial state"""
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.fall_speed = 1000
        self.clearing_lines = []
        self.clear_animation_time = 0
        self.next_piece = self.get_random_piece()
        self.hold_piece = None
        self.can_hold = True
        self.state = PlayingState()
        self.spawn_new_piece()

    def handle_input(self, event):
        """Handle keyboard input"""
        if event.type == pygame.KEYDOWN:
            self.state.handle_input(event, self)

    def update(self, delta_time):
        """Update game state"""
        if self.game_over:
            return

        self.state.update(delta_time, self)

    def draw(self):
        """Draw everything"""
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_ui()

        # Delegate state-specific drawing to current state
        self.state.draw(self)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True

        while running:
            delta_time = self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_input(event)

            self.update(delta_time)
            self.draw()

        pygame.quit()


def main():
    """Main entry point for the game"""
    game = TetrisGame()
    game.run()


if __name__ == "__main__":
    main()
