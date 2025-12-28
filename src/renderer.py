"""Rendering system for drawing game objects."""

from typing import Tuple, Optional, List
import pygame

from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BLACK, COLOR_WHITE,
    COLOR_GOAL, COLOR_MAGNETIC_BLUE
)
from .player import Player
from .platforms import Platform
from .magnets import Magnet
from .enemies import Enemy
from .level import Level


class Camera:
    """Camera for following the player and scrolling the view."""
    
    def __init__(self, width: int, height: int):
        """
        Initialize camera.
        
        Args:
            width: Camera viewport width
            height: Camera viewport height
        """
        self.x = 0.0
        self.y = 0.0
        self.width = width
        self.height = height
        self.smoothing = 0.1
    
    @property
    def offset(self) -> Tuple[float, float]:
        """Get camera offset for rendering."""
        return (self.x, self.y)
    
    def follow(self, target_x: float, target_y: float, level_width: int, level_height: int) -> None:
        """
        Smoothly follow a target position.
        
        Args:
            target_x: Target X position (usually player center)
            target_y: Target Y position (usually player center)
            level_width: Total level width for bounds
            level_height: Total level height for bounds
        """
        # Calculate desired camera position (centered on target)
        desired_x = target_x - self.width / 2
        desired_y = target_y - self.height / 2
        
        # Smooth interpolation
        self.x += (desired_x - self.x) * self.smoothing
        self.y += (desired_y - self.y) * self.smoothing
        
        # Clamp to level bounds
        self.x = max(0, min(self.x, level_width - self.width))
        self.y = max(0, min(self.y, level_height - self.height))
    
    def reset(self, x: float = 0, y: float = 0) -> None:
        """Reset camera position."""
        self.x = x
        self.y = y


class Renderer:
    """Handles all rendering operations."""
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize renderer.
        
        Args:
            screen: Pygame surface to render to
        """
        self.screen = screen
        self.camera = Camera(screen.get_width(), screen.get_height())
        self.font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        self._init_fonts()
    
    def _init_fonts(self) -> None:
        """Initialize fonts."""
        try:
            pygame.font.init()
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        except pygame.error:
            pass
    
    def clear(self, color: Tuple[int, int, int] = COLOR_BLACK) -> None:
        """Clear the screen with a color."""
        self.screen.fill(color)
    
    def draw_level(self, level: Level) -> None:
        """Draw entire level."""
        self.clear(level.background_color)
        
        # Draw magnets (with range indicators)
        for magnet in level.magnets:
            magnet.draw(self.screen, self.camera.offset)
        
        # Draw platforms
        for platform in level.platforms:
            platform.draw(self.screen, self.camera.offset)
        
        # Draw goal
        self.draw_goal(level.goal_rect)
        
        # Draw enemies
        for enemy in level.enemies:
            enemy.draw(self.screen, self.camera.offset)
    
    def draw_player(self, player: Player) -> None:
        """Draw the player."""
        player.draw(self.screen, self.camera.offset)
    
    def draw_goal(self, goal_rect: Tuple[float, float, float, float]) -> None:
        """Draw the level goal."""
        x, y, w, h = goal_rect
        rect = pygame.Rect(
            int(x - self.camera.offset[0]),
            int(y - self.camera.offset[1]),
            int(w),
            int(h)
        )
        pygame.draw.rect(self.screen, COLOR_GOAL, rect)
        pygame.draw.rect(self.screen, COLOR_WHITE, rect, 2)
        
        # Draw star shape or indicator
        center_x = rect.x + rect.width // 2
        center_y = rect.y + rect.height // 2
        pygame.draw.circle(self.screen, COLOR_WHITE, (center_x, center_y), 10)
    
    def draw_hud(self, player: Player, level_name: str = "") -> None:
        """Draw heads-up display."""
        if not self.font:
            return
        
        # Draw level name
        if level_name:
            text = self.font.render(level_name, True, COLOR_WHITE)
            self.screen.blit(text, (10, 10))
        
        # Draw magnetic state
        state_text = "MAGNETIC BOOTS: "
        state_text += "ON" if player.boots_active else "OFF"
        if player.magnetic_state == "sticking":
            state_text += " (STICKING)"
        
        color = COLOR_MAGNETIC_BLUE if player.boots_active else (150, 150, 150)
        text = self.small_font.render(state_text, True, color)
        self.screen.blit(text, (10, self.screen.get_height() - 30))
    
    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        color: Tuple[int, int, int] = COLOR_WHITE,
        font: Optional[pygame.font.Font] = None
    ) -> None:
        """Draw text at specified position."""
        if font is None:
            font = self.font
        if font is None:
            return
        
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))
    
    def draw_centered_text(
        self,
        text: str,
        y: int,
        color: Tuple[int, int, int] = COLOR_WHITE,
        font: Optional[pygame.font.Font] = None
    ) -> None:
        """Draw text centered horizontally."""
        if font is None:
            font = self.font
        if font is None:
            return
        
        surface = font.render(text, True, color)
        x = (self.screen.get_width() - surface.get_width()) // 2
        self.screen.blit(surface, (x, y))
    
    def draw_menu(self, title: str, options: List[str], selected: int) -> None:
        """Draw a menu screen."""
        self.clear((20, 20, 30))
        
        # Draw title
        if self.font:
            title_font = pygame.font.Font(None, 72)
            self.draw_centered_text(title, 100, COLOR_MAGNETIC_BLUE, title_font)
        
        # Draw options
        for i, option in enumerate(options):
            color = COLOR_GOAL if i == selected else COLOR_WHITE
            y = 250 + i * 50
            self.draw_centered_text(option, y, color)
    
    def draw_pause_overlay(self) -> None:
        """Draw pause screen overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        self.draw_centered_text("PAUSED", self.screen.get_height() // 2 - 50)
        if self.small_font:
            self.draw_centered_text(
                "Press ESC to resume or R to restart",
                self.screen.get_height() // 2 + 20,
                font=self.small_font
            )
    
    def draw_game_over(self, won: bool) -> None:
        """Draw game over screen."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        if won:
            self.draw_centered_text("LEVEL COMPLETE!", self.screen.get_height() // 2 - 50, COLOR_GOAL)
        else:
            self.draw_centered_text("GAME OVER", self.screen.get_height() // 2 - 50, (255, 100, 100))
        
        if self.small_font:
            self.draw_centered_text(
                "Press R to restart or ESC for menu",
                self.screen.get_height() // 2 + 20,
                font=self.small_font
            )
    
    def update_camera(self, player: Player, level: Level) -> None:
        """Update camera to follow player."""
        self.camera.follow(
            player.x + player.width / 2,
            player.y + player.height / 2,
            level.width,
            level.height
        )
    
    def present(self) -> None:
        """Present the rendered frame."""
        pygame.display.flip()
