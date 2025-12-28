"""Physics engine for magnetic interactions, gravity, and collisions."""

import math
from typing import Tuple, List, Optional, TYPE_CHECKING

from .constants import (
    GRAVITY, MAX_FALL_SPEED, FRICTION, AIR_RESISTANCE,
    MAGNETIC_STATE_STICKING, POLARITY_ATTRACT, POLARITY_REPEL,
    ORIENTATION_FLOOR, ORIENTATION_CEILING, ORIENTATION_WALL_LEFT, ORIENTATION_WALL_RIGHT
)

if TYPE_CHECKING:
    from .player import Player
    from .magnets import Magnet
    from .platforms import Platform


def calculate_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return math.sqrt(dx * dx + dy * dy)


def calculate_direction(from_pos: Tuple[float, float], to_pos: Tuple[float, float]) -> Tuple[float, float]:
    """Calculate normalized direction vector from one point to another."""
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    distance = calculate_distance(from_pos, to_pos)
    
    if distance == 0:
        return (0.0, 0.0)
    
    return (dx / distance, dy / distance)


def apply_gravity(velocity_y: float, magnetic_state: str, surface_orientation: Optional[str] = None) -> float:
    """Apply gravity to vertical velocity based on magnetic state."""
    if magnetic_state == MAGNETIC_STATE_STICKING:
        return 0.0
    
    new_velocity = velocity_y + GRAVITY
    return min(new_velocity, MAX_FALL_SPEED)


def apply_friction(velocity_x: float, on_ground: bool) -> float:
    """Apply friction to horizontal velocity."""
    if on_ground:
        return velocity_x * FRICTION
    return velocity_x * AIR_RESISTANCE


def calculate_magnetic_force(
    object_pos: Tuple[float, float],
    magnet_pos: Tuple[float, float],
    magnet_range: float,
    magnet_strength: float,
    polarity: str
) -> Tuple[float, float]:
    """Calculate magnetic force applied to an object."""
    distance = calculate_distance(object_pos, magnet_pos)
    
    if distance > magnet_range or distance == 0:
        return (0.0, 0.0)
    
    # Force decreases with distance squared (inverse square law)
    force_magnitude = magnet_strength * (1 - (distance / magnet_range)) ** 2
    
    direction = calculate_direction(object_pos, magnet_pos)
    
    # Reverse direction for repel
    if polarity == POLARITY_REPEL:
        direction = (-direction[0], -direction[1])
    
    return (direction[0] * force_magnitude, direction[1] * force_magnitude)


def check_rect_collision(
    rect1: Tuple[float, float, float, float],
    rect2: Tuple[float, float, float, float]
) -> bool:
    """Check if two rectangles collide. Rect format: (x, y, width, height)."""
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    
    return (x1 < x2 + w2 and
            x1 + w1 > x2 and
            y1 < y2 + h2 and
            y1 + h1 > y2)


def resolve_collision(
    player_rect: Tuple[float, float, float, float],
    platform_rect: Tuple[float, float, float, float],
    velocity: Tuple[float, float]
) -> Tuple[Tuple[float, float], Tuple[float, float], str]:
    """
    Resolve collision between player and platform.
    Returns: (new_position, new_velocity, collision_side)
    """
    px, py, pw, ph = player_rect
    plat_x, plat_y, plat_w, plat_h = platform_rect
    vx, vy = velocity
    
    # Calculate overlap on each axis
    overlap_left = (px + pw) - plat_x
    overlap_right = (plat_x + plat_w) - px
    overlap_top = (py + ph) - plat_y
    overlap_bottom = (plat_y + plat_h) - py
    
    # Find minimum overlap
    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
    
    new_x, new_y = px, py
    new_vx, new_vy = vx, vy
    collision_side = ""
    
    if min_overlap == overlap_top and vy >= 0:
        new_y = plat_y - ph
        new_vy = 0
        collision_side = ORIENTATION_FLOOR
    elif min_overlap == overlap_bottom and vy <= 0:
        new_y = plat_y + plat_h
        new_vy = 0
        collision_side = ORIENTATION_CEILING
    elif min_overlap == overlap_left and vx >= 0:
        new_x = plat_x - pw
        new_vx = 0
        collision_side = ORIENTATION_WALL_RIGHT
    elif min_overlap == overlap_right and vx <= 0:
        new_x = plat_x + plat_w
        new_vx = 0
        collision_side = ORIENTATION_WALL_LEFT
    
    return ((new_x, new_y), (new_vx, new_vy), collision_side)


def get_surface_normal(orientation: str) -> Tuple[float, float]:
    """Get the normal vector for a surface orientation."""
    normals = {
        ORIENTATION_FLOOR: (0, -1),
        ORIENTATION_CEILING: (0, 1),
        ORIENTATION_WALL_LEFT: (1, 0),
        ORIENTATION_WALL_RIGHT: (-1, 0)
    }
    return normals.get(orientation, (0, -1))


def apply_surface_gravity(
    velocity: Tuple[float, float],
    orientation: str
) -> Tuple[float, float]:
    """Apply gravity relative to the surface the player is stuck to."""
    vx, vy = velocity
    
    if orientation == ORIENTATION_FLOOR:
        return (vx, min(vy + GRAVITY, MAX_FALL_SPEED))
    elif orientation == ORIENTATION_CEILING:
        return (vx, max(vy - GRAVITY, -MAX_FALL_SPEED))
    elif orientation == ORIENTATION_WALL_LEFT:
        return (max(vx - GRAVITY, -MAX_FALL_SPEED), vy)
    elif orientation == ORIENTATION_WALL_RIGHT:
        return (min(vx + GRAVITY, MAX_FALL_SPEED), vy)
    
    return (vx, min(vy + GRAVITY, MAX_FALL_SPEED))


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(value, max_val))
