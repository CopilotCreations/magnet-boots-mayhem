"""Enemy classes that respond to magnetic fields."""

from typing import Tuple, List, Optional
import pygame
import math

from .constants import (
    COLOR_ENEMY, GRAVITY, MAX_FALL_SPEED
)
from .physics import check_rect_collision, calculate_distance


class Enemy:
    """Base enemy class that can be affected by magnetic fields."""
    
    def __init__(
        self,
        x: float,
        y: float,
        width: int = 32,
        height: int = 32,
        speed: float = 2.0,
        is_magnetic: bool = True
    ):
        """
        Initialize enemy.
        
        Args:
            x: Starting X position
            y: Starting Y position
            width: Enemy width
            height: Enemy height
            speed: Movement speed
            is_magnetic: Whether affected by magnetic fields
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_x = speed
        self.velocity_y = 0.0
        self.speed = speed
        self.is_magnetic = is_magnetic
        self.alive = True
        self.direction = 1
    
    @property
    def position(self) -> Tuple[float, float]:
        """Get enemy center position."""
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    @property
    def rect(self) -> Tuple[float, float, float, float]:
        """Get enemy bounding rect."""
        return (self.x, self.y, self.width, self.height)
    
    @property
    def pygame_rect(self) -> pygame.Rect:
        """Get enemy as pygame Rect."""
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))
    
    def apply_magnetic_force(self, force: Tuple[float, float]) -> None:
        """Apply magnetic force to enemy."""
        if self.is_magnetic:
            self.velocity_x += force[0]
            self.velocity_y += force[1]
    
    def update(self, platforms: List) -> None:
        """Update enemy position and behavior."""
        if not self.alive:
            return
        
        # Apply gravity
        self.velocity_y = min(self.velocity_y + GRAVITY, MAX_FALL_SPEED)
        
        # Apply velocity
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Basic collision with platforms
        for platform in platforms:
            if check_rect_collision(self.rect, platform.rect):
                # Simple collision resolution
                if self.velocity_y > 0:
                    self.y = platform.y - self.height
                    self.velocity_y = 0
    
    def check_player_collision(self, player_rect: Tuple[float, float, float, float]) -> bool:
        """Check if enemy collides with player."""
        return self.alive and check_rect_collision(self.rect, player_rect)
    
    def kill(self) -> None:
        """Kill the enemy."""
        self.alive = False
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Draw the enemy."""
        if not self.alive:
            return
        
        rect = pygame.Rect(
            int(self.x - camera_offset[0]),
            int(self.y - camera_offset[1]),
            int(self.width),
            int(self.height)
        )
        pygame.draw.rect(surface, COLOR_ENEMY, rect)
        
        # Draw magnetic indicator if magnetic
        if self.is_magnetic:
            pygame.draw.rect(surface, (255, 200, 200), rect, 2)
    
    def to_dict(self) -> dict:
        """Serialize enemy to dictionary."""
        return {
            'type': 'basic',
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'speed': self.speed,
            'is_magnetic': self.is_magnetic
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Enemy':
        """Create enemy from dictionary."""
        return cls(
            x=data['x'],
            y=data['y'],
            width=data.get('width', 32),
            height=data.get('height', 32),
            speed=data.get('speed', 2.0),
            is_magnetic=data.get('is_magnetic', True)
        )


class PatrolEnemy(Enemy):
    """Enemy that patrols between two points."""
    
    def __init__(
        self,
        x: float,
        y: float,
        patrol_distance: float = 100,
        **kwargs
    ):
        super().__init__(x, y, **kwargs)
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.velocity_x = self.speed
    
    def update(self, platforms: List) -> None:
        """Update patrol enemy behavior."""
        if not self.alive:
            return
        
        # Patrol logic
        if self.x >= self.start_x + self.patrol_distance:
            self.direction = -1
            self.velocity_x = -self.speed
        elif self.x <= self.start_x:
            self.direction = 1
            self.velocity_x = self.speed
        
        super().update(platforms)
    
    def to_dict(self) -> dict:
        """Serialize patrol enemy to dictionary."""
        data = super().to_dict()
        data['type'] = 'patrol'
        data['patrol_distance'] = self.patrol_distance
        return data


class FlyingEnemy(Enemy):
    """Enemy that flies in a pattern."""
    
    def __init__(
        self,
        x: float,
        y: float,
        amplitude: float = 50,
        frequency: float = 0.05,
        **kwargs
    ):
        super().__init__(x, y, **kwargs)
        self.start_y = y
        self.amplitude = amplitude
        self.frequency = frequency
        self.time = 0.0
    
    def update(self, platforms: List) -> None:
        """Update flying enemy behavior."""
        if not self.alive:
            return
        
        self.time += 1
        
        # Sinusoidal vertical movement
        self.y = self.start_y + self.amplitude * math.sin(self.time * self.frequency)
        
        # Horizontal movement
        self.x += self.velocity_x
    
    def to_dict(self) -> dict:
        """Serialize flying enemy to dictionary."""
        data = super().to_dict()
        data['type'] = 'flying'
        data['amplitude'] = self.amplitude
        data['frequency'] = self.frequency
        return data


def create_enemy_from_dict(data: dict) -> Enemy:
    """Factory function to create enemy from dictionary."""
    enemy_type = data.get('type', 'basic')
    
    if enemy_type == 'patrol':
        return PatrolEnemy(
            x=data['x'],
            y=data['y'],
            patrol_distance=data.get('patrol_distance', 100),
            width=data.get('width', 32),
            height=data.get('height', 32),
            speed=data.get('speed', 2.0),
            is_magnetic=data.get('is_magnetic', True)
        )
    elif enemy_type == 'flying':
        return FlyingEnemy(
            x=data['x'],
            y=data['y'],
            amplitude=data.get('amplitude', 50),
            frequency=data.get('frequency', 0.05),
            width=data.get('width', 32),
            height=data.get('height', 32),
            speed=data.get('speed', 2.0),
            is_magnetic=data.get('is_magnetic', True)
        )
    else:
        return Enemy.from_dict(data)
