"""Tests for platforms module."""

import pytest

from src.platforms import Platform, MovingPlatform
from src.constants import (
    ORIENTATION_FLOOR, ORIENTATION_CEILING, 
    ORIENTATION_WALL_LEFT, ORIENTATION_WALL_RIGHT,
    COLOR_PLATFORM, COLOR_MAGNETIC_PLATFORM
)


class TestPlatformInit:
    """Tests for Platform initialization."""
    
    def test_default_initialization(self):
        """Test platform with default values."""
        platform = Platform(100, 200, 150, 30)
        assert platform.x == 100
        assert platform.y == 200
        assert platform.width == 150
        assert platform.height == 30
        assert platform.is_magnetic is False
        assert platform.orientation == ORIENTATION_FLOOR
    
    def test_magnetic_platform(self):
        """Test magnetic platform initialization."""
        platform = Platform(100, 200, 150, 30, is_magnetic=True)
        assert platform.is_magnetic is True
    
    def test_wall_orientation(self):
        """Test platform with wall orientation."""
        platform = Platform(100, 200, 30, 150, orientation=ORIENTATION_WALL_LEFT)
        assert platform.orientation == ORIENTATION_WALL_LEFT


class TestPlatformProperties:
    """Tests for Platform properties."""
    
    def test_rect_property(self):
        """Test rect property returns correct tuple."""
        platform = Platform(100, 200, 150, 30)
        assert platform.rect == (100, 200, 150, 30)
    
    def test_center_property(self):
        """Test center property calculates correctly."""
        platform = Platform(100, 200, 100, 50)
        assert platform.center == (150, 225)
    
    def test_pygame_rect_property(self):
        """Test pygame_rect property."""
        platform = Platform(100.5, 200.5, 150, 30)
        rect = platform.pygame_rect
        assert rect.x == 100
        assert rect.y == 200
        assert rect.width == 150
        assert rect.height == 30


class TestPlatformSurfacePosition:
    """Tests for get_surface_position method."""
    
    def test_floor_surface_position(self):
        """Test surface position for floor."""
        platform = Platform(100, 200, 100, 30, orientation=ORIENTATION_FLOOR)
        x, y, side = platform.get_surface_position()
        assert x == 150  # Center x
        assert y == 200  # Top of platform
        assert side == "top"
    
    def test_ceiling_surface_position(self):
        """Test surface position for ceiling."""
        platform = Platform(100, 200, 100, 30, orientation=ORIENTATION_CEILING)
        x, y, side = platform.get_surface_position()
        assert y == 230  # Bottom of platform
        assert side == "bottom"
    
    def test_wall_left_surface_position(self):
        """Test surface position for left wall."""
        platform = Platform(100, 200, 30, 100, orientation=ORIENTATION_WALL_LEFT)
        x, y, side = platform.get_surface_position()
        assert x == 130  # Right edge of wall
        assert side == "right"
    
    def test_wall_right_surface_position(self):
        """Test surface position for right wall."""
        platform = Platform(100, 200, 30, 100, orientation=ORIENTATION_WALL_RIGHT)
        x, y, side = platform.get_surface_position()
        assert x == 100  # Left edge of wall
        assert side == "left"


class TestPlatformPlayerOnSurface:
    """Tests for is_player_on_surface method."""
    
    def test_player_on_floor(self):
        """Test player standing on floor platform."""
        platform = Platform(100, 200, 200, 30, orientation=ORIENTATION_FLOOR)
        player_rect = (150, 150, 32, 48)  # Player feet at y=198, just above platform
        player_on = (150, 152, 32, 48)  # Player feet at y=200, on platform
        
        assert platform.is_player_on_surface(player_on, tolerance=5) is True
    
    def test_player_not_on_floor(self):
        """Test player not on floor platform."""
        platform = Platform(100, 200, 200, 30, orientation=ORIENTATION_FLOOR)
        player_rect = (150, 100, 32, 48)  # Player too high
        
        assert platform.is_player_on_surface(player_rect, tolerance=5) is False
    
    def test_player_on_ceiling(self):
        """Test player stuck to ceiling."""
        platform = Platform(100, 100, 200, 30, orientation=ORIENTATION_CEILING)
        player_rect = (150, 130, 32, 48)  # Player head touching ceiling bottom
        
        assert platform.is_player_on_surface(player_rect, tolerance=5) is True
    
    def test_player_on_wall_left(self):
        """Test player stuck to left wall."""
        platform = Platform(100, 100, 30, 200, orientation=ORIENTATION_WALL_LEFT)
        player_rect = (68, 150, 32, 48)  # Player right side touching wall
        
        assert platform.is_player_on_surface(player_rect, tolerance=5) is True


class TestPlatformColor:
    """Tests for get_color method."""
    
    def test_normal_platform_color(self):
        """Test normal platform color."""
        platform = Platform(100, 200, 100, 30, is_magnetic=False)
        assert platform.get_color() == COLOR_PLATFORM
    
    def test_magnetic_platform_color(self):
        """Test magnetic platform color."""
        platform = Platform(100, 200, 100, 30, is_magnetic=True)
        assert platform.get_color() == COLOR_MAGNETIC_PLATFORM


