"""Level class for loading and managing game levels."""

from typing import List, Tuple, Optional, Dict, Any
import json
import os

from .platforms import Platform, MovingPlatform
from .magnets import Magnet
from .enemies import Enemy, create_enemy_from_dict
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ORIENTATION_FLOOR, ORIENTATION_WALL_LEFT, ORIENTATION_WALL_RIGHT, ORIENTATION_CEILING,
    POLARITY_ATTRACT, POLARITY_REPEL
)


class Level:
    """Manages level data including platforms, magnets, enemies, and goals."""
    
    def __init__(self, name: str = "Untitled"):
        """
        Initialize an empty level.
        
        Args:
            name: Level name
        """
        self.name = name
        self.platforms: List[Platform] = []
        self.magnets: List[Magnet] = []
        self.enemies: List[Enemy] = []
        self.player_start: Tuple[float, float] = (100, 100)
        self.goal_position: Tuple[float, float] = (700, 500)
        self.goal_size: Tuple[float, float] = (50, 50)
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.background_color = (30, 30, 40)
    
    def add_platform(self, platform: Platform) -> None:
        """Add a platform to the level."""
        self.platforms.append(platform)
    
    def add_magnet(self, magnet: Magnet) -> None:
        """Add a magnet to the level."""
        self.magnets.append(magnet)
    
    def add_enemy(self, enemy: Enemy) -> None:
        """Add an enemy to the level."""
        self.enemies.append(enemy)
    
    def set_player_start(self, x: float, y: float) -> None:
        """Set player starting position."""
        self.player_start = (x, y)
    
    def set_goal(self, x: float, y: float, width: float = 50, height: float = 50) -> None:
        """Set goal position and size."""
        self.goal_position = (x, y)
        self.goal_size = (width, height)
    
    @property
    def goal_rect(self) -> Tuple[float, float, float, float]:
        """Get goal bounding rect."""
        return (
            self.goal_position[0],
            self.goal_position[1],
            self.goal_size[0],
            self.goal_size[1]
        )
    
    def get_total_magnetic_force(self, position: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate total magnetic force at a position from all magnets."""
        total_fx, total_fy = 0.0, 0.0
        
        for magnet in self.magnets:
            force = magnet.get_force_on_object(position)
            total_fx += force[0]
            total_fy += force[1]
        
        return (total_fx, total_fy)
    
    def update(self) -> None:
        """Update all level elements."""
        # Update moving platforms
        for platform in self.platforms:
            if isinstance(platform, MovingPlatform):
                platform.update()
        
        # Update enemies
        for enemy in self.enemies:
            # Apply magnetic forces to enemies
            if enemy.is_magnetic:
                force = self.get_total_magnetic_force(enemy.position)
                enemy.apply_magnetic_force(force)
            enemy.update(self.platforms)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize level to dictionary."""
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'background_color': self.background_color,
            'player_start': list(self.player_start),
            'goal_position': list(self.goal_position),
            'goal_size': list(self.goal_size),
            'platforms': [p.to_dict() for p in self.platforms],
            'magnets': [m.to_dict() for m in self.magnets],
            'enemies': [e.to_dict() for e in self.enemies]
        }
    
    def save(self, filepath: str) -> None:
        """Save level to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Level':
        """Create level from dictionary."""
        level = cls(name=data.get('name', 'Untitled'))
        level.width = data.get('width', SCREEN_WIDTH)
        level.height = data.get('height', SCREEN_HEIGHT)
        level.background_color = tuple(data.get('background_color', (30, 30, 40)))
        level.player_start = tuple(data.get('player_start', [100, 100]))
        level.goal_position = tuple(data.get('goal_position', [700, 500]))
        level.goal_size = tuple(data.get('goal_size', [50, 50]))
        
        # Load platforms
        for p_data in data.get('platforms', []):
            if p_data.get('moving', False):
                level.add_platform(MovingPlatform.from_dict(p_data))
            else:
                level.add_platform(Platform.from_dict(p_data))
        
        # Load magnets
        for m_data in data.get('magnets', []):
            level.add_magnet(Magnet.from_dict(m_data))
        
        # Load enemies
        for e_data in data.get('enemies', []):
            level.add_enemy(create_enemy_from_dict(e_data))
        
        return level
    
    @classmethod
    def load(cls, filepath: str) -> 'Level':
        """Load level from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


def create_demo_level() -> Level:
    """Create a demo level showcasing magnetic mechanics."""
    level = Level(name="Demo Level")
    level.width = 1200
    level.height = 800
    
    # Ground platform
    level.add_platform(Platform(0, 750, 1200, 50, is_magnetic=False, orientation=ORIENTATION_FLOOR))
    
    # Left wall (magnetic)
    level.add_platform(Platform(0, 200, 50, 550, is_magnetic=True, orientation=ORIENTATION_WALL_LEFT))
    
    # Right wall (magnetic)
    level.add_platform(Platform(1150, 200, 50, 550, is_magnetic=True, orientation=ORIENTATION_WALL_RIGHT))
    
    # Ceiling section (magnetic)
    level.add_platform(Platform(200, 200, 300, 30, is_magnetic=True, orientation=ORIENTATION_CEILING))
    
    # Floating platforms
    level.add_platform(Platform(300, 600, 150, 30, is_magnetic=True, orientation=ORIENTATION_FLOOR))
    level.add_platform(Platform(550, 500, 150, 30, is_magnetic=False, orientation=ORIENTATION_FLOOR))
    level.add_platform(Platform(800, 400, 150, 30, is_magnetic=True, orientation=ORIENTATION_FLOOR))
    
    # Ceiling platform for upside-down walking
    level.add_platform(Platform(600, 250, 200, 30, is_magnetic=True, orientation=ORIENTATION_CEILING))
    
    # Add magnets
    level.add_magnet(Magnet(400, 450, POLARITY_ATTRACT, range_=120, strength=0.6))
    level.add_magnet(Magnet(900, 550, POLARITY_REPEL, range_=100, strength=0.8))
    
    # Set player start and goal
    level.set_player_start(100, 680)
    level.set_goal(1050, 300, 50, 50)
    
    return level


def create_tutorial_level() -> Level:
    """Create a simple tutorial level."""
    level = Level(name="Tutorial")
    level.width = 800
    level.height = 600
    
    # Ground
    level.add_platform(Platform(0, 550, 800, 50, is_magnetic=False, orientation=ORIENTATION_FLOOR))
    
    # Simple magnetic wall
    level.add_platform(Platform(350, 300, 30, 250, is_magnetic=True, orientation=ORIENTATION_WALL_RIGHT))
    
    # Platform after wall
    level.add_platform(Platform(400, 350, 150, 30, is_magnetic=True, orientation=ORIENTATION_FLOOR))
    
    # Goal platform
    level.add_platform(Platform(600, 450, 150, 30, is_magnetic=False, orientation=ORIENTATION_FLOOR))
    
    level.set_player_start(50, 480)
    level.set_goal(650, 400, 50, 50)
    
    return level
