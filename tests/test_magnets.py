"""Tests for magnets module."""

import pytest
from unittest.mock import MagicMock, patch

from src.magnets import Magnet
from src.constants import (
    POLARITY_ATTRACT, POLARITY_REPEL,
    MAGNET_DEFAULT_RANGE, MAGNET_DEFAULT_STRENGTH,
    COLOR_MAGNETIC_BLUE, COLOR_MAGNETIC_RED
)


class TestMagnetInit:
    """Tests for Magnet initialization."""
    
    def test_default_initialization(self):
        """Test magnet with default values."""
        magnet = Magnet(100, 200)
        assert magnet.x == 100
        assert magnet.y == 200
        assert magnet.polarity == POLARITY_ATTRACT
        assert magnet.range == MAGNET_DEFAULT_RANGE
        assert magnet.strength == MAGNET_DEFAULT_STRENGTH
        assert magnet.active is True
    
    def test_custom_initialization(self):
        """Test magnet with custom values."""
        magnet = Magnet(50, 75, POLARITY_REPEL, range_=200, strength=1.5, width=64, height=64)
        assert magnet.x == 50
        assert magnet.y == 75
        assert magnet.polarity == POLARITY_REPEL
        assert magnet.range == 200
        assert magnet.strength == 1.5
        assert magnet.width == 64
        assert magnet.height == 64


class TestMagnetProperties:
    """Tests for Magnet properties."""
    
    def test_position_property(self):
        """Test position property returns center."""
        magnet = Magnet(100, 200)
        assert magnet.position == (100, 200)
    
    def test_rect_property(self):
        """Test rect property returns bounding box."""
        magnet = Magnet(100, 200, width=32, height=32)
        expected = (100 - 16, 200 - 16, 32, 32)
        assert magnet.rect == expected


class TestMagnetForce:
    """Tests for magnetic force calculations."""
    
    def test_force_in_range(self):
        """Test force is applied when object is in range."""
        magnet = Magnet(100, 100, POLARITY_ATTRACT, range_=150, strength=1.0)
        force = magnet.get_force_on_object((50, 100))
        assert force[0] > 0  # Attracted toward magnet (right)
        assert force[1] == pytest.approx(0.0)
    
    def test_force_out_of_range(self):
        """Test no force when object is out of range."""
        magnet = Magnet(100, 100, range_=50)
        force = magnet.get_force_on_object((200, 100))
        assert force == (0.0, 0.0)
    
    def test_force_when_inactive(self):
        """Test no force when magnet is inactive."""
        magnet = Magnet(100, 100, range_=150)
        magnet.active = False
        force = magnet.get_force_on_object((50, 100))
        assert force == (0.0, 0.0)
    
    def test_repel_force_direction(self):
        """Test repel force pushes away."""
        magnet = Magnet(100, 100, POLARITY_REPEL, range_=150, strength=1.0)
        force = magnet.get_force_on_object((50, 100))
        assert force[0] < 0  # Pushed away from magnet (left)


class TestMagnetIsInRange:
    """Tests for is_in_range method."""
    
    def test_in_range(self):
        """Test object within range."""
        magnet = Magnet(100, 100, range_=100)
        assert magnet.is_in_range((150, 100)) is True
    
    def test_out_of_range(self):
        """Test object outside range."""
        magnet = Magnet(100, 100, range_=50)
        assert magnet.is_in_range((200, 100)) is False
    
    def test_at_boundary(self):
        """Test object at exact range boundary."""
        magnet = Magnet(100, 100, range_=50)
        assert magnet.is_in_range((150, 100)) is True


class TestMagnetToggle:
    """Tests for toggle method."""
    
    def test_toggle_off(self):
        """Test toggling magnet off."""
        magnet = Magnet(100, 100)
        assert magnet.active is True
        magnet.toggle()
        assert magnet.active is False
    
    def test_toggle_on(self):
        """Test toggling magnet on."""
        magnet = Magnet(100, 100)
        magnet.active = False
        magnet.toggle()
        assert magnet.active is True


class TestMagnetSetPolarity:
    """Tests for set_polarity method."""
    
    def test_set_attract(self):
        """Test setting attract polarity."""
        magnet = Magnet(100, 100, POLARITY_REPEL)
        magnet.set_polarity(POLARITY_ATTRACT)
        assert magnet.polarity == POLARITY_ATTRACT
    
    def test_set_repel(self):
        """Test setting repel polarity."""
        magnet = Magnet(100, 100, POLARITY_ATTRACT)
        magnet.set_polarity(POLARITY_REPEL)
        assert magnet.polarity == POLARITY_REPEL
    
    def test_invalid_polarity(self):
        """Test setting invalid polarity does nothing."""
        magnet = Magnet(100, 100, POLARITY_ATTRACT)
        magnet.set_polarity("invalid")
        assert magnet.polarity == POLARITY_ATTRACT


class TestMagnetGetColor:
    """Tests for get_color method."""
    
    def test_attract_color(self):
        """Test attract polarity color."""
        magnet = Magnet(100, 100, POLARITY_ATTRACT)
        assert magnet.get_color() == COLOR_MAGNETIC_BLUE
    
    def test_repel_color(self):
        """Test repel polarity color."""
        magnet = Magnet(100, 100, POLARITY_REPEL)
        assert magnet.get_color() == COLOR_MAGNETIC_RED


class TestMagnetSerialization:
    """Tests for serialization methods."""
    
    def test_to_dict(self):
        """Test magnet serialization to dict."""
        magnet = Magnet(100, 200, POLARITY_REPEL, range_=120, strength=0.8, width=48, height=48)
        magnet.active = False
        
        data = magnet.to_dict()
        
        assert data['x'] == 100
        assert data['y'] == 200
        assert data['polarity'] == POLARITY_REPEL
        assert data['range'] == 120
        assert data['strength'] == 0.8
        assert data['width'] == 48
        assert data['height'] == 48
        assert data['active'] is False
    
    def test_from_dict(self):
        """Test magnet deserialization from dict."""
        data = {
            'x': 150,
            'y': 250,
            'polarity': POLARITY_REPEL,
            'range': 180,
            'strength': 1.2,
            'width': 64,
            'height': 64,
            'active': False
        }
        
        magnet = Magnet.from_dict(data)
        
        assert magnet.x == 150
        assert magnet.y == 250
        assert magnet.polarity == POLARITY_REPEL
        assert magnet.range == 180
        assert magnet.strength == 1.2
        assert magnet.width == 64
        assert magnet.height == 64
        assert magnet.active is False
    
    def test_roundtrip_serialization(self):
        """Test serialization roundtrip preserves data."""
        original = Magnet(100, 200, POLARITY_REPEL, range_=100, strength=0.5)
        original.active = False
        
        data = original.to_dict()
        restored = Magnet.from_dict(data)
        
        assert restored.x == original.x
        assert restored.y == original.y
        assert restored.polarity == original.polarity
        assert restored.range == original.range
        assert restored.strength == original.strength
        assert restored.active == original.active
