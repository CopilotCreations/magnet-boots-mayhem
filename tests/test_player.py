"""Tests for player module."""

import pytest
from unittest.mock import MagicMock

from src.player import Player
from src.platforms import Platform
from src.constants import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_JUMP_STRENGTH,
    MAGNETIC_STATE_NORMAL, MAGNETIC_STATE_STICKING,
    ORIENTATION_FLOOR, ORIENTATION_CEILING, ORIENTATION_WALL_LEFT, ORIENTATION_WALL_RIGHT
)


class TestPlayerInit:
    """Tests for Player initialization."""
    
    def test_initialization(self):
        """Test player initialization with specified position.

        Verifies that the player is created with correct initial position,
        dimensions, velocity, magnetic state, and ground status.
        """
        player = Player(100, 200)
        assert player.x == 100
        assert player.y == 200
        assert player.width == PLAYER_WIDTH
        assert player.height == PLAYER_HEIGHT
        assert player.velocity_x == 0.0
        assert player.velocity_y == 0.0
        assert player.magnetic_state == MAGNETIC_STATE_NORMAL
        assert player.on_ground is False
        assert player.boots_active is True
    
    def test_initial_state(self):
        """Test player initial state values.

        Verifies that a new player has correct default state values including
        no current surface, floor orientation, facing right, and jump settings.
        """
        player = Player(0, 0)
        assert player.current_surface is None
        assert player.current_orientation == ORIENTATION_FLOOR
        assert player.facing_right is True
        assert player.jump_count == 0
        assert player.max_jumps == 2


class TestPlayerProperties:
    """Tests for Player properties."""
    
    def test_position_property(self):
        """Test position property returns center of the player.

        Verifies that the position property calculates and returns
        the center point of the player's bounding box.
        """
        player = Player(100, 200)
        center = player.position
        assert center == (100 + PLAYER_WIDTH / 2, 200 + PLAYER_HEIGHT / 2)
    
    def test_rect_property(self):
        """Test rect property returns bounding box tuple.

        Verifies that the rect property returns a tuple containing
        the player's x, y position and width, height dimensions.
        """
        player = Player(100, 200)
        assert player.rect == (100, 200, PLAYER_WIDTH, PLAYER_HEIGHT)
    
    def test_velocity_property(self):
        """Test velocity property returns velocity tuple.

        Verifies that the velocity property returns a tuple containing
        the player's current x and y velocity components.
        """
        player = Player(100, 200)
        player.velocity_x = 5.0
        player.velocity_y = 3.0
        assert player.velocity == (5.0, 3.0)


class TestPlayerMove:
    """Tests for move method."""
    
    def test_move_right(self):
        """Test moving player to the right.

        Verifies that moving right sets positive x velocity to PLAYER_SPEED
        and updates facing direction to right.
        """
        player = Player(100, 200)
        player.move(1, 0)
        assert player.velocity_x == PLAYER_SPEED
        assert player.facing_right is True
    
    def test_move_left(self):
        """Test moving player to the left.

        Verifies that moving left sets negative x velocity to -PLAYER_SPEED
        and updates facing direction to left.
        """
        player = Player(100, 200)
        player.move(-1, 0)
        assert player.velocity_x == -PLAYER_SPEED
        assert player.facing_right is False
    
    def test_move_when_sticking_floor(self):
        """Test horizontal movement when magnetically attached to floor.

        Verifies that horizontal movement is still possible when the player
        is in the sticking state on a floor-oriented surface.
        """
        player = Player(100, 200)
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.current_orientation = ORIENTATION_FLOOR
        player.move(1, 0)
        assert player.velocity_x == PLAYER_SPEED
    
    def test_move_when_sticking_wall(self):
        """Test vertical movement when magnetically attached to a wall.

        Verifies that vertical movement works correctly when the player
        is in the sticking state on a wall-oriented surface.
        """
        player = Player(100, 200)
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.current_orientation = ORIENTATION_WALL_LEFT
        player.move(0, -1)
        assert player.velocity_y == -PLAYER_SPEED


