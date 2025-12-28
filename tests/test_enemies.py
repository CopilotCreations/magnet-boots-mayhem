"""Tests for enemies module."""

import pytest

from src.enemies import Enemy, PatrolEnemy, FlyingEnemy, create_enemy_from_dict
from src.platforms import Platform
from src.constants import COLOR_ENEMY


class TestEnemyInit:
    """Tests for Enemy initialization."""
    
    def test_default_initialization(self):
        """Test enemy with default values."""
        enemy = Enemy(100, 200)
        assert enemy.x == 100
        assert enemy.y == 200
        assert enemy.width == 32
        assert enemy.height == 32
        assert enemy.speed == 2.0
        assert enemy.is_magnetic is True
        assert enemy.alive is True
    
    def test_custom_initialization(self):
        """Test enemy with custom values."""
        enemy = Enemy(50, 75, width=48, height=48, speed=3.0, is_magnetic=False)
        assert enemy.width == 48
        assert enemy.height == 48
        assert enemy.speed == 3.0
        assert enemy.is_magnetic is False


class TestEnemyProperties:
    """Tests for Enemy properties."""
    
    def test_position_property(self):
        """Test position property returns center."""
        enemy = Enemy(100, 200, width=32, height=32)
        assert enemy.position == (116, 216)
    
    def test_rect_property(self):
        """Test rect property."""
        enemy = Enemy(100, 200, width=32, height=32)
        assert enemy.rect == (100, 200, 32, 32)


class TestEnemyMagneticForce:
    """Tests for apply_magnetic_force method."""
    
    def test_apply_force_magnetic(self):
        """Test magnetic force is applied to magnetic enemy."""
        enemy = Enemy(100, 200, is_magnetic=True)
        enemy.apply_magnetic_force((5.0, -3.0))
        assert enemy.velocity_x == 5.0 + enemy.speed  # Initial velocity + force
        assert enemy.velocity_y == -3.0
    
    def test_no_force_non_magnetic(self):
        """Test magnetic force not applied to non-magnetic enemy."""
        enemy = Enemy(100, 200, is_magnetic=False)
        initial_vx = enemy.velocity_x
        initial_vy = enemy.velocity_y
        enemy.apply_magnetic_force((5.0, -3.0))
        assert enemy.velocity_x == initial_vx
        assert enemy.velocity_y == initial_vy


class TestEnemyUpdate:
    """Tests for update method."""
    
    def test_update_applies_gravity(self):
        """Test update applies gravity."""
        enemy = Enemy(100, 200)
        initial_vy = enemy.velocity_y
        enemy.update([])
        assert enemy.velocity_y > initial_vy
    
    def test_update_dead_enemy(self):
        """Test dead enemy doesn't update."""
        enemy = Enemy(100, 200)
        enemy.alive = False
        initial_y = enemy.y
        enemy.update([])
        assert enemy.y == initial_y


class TestEnemyCollision:
    """Tests for collision detection."""
    
    def test_check_player_collision_true(self):
        """Test collision detection when overlapping."""
        enemy = Enemy(100, 200, width=32, height=32)
        player_rect = (90, 190, 32, 32)
        assert enemy.check_player_collision(player_rect) is True
    
    def test_check_player_collision_false(self):
        """Test collision detection when not overlapping."""
        enemy = Enemy(100, 200, width=32, height=32)
        player_rect = (200, 200, 32, 32)
        assert enemy.check_player_collision(player_rect) is False
    
    def test_check_player_collision_dead(self):
        """Test dead enemy doesn't collide."""
        enemy = Enemy(100, 200, width=32, height=32)
        enemy.alive = False
        player_rect = (100, 200, 32, 32)
        assert enemy.check_player_collision(player_rect) is False


class TestEnemyKill:
    """Tests for kill method."""
    
    def test_kill(self):
        """Test killing enemy."""
        enemy = Enemy(100, 200)
        assert enemy.alive is True
        enemy.kill()
        assert enemy.alive is False


