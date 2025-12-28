"""Player class with magnetic boots capability."""

from typing import Tuple, Optional, List
import pygame

from .constants import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_JUMP_STRENGTH,
    MAGNETIC_STATE_NORMAL, MAGNETIC_STATE_STICKING,
    COLOR_PLAYER, SCREEN_WIDTH, SCREEN_HEIGHT,
    ORIENTATION_FLOOR, ORIENTATION_CEILING, ORIENTATION_WALL_LEFT, ORIENTATION_WALL_RIGHT
)
from .physics import (
    apply_gravity, apply_friction, check_rect_collision, resolve_collision,
    get_surface_normal, clamp
)
from .platforms import Platform


class Player:
    """Player character with magnetic boots."""
    
    def __init__(self, x: float, y: float):
        """
        Initialize player.
        
        Args:
            x: Starting X position
            y: Starting Y position
        """
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.magnetic_state = MAGNETIC_STATE_NORMAL
        self.current_surface: Optional[Platform] = None
        self.current_orientation = ORIENTATION_FLOOR
        self.on_ground = False
        self.facing_right = True
        self.boots_active = True
        self.jump_count = 0
        self.max_jumps = 2
    
    @property
    def position(self) -> Tuple[float, float]:
        """Get player center position."""
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    @property
    def rect(self) -> Tuple[float, float, float, float]:
        """Get player bounding rect."""
        return (self.x, self.y, self.width, self.height)
    
    @property
    def pygame_rect(self) -> pygame.Rect:
        """Get player as pygame Rect."""
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))
    
    @property
    def velocity(self) -> Tuple[float, float]:
        """Get velocity tuple."""
        return (self.velocity_x, self.velocity_y)
    
    def move(self, horizontal: float, vertical: float = 0) -> None:
        """
        Move player horizontally (and vertically when on walls/ceiling).
        
        Args:
            horizontal: Horizontal input (-1, 0, or 1)
            vertical: Vertical input for wall climbing (-1, 0, or 1)
        """
        if horizontal != 0:
            self.facing_right = horizontal > 0
        
        if self.magnetic_state == MAGNETIC_STATE_STICKING:
            # When sticking, movement is relative to surface
            if self.current_orientation in (ORIENTATION_FLOOR, ORIENTATION_CEILING):
                self.velocity_x = horizontal * PLAYER_SPEED
            elif self.current_orientation in (ORIENTATION_WALL_LEFT, ORIENTATION_WALL_RIGHT):
                self.velocity_y = vertical * PLAYER_SPEED
        else:
            # Normal movement
            self.velocity_x = horizontal * PLAYER_SPEED
    
    def jump(self) -> bool:
        """
        Make player jump.
        
        Returns:
            True if jump was successful
        """
        if self.magnetic_state == MAGNETIC_STATE_STICKING:
            # Jump off surface
            self.detach_from_surface()
            normal = get_surface_normal(self.current_orientation)
            self.velocity_x += normal[0] * PLAYER_JUMP_STRENGTH
            self.velocity_y += normal[1] * PLAYER_JUMP_STRENGTH
            self.jump_count = 1
            return True
        
        if self.on_ground or self.jump_count < self.max_jumps:
            self.velocity_y = -PLAYER_JUMP_STRENGTH
            self.on_ground = False
            self.jump_count += 1
            return True
        
        return False
    
    def toggle_magnetic_state(self) -> None:
        """Toggle magnetic boots on/off."""
        self.boots_active = not self.boots_active
        
        if not self.boots_active and self.magnetic_state == MAGNETIC_STATE_STICKING:
            self.detach_from_surface()
    
    def apply_gravity(self) -> None:
        """Apply gravity to player."""
        if self.magnetic_state != MAGNETIC_STATE_STICKING:
            self.velocity_y = apply_gravity(self.velocity_y, self.magnetic_state)
    
    def apply_friction(self) -> None:
        """Apply friction to player movement."""
        self.velocity_x = apply_friction(self.velocity_x, self.on_ground)
    
    def stick_to_surface(self, platform: Platform, collision_side: str) -> None:
        """
        Attach to a magnetic surface.
        
        Args:
            platform: The platform to stick to
            collision_side: Which side of the platform was hit
        """
        if not self.boots_active or not platform.is_magnetic:
            return
        
        self.magnetic_state = MAGNETIC_STATE_STICKING
        self.current_surface = platform
        self.current_orientation = collision_side
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = True
        self.jump_count = 0
    
    def detach_from_surface(self) -> None:
        """Detach from current surface."""
        self.magnetic_state = MAGNETIC_STATE_NORMAL
        self.current_surface = None
        self.on_ground = False
    
    def apply_magnetic_force(self, force: Tuple[float, float]) -> None:
        """Apply external magnetic force to player."""
        if self.magnetic_state != MAGNETIC_STATE_STICKING:
            self.velocity_x += force[0]
            self.velocity_y += force[1]
    
    def update(self, platforms: List[Platform]) -> None:
        """
        Update player physics and handle collisions.
        
        Args:
            platforms: List of platforms to check collision against
        """
        # Apply physics
        self.apply_gravity()
        self.apply_friction()
        
        # Store old position for collision resolution
        old_x, old_y = self.x, self.y
        
        # Apply velocity
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Reset ground state
        was_on_ground = self.on_ground
        if self.magnetic_state != MAGNETIC_STATE_STICKING:
            self.on_ground = False
        
        # Handle collisions
        for platform in platforms:
            if check_rect_collision(self.rect, platform.rect):
                (new_pos, new_vel, collision_side) = resolve_collision(
                    self.rect,
                    platform.rect,
                    self.velocity
                )
                self.x, self.y = new_pos
                self.velocity_x, self.velocity_y = new_vel
                
                # Check for magnetic sticking
                if collision_side and platform.is_magnetic and self.boots_active:
                    self.stick_to_surface(platform, collision_side)
                elif collision_side == ORIENTATION_FLOOR:
                    self.on_ground = True
                    self.jump_count = 0
        
        # Check if still on current surface when sticking
        if self.magnetic_state == MAGNETIC_STATE_STICKING and self.current_surface:
            if not self.current_surface.is_player_on_surface(self.rect, tolerance=10):
                self.detach_from_surface()
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Draw the player."""
        rect = pygame.Rect(
            int(self.x - camera_offset[0]),
            int(self.y - camera_offset[1]),
            int(self.width),
            int(self.height)
        )
        
        # Draw body
        color = COLOR_PLAYER
        if self.magnetic_state == MAGNETIC_STATE_STICKING:
            color = (100, 200, 255)  # Glowing blue when sticking
        
        pygame.draw.rect(surface, color, rect)
        
        # Draw boots indicator
        boot_color = (0, 100, 255) if self.boots_active else (100, 100, 100)
        boot_rect = pygame.Rect(
            rect.x,
            rect.y + rect.height - 8,
            rect.width,
            8
        )
        pygame.draw.rect(surface, boot_color, boot_rect)
        
        # Draw facing direction indicator
        eye_x = rect.x + (rect.width * 0.7 if self.facing_right else rect.width * 0.3)
        pygame.draw.circle(surface, (255, 255, 255), (int(eye_x), rect.y + 10), 4)
    
    def reset(self, x: float, y: float) -> None:
        """Reset player to specified position."""
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.magnetic_state = MAGNETIC_STATE_NORMAL
        self.current_surface = None
        self.current_orientation = ORIENTATION_FLOOR
        self.on_ground = False
        self.boots_active = True
        self.jump_count = 0
