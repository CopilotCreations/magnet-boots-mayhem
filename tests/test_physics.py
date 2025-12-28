"""Tests for physics module."""

import pytest
import math

from src.physics import (
    calculate_distance,
    calculate_direction,
    apply_gravity,
    apply_friction,
    calculate_magnetic_force,
    check_rect_collision,
    resolve_collision,
    get_surface_normal,
    apply_surface_gravity,
    clamp
)
from src.constants import (
    GRAVITY, MAX_FALL_SPEED, FRICTION, AIR_RESISTANCE,
    MAGNETIC_STATE_NORMAL, MAGNETIC_STATE_STICKING,
    POLARITY_ATTRACT, POLARITY_REPEL,
    ORIENTATION_FLOOR, ORIENTATION_CEILING, ORIENTATION_WALL_LEFT, ORIENTATION_WALL_RIGHT
)


class TestCalculateDistance:
    """Tests for calculate_distance function."""
    
    def test_zero_distance(self):
        """Test distance between same point."""
        assert calculate_distance((0, 0), (0, 0)) == 0
        assert calculate_distance((5, 5), (5, 5)) == 0
    
    def test_horizontal_distance(self):
        """Test horizontal distance."""
        assert calculate_distance((0, 0), (10, 0)) == 10
        assert calculate_distance((5, 0), (0, 0)) == 5
    
    def test_vertical_distance(self):
        """Test vertical distance."""
        assert calculate_distance((0, 0), (0, 10)) == 10
        assert calculate_distance((0, 5), (0, 0)) == 5
    
    def test_diagonal_distance(self):
        """Test diagonal distance (3-4-5 triangle)."""
        assert calculate_distance((0, 0), (3, 4)) == 5
        assert calculate_distance((0, 0), (6, 8)) == 10
    
    def test_negative_coordinates(self):
        """Test with negative coordinates."""
        assert calculate_distance((-5, -5), (0, 0)) == pytest.approx(math.sqrt(50))


class TestCalculateDirection:
    """Tests for calculate_direction function."""
    
    def test_zero_distance(self):
        """Test direction when points are the same."""
        assert calculate_direction((0, 0), (0, 0)) == (0.0, 0.0)
    
    def test_right_direction(self):
        """Test direction to the right."""
        direction = calculate_direction((0, 0), (10, 0))
        assert direction[0] == pytest.approx(1.0)
        assert direction[1] == pytest.approx(0.0)
    
    def test_up_direction(self):
        """Test direction upward."""
        direction = calculate_direction((0, 0), (0, -10))
        assert direction[0] == pytest.approx(0.0)
        assert direction[1] == pytest.approx(-1.0)
    
    def test_diagonal_direction(self):
        """Test diagonal direction is normalized."""
        direction = calculate_direction((0, 0), (10, 10))
        magnitude = math.sqrt(direction[0]**2 + direction[1]**2)
        assert magnitude == pytest.approx(1.0)


class TestApplyGravity:
    """Tests for apply_gravity function."""
    
    def test_normal_state_applies_gravity(self):
        """Test gravity is applied in normal state."""
        velocity = apply_gravity(0, MAGNETIC_STATE_NORMAL)
        assert velocity == GRAVITY
    
    def test_sticking_state_no_gravity(self):
        """Test gravity is not applied when sticking."""
        velocity = apply_gravity(5, MAGNETIC_STATE_STICKING)
        assert velocity == 0.0
    
    def test_max_fall_speed(self):
        """Test velocity is capped at max fall speed."""
        velocity = apply_gravity(MAX_FALL_SPEED, MAGNETIC_STATE_NORMAL)
        assert velocity == MAX_FALL_SPEED
    
    def test_cumulative_gravity(self):
        """Test gravity accumulates."""
        velocity = 0
        for _ in range(5):
            velocity = apply_gravity(velocity, MAGNETIC_STATE_NORMAL)
        assert velocity == 5 * GRAVITY


class TestApplyFriction:
    """Tests for apply_friction function."""
    
    def test_ground_friction(self):
        """Test friction on ground."""
        velocity = apply_friction(10, on_ground=True)
        assert velocity == 10 * FRICTION
    
    def test_air_resistance(self):
        """Test air resistance when not on ground."""
        velocity = apply_friction(10, on_ground=False)
        assert velocity == 10 * AIR_RESISTANCE
    
    def test_zero_velocity(self):
        """Test friction on zero velocity."""
        assert apply_friction(0, on_ground=True) == 0
        assert apply_friction(0, on_ground=False) == 0


