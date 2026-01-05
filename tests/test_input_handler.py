"""Tests for input_handler module."""

import pytest
from unittest.mock import MagicMock, patch
import pygame

from src.input_handler import InputHandler, InputAction, create_game_input_handler


class TestInputHandlerInit:
    """Tests for InputHandler initialization."""
    
    def test_default_initialization(self):
        """Test handler with default bindings.

        Verifies that a new InputHandler instance is created with default
        key bindings and empty key state sets.
        """
        handler = InputHandler()
        assert handler.bindings == InputHandler.DEFAULT_BINDINGS
        assert len(handler.keys_pressed) == 0
        assert len(handler.keys_just_pressed) == 0
        assert len(handler.keys_just_released) == 0
    
    def test_custom_bindings(self):
        """Test handler with custom bindings.

        Verifies that custom bindings override defaults while preserving
        other default bindings.
        """
        custom = {'jump': pygame.K_w}
        handler = InputHandler(custom_bindings=custom)
        assert handler.bindings['jump'] == pygame.K_w
        # Other bindings should still exist
        assert 'move_left' in handler.bindings


class TestInputHandlerUpdate:
    """Tests for update method."""
    
    def test_keydown_event(self):
        """Test handling keydown event.

        Verifies that a KEYDOWN event adds the key to both keys_pressed
        and keys_just_pressed sets.
        """
        handler = InputHandler()
        
        keydown_event = MagicMock()
        keydown_event.type = pygame.KEYDOWN
        keydown_event.key = pygame.K_SPACE
        
        handler.update([keydown_event])
        
        assert pygame.K_SPACE in handler.keys_pressed
        assert pygame.K_SPACE in handler.keys_just_pressed
    
    def test_keyup_event(self):
        """Test handling keyup event.

        Verifies that a KEYUP event removes the key from keys_pressed
        and adds it to keys_just_released.
        """
        handler = InputHandler()
        handler.keys_pressed.add(pygame.K_SPACE)
        
        keyup_event = MagicMock()
        keyup_event.type = pygame.KEYUP
        keyup_event.key = pygame.K_SPACE
        
        handler.update([keyup_event])
        
        assert pygame.K_SPACE not in handler.keys_pressed
        assert pygame.K_SPACE in handler.keys_just_released
    
    def test_just_pressed_cleared_each_frame(self):
        """Test just_pressed is cleared each frame.

        Verifies that keys_just_pressed is cleared at the start of each
        update call to ensure single-frame detection.
        """
        handler = InputHandler()
        handler.keys_just_pressed.add(pygame.K_SPACE)
        
        handler.update([])
        
        assert pygame.K_SPACE not in handler.keys_just_pressed


class TestInputHandlerActionChecks:
    """Tests for action check methods."""
    
    def test_is_action_pressed(self):
        """Test is_action_pressed method.

        Verifies that is_action_pressed returns True when the bound key
        is in keys_pressed and False otherwise.
        """
        handler = InputHandler()
        handler.keys_pressed.add(pygame.K_SPACE)
        
        assert handler.is_action_pressed('jump') is True
        assert handler.is_action_pressed('toggle_magnetic') is False
    
    def test_is_action_pressed_alt_key(self):
        """Test is_action_pressed with alternate key.

        Verifies that actions with alternate key bindings are correctly
        detected when the alternate key is pressed.
        """
        handler = InputHandler()
        handler.keys_pressed.add(pygame.K_a)
        
        assert handler.is_action_pressed('move_left') is True
    
    def test_is_action_just_pressed(self):
        """Test is_action_just_pressed method.

        Verifies that is_action_just_pressed returns True only when the
        bound key is in keys_just_pressed set.
        """
        handler = InputHandler()
        handler.keys_just_pressed.add(pygame.K_SPACE)
        
        assert handler.is_action_just_pressed('jump') is True
        assert handler.is_action_just_pressed('toggle_magnetic') is False
    
    def test_is_action_just_released(self):
        """Test is_action_just_released method.

        Verifies that is_action_just_released returns True only when the
        bound key is in keys_just_released set.
        """
        handler = InputHandler()
        handler.keys_just_released.add(pygame.K_SPACE)
        
        assert handler.is_action_just_released('jump') is True
        assert handler.is_action_just_released('toggle_magnetic') is False
    
    def test_unknown_action(self):
        """Test checking unknown action.

        Verifies that checking an unbound action name returns False
        rather than raising an error.
        """
        handler = InputHandler()
        assert handler.is_action_pressed('unknown_action') is False


