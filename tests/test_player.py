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
        """Test player with initial position."""
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
        """Test player initial state values."""
        player = Player(0, 0)
        assert player.current_surface is None
        assert player.current_orientation == ORIENTATION_FLOOR
        assert player.facing_right is True
        assert player.jump_count == 0
        assert player.max_jumps == 2


class TestPlayerProperties:
    """Tests for Player properties."""
    
    def test_position_property(self):
        """Test position property returns center."""
        player = Player(100, 200)
        center = player.position
        assert center == (100 + PLAYER_WIDTH / 2, 200 + PLAYER_HEIGHT / 2)
    
    def test_rect_property(self):
        """Test rect property."""
        player = Player(100, 200)
        assert player.rect == (100, 200, PLAYER_WIDTH, PLAYER_HEIGHT)
    
    def test_velocity_property(self):
        """Test velocity property."""
        player = Player(100, 200)
        player.velocity_x = 5.0
        player.velocity_y = 3.0
        assert player.velocity == (5.0, 3.0)


class TestPlayerMove:
    """Tests for move method."""
    
    def test_move_right(self):
        """Test moving right."""
        player = Player(100, 200)
        player.move(1, 0)
        assert player.velocity_x == PLAYER_SPEED
        assert player.facing_right is True
    
    def test_move_left(self):
        """Test moving left."""
        player = Player(100, 200)
        player.move(-1, 0)
        assert player.velocity_x == -PLAYER_SPEED
        assert player.facing_right is False
    
    def test_move_when_sticking_floor(self):
        """Test movement when sticking to floor."""
        player = Player(100, 200)
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.current_orientation = ORIENTATION_FLOOR
        player.move(1, 0)
        assert player.velocity_x == PLAYER_SPEED
    
    def test_move_when_sticking_wall(self):
        """Test movement when sticking to wall."""
        player = Player(100, 200)
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.current_orientation = ORIENTATION_WALL_LEFT
        player.move(0, -1)
        assert player.velocity_y == -PLAYER_SPEED


class TestPlayerJump:
    """Tests for jump method."""
    
    def test_jump_on_ground(self):
        """Test jumping from ground."""
        player = Player(100, 200)
        player.on_ground = True
        result = player.jump()
        assert result is True
        assert player.velocity_y == -PLAYER_JUMP_STRENGTH
        assert player.on_ground is False
        assert player.jump_count == 1
    
    def test_double_jump(self):
        """Test double jump."""
        player = Player(100, 200)
        player.on_ground = False
        player.jump_count = 1
        result = player.jump()
        assert result is True
        assert player.jump_count == 2
    
    def test_triple_jump_fails(self):
        """Test third jump fails."""
        player = Player(100, 200)
        player.on_ground = False
        player.jump_count = 2
        result = player.jump()
        assert result is False
    
    def test_jump_from_surface(self):
        """Test jumping off magnetic surface."""
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
        """Test toggling boots off."""
        player = Player(100, 200)
        assert player.boots_active is True
        player.toggle_magnetic_state()
        assert player.boots_active is False
    
    def test_toggle_boots_on(self):
        """Test toggling boots on."""
        player = Player(100, 200)
        player.boots_active = False
        player.toggle_magnetic_state()
        assert player.boots_active is True
    
    def test_toggle_detaches_when_sticking(self):
        """Test toggling boots off detaches from surface."""
        player = Player(100, 200)
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.current_surface = Platform(0, 0, 100, 20)
        
        player.toggle_magnetic_state()
        
        assert player.boots_active is False
        assert player.magnetic_state == MAGNETIC_STATE_NORMAL


class TestPlayerGravity:
    """Tests for gravity application."""
    
    def test_apply_gravity_normal(self):
        """Test gravity is applied in normal state."""
        player = Player(100, 200)
        initial_velocity = player.velocity_y
        player.apply_gravity()
        assert player.velocity_y > initial_velocity
    
    def test_no_gravity_when_sticking(self):
        """Test gravity is not applied when sticking."""
        player = Player(100, 200)
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.velocity_y = 0
        player.apply_gravity()
        assert player.velocity_y == 0


class TestPlayerStickToSurface:
    """Tests for stick_to_surface method."""
    
    def test_stick_to_magnetic_surface(self):
        """Test sticking to magnetic surface."""
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
        """Test cannot stick to non-magnetic surface."""
        player = Player(100, 200)
        platform = Platform(0, 250, 200, 30, is_magnetic=False)
        
        player.stick_to_surface(platform, ORIENTATION_FLOOR)
        
        assert player.magnetic_state == MAGNETIC_STATE_NORMAL
        assert player.current_surface is None
    
    def test_no_stick_when_boots_off(self):
        """Test cannot stick when boots are off."""
        player = Player(100, 200)
        player.boots_active = False
        platform = Platform(0, 250, 200, 30, is_magnetic=True)
        
        player.stick_to_surface(platform, ORIENTATION_FLOOR)
        
        assert player.magnetic_state == MAGNETIC_STATE_NORMAL


class TestPlayerDetachFromSurface:
    """Tests for detach_from_surface method."""
    
    def test_detach(self):
        """Test detaching from surface."""
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
        """Test magnetic force is applied in normal state."""
        player = Player(100, 200)
        player.apply_magnetic_force((5.0, -3.0))
        assert player.velocity_x == 5.0
        assert player.velocity_y == -3.0
    
    def test_no_force_when_sticking(self):
        """Test magnetic force not applied when sticking."""
        player = Player(100, 200)
        player.magnetic_state = MAGNETIC_STATE_STICKING
        player.apply_magnetic_force((5.0, -3.0))
        assert player.velocity_x == 0
        assert player.velocity_y == 0


class TestPlayerUpdate:
    """Tests for update method."""
    
    def test_update_applies_velocity(self):
        """Test update applies velocity to position."""
        player = Player(100, 200)
        player.velocity_x = 10
        player.velocity_y = 5
        
        player.update([])
        
        # Position should have changed (though gravity also applied)
        assert player.x != 100 or player.y != 200
    
    def test_update_collision_detection(self):
        """Test update handles platform collision."""
        player = Player(100, 200)
        player.velocity_y = 10
        platform = Platform(0, 230, 200, 30, is_magnetic=False)
        
        player.update([platform])
        
        # Player should have landed on platform
        assert player.y <= 230 - player.height + 5  # Allowing some tolerance


class TestPlayerReset:
    """Tests for reset method."""
    
    def test_reset(self):
        """Test player reset to position."""
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
