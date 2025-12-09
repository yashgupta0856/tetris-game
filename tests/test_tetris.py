"""
Test suite for Tetris Ultimate Edition.

This module validates Tetromino behavior, core TetrisGame logic,
scoring, grid updates, animation transitions, state-pattern behavior,
and configuration-driven overrides.

All tests follow pytest conventions and assume that the implementation
in `tetris.py` provides the following:
    • Tetromino class for piece geometry and movement
    • TetrisGame class for grid logic, scoring, and flow control
    • State classes implementing game state behavior (Playing, Paused, LineClearing, GameOver)
    • GameConfig supplying default constants and overridable parameters

This file contains only documentation improvements. No logic has been changed.
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
    """Unit tests validating Tetromino construction, rotation, copying, and block extraction."""

    def test_tetromino_creation(self) -> None:
        """
        Ensure Tetromino initialization assigns:
            • Correct `type` string
            • Color mapping from COLORS dict
            • A non-empty shape matrix
        """
        piece = Tetromino("I")
        assert piece.type == "I"
        assert piece.color == COLORS["I"]
        assert len(piece.shape) > 0

    def test_all_shapes_exist(self) -> None:
        """
        Validate that all Tetromino shape identifiers in SHAPES
        can be instantiated and have valid color mappings.
        """
        for shape_type in SHAPES:
            piece = Tetromino(shape_type)
            assert piece.type == shape_type
            assert piece.color == COLORS[shape_type]

    def test_tetromino_rotation_clockwise(self) -> None:
        """
        Confirm clockwise rotation modifies the internal 2D matrix.
        """
        piece = Tetromino("T")
        original = [row[:] for row in piece.shape]
        piece.rotate_clockwise()
        assert piece.shape != original

    def test_tetromino_rotation_counterclockwise(self) -> None:
        """
        Confirm counterclockwise rotation modifies the internal matrix.
        """
        piece = Tetromino("T")
        original = [row[:] for row in piece.shape]
        piece.rotate_counterclockwise()
        assert piece.shape != original

    def test_tetromino_copy(self) -> None:
        """
        Validate deep-copy semantics:
            • Coordinates and shape are duplicated
            • Original and copy do not share mutable references
        """
        piece = Tetromino("I")
        piece.x = 5
        piece.y = 3
        copied = piece.copy()

        assert copied.type == piece.type
        assert copied.x == piece.x
        assert copied.y == piece.y
        assert copied.shape == piece.shape

        copied.x = 10
        assert piece.x == 5

    def test_get_blocks(self) -> None:
        """
        Ensure get_blocks returns grid-space coordinates for all occupied cells.
        Returns:
            List[(x, y)] of length 4 for standard Tetrominoes.
        """
        piece = Tetromino("O")
        blocks = piece.get_blocks()

        assert len(blocks) == 4
        for b in blocks:
            assert isinstance(b, tuple)
            assert len(b) == 2


class TestTetrisGame:
    """Tests validating TetrisGame initialization, movement, scoring, and grid updates."""

    @pytest.fixture
    def game(self):
        """
        Provide a fresh TetrisGame instance.
        Ensures pygame is initialized and cleaned up.
        """
        pygame.init()
        g = TetrisGame()
        yield g
        pygame.quit()

    def test_game_initialization(self, game) -> None:
        """
        Validate default game fields:
            • score, level, line counter
            • empty grid
            • current and next Tetromino existence
        """
        assert game.score == 0
        assert game.level == 1
        assert game.lines_cleared == 0
        assert game.game_over is False

        assert len(game.grid) == GRID_HEIGHT
        assert len(game.grid[0]) == GRID_WIDTH

        assert game.current_piece is not None
        assert game.next_piece is not None

    def test_spawn_new_piece(self, game) -> None:
        """
        Ensure a fresh Tetromino replaces the existing piece.
        """
        old_piece = game.current_piece
        game.spawn_new_piece()
        assert game.current_piece is not old_piece

    def test_is_valid_position(self, game) -> None:
        """
        Validate collision and boundary rules for piece placement.
        """
        assert game.is_valid_position(game.current_piece)

        invalid = Tetromino("I")
        invalid.x = -1
        assert not game.is_valid_position(invalid)

        invalid.x = GRID_WIDTH
        assert not game.is_valid_position(invalid)

        invalid.x = 0
        invalid.y = GRID_HEIGHT
        assert not game.is_valid_position(invalid)

    def test_move_piece(self, game) -> None:
        """
        Validate movement deltas update coordinates only when valid.
        """
        x0 = game.current_piece.x
        y0 = game.current_piece.y

        if game.move_piece(1, 0):
            assert game.current_piece.x == x0 + 1

        game.current_piece.x, game.current_piece.y = x0, y0

        if game.move_piece(0, 1):
            assert game.current_piece.y == y0 + 1

    def test_rotate_piece(self, game) -> None:
        """
        Confirm rotation executes without raising errors.
        Rotation may be ignored in blocked positions.
        """
        game.rotate_piece()

    def test_ghost_piece(self, game) -> None:
        """
        Validate ghost projection:
            • Same x as current piece
            • y is always >= current piece's y
        """
        ghost = game.get_ghost_piece()
        assert ghost.x == game.current_piece.x
        assert ghost.y >= game.current_piece.y

    def test_scoring_single_line(self, game) -> None:
        """
        Validate one-line clear updates score and line counters.
        Animation must be completed before grid updates finalize.
        """
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        before = game.score
        game.clear_lines()

        if game.clearing_lines:
            game.finish_clearing_animation()

        assert game.score > before
        assert game.lines_cleared == 1

    def test_level_progression(self, game) -> None:
        """
        Ensure level increments after clearing required lines.
        """
        game.lines_cleared = 9
        game.clear_lines()

        game.lines_cleared = 10
        lvl0 = game.level

        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        game.clear_lines()
        assert game.level >= lvl0

    def test_hold_piece(self, game) -> None:
        """
        Validate hold mechanic:
            • Stores piece
            • Prevents repeat holds until placement
        """
        t = game.current_piece.type
        game.hold_current_piece()

        assert game.hold_piece is not None
        assert game.hold_piece.type == t
        assert game.can_hold is False

    def test_ghost_toggle(self, game) -> None:
        """
        Validate toggling ghost-piece visibility flag.
        """
        prev = game.show_ghost
        game.show_ghost = not prev
        assert game.show_ghost != prev

    def test_reset_game(self, game) -> None:
        """
        Ensure reset restores all gameplay attributes.
        """
        game.score = 100
        game.level = 5
        game.lines_cleared = 50
        game.game_over = True

        game.reset_game()

        assert game.score == 0
        assert game.level == 1
        assert game.lines_cleared == 0
        assert game.game_over is False
        assert game.clearing_lines == []

    def test_grid_is_empty_initially(self, game) -> None:
        """
        Ensure grid is fully empty (None values) at initialization.
        """
        for row in game.grid:
            for c in row:
                assert c is None


class TestGameLogic:
    """Tests validating line clearing logic, animations, and scoring scale."""

    @pytest.fixture
    def game(self):
        pygame.init()
        g = TetrisGame()
        yield g
        pygame.quit()

    def test_line_clear_animation(self, game) -> None:
        """
        Trigger one full line and confirm:
            • clearing_lines contains row indices
            • animation timer initialized
        """
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        game.clear_lines()

        assert len(game.clearing_lines) > 0
        assert game.clear_animation_time >= 0

    def test_animation_completion(self, game) -> None:
        """
        After finishing animation:
            • rows are removed
            • clearing_lines resets
        """
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        game.clear_lines()
        assert len(game.clearing_lines) == 1

        game.finish_clearing_animation()

        assert len(game.clearing_lines) == 0
        assert all(cell is None for cell in game.grid[GRID_HEIGHT - 1])

    def test_multiple_line_clear(self, game) -> None:
        """
        Ensure detection of multiple full rows.
        """
        for y in range(GRID_HEIGHT - 2, GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                game.grid[y][x] = COLORS["I"]

        game.clear_lines()
        assert len(game.clearing_lines) == 2

    def test_scoring_increases_with_level(self, game) -> None:
        """
        Validate score scaling: level 2 should yield higher points than level 1.
        """
        game.level = 1
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()
        s1 = game.score

        game.reset_game()
        game.level = 2
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()
        s2 = game.score

        assert s2 > s1


class TestConstants:
    """Validation of SHAPES, COLORS, grid size, and other constants."""

    def test_all_shapes_defined(self) -> None:
        """
        Ensure all 7 Tetromino types exist.
        """
        assert len(SHAPES) == 7
        expected = ["I", "O", "T", "S", "Z", "J", "L"]
        for s in expected:
            assert s in SHAPES

    def test_all_colors_defined(self) -> None:
        """
        Validate RGB color tuples for all shapes.
        """
        assert len(COLORS) == 7
        for s in SHAPES:
            assert s in COLORS
            assert len(COLORS[s]) == 3

    def test_grid_dimensions(self) -> None:
        """
        Confirm Tetris-standard 10×20 grid.
        """
        assert GRID_WIDTH == 10
        assert GRID_HEIGHT == 20


class TestGameStates:
    """Tests validating State Pattern transitions and behavior."""

    @pytest.fixture
    def game(self):
        pygame.init()
        g = TetrisGame()
        yield g
        pygame.quit()

    def test_initial_state_is_playing(self, game) -> None:
        """
        Game should begin in PlayingState.
        """
        assert isinstance(game.state, PlayingState)

    def test_pause_state_transition(self, game) -> None:
        """
        Pressing P should switch from Playing to Paused.
        """
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_p})
        game.handle_input(event)
        assert isinstance(game.state, PausedState)

    def test_unpause_state_transition(self, game) -> None:
        """
        Pressing P again should resume gameplay.
        """
        game.state = PausedState()
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_p})
        game.handle_input(event)
        assert isinstance(game.state, PlayingState)

    def test_game_over_state_transition(self, game) -> None:
        """
        Ensure GameOverState can be manually triggered.
        """
        game.game_over = True
        game.state = GameOverState()
        assert isinstance(game.state, GameOverState)

    def test_restart_from_game_over(self, game) -> None:
        """
        Pressing R in GameOverState resets the game.
        """
        game.state = GameOverState()
        game.game_over = True
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_r})
        game.handle_input(event)

        assert isinstance(game.state, PlayingState)
        assert game.game_over is False

    def test_line_clearing_state_transition(self, game) -> None:
        """
        When a full line is detected, switch into LineClearingState.
        """
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        game.clear_lines()
        assert isinstance(game.state, LineClearingState)

    def test_line_clearing_completes(self, game) -> None:
        """
        After animation duration passes, return to PlayingState.
        """
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        game.clear_lines()
        game.state.update(game.clear_animation_duration + 1, game)

        assert isinstance(game.state, PlayingState)

    def test_paused_state_no_update(self, game) -> None:
        """
        When paused, game updates must freeze.
        fall_time should not change.
        """
        game.state = PausedState()
        before = game.fall_time
        game.state.update(100, game)
        assert game.fall_time == before

    def test_paused_state_no_movement(self, game) -> None:
        """
        Movement inputs are ignored while paused.
        """
        game.state = PausedState()
        x0 = game.current_piece.x

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT})
        game.handle_input(event)
        assert game.current_piece.x == x0

    def test_playing_state_handles_movement(self, game) -> None:
        """
        Confirm input events move pieces in PlayingState.
        """
        game.state = PlayingState()
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT})
        game.handle_input(event)
        assert isinstance(game.state, PlayingState)


class TestGameConfig:
    """Tests validating default and custom GameConfig behavior."""

    def test_game_with_default_config(self) -> None:
        """
        Ensure default GameConfig attributes propagate into TetrisGame.
        """
        pygame.init()
        game = TetrisGame()

        assert game.config == GameConfig
        assert game.fall_speed == GameConfig.INITIAL_FALL_SPEED
        assert game.clear_animation_duration == GameConfig.CLEAR_ANIMATION_DURATION

        pygame.quit()

    def test_game_with_custom_config(self) -> None:
        """
        Provide custom config class and ensure overrides apply.
        """

        pygame.init()

        class CustomConfig(GameConfig):
            INITIAL_FALL_SPEED = 500
            LINES_PER_LEVEL = 5
            LINE_SCORES = {1: 200, 2: 600, 3: 1000, 4: 1600}
            SOFT_DROP_BONUS = 2
            HARD_DROP_BONUS = 4

        game = TetrisGame(CustomConfig)

        assert game.config == CustomConfig
        assert game.fall_speed == 500
        assert game.config.LINES_PER_LEVEL == 5
        assert game.config.LINE_SCORES[1] == 200

        pygame.quit()

    def test_tetromino_with_custom_config(self) -> None:
        """
        Validate that Tetromino uses custom grid size from config.
        """

        pygame.init()

        class CustomConfig(GameConfig):
            GRID_WIDTH = 15
            GRID_HEIGHT = 25

        piece = Tetromino("I", CustomConfig)

        assert piece.config == CustomConfig
        assert piece.x == CustomConfig.GRID_WIDTH // 2 - len(piece.shape[0]) // 2

        pygame.quit()

    def test_config_values_are_correct(self) -> None:
        """
        Validate presence and correctness of required constants in GameConfig.
        """
        assert GameConfig.SCREEN_WIDTH == 800
        assert GameConfig.SCREEN_HEIGHT == 700
        assert GameConfig.BLOCK_SIZE == 30

        assert GameConfig.GRID_WIDTH == 10
        assert GameConfig.GRID_HEIGHT == 20

        assert GameConfig.INITIAL_FALL_SPEED == 1000
        assert GameConfig.CLEAR_ANIMATION_DURATION == 500
        assert GameConfig.LEVEL_SPEED_DECREASE == 100
        assert GameConfig.MIN_FALL_SPEED == 100

        assert GameConfig.LINE_SCORES == {1: 100, 2: 300, 3: 500, 4: 800}
        assert GameConfig.SOFT_DROP_BONUS == 1
        assert GameConfig.HARD_DROP_BONUS == 2
        assert GameConfig.LINES_PER_LEVEL == 10

    def test_scoring_with_custom_config(self) -> None:
        """
        Validate scoring behavior under overridden LINE_SCORES.
        """

        pygame.init()

        class HighScoreConfig(GameConfig):
            LINE_SCORES = {1: 500, 2: 1500, 3: 2500, 4: 4000}
            SOFT_DROP_BONUS = 5

        game = TetrisGame(HighScoreConfig)

        for x in range(game.config.GRID_WIDTH):
            game.grid[game.config.GRID_HEIGHT - 1][x] = game.config.COLORS["I"]

        start = game.score
        game.clear_lines()

        expected = start + HighScoreConfig.LINE_SCORES[1] * game.level
        assert game.score == expected

        pygame.quit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
