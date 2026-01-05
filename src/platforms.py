"""Platform classes for floor, wall, and ceiling surfaces."""

from typing import Tuple, Optional
import pygame

from .constants import (
    ORIENTATION_FLOOR, ORIENTATION_WALL_LEFT, ORIENTATION_WALL_RIGHT, ORIENTATION_CEILING,
    COLOR_PLATFORM, COLOR_MAGNETIC_PLATFORM
)


class Platform:
    """A platform that can be magnetic or normal."""
    
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        is_magnetic: bool = False,
        orientation: str = ORIENTATION_FLOOR
    ):
        """
        Initialize a platform.
        
        Args:
            x: X position (top-left)
            y: Y position (top-left)
            width: Platform width
            height: Platform height
            is_magnetic: Whether player can stick to this surface
            orientation: Surface orientation for gravity/movement
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_magnetic = is_magnetic
        self.orientation = orientation
    
    @property
    def rect(self) -> Tuple[float, float, float, float]:
        """Get platform bounding rect.

        Returns:
            Tuple containing (x, y, width, height) of the platform.
        """
        return (self.x, self.y, self.width, self.height)
    
    @property
    def pygame_rect(self) -> pygame.Rect:
        """Get platform as pygame Rect.

        Returns:
            A pygame.Rect object representing the platform bounds.
        """
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))
    
    @property
    def center(self) -> Tuple[float, float]:
        """Get platform center position.

        Returns:
            Tuple containing (x, y) coordinates of the platform center.
        """
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    def get_surface_position(self) -> Tuple[float, float, str]:
        """Get the position and side where player would stick.

        Returns:
            Tuple containing (x, y, side) where side is one of
            "top", "bottom", "left", or "right".
        """
        if self.orientation == ORIENTATION_FLOOR:
            return (self.x + self.width / 2, self.y, "top")
        elif self.orientation == ORIENTATION_CEILING:
            return (self.x + self.width / 2, self.y + self.height, "bottom")
        elif self.orientation == ORIENTATION_WALL_LEFT:
            return (self.x + self.width, self.y + self.height / 2, "right")
        elif self.orientation == ORIENTATION_WALL_RIGHT:
            return (self.x, self.y + self.height / 2, "left")
        return (self.x + self.width / 2, self.y, "top")
    
    def is_player_on_surface(
        self,
        player_rect: Tuple[float, float, float, float],
        tolerance: float = 5.0
    ) -> bool:
        """Check if player is on this platform's surface.

        Args:
            player_rect: Player bounding box (x, y, width, height).
            tolerance: Distance tolerance for contact detection.

        Returns:
            True if player is within tolerance of the platform surface,
            False otherwise.
        """
        px, py, pw, ph = player_rect
        
        if self.orientation == ORIENTATION_FLOOR:
            # Player bottom touching platform top
            return (abs((py + ph) - self.y) <= tolerance and
                    px + pw > self.x and px < self.x + self.width)
        
        elif self.orientation == ORIENTATION_CEILING:
            # Player top touching platform bottom
            return (abs(py - (self.y + self.height)) <= tolerance and
                    px + pw > self.x and px < self.x + self.width)
        
        elif self.orientation == ORIENTATION_WALL_LEFT:
            # Player right touching wall left
            return (abs((px + pw) - self.x) <= tolerance and
                    py + ph > self.y and py < self.y + self.height)
        
        elif self.orientation == ORIENTATION_WALL_RIGHT:
            # Player left touching wall right
            return (abs(px - (self.x + self.width)) <= tolerance and
                    py + ph > self.y and py < self.y + self.height)
        
        return False
    
    def get_color(self) -> Tuple[int, int, int]:
        """Get platform color based on magnetic state.

        Returns:
            RGB tuple for the platform color. Returns magnetic color
            if platform is magnetic, otherwise returns normal color.
        """
        if self.is_magnetic:
            return COLOR_MAGNETIC_PLATFORM
        return COLOR_PLATFORM
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Draw the platform.

        Args:
            surface: The pygame surface to draw on.
            camera_offset: Tuple (x, y) offset for camera scrolling.
        """
        rect = pygame.Rect(
            int(self.x - camera_offset[0]),
            int(self.y - camera_offset[1]),
            int(self.width),
            int(self.height)
        )
        pygame.draw.rect(surface, self.get_color(), rect)
        
        # Draw magnetic indicator
        if self.is_magnetic:
            pygame.draw.rect(surface, (150, 150, 255), rect, 3)
    
    def to_dict(self) -> dict:
        """Serialize platform to dictionary.

        Returns:
            Dictionary containing all platform properties.
        """
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'is_magnetic': self.is_magnetic,
            'orientation': self.orientation
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Platform':
        """Create platform from dictionary.

        Args:
            data: Dictionary containing platform properties.

        Returns:
            A new Platform instance.
        """
        return cls(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height'],
            is_magnetic=data.get('is_magnetic', False),
            orientation=data.get('orientation', ORIENTATION_FLOOR)
        )


class MovingPlatform(Platform):
    """A platform that moves between two points."""
    
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        end_x: float,
        end_y: float,
        speed: float = 2.0,
        is_magnetic: bool = False,
        orientation: str = ORIENTATION_FLOOR
    ):
        """Initialize a moving platform.

        Args:
            x: Initial X position (top-left).
            y: Initial Y position (top-left).
            width: Platform width.
            height: Platform height.
            end_x: Destination X position.
            end_y: Destination Y position.
            speed: Movement speed multiplier.
            is_magnetic: Whether player can stick to this surface.
            orientation: Surface orientation for gravity/movement.
        """
        super().__init__(x, y, width, height, is_magnetic, orientation)
        self.start_x = x
        self.start_y = y
        self.end_x = end_x
        self.end_y = end_y
        self.speed = speed
        self.direction = 1  # 1 = towards end, -1 = towards start
        self.progress = 0.0  # 0 to 1
    
    def update(self) -> None:
        """Update platform position.

        Moves the platform along its path between start and end points.
        Reverses direction when reaching either endpoint.
        """
        self.progress += self.speed * self.direction * 0.01
        
        if self.progress >= 1.0:
            self.progress = 1.0
            self.direction = -1
        elif self.progress <= 0.0:
            self.progress = 0.0
            self.direction = 1
        
        self.x = self.start_x + (self.end_x - self.start_x) * self.progress
        self.y = self.start_y + (self.end_y - self.start_y) * self.progress
    
    def get_velocity(self) -> Tuple[float, float]:
        """Get current platform velocity.

        Returns:
            Tuple containing (dx, dy) velocity components.
        """
        dx = (self.end_x - self.start_x) * self.speed * 0.01 * self.direction
        dy = (self.end_y - self.start_y) * self.speed * 0.01 * self.direction
        return (dx, dy)
    
    def to_dict(self) -> dict:
        """Serialize moving platform to dictionary.

        Returns:
            Dictionary containing all moving platform properties,
            including inherited Platform properties.
        """
        data = super().to_dict()
        data.update({
            'end_x': self.end_x,
            'end_y': self.end_y,
            'speed': self.speed,
            'moving': True
        })
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MovingPlatform':
        """Create moving platform from dictionary.

        Args:
            data: Dictionary containing moving platform properties.

        Returns:
            A new MovingPlatform instance.
        """
        return cls(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height'],
            end_x=data['end_x'],
            end_y=data['end_y'],
            speed=data.get('speed', 2.0),
            is_magnetic=data.get('is_magnetic', False),
            orientation=data.get('orientation', ORIENTATION_FLOOR)
        )
