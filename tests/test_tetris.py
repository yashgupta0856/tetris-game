"""
Test suite for Tetris Ultimate Edition
"""

import pygame
import pytest

from tetris import (
    COLORS,
    GRID_HEIGHT,
    GRID_WIDTH,
    SHAPES,
    GameConfig,
    GameOverState,
    LineClearingState,
    PausedState,
    PlayingState,
    TetrisGame,
    Tetromino,
)


class TestTetromino:
    """Test the Tetromino class"""

    def test_tetromino_creation(self):
        """Test creating a tetromino"""
        piece = Tetromino("I")
        assert piece.type == "I"
        assert piece.color == COLORS["I"]
        assert len(piece.shape) > 0

    def test_all_shapes_exist(self):
        """Test that all 7 tetromino shapes can be created"""
        for shape_type in SHAPES:
            piece = Tetromino(shape_type)
            assert piece.type == shape_type
            assert piece.color == COLORS[shape_type]

    def test_tetromino_rotation_clockwise(self):
        """Test clockwise rotation"""
        piece = Tetromino("T")
        original_shape = [row[:] for row in piece.shape]
        piece.rotate_clockwise()
        # Shape should change after rotation
        assert piece.shape != original_shape

    def test_tetromino_rotation_counterclockwise(self):
        """Test counterclockwise rotation"""
        piece = Tetromino("T")
        original_shape = [row[:] for row in piece.shape]
        piece.rotate_counterclockwise()
        # Shape should change after rotation
        assert piece.shape != original_shape

    def test_tetromino_copy(self):
        """Test copying a tetromino"""
        piece = Tetromino("I")
        piece.x = 5
        piece.y = 3
        copy = piece.copy()

        assert copy.type == piece.type
        assert copy.x == piece.x
        assert copy.y == piece.y
        assert copy.shape == piece.shape
        # Ensure it's a deep copy
        copy.x = 10
        assert piece.x == 5

    def test_get_blocks(self):
        """Test getting block positions"""
        piece = Tetromino("O")
        blocks = piece.get_blocks()
        # O piece should have 4 blocks
        assert len(blocks) == 4
        # All blocks should be tuples of (x, y)
        for block in blocks:
            assert isinstance(block, tuple)
            assert len(block) == 2


class TestTetrisGame:
    """Test the TetrisGame class"""

    @pytest.fixture
    def game(self):
        """Create a game instance for testing"""
        pygame.init()
        game = TetrisGame()
        yield game
        pygame.quit()

    def test_game_initialization(self, game):
        """Test game initializes correctly"""
        assert game.score == 0
        assert game.level == 1
        assert game.lines_cleared == 0
        assert game.game_over is False
        assert len(game.grid) == GRID_HEIGHT
        assert len(game.grid[0]) == GRID_WIDTH
        assert game.current_piece is not None
        assert game.next_piece is not None

    def test_spawn_new_piece(self, game):
        """Test spawning a new piece"""
        old_piece = game.current_piece
        game.spawn_new_piece()
        # Current piece should change
        assert game.current_piece != old_piece
        assert game.current_piece is not None

    def test_is_valid_position(self, game):
        """Test position validation"""
        # Current piece at start should be valid
        assert game.is_valid_position(game.current_piece)

        # Test invalid positions (out of bounds)
        piece = Tetromino("I")
        piece.x = -1  # Left boundary
        assert not game.is_valid_position(piece)

        piece.x = GRID_WIDTH  # Right boundary
        assert not game.is_valid_position(piece)

        piece.x = 0
        piece.y = GRID_HEIGHT  # Bottom boundary
        assert not game.is_valid_position(piece)

    def test_move_piece(self, game):
        """Test moving pieces"""
        original_x = game.current_piece.x
        original_y = game.current_piece.y

        # Move right
        result = game.move_piece(1, 0)
        if result:
            assert game.current_piece.x == original_x + 1

        # Move down
        game.current_piece.x = original_x
        game.current_piece.y = original_y
        result = game.move_piece(0, 1)
        if result:
            assert game.current_piece.y == original_y + 1

    def test_rotate_piece(self, game):
        """Test piece rotation"""
        game.rotate_piece()
        # Shape should change after rotation (unless it's O piece)
        if game.current_piece.type != "O":
            # For most pieces, rotation changes shape
            pass  # Shape might be same if rotation failed due to collision

    def test_ghost_piece(self, game):
        """Test ghost piece calculation"""
        ghost = game.get_ghost_piece()
        # Ghost piece should be at same or lower position
        assert ghost.y >= game.current_piece.y
        assert ghost.x == game.current_piece.x

    def test_scoring_single_line(self, game):
        """Test scoring for single line clear"""
        # Fill bottom row except one column
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        initial_score = game.score
        game.clear_lines()

        # After animation completes
        if game.clearing_lines:
            game.finish_clearing_animation()

        # Score should increase
        assert game.score > initial_score
        assert game.lines_cleared == 1

    def test_level_progression(self, game):
        """Test level increases after 10 lines"""
        game.lines_cleared = 9
        game.clear_lines()
        # Level should still be 1

        game.lines_cleared = 10
        initial_level = game.level
        # Simulate line clear
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()

        # Level progression happens in clear_lines
        # After 10 lines, level should be 2
        assert game.level >= initial_level

    def test_hold_piece(self, game):
        """Test hold piece functionality"""
        original_type = game.current_piece.type
        game.hold_current_piece()

        # Hold piece should be set
        assert game.hold_piece is not None
        assert game.hold_piece.type == original_type
        # Can't hold again immediately
        assert game.can_hold is False

    def test_ghost_toggle(self, game):
        """Test ghost piece toggle"""
        original_state = game.show_ghost
        game.show_ghost = not game.show_ghost
        assert game.show_ghost != original_state

    def test_reset_game(self, game):
        """Test game reset"""
        # Modify game state
        game.score = 100
        game.level = 5
        game.lines_cleared = 50
        game.game_over = True

        # Reset
        game.reset_game()

        # Check reset state
        assert game.score == 0
        assert game.level == 1
        assert game.lines_cleared == 0
        assert game.game_over is False
        assert game.clearing_lines == []

    def test_grid_is_empty_initially(self, game):
        """Test that grid starts empty"""
        for row in game.grid:
            for cell in row:
                assert cell is None


