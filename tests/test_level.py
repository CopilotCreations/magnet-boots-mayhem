"""Tests for level module."""

import pytest
import json
import tempfile
import os

from src.level import Level, create_demo_level, create_tutorial_level
from src.platforms import Platform, MovingPlatform
from src.magnets import Magnet
from src.enemies import Enemy, PatrolEnemy
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ORIENTATION_FLOOR, POLARITY_ATTRACT
)


class TestLevelInit:
    """Tests for Level initialization."""
    
    def test_default_initialization(self):
        """Test level with default values."""
        level = Level()
        assert level.name == "Untitled"
        assert level.platforms == []
        assert level.magnets == []
        assert level.enemies == []
        assert level.player_start == (100, 100)
        assert level.goal_position == (700, 500)
        assert level.width == SCREEN_WIDTH
        assert level.height == SCREEN_HEIGHT
    
    def test_named_level(self):
        """Test level with custom name."""
        level = Level(name="Test Level")
        assert level.name == "Test Level"


class TestLevelAddElements:
    """Tests for adding elements to level."""
    
    def test_add_platform(self):
        """Test adding platform."""
        level = Level()
        platform = Platform(100, 200, 150, 30)
        level.add_platform(platform)
        assert len(level.platforms) == 1
        assert level.platforms[0] == platform
    
    def test_add_magnet(self):
        """Test adding magnet."""
        level = Level()
        magnet = Magnet(100, 200)
        level.add_magnet(magnet)
        assert len(level.magnets) == 1
        assert level.magnets[0] == magnet
    
    def test_add_enemy(self):
        """Test adding enemy."""
        level = Level()
        enemy = Enemy(100, 200)
        level.add_enemy(enemy)
        assert len(level.enemies) == 1
        assert level.enemies[0] == enemy


class TestLevelSetters:
    """Tests for level setters."""
    
    def test_set_player_start(self):
        """Test setting player start position."""
        level = Level()
        level.set_player_start(50, 100)
        assert level.player_start == (50, 100)
    
    def test_set_goal(self):
        """Test setting goal position and size."""
        level = Level()
        level.set_goal(600, 400, 60, 60)
        assert level.goal_position == (600, 400)
        assert level.goal_size == (60, 60)


class TestLevelGoalRect:
    """Tests for goal_rect property."""
    
    def test_goal_rect(self):
        """Test goal rect calculation."""
        level = Level()
        level.set_goal(100, 200, 50, 75)
        assert level.goal_rect == (100, 200, 50, 75)


class TestLevelMagneticForce:
    """Tests for get_total_magnetic_force method."""
    
    def test_no_magnets(self):
        """Test force with no magnets."""
        level = Level()
        force = level.get_total_magnetic_force((100, 100))
        assert force == (0.0, 0.0)
    
    def test_single_magnet(self):
        """Test force from single magnet."""
        level = Level()
        magnet = Magnet(200, 100, POLARITY_ATTRACT, range_=150, strength=1.0)
        level.add_magnet(magnet)
        
        force = level.get_total_magnetic_force((100, 100))
        assert force[0] > 0  # Pulled toward magnet
    
    def test_multiple_magnets(self):
        """Test combined force from multiple magnets."""
        level = Level()
        magnet1 = Magnet(0, 100, POLARITY_ATTRACT, range_=200, strength=1.0)
        magnet2 = Magnet(200, 100, POLARITY_ATTRACT, range_=200, strength=1.0)
        level.add_magnet(magnet1)
        level.add_magnet(magnet2)
        
        # Force at midpoint should be near zero (balanced)
        force = level.get_total_magnetic_force((100, 100))
        assert abs(force[0]) < 0.1


class TestLevelUpdate:
    """Tests for update method."""
    
    def test_update_moving_platforms(self):
        """Test moving platforms are updated."""
        level = Level()
        platform = MovingPlatform(100, 200, 50, 20, end_x=200, end_y=200, speed=5.0)
        level.add_platform(platform)
        
        initial_x = platform.x
        level.update()
        assert platform.x != initial_x
    
    def test_update_enemies(self):
        """Test enemies are updated."""
        level = Level()
        enemy = Enemy(100, 200)
        level.add_enemy(enemy)
        
        initial_y = enemy.y
        level.update()
        assert enemy.y != initial_y  # Gravity applied


