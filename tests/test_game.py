"""Tests for game module."""

import pytest
from unittest.mock import MagicMock, patch

# Mock pygame before importing game module
pygame_mock = MagicMock()


class TestGameState:
    """Tests for GameState enum."""
    
    def test_game_states_exist(self):
        """Test all expected game states exist."""
        from src.game import GameState
        
        assert hasattr(GameState, 'MENU')
        assert hasattr(GameState, 'PLAYING')
        assert hasattr(GameState, 'PAUSED')
        assert hasattr(GameState, 'LEVEL_COMPLETE')
        assert hasattr(GameState, 'GAME_OVER')
    
    def test_states_are_unique(self):
        """Test all states have unique values."""
        from src.game import GameState
        
        states = [GameState.MENU, GameState.PLAYING, GameState.PAUSED,
                  GameState.LEVEL_COMPLETE, GameState.GAME_OVER]
        values = [s.value for s in states]
        assert len(values) == len(set(values))


class TestGameInit:
    """Tests for Game initialization."""
    
    @patch('src.game.pygame')
    def test_initialization(self, mock_pygame):
        """Test game initializes correctly."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        
        assert game.running is True
        assert game.state == GameState.MENU
        assert game.player is None
        assert game.current_level is None
        assert len(game.levels) > 0
    
    @patch('src.game.pygame')
    def test_levels_loaded(self, mock_pygame):
        """Test levels are loaded on init."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game
        
        game = Game()
        
        assert len(game.levels) >= 2  # Tutorial and demo
        assert game.levels[0].name == "Tutorial"
        assert game.levels[1].name == "Demo Level"


class TestGameStartLevel:
    """Tests for _start_level method."""
    
    @patch('src.game.pygame')
    def test_start_valid_level(self, mock_pygame):
        """Test starting a valid level."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        game._start_level(0)
        
        assert game.current_level_index == 0
        assert game.current_level is not None
        assert game.player is not None
        assert game.state == GameState.PLAYING
    
    @patch('src.game.pygame')
    def test_start_invalid_level(self, mock_pygame):
        """Test starting an invalid level index."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        initial_state = game.state
        game._start_level(999)
        
        # State should not change
        assert game.state == initial_state


class TestGameRestartLevel:
    """Tests for _restart_level method."""
    
    @patch('src.game.pygame')
    def test_restart_level(self, mock_pygame):
        """Test restarting current level."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        game._start_level(0)
        
        # Modify player position
        game.player.x = 500
        game.player.y = 300
        
        game._restart_level()
        
        assert game.state == GameState.PLAYING
        assert game.player.x == game.current_level.player_start[0]
        assert game.player.y == game.current_level.player_start[1]


class TestGameNextLevel:
    """Tests for _next_level method."""
    
    @patch('src.game.pygame')
    def test_next_level_exists(self, mock_pygame):
        """Test advancing to next level when it exists."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        game._start_level(0)
        
        game._next_level()
        
        assert game.current_level_index == 1
        assert game.state == GameState.PLAYING
    
    @patch('src.game.pygame')
    def test_next_level_not_exists(self, mock_pygame):
        """Test advancing when no more levels."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        game._start_level(len(game.levels) - 1)  # Start last level
        
        game._next_level()
        
        assert game.state == GameState.MENU


class TestGameHandleEvents:
    """Tests for handle_events method."""
    
    @patch('src.game.pygame')
    def test_quit_event(self, mock_pygame):
        """Test handling quit event."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        mock_pygame.QUIT = 256
        
        quit_event = MagicMock()
        quit_event.type = 256
        mock_pygame.event.get.return_value = [quit_event]
        
        from src.game import Game
        
        game = Game()
        game.handle_events()
        
        assert game.running is False


