"""Input handling for keyboard controls."""

from typing import Dict, Callable, Optional, Set
import pygame


class InputHandler:
    """Handles keyboard input and key mappings."""
    
    # Default key bindings
    DEFAULT_BINDINGS = {
        'move_left': pygame.K_LEFT,
        'move_left_alt': pygame.K_a,
        'move_right': pygame.K_RIGHT,
        'move_right_alt': pygame.K_d,
        'move_up': pygame.K_UP,
        'move_up_alt': pygame.K_w,
        'move_down': pygame.K_DOWN,
        'move_down_alt': pygame.K_s,
        'jump': pygame.K_SPACE,
        'toggle_magnetic': pygame.K_m,
        'sprint': pygame.K_LSHIFT,
        'pause': pygame.K_ESCAPE,
        'restart': pygame.K_r,
    }
    
    def __init__(self, custom_bindings: Optional[Dict[str, int]] = None):
        """
        Initialize input handler with optional custom key bindings.
        
        Args:
            custom_bindings: Dictionary mapping action names to pygame key codes
        """
        self.bindings = self.DEFAULT_BINDINGS.copy()
        if custom_bindings:
            self.bindings.update(custom_bindings)
        
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()
    
    def update(self, events: list) -> None:
        """
        Update input state based on pygame events.
        
        Args:
            events: List of pygame events
        """
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self.keys_just_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
                self.keys_just_released.add(event.key)
    
    def is_action_pressed(self, action: str) -> bool:
        """Check if an action's key is currently pressed."""
        key = self.bindings.get(action)
        alt_key = self.bindings.get(f"{action}_alt")
        
        if key and key in self.keys_pressed:
            return True
        if alt_key and alt_key in self.keys_pressed:
            return True
        return False
    
    def is_action_just_pressed(self, action: str) -> bool:
        """Check if an action's key was just pressed this frame."""
        key = self.bindings.get(action)
        alt_key = self.bindings.get(f"{action}_alt")
        
        if key and key in self.keys_just_pressed:
            return True
        if alt_key and alt_key in self.keys_just_pressed:
            return True
        return False
    
    def is_action_just_released(self, action: str) -> bool:
        """Check if an action's key was just released this frame."""
        key = self.bindings.get(action)
        alt_key = self.bindings.get(f"{action}_alt")
        
        if key and key in self.keys_just_released:
            return True
        if alt_key and alt_key in self.keys_just_released:
            return True
        return False
    
    def get_movement_vector(self) -> tuple:
        """
        Get normalized movement vector from input.
        
        Returns:
            Tuple of (horizontal, vertical) movement (-1, 0, or 1 each)
        """
        horizontal = 0
        vertical = 0
        
        if self.is_action_pressed('move_left'):
            horizontal -= 1
        if self.is_action_pressed('move_right'):
            horizontal += 1
        if self.is_action_pressed('move_up'):
            vertical -= 1
        if self.is_action_pressed('move_down'):
            vertical += 1
        
        return (horizontal, vertical)
    
    def set_binding(self, action: str, key: int) -> None:
        """Set a custom key binding for an action."""
        self.bindings[action] = key
    
    def get_binding(self, action: str) -> Optional[int]:
        """Get the key code for an action."""
        return self.bindings.get(action)
    
    def get_binding_name(self, action: str) -> str:
        """Get human-readable name for an action's key binding."""
        key = self.bindings.get(action)
        if key is None:
            return "Unbound"
        return pygame.key.name(key).upper()
    
    def reset_to_defaults(self) -> None:
        """Reset all bindings to defaults."""
        self.bindings = self.DEFAULT_BINDINGS.copy()


class InputAction:
    """Represents an input action with callbacks."""
    
    def __init__(self, name: str):
        self.name = name
        self.on_pressed: Optional[Callable] = None
        self.on_released: Optional[Callable] = None
        self.on_held: Optional[Callable] = None
    
    def bind_pressed(self, callback: Callable) -> 'InputAction':
        """Bind a callback to key press."""
        self.on_pressed = callback
        return self
    
    def bind_released(self, callback: Callable) -> 'InputAction':
        """Bind a callback to key release."""
        self.on_released = callback
        return self
    
    def bind_held(self, callback: Callable) -> 'InputAction':
        """Bind a callback to key held."""
        self.on_held = callback
        return self


def create_game_input_handler() -> InputHandler:
    """Create and return a configured input handler for the game."""
    return InputHandler()