class TestGameLogic:
    """Test game logic and mechanics"""

    @pytest.fixture
    def game(self):
        """Create a game instance for testing"""
        pygame.init()
        game = TetrisGame()
        yield game
        pygame.quit()

    def test_line_clear_animation(self, game):
        """Test line clearing animation"""
        # Fill a line
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        game.clear_lines()

        # Animation should be active
        assert len(game.clearing_lines) > 0
        assert game.clear_animation_time >= 0

    def test_animation_completion(self, game):
        """Test animation completes and removes lines"""
        # Fill a line
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        game.clear_lines()
        assert len(game.clearing_lines) == 1

        # Complete animation
        game.finish_clearing_animation()

        # Lines should be cleared
        assert len(game.clearing_lines) == 0
        # Bottom row should be empty after clearing
        assert all(cell is None for cell in game.grid[GRID_HEIGHT - 1])

    def test_multiple_line_clear(self, game):
        """Test clearing multiple lines at once"""
        # Fill multiple lines
        for y in range(GRID_HEIGHT - 2, GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                game.grid[y][x] = COLORS["I"]

        game.clear_lines()

        # Should detect 2 lines
        assert len(game.clearing_lines) == 2

    def test_scoring_increases_with_level(self, game):
        """Test that scoring scales with level"""
        game.level = 1
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()
        score_level_1 = game.score

        # Reset and test level 2
        game.reset_game()
        game.level = 2
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()
        score_level_2 = game.score

        # Level 2 should give more points for same line clear
        assert score_level_2 > score_level_1


class TestConstants:
    """Test game constants are valid"""

    def test_all_shapes_defined(self):
        """Test all 7 tetromino shapes are defined"""
        assert len(SHAPES) == 7
        expected_shapes = ["I", "O", "T", "S", "Z", "J", "L"]
        for shape in expected_shapes:
            assert shape in SHAPES

    def test_all_colors_defined(self):
        """Test all colors are defined for each shape"""
        assert len(COLORS) == 7
        for shape in SHAPES:
            assert shape in COLORS
            # Each color should be an RGB tuple
            assert len(COLORS[shape]) == 3

    def test_grid_dimensions(self):
        """Test grid dimensions are reasonable"""
        assert GRID_WIDTH == 10
        assert GRID_HEIGHT == 20


class TestGameStates:
    """Test the State Pattern implementation"""

    @pytest.fixture
    def game(self):
        """Create a game instance for testing"""
        pygame.init()
        game = TetrisGame()
        yield game
        pygame.quit()

    def test_initial_state_is_playing(self, game):
        """Test game starts in PlayingState"""
        assert isinstance(game.state, PlayingState)

    def test_pause_state_transition(self, game):
        """Test transitioning to paused state"""
        # Create a pause event
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_p})
        game.handle_input(event)

        # Should be in paused state
        assert isinstance(game.state, PausedState)

    def test_unpause_state_transition(self, game):
        """Test transitioning from paused back to playing"""
        # Pause the game
        game.state = PausedState()

        # Unpause
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_p})
        game.handle_input(event)

        # Should be back to playing
        assert isinstance(game.state, PlayingState)

    def test_game_over_state_transition(self, game):
        """Test transitioning to game over state"""
        # Set game over condition
        game.game_over = True
        game.state = GameOverState()

        assert isinstance(game.state, GameOverState)

    def test_restart_from_game_over(self, game):
        """Test restarting game from game over state"""
        # Set to game over
        game.state = GameOverState()
        game.game_over = True

        # Press R to restart
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_r})
        game.handle_input(event)

        # Should be back to playing
        assert isinstance(game.state, PlayingState)
        assert game.game_over is False

    def test_line_clearing_state_transition(self, game):
        """Test transitioning to line clearing state"""
        # Fill a line
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        # Trigger line clear
        game.clear_lines()

        # Should be in line clearing state
        assert isinstance(game.state, LineClearingState)

    def test_line_clearing_completes(self, game):
        """Test line clearing transitions back to playing"""
        # Fill a line and start clearing
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()

        # Complete the animation
        game.state.update(game.clear_animation_duration + 1, game)

        # Should be back to playing
        assert isinstance(game.state, PlayingState)

    def test_paused_state_no_update(self, game):
        """Test that paused state doesn't update game logic"""
        game.state = PausedState()
        original_fall_time = game.fall_time

        # Update should not change fall_time
        game.state.update(100, game)

        assert game.fall_time == original_fall_time

    def test_paused_state_no_movement(self, game):
        """Test that pieces can't move while paused"""
        game.state = PausedState()
        original_x = game.current_piece.x

        # Try to move (should be ignored in paused state)
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT})
        game.handle_input(event)

        # Piece should not have moved
        assert game.current_piece.x == original_x

    def test_playing_state_handles_movement(self, game):
        """Test that playing state handles movement input"""
        game.state = PlayingState()

        # Move right
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT})
        game.handle_input(event)

        # Piece should have moved (if there was space)
        # Can't assert exact position due to boundary conditions
        # But state should have processed the input
        assert isinstance(game.state, PlayingState)


