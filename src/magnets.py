"""Magnet class for magnetic zones that attract or repel objects."""

from typing import Tuple, Optional
import pygame

from .constants import (
    MAGNET_DEFAULT_RANGE, MAGNET_DEFAULT_STRENGTH,
    POLARITY_ATTRACT, POLARITY_REPEL,
    COLOR_MAGNETIC_BLUE, COLOR_MAGNETIC_RED
)
from .physics import calculate_magnetic_force


class Magnet:
    """A magnetic zone that can attract or repel objects."""
    
    def __init__(
        self,
        x: float,
        y: float,
        polarity: str = POLARITY_ATTRACT,
        range_: float = MAGNET_DEFAULT_RANGE,
        strength: float = MAGNET_DEFAULT_STRENGTH,
        width: int = 32,
        height: int = 32
    ):
        """
        Initialize a magnet.
        
        Args:
            x: X position (center)
            y: Y position (center)
            polarity: POLARITY_ATTRACT or POLARITY_REPEL
            range_: Effective range of the magnetic field
            strength: Force multiplier
            width: Visual width
            height: Visual height
        """
        self.x = x
        self.y = y
        self.polarity = polarity
        self.range = range_
        self.strength = strength
        self.width = width
        self.height = height
        self.active = True
    
    @property
    def position(self) -> Tuple[float, float]:
        """Get magnet center position."""
        return (self.x, self.y)
    
    @property
    def rect(self) -> Tuple[float, float, float, float]:
        """Get magnet bounding rect."""
        return (
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width,
            self.height
        )
    
    def get_force_on_object(self, object_pos: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate the force this magnet applies to an object at given position."""
        if not self.active:
            return (0.0, 0.0)
        
        return calculate_magnetic_force(
            object_pos,
            self.position,
            self.range,
            self.strength,
            self.polarity
        )
    
    def is_in_range(self, object_pos: Tuple[float, float]) -> bool:
        """Check if an object is within the magnet's range."""
        from .physics import calculate_distance
        return calculate_distance(object_pos, self.position) <= self.range
    
    def toggle(self) -> None:
        """Toggle magnet on/off."""
        self.active = not self.active
    
    def set_polarity(self, polarity: str) -> None:
        """Set magnet polarity."""
        if polarity in (POLARITY_ATTRACT, POLARITY_REPEL):
            self.polarity = polarity
    
    def get_color(self) -> Tuple[int, int, int]:
        """Get color based on polarity."""
        if self.polarity == POLARITY_ATTRACT:
            return COLOR_MAGNETIC_BLUE
        return COLOR_MAGNETIC_RED
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Draw the magnet."""
        if not self.active:
            return
        
        # Draw range indicator (semi-transparent)
        range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        color = self.get_color()
        pygame.draw.circle(
            range_surface,
            (*color, 50),
            (self.range, self.range),
            int(self.range)
        )
        
        screen_x = int(self.x - self.range - camera_offset[0])
        screen_y = int(self.y - self.range - camera_offset[1])
        surface.blit(range_surface, (screen_x, screen_y))
        
        # Draw magnet core
        core_rect = pygame.Rect(
            int(self.x - self.width / 2 - camera_offset[0]),
            int(self.y - self.height / 2 - camera_offset[1]),
            self.width,
            self.height
        )
        pygame.draw.rect(surface, color, core_rect)
        pygame.draw.rect(surface, (255, 255, 255), core_rect, 2)
    
    def to_dict(self) -> dict:
        """Serialize magnet to dictionary."""
        return {
            'x': self.x,
            'y': self.y,
            'polarity': self.polarity,
            'range': self.range,
            'strength': self.strength,
            'width': self.width,
            'height': self.height,
            'active': self.active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Magnet':
        """Create magnet from dictionary."""
        magnet = cls(
            x=data['x'],
            y=data['y'],
            polarity=data.get('polarity', POLARITY_ATTRACT),
            range_=data.get('range', MAGNET_DEFAULT_RANGE),
            strength=data.get('strength', MAGNET_DEFAULT_STRENGTH),
            width=data.get('width', 32),
            height=data.get('height', 32)
        )
        magnet.active = data.get('active', True)
        return magnet