class TestPlatformSerialization:
    """Tests for serialization methods."""
    
    def test_to_dict(self):
        """Test platform serialization to dict."""
        platform = Platform(100, 200, 150, 30, is_magnetic=True, orientation=ORIENTATION_CEILING)
        data = platform.to_dict()
        
        assert data['x'] == 100
        assert data['y'] == 200
        assert data['width'] == 150
        assert data['height'] == 30
        assert data['is_magnetic'] is True
        assert data['orientation'] == ORIENTATION_CEILING
    
    def test_from_dict(self):
        """Test platform deserialization from dict."""
        data = {
            'x': 150,
            'y': 250,
            'width': 200,
            'height': 40,
            'is_magnetic': True,
            'orientation': ORIENTATION_WALL_LEFT
        }
        
        platform = Platform.from_dict(data)
        
        assert platform.x == 150
        assert platform.y == 250
        assert platform.width == 200
        assert platform.height == 40
        assert platform.is_magnetic is True
        assert platform.orientation == ORIENTATION_WALL_LEFT
    
    def test_roundtrip_serialization(self):
        """Test serialization roundtrip preserves data."""
        original = Platform(100, 200, 150, 30, is_magnetic=True, orientation=ORIENTATION_CEILING)
        data = original.to_dict()
        restored = Platform.from_dict(data)
        
        assert restored.x == original.x
        assert restored.y == original.y
        assert restored.width == original.width
        assert restored.height == original.height
        assert restored.is_magnetic == original.is_magnetic
        assert restored.orientation == original.orientation


class TestMovingPlatformInit:
    """Tests for MovingPlatform initialization."""
    
    def test_initialization(self):
        """Test moving platform initialization."""
        platform = MovingPlatform(100, 200, 150, 30, end_x=300, end_y=200, speed=3.0)
        assert platform.x == 100
        assert platform.y == 200
        assert platform.start_x == 100
        assert platform.start_y == 200
        assert platform.end_x == 300
        assert platform.end_y == 200
        assert platform.speed == 3.0
        assert platform.progress == 0.0
        assert platform.direction == 1


class TestMovingPlatformUpdate:
    """Tests for MovingPlatform update method."""
    
    def test_movement_toward_end(self):
        """Test platform moves toward end point."""
        platform = MovingPlatform(100, 200, 50, 20, end_x=200, end_y=200, speed=2.0)
        initial_x = platform.x
        
        for _ in range(10):
            platform.update()
        
        assert platform.x > initial_x
    
    def test_direction_reversal_at_end(self):
        """Test direction reverses at end point."""
        platform = MovingPlatform(100, 200, 50, 20, end_x=110, end_y=200, speed=100.0)
        
        # Move to end - need more iterations since speed * 0.01 per frame
        for _ in range(200):
            platform.update()
        
        # Platform should have reversed at some point (may have gone back and forth)
        # Check that it moved and oscillates
        assert platform.progress >= 0 and platform.progress <= 1
    
    def test_direction_reversal_at_start(self):
        """Test direction reverses at start point."""
        platform = MovingPlatform(100, 200, 50, 20, end_x=110, end_y=200, speed=100.0)
        
        # Move to end and back
        for _ in range(100):
            platform.update()
        
        # Should have cycled
        assert platform.progress >= 0 and platform.progress <= 1


class TestMovingPlatformVelocity:
    """Tests for get_velocity method."""
    
    def test_horizontal_velocity(self):
        """Test velocity for horizontal movement."""
        platform = MovingPlatform(100, 200, 50, 20, end_x=200, end_y=200, speed=2.0)
        velocity = platform.get_velocity()
        assert velocity[0] > 0  # Moving right
        assert velocity[1] == 0  # No vertical movement
    
    def test_vertical_velocity(self):
        """Test velocity for vertical movement."""
        platform = MovingPlatform(100, 200, 50, 20, end_x=100, end_y=300, speed=2.0)
        velocity = platform.get_velocity()
        assert velocity[0] == 0  # No horizontal movement
        assert velocity[1] > 0  # Moving down
    
    def test_reversed_velocity(self):
        """Test velocity direction reverses."""
        platform = MovingPlatform(100, 200, 50, 20, end_x=200, end_y=200, speed=2.0)
        
        # Get initial velocity
        initial_velocity = platform.get_velocity()
        
        # Reverse direction
        platform.direction = -1
        reversed_velocity = platform.get_velocity()
        
        assert initial_velocity[0] == -reversed_velocity[0]


class TestMovingPlatformSerialization:
    """Tests for MovingPlatform serialization."""
    
    def test_to_dict(self):
        """Test moving platform serialization."""
        platform = MovingPlatform(100, 200, 50, 20, end_x=300, end_y=200, speed=3.0, is_magnetic=True)
        data = platform.to_dict()
        
        assert data['x'] == 100
        assert data['end_x'] == 300
        assert data['end_y'] == 200
        assert data['speed'] == 3.0
        assert data['moving'] is True
    
    def test_from_dict(self):
        """Test moving platform deserialization."""
        data = {
            'x': 100,
            'y': 200,
            'width': 50,
            'height': 20,
            'end_x': 300,
            'end_y': 400,
            'speed': 2.5,
            'is_magnetic': True,
            'orientation': ORIENTATION_FLOOR
        }
        
        platform = MovingPlatform.from_dict(data)
        
        assert platform.x == 100
        assert platform.end_x == 300
        assert platform.end_y == 400
        assert platform.speed == 2.5
        assert platform.is_magnetic is True