class TestLevelSerialization:
    """Tests for serialization methods."""
    
    def test_to_dict(self):
        """Test level serialization to dict."""
        level = Level(name="Test Level")
        level.width = 1000
        level.height = 800
        level.set_player_start(50, 60)
        level.set_goal(900, 700, 40, 40)
        level.add_platform(Platform(100, 200, 150, 30))
        level.add_magnet(Magnet(300, 300))
        level.add_enemy(Enemy(400, 400))
        
        data = level.to_dict()
        
        assert data['name'] == "Test Level"
        assert data['width'] == 1000
        assert data['height'] == 800
        assert data['player_start'] == [50, 60]
        assert data['goal_position'] == [900, 700]
        assert data['goal_size'] == [40, 40]
        assert len(data['platforms']) == 1
        assert len(data['magnets']) == 1
        assert len(data['enemies']) == 1
    
    def test_from_dict(self):
        """Test level deserialization from dict."""
        data = {
            'name': 'Loaded Level',
            'width': 1200,
            'height': 900,
            'player_start': [75, 80],
            'goal_position': [1100, 800],
            'goal_size': [60, 60],
            'background_color': [40, 40, 50],
            'platforms': [{'x': 100, 'y': 200, 'width': 150, 'height': 30}],
            'magnets': [{'x': 300, 'y': 300}],
            'enemies': [{'type': 'basic', 'x': 400, 'y': 400}]
        }
        
        level = Level.from_dict(data)
        
        assert level.name == 'Loaded Level'
        assert level.width == 1200
        assert level.height == 900
        assert level.player_start == (75, 80)
        assert level.goal_position == (1100, 800)
        assert level.goal_size == (60, 60)
        assert len(level.platforms) == 1
        assert len(level.magnets) == 1
        assert len(level.enemies) == 1
    
    def test_from_dict_with_moving_platform(self):
        """Test loading moving platform from dict."""
        data = {
            'name': 'Test',
            'platforms': [{
                'x': 100,
                'y': 200,
                'width': 50,
                'height': 20,
                'end_x': 300,
                'end_y': 200,
                'speed': 2.0,
                'moving': True
            }],
            'magnets': [],
            'enemies': []
        }
        
        level = Level.from_dict(data)
        
        assert len(level.platforms) == 1
        assert isinstance(level.platforms[0], MovingPlatform)
    
    def test_roundtrip_serialization(self):
        """Test serialization roundtrip preserves data."""
        original = Level(name="Roundtrip Test")
        original.set_player_start(100, 150)
        original.set_goal(800, 600, 50, 50)
        original.add_platform(Platform(200, 300, 100, 20, is_magnetic=True))
        original.add_magnet(Magnet(400, 400, strength=0.5))
        
        data = original.to_dict()
        restored = Level.from_dict(data)
        
        assert restored.name == original.name
        assert restored.player_start == original.player_start
        assert restored.goal_position == original.goal_position
        assert len(restored.platforms) == len(original.platforms)
        assert len(restored.magnets) == len(original.magnets)


class TestLevelSaveLoad:
    """Tests for save/load file methods."""
    
    def test_save_and_load(self):
        """Test saving and loading level from file."""
        level = Level(name="File Test")
        level.set_player_start(100, 200)
        level.add_platform(Platform(0, 500, 800, 50))
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        try:
            level.save(filepath)
            loaded = Level.load(filepath)
            
            assert loaded.name == level.name
            assert loaded.player_start == level.player_start
            assert len(loaded.platforms) == 1
        finally:
            os.unlink(filepath)


class TestDemoLevel:
    """Tests for create_demo_level function."""
    
    def test_demo_level_created(self):
        """Test demo level is created correctly."""
        level = create_demo_level()
        
        assert level.name == "Demo Level"
        assert level.width == 1200
        assert level.height == 800
        assert len(level.platforms) > 0
        assert len(level.magnets) > 0
        assert level.player_start != level.goal_position
    
    def test_demo_level_has_magnetic_platforms(self):
        """Test demo level has magnetic platforms."""
        level = create_demo_level()
        
        magnetic_count = sum(1 for p in level.platforms if p.is_magnetic)
        assert magnetic_count > 0


class TestTutorialLevel:
    """Tests for create_tutorial_level function."""
    
    def test_tutorial_level_created(self):
        """Test tutorial level is created correctly."""
        level = create_tutorial_level()
        
        assert level.name == "Tutorial"
        assert len(level.platforms) > 0
        assert level.player_start != level.goal_position
    
    def test_tutorial_level_simpler_than_demo(self):
        """Test tutorial level is simpler."""
        tutorial = create_tutorial_level()
        demo = create_demo_level()
        
        assert len(tutorial.platforms) <= len(demo.platforms)