class TestGameUpdateMenu:
    """Tests for update_menu method."""
    
    @patch('src.game.pygame')
    def test_menu_navigation_up(self, mock_pygame):
        """Test menu navigation up."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game
        
        game = Game()
        game.menu_selection = 1
        game.input_handler.keys_just_pressed.add(mock_pygame.K_UP)
        game.input_handler.is_action_just_pressed = lambda a: a == 'move_up'
        
        game.update_menu()
        
        assert game.menu_selection == 0
    
    @patch('src.game.pygame')
    def test_menu_navigation_down(self, mock_pygame):
        """Test menu navigation down."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game
        
        game = Game()
        game.menu_selection = 0
        game.input_handler.is_action_just_pressed = lambda a: a == 'move_down'
        
        game.update_menu()
        
        assert game.menu_selection == 1
    
    @patch('src.game.pygame')
    def test_menu_quit_selection(self, mock_pygame):
        """Test selecting quit from menu."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game
        
        game = Game()
        game.menu_selection = 2  # Quit
        game.input_handler.is_action_just_pressed = lambda a: a == 'jump'
        
        game.update_menu()
        
        assert game.running is False


class TestGameUpdatePlaying:
    """Tests for update_playing method."""
    
    @patch('src.game.pygame')
    def test_pause_game(self, mock_pygame):
        """Test pausing game."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        game._start_level(0)
        game.input_handler.is_action_just_pressed = lambda a: a == 'pause'
        
        game.update_playing()
        
        assert game.state == GameState.PAUSED
    
    @patch('src.game.pygame')
    def test_player_falls_off_level(self, mock_pygame):
        """Test game over when player falls off level."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        game._start_level(0)
        game.player.y = game.current_level.height + 200
        game.input_handler.is_action_just_pressed = lambda a: False
        game.input_handler.is_action_pressed = lambda a: False
        game.input_handler.get_movement_vector = lambda: (0, 0)
        
        game.update_playing()
        
        assert game.state == GameState.GAME_OVER


class TestGameUpdatePaused:
    """Tests for update_paused method."""
    
    @patch('src.game.pygame')
    def test_unpause_game(self, mock_pygame):
        """Test unpausing game."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        game._start_level(0)
        game.state = GameState.PAUSED
        game.input_handler.is_action_just_pressed = lambda a: a == 'pause'
        
        game.update_paused()
        
        assert game.state == GameState.PLAYING
    
    @patch('src.game.pygame')
    def test_restart_from_pause(self, mock_pygame):
        """Test restarting from pause."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        game._start_level(0)
        game.state = GameState.PAUSED
        game.player.x = 500  # Modify position
        game.input_handler.is_action_just_pressed = lambda a: a == 'restart'
        
        game.update_paused()
        
        assert game.state == GameState.PLAYING
        assert game.player.x == game.current_level.player_start[0]


class TestGameUpdateLevelComplete:
    """Tests for update_level_complete method."""
    
    @patch('src.game.pygame')
    def test_advance_level(self, mock_pygame):
        """Test advancing to next level."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        game._start_level(0)
        game.state = GameState.LEVEL_COMPLETE
        game.input_handler.is_action_just_pressed = lambda a: a == 'jump'
        
        game.update_level_complete()
        
        assert game.current_level_index == 1


class TestGameUpdateGameOver:
    """Tests for update_game_over method."""
    
    @patch('src.game.pygame')
    def test_restart_after_game_over(self, mock_pygame):
        """Test restarting after game over."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        game._start_level(0)
        game.state = GameState.GAME_OVER
        game.input_handler.is_action_just_pressed = lambda a: a == 'restart'
        
        game.update_game_over()
        
        assert game.state == GameState.PLAYING
    
    @patch('src.game.pygame')
    def test_menu_after_game_over(self, mock_pygame):
        """Test returning to menu after game over."""
        mock_pygame.display.set_mode.return_value = MagicMock()
        
        from src.game import Game, GameState
        
        game = Game()
        game._start_level(0)
        game.state = GameState.GAME_OVER
        game.input_handler.is_action_just_pressed = lambda a: a == 'pause'
        
        game.update_game_over()
        
        assert game.state == GameState.MENU