class TestInputHandlerMovementVector:
    """Tests for get_movement_vector method."""
    
    def test_no_movement(self):
        """Test movement vector with no keys pressed.

        Verifies that the movement vector is (0, 0) when no movement
        keys are pressed.
        """
        handler = InputHandler()
        assert handler.get_movement_vector() == (0, 0)
    
    def test_move_right(self):
        """Test movement vector for right.

        Verifies that pressing the right arrow key returns (1, 0).
        """
        handler = InputHandler()
        handler.keys_pressed.add(pygame.K_RIGHT)
        assert handler.get_movement_vector() == (1, 0)
    
    def test_move_left(self):
        """Test movement vector for left.

        Verifies that pressing the left arrow key returns (-1, 0).
        """
        handler = InputHandler()
        handler.keys_pressed.add(pygame.K_LEFT)
        assert handler.get_movement_vector() == (-1, 0)
    
    def test_move_up(self):
        """Test movement vector for up.

        Verifies that pressing the up arrow key returns (0, -1).
        """
        handler = InputHandler()
        handler.keys_pressed.add(pygame.K_UP)
        assert handler.get_movement_vector() == (0, -1)
    
    def test_move_down(self):
        """Test movement vector for down.

        Verifies that pressing the down arrow key returns (0, 1).
        """
        handler = InputHandler()
        handler.keys_pressed.add(pygame.K_DOWN)
        assert handler.get_movement_vector() == (0, 1)
    
    def test_diagonal_movement(self):
        """Test diagonal movement vector.

        Verifies that pressing both right and up keys returns (1, -1)
        for diagonal movement.
        """
        handler = InputHandler()
        handler.keys_pressed.add(pygame.K_RIGHT)
        handler.keys_pressed.add(pygame.K_UP)
        assert handler.get_movement_vector() == (1, -1)
    
    def test_opposite_keys_cancel(self):
        """Test opposite keys cancel out.

        Verifies that pressing both left and right keys results in
        zero horizontal movement.
        """
        handler = InputHandler()
        handler.keys_pressed.add(pygame.K_LEFT)
        handler.keys_pressed.add(pygame.K_RIGHT)
        assert handler.get_movement_vector()[0] == 0


class TestInputHandlerBindings:
    """Tests for binding methods."""
    
    def test_set_binding(self):
        """Test setting custom binding.

        Verifies that set_binding correctly updates the key binding
        for an action.
        """
        handler = InputHandler()
        handler.set_binding('jump', pygame.K_w)
        assert handler.bindings['jump'] == pygame.K_w
    
    def test_get_binding(self):
        """Test getting binding.

        Verifies that get_binding returns the correct key code for
        a bound action.
        """
        handler = InputHandler()
        assert handler.get_binding('jump') == pygame.K_SPACE
    
    def test_get_binding_nonexistent(self):
        """Test getting nonexistent binding.

        Verifies that get_binding returns None for an action that
        does not exist in the bindings.
        """
        handler = InputHandler()
        assert handler.get_binding('nonexistent') is None
    
    def test_get_binding_name(self):
        """Test getting binding name.

        Verifies that get_binding_name returns the human-readable
        name of the key bound to an action.
        """
        handler = InputHandler()
        name = handler.get_binding_name('jump')
        assert name == 'SPACE'
    
    def test_get_binding_name_unbound(self):
        """Test getting name for unbound action.

        Verifies that get_binding_name returns 'Unbound' for actions
        that do not have a key binding.
        """
        handler = InputHandler()
        assert handler.get_binding_name('nonexistent') == 'Unbound'
    
    def test_reset_to_defaults(self):
        """Test resetting to default bindings.

        Verifies that reset_to_defaults restores all bindings to their
        original default values.
        """
        handler = InputHandler()
        handler.set_binding('jump', pygame.K_w)
        handler.reset_to_defaults()
        assert handler.bindings['jump'] == pygame.K_SPACE


class TestInputAction:
    """Tests for InputAction class."""
    
    def test_initialization(self):
        """Test action initialization.

        Verifies that a new InputAction is created with the given name
        and all callbacks set to None.
        """
        action = InputAction('test')
        assert action.name == 'test'
        assert action.on_pressed is None
        assert action.on_released is None
        assert action.on_held is None
    
    def test_bind_pressed(self):
        """Test binding pressed callback.

        Verifies that bind_pressed sets the on_pressed callback and
        returns the action for fluent chaining.
        """
        action = InputAction('test')
        callback = MagicMock()
        
        result = action.bind_pressed(callback)
        
        assert action.on_pressed == callback
        assert result == action  # Fluent interface
    
    def test_bind_released(self):
        """Test binding released callback.

        Verifies that bind_released sets the on_released callback and
        returns the action for fluent chaining.
        """
        action = InputAction('test')
        callback = MagicMock()
        
        result = action.bind_released(callback)
        
        assert action.on_released == callback
        assert result == action
    
    def test_bind_held(self):
        """Test binding held callback.

        Verifies that bind_held sets the on_held callback and returns
        the action for fluent chaining.
        """
        action = InputAction('test')
        callback = MagicMock()
        
        result = action.bind_held(callback)
        
        assert action.on_held == callback
        assert result == action
    
    def test_fluent_chaining(self):
        """Test fluent interface chaining.

        Verifies that all bind methods can be chained together in a
        single expression to set multiple callbacks.
        """
        action = InputAction('test')
        pressed = MagicMock()
        released = MagicMock()
        held = MagicMock()
        
        action.bind_pressed(pressed).bind_released(released).bind_held(held)
        
        assert action.on_pressed == pressed
        assert action.on_released == released
        assert action.on_held == held


class TestCreateGameInputHandler:
    """Tests for create_game_input_handler factory function."""
    
    def test_creates_handler(self):
        """Test factory creates input handler.

        Verifies that the factory function returns a valid InputHandler
        instance configured for game use.
        """
        handler = create_game_input_handler()
        assert isinstance(handler, InputHandler)