class TestPlayerJump:
    """Tests for jump method."""
    
    def test_jump_on_ground(self):
        """Test jumping when player is on the ground.

        Verifies that jumping from ground applies upward velocity,
        sets on_ground to False, and increments jump count.
        """
        player = Player(100, 200)
        player.on_ground = True
        result = player.jump()
        assert result is True
        assert player.velocity_y == -PLAYER_JUMP_STRENGTH
        assert player.on_ground is False
        assert player.jump_count == 1
    
    def test_double_jump(self):
        """Test performing a double jump in mid-air.

        Verifies that a second jump is allowed when the player has
        already jumped once but has not exceeded max_jumps.
        """
        player = Player(100, 200)
        player.on_ground = False
        player.jump_count = 1
        result = player.jump()
        assert result is True
        assert player.jump_count == 2
    
    def test_triple_jump_fails(self):
        """Test that a third jump attempt fails.

        Verifies that jump returns False when the player has already
        used the maximum number of allowed jumps.
        """
        player = Player(100, 200)
        player.on_ground = False
        player.jump_count = 2
        result = player.jump()
        assert result is False
    
    def test_jump_from_surface(self):
        """Test jumping off a magnetic surface.

        Verifies that jumping from a wall surface detaches the player,
        resets magnetic state to normal, and applies push-off velocity.
        """
        player = Player(100, 200)
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.current_orientation = ORIENTATION_WALL_LEFT
        
        result = player.jump()
        
        assert result is True
        assert player.magnetic_state == MAGNETIC_STATE_NORMAL
        assert player.velocity_x > 0  # Pushed away from left wall


class TestPlayerToggleMagneticState:
    """Tests for toggle_magnetic_state method."""
    
    def test_toggle_boots_off(self):
        """Test toggling magnetic boots from active to inactive.

        Verifies that calling toggle_magnetic_state when boots are active
        sets boots_active to False.
        """
        player = Player(100, 200)
        assert player.boots_active is True
        player.toggle_magnetic_state()
        assert player.boots_active is False
    
    def test_toggle_boots_on(self):
        """Test toggling magnetic boots from inactive to active.

        Verifies that calling toggle_magnetic_state when boots are inactive
        sets boots_active to True.
        """
        player = Player(100, 200)
        player.boots_active = False
        player.toggle_magnetic_state()
        assert player.boots_active is True
    
    def test_toggle_detaches_when_sticking(self):
        """Test that toggling boots off detaches player from surface.

        Verifies that disabling boots while magnetically attached causes
        the player to detach and return to normal magnetic state.
        """
        player = Player(100, 200)
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.current_surface = Platform(0, 0, 100, 20)
        
        player.toggle_magnetic_state()
        
        assert player.boots_active is False
        assert player.magnetic_state == MAGNETIC_STATE_NORMAL


class TestPlayerGravity:
    """Tests for gravity application."""
    
    def test_apply_gravity_normal(self):
        """Test gravity is applied when player is in normal state.

        Verifies that calling apply_gravity increases the player's
        downward velocity when not magnetically attached to a surface.
        """
        player = Player(100, 200)
        initial_velocity = player.velocity_y
        player.apply_gravity()
        assert player.velocity_y > initial_velocity
    
    def test_no_gravity_when_sticking(self):
        """Test gravity is not applied when magnetically attached.

        Verifies that apply_gravity has no effect on velocity when
        the player is in the sticking magnetic state.
        """
        player = Player(100, 200)
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.velocity_y = 0
        player.apply_gravity()
        assert player.velocity_y == 0


