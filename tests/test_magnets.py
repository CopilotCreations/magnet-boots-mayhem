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
        """Test magnet with default values.
        
        Verifies that a Magnet created with only x and y coordinates
        uses default values for polarity, range, strength, and active state.
        """
        magnet = Magnet(100, 200)
        assert magnet.x == 100
        assert magnet.y == 200
        assert magnet.polarity == POLARITY_ATTRACT
        assert magnet.range == MAGNET_DEFAULT_RANGE
        assert magnet.strength == MAGNET_DEFAULT_STRENGTH
        assert magnet.active is True
    
    def test_custom_initialization(self):
        """Test magnet with custom values.
        
        Verifies that a Magnet created with custom parameters correctly
        stores all provided values including polarity, range, strength,
        width, and height.
        """
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
        """Test position property returns center.
        
        Verifies that the position property returns a tuple containing
        the magnet's x and y coordinates.
        """
        magnet = Magnet(100, 200)
        assert magnet.position == (100, 200)
    
    def test_rect_property(self):
        """Test rect property returns bounding box.
        
        Verifies that the rect property returns a tuple representing
        the bounding box (left, top, width, height) centered on the
        magnet's position.
        """
        magnet = Magnet(100, 200, width=32, height=32)
        expected = (100 - 16, 200 - 16, 32, 32)
        assert magnet.rect == expected


class TestMagnetForce:
    """Tests for magnetic force calculations."""
    
    def test_force_in_range(self):
        """Test force is applied when object is in range.
        
        Verifies that get_force_on_object returns a non-zero force vector
        when the target object is within the magnet's effective range.
        """
        magnet = Magnet(100, 100, POLARITY_ATTRACT, range_=150, strength=1.0)
        force = magnet.get_force_on_object((50, 100))
        assert force[0] > 0  # Attracted toward magnet (right)
        assert force[1] == pytest.approx(0.0)
    
    def test_force_out_of_range(self):
        """Test no force when object is out of range.
        
        Verifies that get_force_on_object returns a zero force vector
        when the target object is outside the magnet's effective range.
        """
        magnet = Magnet(100, 100, range_=50)
        force = magnet.get_force_on_object((200, 100))
        assert force == (0.0, 0.0)
    
    def test_force_when_inactive(self):
        """Test no force when magnet is inactive.
        
        Verifies that get_force_on_object returns a zero force vector
        when the magnet's active state is set to False, regardless of
        distance.
        """
        magnet = Magnet(100, 100, range_=150)
        magnet.active = False
        force = magnet.get_force_on_object((50, 100))
        assert force == (0.0, 0.0)
    
    def test_repel_force_direction(self):
        """Test repel force pushes away.
        
        Verifies that a magnet with POLARITY_REPEL generates a force
        vector that pushes the target object away from the magnet.
        """
        magnet = Magnet(100, 100, POLARITY_REPEL, range_=150, strength=1.0)
        force = magnet.get_force_on_object((50, 100))
        assert force[0] < 0  # Pushed away from magnet (left)


class TestMagnetIsInRange:
    """Tests for is_in_range method."""
    
    def test_in_range(self):
        """Test object within range.
        
        Verifies that is_in_range returns True when the target object
        is positioned within the magnet's effective range.
        """
        magnet = Magnet(100, 100, range_=100)
        assert magnet.is_in_range((150, 100)) is True
    
    def test_out_of_range(self):
        """Test object outside range.
        
        Verifies that is_in_range returns False when the target object
        is positioned outside the magnet's effective range.
        """
        magnet = Magnet(100, 100, range_=50)
        assert magnet.is_in_range((200, 100)) is False
    
    def test_at_boundary(self):
        """Test object at exact range boundary.
        
        Verifies that is_in_range returns True when the target object
        is positioned exactly at the edge of the magnet's effective range.
        """
        magnet = Magnet(100, 100, range_=50)
        assert magnet.is_in_range((150, 100)) is True


class TestMagnetToggle:
    """Tests for toggle method."""
    
    def test_toggle_off(self):
        """Test toggling magnet off.
        
        Verifies that calling toggle() on an active magnet sets its
        active state to False.
        """
        magnet = Magnet(100, 100)
        assert magnet.active is True
        magnet.toggle()
        assert magnet.active is False
    
    def test_toggle_on(self):
        """Test toggling magnet on.
        
        Verifies that calling toggle() on an inactive magnet sets its
        active state to True.
        """
        magnet = Magnet(100, 100)
        magnet.active = False
        magnet.toggle()
        assert magnet.active is True


class TestMagnetSetPolarity:
    """Tests for set_polarity method."""
    
    def test_set_attract(self):
        """Test setting attract polarity.
        
        Verifies that set_polarity correctly changes the magnet's
        polarity to POLARITY_ATTRACT.
        """
        magnet = Magnet(100, 100, POLARITY_REPEL)
        magnet.set_polarity(POLARITY_ATTRACT)
        assert magnet.polarity == POLARITY_ATTRACT
    
    def test_set_repel(self):
        """Test setting repel polarity.
        
        Verifies that set_polarity correctly changes the magnet's
        polarity to POLARITY_REPEL.
        """
        magnet = Magnet(100, 100, POLARITY_ATTRACT)
        magnet.set_polarity(POLARITY_REPEL)
        assert magnet.polarity == POLARITY_REPEL
    
    def test_invalid_polarity(self):
        """Test setting invalid polarity does nothing.
        
        Verifies that set_polarity ignores invalid polarity values
        and preserves the magnet's current polarity setting.
        """
        magnet = Magnet(100, 100, POLARITY_ATTRACT)
        magnet.set_polarity("invalid")
        assert magnet.polarity == POLARITY_ATTRACT


class TestMagnetGetColor:
    """Tests for get_color method."""
    
    def test_attract_color(self):
        """Test attract polarity color.
        
        Verifies that get_color returns COLOR_MAGNETIC_BLUE when the
        magnet has POLARITY_ATTRACT polarity.
        """
        magnet = Magnet(100, 100, POLARITY_ATTRACT)
        assert magnet.get_color() == COLOR_MAGNETIC_BLUE
    
    def test_repel_color(self):
        """Test repel polarity color.
        
        Verifies that get_color returns COLOR_MAGNETIC_RED when the
        magnet has POLARITY_REPEL polarity.
        """
        magnet = Magnet(100, 100, POLARITY_REPEL)
        assert magnet.get_color() == COLOR_MAGNETIC_RED


class TestMagnetSerialization:
    """Tests for serialization methods."""
    
    def test_to_dict(self):
        """Test magnet serialization to dict.
        
        Verifies that to_dict correctly converts a Magnet instance
        to a dictionary containing all of its properties.
        """
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
        """Test magnet deserialization from dict.
        
        Verifies that from_dict correctly creates a Magnet instance
        from a dictionary containing all required properties.
        """
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
        """Test serialization roundtrip preserves data.
        
        Verifies that serializing a Magnet to dict and then deserializing
        it back produces an equivalent Magnet with identical property values.
        """
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