class TestCalculateMagneticForce:
    """Tests for calculate_magnetic_force function."""
    
    def test_out_of_range(self):
        """Test no force when out of range."""
        force = calculate_magnetic_force((0, 0), (200, 0), 100, 1.0, POLARITY_ATTRACT)
        assert force == (0.0, 0.0)
    
    def test_attract_force(self):
        """Test attract force direction."""
        force = calculate_magnetic_force((0, 0), (50, 0), 100, 1.0, POLARITY_ATTRACT)
        assert force[0] > 0  # Should be pulled right toward magnet
        assert force[1] == pytest.approx(0.0)
    
    def test_repel_force(self):
        """Test repel force direction."""
        force = calculate_magnetic_force((0, 0), (50, 0), 100, 1.0, POLARITY_REPEL)
        assert force[0] < 0  # Should be pushed left away from magnet
        assert force[1] == pytest.approx(0.0)
    
    def test_force_decreases_with_distance(self):
        """Test force is stronger when closer."""
        close_force = calculate_magnetic_force((0, 0), (20, 0), 100, 1.0, POLARITY_ATTRACT)
        far_force = calculate_magnetic_force((0, 0), (80, 0), 100, 1.0, POLARITY_ATTRACT)
        assert abs(close_force[0]) > abs(far_force[0])
    
    def test_zero_distance(self):
        """Test force at zero distance."""
        force = calculate_magnetic_force((50, 50), (50, 50), 100, 1.0, POLARITY_ATTRACT)
        assert force == (0.0, 0.0)


class TestCheckRectCollision:
    """Tests for check_rect_collision function."""
    
    def test_no_collision(self):
        """Test non-overlapping rectangles."""
        assert not check_rect_collision((0, 0, 10, 10), (20, 20, 10, 10))
    
    def test_collision(self):
        """Test overlapping rectangles."""
        assert check_rect_collision((0, 0, 20, 20), (10, 10, 20, 20))
    
    def test_touching_not_collision(self):
        """Test rectangles touching edges don't collide."""
        assert not check_rect_collision((0, 0, 10, 10), (10, 0, 10, 10))
    
    def test_contained(self):
        """Test one rectangle inside another."""
        assert check_rect_collision((0, 0, 100, 100), (25, 25, 10, 10))


class TestResolveCollision:
    """Tests for resolve_collision function."""
    
    def test_resolve_top_collision(self):
        """Test collision from top (landing on platform)."""
        player_rect = (50, 90, 20, 20)  # Player just above platform
        platform_rect = (0, 100, 200, 20)
        velocity = (0, 5)
        
        new_pos, new_vel, side = resolve_collision(player_rect, platform_rect, velocity)
        assert side == ORIENTATION_FLOOR
        assert new_vel[1] == 0
    
    def test_resolve_bottom_collision(self):
        """Test collision from bottom (hitting ceiling)."""
        player_rect = (50, 20, 20, 20)
        platform_rect = (0, 0, 200, 20)
        velocity = (0, -5)
        
        new_pos, new_vel, side = resolve_collision(player_rect, platform_rect, velocity)
        assert side == ORIENTATION_CEILING
        assert new_vel[1] == 0


class TestGetSurfaceNormal:
    """Tests for get_surface_normal function."""
    
    def test_floor_normal(self):
        """Test floor surface normal points up."""
        assert get_surface_normal(ORIENTATION_FLOOR) == (0, -1)
    
    def test_ceiling_normal(self):
        """Test ceiling surface normal points down."""
        assert get_surface_normal(ORIENTATION_CEILING) == (0, 1)
    
    def test_wall_left_normal(self):
        """Test left wall normal points right."""
        assert get_surface_normal(ORIENTATION_WALL_LEFT) == (1, 0)
    
    def test_wall_right_normal(self):
        """Test right wall normal points left."""
        assert get_surface_normal(ORIENTATION_WALL_RIGHT) == (-1, 0)
    
    def test_unknown_orientation(self):
        """Test unknown orientation defaults to floor."""
        assert get_surface_normal("unknown") == (0, -1)


class TestApplySurfaceGravity:
    """Tests for apply_surface_gravity function."""
    
    def test_floor_gravity(self):
        """Test gravity on floor surface."""
        velocity = apply_surface_gravity((0, 0), ORIENTATION_FLOOR)
        assert velocity[1] > 0  # Falls down
    
    def test_ceiling_gravity(self):
        """Test gravity on ceiling surface (inverted)."""
        velocity = apply_surface_gravity((0, 0), ORIENTATION_CEILING)
        assert velocity[1] < 0  # Falls up
    
    def test_wall_left_gravity(self):
        """Test gravity on left wall."""
        velocity = apply_surface_gravity((0, 0), ORIENTATION_WALL_LEFT)
        assert velocity[0] < 0  # Falls left
    
    def test_wall_right_gravity(self):
        """Test gravity on right wall."""
        velocity = apply_surface_gravity((0, 0), ORIENTATION_WALL_RIGHT)
        assert velocity[0] > 0  # Falls right


class TestClamp:
    """Tests for clamp function."""
    
    def test_clamp_below_min(self):
        """Test value below minimum is clamped."""
        assert clamp(-10, 0, 100) == 0
    
    def test_clamp_above_max(self):
        """Test value above maximum is clamped."""
        assert clamp(150, 0, 100) == 100
    
    def test_clamp_in_range(self):
        """Test value in range is unchanged."""
        assert clamp(50, 0, 100) == 50
    
    def test_clamp_at_boundaries(self):
        """Test values at boundaries."""
        assert clamp(0, 0, 100) == 0
        assert clamp(100, 0, 100) == 100