class TestPlayerStickToSurface:
    """Tests for stick_to_surface method."""
    
    def test_stick_to_magnetic_surface(self):
        """Test successfully sticking to a magnetic platform.

        Verifies that attaching to a magnetic surface updates magnetic state,
        stores the surface reference, sets orientation, resets velocity,
        and marks the player as on_ground.
        """
        player = Player(100, 200)
        platform = Platform(0, 250, 200, 30, is_magnetic=True)
        
        player.stick_to_surface(platform, ORIENTATION_FLOOR)
        
        assert player.magnetic_state == MAGNETIC_STATE_STICKING
        assert player.current_surface == platform
        assert player.current_orientation == ORIENTATION_FLOOR
        assert player.velocity_x == 0
        assert player.velocity_y == 0
        assert player.on_ground is True
    
    def test_no_stick_to_non_magnetic(self):
        """Test that player cannot stick to non-magnetic surfaces.

        Verifies that attempting to stick to a non-magnetic platform
        leaves the player in normal state with no current surface.
        """
        player = Player(100, 200)
        platform = Platform(0, 250, 200, 30, is_magnetic=False)
        
        player.stick_to_surface(platform, ORIENTATION_FLOOR)
        
        assert player.magnetic_state == MAGNETIC_STATE_NORMAL
        assert player.current_surface is None
    
    def test_no_stick_when_boots_off(self):
        """Test that player cannot stick when magnetic boots are disabled.

        Verifies that stick_to_surface has no effect when boots_active
        is False, even on a magnetic platform.
        """
        player = Player(100, 200)
        player.boots_active = False
        platform = Platform(0, 250, 200, 30, is_magnetic=True)
        
        player.stick_to_surface(platform, ORIENTATION_FLOOR)
        
        assert player.magnetic_state == MAGNETIC_STATE_NORMAL


class TestPlayerDetachFromSurface:
    """Tests for detach_from_surface method."""
    
    def test_detach(self):
        """Test detaching player from a magnetic surface.

        Verifies that detach_from_surface resets magnetic state to normal,
        clears the current surface reference, and sets on_ground to False.
        """
        player = Player(100, 200)
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.current_surface = Platform(0, 0, 100, 20)
        player.on_ground = True
        
        player.detach_from_surface()
        
        assert player.magnetic_state == MAGNETIC_STATE_NORMAL
        assert player.current_surface is None
        assert player.on_ground is False


class TestPlayerApplyMagneticForce:
    """Tests for apply_magnetic_force method."""
    
    def test_apply_force_normal_state(self):
        """Test magnetic force is applied when player is in normal state.

        Verifies that apply_magnetic_force adds the force vector to
        the player's velocity when not magnetically attached.
        """
        player = Player(100, 200)
        player.apply_magnetic_force((5.0, -3.0))
        assert player.velocity_x == 5.0
        assert player.velocity_y == -3.0
    
    def test_no_force_when_sticking(self):
        """Test magnetic force is ignored when magnetically attached.

        Verifies that apply_magnetic_force has no effect on velocity
        when the player is in the sticking magnetic state.
        """
        player = Player(100, 200)
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.apply_magnetic_force((5.0, -3.0))
        assert player.velocity_x == 0
        assert player.velocity_y == 0


class TestPlayerUpdate:
    """Tests for update method."""
    
    def test_update_applies_velocity(self):
        """Test that update method applies velocity to player position.

        Verifies that calling update with velocity set causes the player's
        position to change based on the current velocity values.
        """
        player = Player(100, 200)
        player.velocity_x = 10
        player.velocity_y = 5
        
        player.update([])
        
        # Position should have changed (though gravity also applied)
        assert player.x != 100 or player.y != 200
    
    def test_update_collision_detection(self):
        """Test that update method handles platform collision detection.

        Verifies that the player stops and lands on a platform when
        moving downward and colliding with a platform below.
        """
        player = Player(100, 200)
        player.velocity_y = 10
        platform = Platform(0, 230, 200, 30, is_magnetic=False)
        
        player.update([platform])
        
        # Player should have landed on platform
        assert player.y <= 230 - player.height + 5  # Allowing some tolerance


class TestPlayerReset:
    """Tests for reset method."""
    
    def test_reset(self):
        """Test resetting player to a new position with default state.

        Verifies that reset moves the player to the specified position and
        restores all state values to their defaults including velocity,
        magnetic state, boots active status, and jump count.
        """
        player = Player(100, 200)
        player.velocity_x = 10
        player.velocity_y = -5
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.boots_active = False
        
        player.reset(50, 100)
        
        assert player.x == 50
        assert player.y == 100
        assert player.velocity_x == 0
        assert player.velocity_y == 0
        assert player.magnetic_state == MAGNETIC_STATE_NORMAL
        assert player.boots_active is True
        assert player.jump_count == 0
