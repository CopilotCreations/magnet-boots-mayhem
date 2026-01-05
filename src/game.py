"""Main game class handling the game loop and state management."""

from typing import Optional, List
from enum import Enum, auto
import pygame

from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    MAGNETIC_STATE_STICKING
)
from .player import Player
from .level import Level, create_demo_level, create_tutorial_level
from .input_handler import InputHandler
from .renderer import Renderer
from .physics import check_rect_collision


class GameState(Enum):
    """Game state enumeration."""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    LEVEL_COMPLETE = auto()
    GAME_OVER = auto()


class Game:
    """Main game class."""
    
    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        """
        Initialize the game.
        
        Args:
            width: Screen width
            height: Screen height
        """
        pygame.init()
        pygame.display.set_caption(TITLE)
        
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        self.renderer = Renderer(self.screen)
        self.input_handler = InputHandler()
        
        self.player: Optional[Player] = None
        self.current_level: Optional[Level] = None
        self.levels: List[Level] = []
        self.current_level_index = 0
        
        self.menu_selection = 0
        self.menu_options = ["Start Game", "Tutorial", "Quit"]
        
        self._load_levels()
    
    def _load_levels(self) -> None:
        """Load all game levels.
        
        Initializes the levels list with tutorial and demo levels.
        """
        self.levels = [
            create_tutorial_level(),
            create_demo_level()
        ]
    
    def _start_level(self, level_index: int) -> None:
        """Start a specific level.
        
        Args:
            level_index: The index of the level to start in the levels list.
        """
        if 0 <= level_index < len(self.levels):
            self.current_level_index = level_index
            self.current_level = self.levels[level_index]
            self.player = Player(*self.current_level.player_start)
            self.renderer.camera.reset()
            self.state = GameState.PLAYING
    
    def _restart_level(self) -> None:
        """Restart the current level.
        
        Resets player position, camera, game state, and revives all enemies.
        """
        if self.current_level and self.player:
            self.player.reset(*self.current_level.player_start)
            self.renderer.camera.reset()
            self.state = GameState.PLAYING
            
            # Reset enemies
            for enemy in self.current_level.enemies:
                enemy.alive = True
    
    def _next_level(self) -> None:
        """Advance to the next level.
        
        If all levels are complete, returns to the main menu.
        """
        next_index = self.current_level_index + 1
        if next_index < len(self.levels):
            self._start_level(next_index)
        else:
            # All levels complete
            self.state = GameState.MENU
    
    def handle_events(self) -> List:
        """Handle pygame events.
        
        Processes quit events and updates the input handler.
        
        Returns:
            List of pygame events that occurred this frame.
        """
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        
        self.input_handler.update(events)
        return events
    
    def update_menu(self) -> None:
        """Update menu state.
        
        Handles menu navigation and selection using up/down keys and jump to confirm.
        """
        if self.input_handler.is_action_just_pressed('move_up'):
            self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
        elif self.input_handler.is_action_just_pressed('move_down'):
            self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
        elif self.input_handler.is_action_just_pressed('jump'):
            if self.menu_selection == 0:  # Start Game
                self._start_level(1)  # Demo level
            elif self.menu_selection == 1:  # Tutorial
                self._start_level(0)
            elif self.menu_selection == 2:  # Quit
                self.running = False
    
    def update_playing(self) -> None:
        """Update game playing state.
        
        Handles player input, physics, enemy collisions, goal detection,
        and camera updates during active gameplay.
        """
        if not self.player or not self.current_level:
            return
        
        # Handle pause
        if self.input_handler.is_action_just_pressed('pause'):
            self.state = GameState.PAUSED
            return
        
        # Handle restart
        if self.input_handler.is_action_just_pressed('restart'):
            self._restart_level()
            return
        
        # Handle player input
        movement = self.input_handler.get_movement_vector()
        self.player.move(movement[0], movement[1])
        
        if self.input_handler.is_action_just_pressed('jump'):
            self.player.jump()
        
        if self.input_handler.is_action_just_pressed('toggle_magnetic'):
            self.player.toggle_magnetic_state()
        
        # Apply magnetic forces from magnets
        magnetic_force = self.current_level.get_total_magnetic_force(self.player.position)
        self.player.apply_magnetic_force(magnetic_force)
        
        # Update player
        self.player.update(self.current_level.platforms)
        
        # Update level (enemies, moving platforms)
        self.current_level.update()
        
        # Check enemy collisions
        for enemy in self.current_level.enemies:
            if enemy.check_player_collision(self.player.rect):
                # Player hit by enemy - game over
                self.state = GameState.GAME_OVER
                return
        
        # Check goal
        if check_rect_collision(self.player.rect, self.current_level.goal_rect):
            self.state = GameState.LEVEL_COMPLETE
            return
        
        # Check if player fell off level
        if self.player.y > self.current_level.height + 100:
            self.state = GameState.GAME_OVER
            return
        
        # Update camera
        self.renderer.update_camera(self.player, self.current_level)
    
    def update_paused(self) -> None:
        """Update paused state.
        
        Handles unpausing the game or restarting the level.
        """
        if self.input_handler.is_action_just_pressed('pause'):
            self.state = GameState.PLAYING
        elif self.input_handler.is_action_just_pressed('restart'):
            self._restart_level()
    
    def update_level_complete(self) -> None:
        """Update level complete state.
        
        Handles advancing to the next level or returning to the menu.
        """
        if self.input_handler.is_action_just_pressed('jump'):
            self._next_level()
        elif self.input_handler.is_action_just_pressed('pause'):
            self.state = GameState.MENU
    
    def update_game_over(self) -> None:
        """Update game over state.
        
        Handles restarting the level or returning to the menu.
        """
        if self.input_handler.is_action_just_pressed('restart'):
            self._restart_level()
        elif self.input_handler.is_action_just_pressed('pause'):
            self.state = GameState.MENU
    
    def update(self) -> None:
        """Update game state.
        
        Delegates to the appropriate state-specific update method based on
        the current game state.
        """
        if self.state == GameState.MENU:
            self.update_menu()
        elif self.state == GameState.PLAYING:
            self.update_playing()
        elif self.state == GameState.PAUSED:
            self.update_paused()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.update_level_complete()
        elif self.state == GameState.GAME_OVER:
            self.update_game_over()
    
    def render(self) -> None:
        """Render the current game state.
        
        Draws the appropriate visuals based on the current game state,
        including menu, gameplay, pause overlay, or game over screens.
        """
        if self.state == GameState.MENU:
            self.renderer.draw_menu(TITLE, self.menu_options, self.menu_selection)
        
        elif self.state == GameState.PLAYING:
            if self.current_level and self.player:
                self.renderer.draw_level(self.current_level)
                self.renderer.draw_player(self.player)
                self.renderer.draw_hud(self.player, self.current_level.name)
        
        elif self.state == GameState.PAUSED:
            if self.current_level and self.player:
                self.renderer.draw_level(self.current_level)
                self.renderer.draw_player(self.player)
                self.renderer.draw_hud(self.player, self.current_level.name)
            self.renderer.draw_pause_overlay()
        
        elif self.state == GameState.LEVEL_COMPLETE:
            if self.current_level and self.player:
                self.renderer.draw_level(self.current_level)
                self.renderer.draw_player(self.player)
            self.renderer.draw_game_over(won=True)
        
        elif self.state == GameState.GAME_OVER:
            if self.current_level and self.player:
                self.renderer.draw_level(self.current_level)
                self.renderer.draw_player(self.player)
            self.renderer.draw_game_over(won=False)
        
        self.renderer.present()
    
    def run(self) -> None:
        """Main game loop.
        
        Continuously processes events, updates state, and renders frames
        until the game is terminated. Cleans up pygame on exit.
        """
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()


def main() -> None:
    """Entry point for the game.
    
    Creates a Game instance and starts the main game loop.
    """
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
