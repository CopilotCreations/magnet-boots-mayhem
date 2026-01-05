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
        """Get enemy center position.

        Returns:
            Tuple[float, float]: The (x, y) coordinates of the enemy's center.
        """
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    @property
    def rect(self) -> Tuple[float, float, float, float]:
        """Get enemy bounding rect.

        Returns:
            Tuple[float, float, float, float]: The (x, y, width, height) bounding rectangle.
        """
        return (self.x, self.y, self.width, self.height)
    
    @property
    def pygame_rect(self) -> pygame.Rect:
        """Get enemy as pygame Rect.

        Returns:
            pygame.Rect: The enemy's bounding rectangle as a pygame Rect object.
        """
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))
    
    def apply_magnetic_force(self, force: Tuple[float, float]) -> None:
        """Apply magnetic force to enemy.

        Args:
            force: A tuple (fx, fy) representing the magnetic force vector to apply.
        """
        if self.is_magnetic:
            self.velocity_x += force[0]
            self.velocity_y += force[1]
    
    def update(self, platforms: List) -> None:
        """Update enemy position and behavior.

        Applies gravity, updates position based on velocity, and handles
        collision detection with platforms.

        Args:
            platforms: List of platform objects to check for collisions.
        """
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
        """Check if enemy collides with player.

        Args:
            player_rect: The player's bounding rectangle as (x, y, width, height).

        Returns:
            bool: True if the enemy is alive and collides with the player.
        """
        return self.alive and check_rect_collision(self.rect, player_rect)
    
    def kill(self) -> None:
        """Kill the enemy.

        Sets the enemy's alive state to False, preventing further updates
        and rendering.
        """
        self.alive = False
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Draw the enemy.

        Renders the enemy rectangle on the given surface, adjusted for camera
        offset. Magnetic enemies have a distinct border indicator.

        Args:
            surface: The pygame surface to draw on.
            camera_offset: The (x, y) camera offset for scrolling. Defaults to (0, 0).
        """
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
        """Serialize enemy to dictionary.

        Returns:
            dict: A dictionary containing the enemy's properties for serialization.
        """
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
        """Create enemy from dictionary.

        Args:
            data: Dictionary containing enemy properties. Required keys: 'x', 'y'.
                Optional keys: 'width', 'height', 'speed', 'is_magnetic'.

        Returns:
            Enemy: A new Enemy instance created from the dictionary data.
        """
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
        """Initialize patrol enemy.

        Args:
            x: Starting X position.
            y: Starting Y position.
            patrol_distance: Distance to patrol from the starting position.
                Defaults to 100.
            **kwargs: Additional keyword arguments passed to the base Enemy class.
        """
        super().__init__(x, y, **kwargs)
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.velocity_x = self.speed
    
    def update(self, platforms: List) -> None:
        """Update patrol enemy behavior.

        Handles patrol logic by reversing direction when reaching patrol
        boundaries, then delegates to the parent update method.

        Args:
            platforms: List of platform objects to check for collisions.
        """
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
        """Serialize patrol enemy to dictionary.

        Returns:
            dict: A dictionary containing the patrol enemy's properties,
                including patrol-specific attributes.
        """
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
        """Initialize flying enemy.

        Args:
            x: Starting X position.
            y: Starting Y position.
            amplitude: Vertical oscillation amplitude in pixels. Defaults to 50.
            frequency: Oscillation frequency (radians per frame). Defaults to 0.05.
            **kwargs: Additional keyword arguments passed to the base Enemy class.
        """
        super().__init__(x, y, **kwargs)
        self.start_y = y
        self.amplitude = amplitude
        self.frequency = frequency
        self.time = 0.0
    
    def update(self, platforms: List) -> None:
        """Update flying enemy behavior.

        Updates position using sinusoidal vertical movement and constant
        horizontal velocity. Ignores gravity and platform collisions.

        Args:
            platforms: List of platform objects (unused, but kept for interface
                consistency with base class).
        """
        if not self.alive:
            return
        
        self.time += 1
        
        # Sinusoidal vertical movement
        self.y = self.start_y + self.amplitude * math.sin(self.time * self.frequency)
        
        # Horizontal movement
        self.x += self.velocity_x
    
    def to_dict(self) -> dict:
        """Serialize flying enemy to dictionary.

        Returns:
            dict: A dictionary containing the flying enemy's properties,
                including flight-specific attributes.
        """
        data = super().to_dict()
        data['type'] = 'flying'
        data['amplitude'] = self.amplitude
        data['frequency'] = self.frequency
        return data


def create_enemy_from_dict(data: dict) -> Enemy:
    """Factory function to create enemy from dictionary.

    Creates the appropriate Enemy subclass based on the 'type' field
    in the data dictionary.

    Args:
        data: Dictionary containing enemy properties. Required keys: 'x', 'y'.
            The 'type' key determines which enemy class is instantiated:
            'patrol', 'flying', or 'basic' (default).

    Returns:
        Enemy: An instance of Enemy, PatrolEnemy, or FlyingEnemy based on type.
    """
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