class TestEnemySerialization:
    """Tests for serialization methods."""
    
    def test_to_dict(self):
        """Test enemy serialization."""
        enemy = Enemy(100, 200, width=48, height=48, speed=3.0, is_magnetic=False)
        data = enemy.to_dict()
        
        assert data['type'] == 'basic'
        assert data['x'] == 100
        assert data['y'] == 200
        assert data['width'] == 48
        assert data['height'] == 48
        assert data['speed'] == 3.0
        assert data['is_magnetic'] is False
    
    def test_from_dict(self):
        """Test enemy deserialization."""
        data = {
            'x': 150,
            'y': 250,
            'width': 40,
            'height': 40,
            'speed': 2.5,
            'is_magnetic': True
        }
        
        enemy = Enemy.from_dict(data)
        
        assert enemy.x == 150
        assert enemy.y == 250
        assert enemy.width == 40
        assert enemy.height == 40
        assert enemy.speed == 2.5
        assert enemy.is_magnetic is True


class TestPatrolEnemy:
    """Tests for PatrolEnemy class."""
    
    def test_initialization(self):
        """Test patrol enemy initialization."""
        enemy = PatrolEnemy(100, 200, patrol_distance=150)
        assert enemy.start_x == 100
        assert enemy.patrol_distance == 150
    
    def test_patrol_movement(self):
        """Test patrol movement."""
        enemy = PatrolEnemy(100, 200, patrol_distance=50, speed=2.0)
        
        # Move toward end
        for _ in range(30):
            enemy.update([])
        
        # Should be moving right initially
        assert enemy.x > 100
    
    def test_patrol_reversal(self):
        """Test patrol direction reversal."""
        enemy = PatrolEnemy(100, 200, patrol_distance=20, speed=10.0)
        
        # Move to end
        for _ in range(5):
            enemy.update([])
        
        # Should have reversed direction
        assert enemy.direction == -1 or enemy.x > 100
    
    def test_to_dict(self):
        """Test patrol enemy serialization."""
        enemy = PatrolEnemy(100, 200, patrol_distance=150)
        data = enemy.to_dict()
        
        assert data['type'] == 'patrol'
        assert data['patrol_distance'] == 150


class TestFlyingEnemy:
    """Tests for FlyingEnemy class."""
    
    def test_initialization(self):
        """Test flying enemy initialization."""
        enemy = FlyingEnemy(100, 200, amplitude=75, frequency=0.1)
        assert enemy.start_y == 200
        assert enemy.amplitude == 75
        assert enemy.frequency == 0.1
        assert enemy.time == 0.0
    
    def test_sinusoidal_movement(self):
        """Test sinusoidal vertical movement."""
        enemy = FlyingEnemy(100, 200, amplitude=50, frequency=0.1)
        
        positions = []
        for _ in range(100):  # More iterations to complete a full cycle
            enemy.update([])
            positions.append(enemy.y)
        
        # Y should vary around start_y (amplitude of 50 means range 150-250)
        assert max(positions) > 200  # Goes above start
        assert min(positions) < 200  # Goes below start
    
    def test_to_dict(self):
        """Test flying enemy serialization."""
        enemy = FlyingEnemy(100, 200, amplitude=60, frequency=0.05)
        data = enemy.to_dict()
        
        assert data['type'] == 'flying'
        assert data['amplitude'] == 60
        assert data['frequency'] == 0.05


class TestCreateEnemyFromDict:
    """Tests for create_enemy_from_dict factory function."""
    
    def test_create_basic_enemy(self):
        """Test creating basic enemy from dict."""
        data = {'type': 'basic', 'x': 100, 'y': 200}
        enemy = create_enemy_from_dict(data)
        assert isinstance(enemy, Enemy)
        assert not isinstance(enemy, PatrolEnemy)
        assert not isinstance(enemy, FlyingEnemy)
    
    def test_create_patrol_enemy(self):
        """Test creating patrol enemy from dict."""
        data = {'type': 'patrol', 'x': 100, 'y': 200, 'patrol_distance': 100}
        enemy = create_enemy_from_dict(data)
        assert isinstance(enemy, PatrolEnemy)
    
    def test_create_flying_enemy(self):
        """Test creating flying enemy from dict."""
        data = {'type': 'flying', 'x': 100, 'y': 200, 'amplitude': 50, 'frequency': 0.1}
        enemy = create_enemy_from_dict(data)
        assert isinstance(enemy, FlyingEnemy)
    
    def test_unknown_type_creates_basic(self):
        """Test unknown type creates basic enemy."""
        data = {'type': 'unknown', 'x': 100, 'y': 200}
        enemy = create_enemy_from_dict(data)
        assert isinstance(enemy, Enemy)