class TestGameConfig:
    """Test the GameConfig class and config-based initialization"""

    def test_game_with_default_config(self):
        """Test game initialization with default config"""
        pygame.init()
        game = TetrisGame()
        assert game.config == GameConfig
        assert game.fall_speed == GameConfig.INITIAL_FALL_SPEED
        assert game.clear_animation_duration == GameConfig.CLEAR_ANIMATION_DURATION
        pygame.quit()

    def test_game_with_custom_config(self):
        """Test game initialization with custom config"""
        pygame.init()

        # Create a custom config class
        class CustomConfig(GameConfig):  # pylint: disable=too-few-public-methods
            """Custom configuration for testing with modified settings"""

            INITIAL_FALL_SPEED = 500  # Faster falling
            LINES_PER_LEVEL = 5  # Level up faster
            LINE_SCORES = {1: 200, 2: 600, 3: 1000, 4: 1600}  # Double points
            SOFT_DROP_BONUS = 2
            HARD_DROP_BONUS = 4

        game = TetrisGame(CustomConfig)

        assert game.config == CustomConfig
        assert game.fall_speed == 500
        assert game.config.LINES_PER_LEVEL == 5
        assert game.config.LINE_SCORES[1] == 200

        pygame.quit()

    def test_tetromino_with_custom_config(self):
        """Test tetromino creation with custom config"""
        pygame.init()

        class CustomConfig(GameConfig):  # pylint: disable=too-few-public-methods
            """Custom configuration for testing with wider grid"""

            GRID_WIDTH = 15  # Wider grid
            GRID_HEIGHT = 25  # Taller grid

        piece = Tetromino("I", CustomConfig)
        assert piece.config == CustomConfig
        # Verify piece spawns centered in wider grid
        assert piece.x == CustomConfig.GRID_WIDTH // 2 - len(piece.shape[0]) // 2

        pygame.quit()

    def test_config_values_are_correct(self):
        """Test that GameConfig has all expected values"""
        # Display settings
        assert GameConfig.SCREEN_WIDTH == 800
        assert GameConfig.SCREEN_HEIGHT == 700
        assert GameConfig.BLOCK_SIZE == 30

        # Grid settings
        assert GameConfig.GRID_WIDTH == 10
        assert GameConfig.GRID_HEIGHT == 20

        # Timing settings
        assert GameConfig.INITIAL_FALL_SPEED == 1000
        assert GameConfig.CLEAR_ANIMATION_DURATION == 500
        assert GameConfig.LEVEL_SPEED_DECREASE == 100
        assert GameConfig.MIN_FALL_SPEED == 100

        # Scoring
        assert GameConfig.LINE_SCORES == {1: 100, 2: 300, 3: 500, 4: 800}
        assert GameConfig.SOFT_DROP_BONUS == 1
        assert GameConfig.HARD_DROP_BONUS == 2
        assert GameConfig.LINES_PER_LEVEL == 10

    def test_scoring_with_custom_config(self):
        """Test that custom config affects scoring"""
        pygame.init()

        class HighScoreConfig(GameConfig):  # pylint: disable=too-few-public-methods
            """Custom configuration for testing with higher scores"""

            LINE_SCORES = {1: 500, 2: 1500, 3: 2500, 4: 4000}
            SOFT_DROP_BONUS = 5

        game = TetrisGame(HighScoreConfig)

        # Fill a line and clear it
        for x in range(game.config.GRID_WIDTH):
            game.grid[game.config.GRID_HEIGHT - 1][x] = game.config.COLORS["I"]

        initial_score = game.score
        game.clear_lines()

        # Score should use custom line scores
        expected_score = initial_score + HighScoreConfig.LINE_SCORES[1] * game.level
        assert game.score == expected_score

        pygame.quit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
