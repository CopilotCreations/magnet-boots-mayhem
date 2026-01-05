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
        """Test distance between same point.

        Verifies that the distance between identical points is zero.
        """
        assert calculate_distance((0, 0), (0, 0)) == 0
        assert calculate_distance((5, 5), (5, 5)) == 0
    
    def test_horizontal_distance(self):
        """Test horizontal distance.

        Verifies distance calculation along the x-axis only.
        """
        assert calculate_distance((0, 0), (10, 0)) == 10
        assert calculate_distance((5, 0), (0, 0)) == 5
    
    def test_vertical_distance(self):
        """Test vertical distance.

        Verifies distance calculation along the y-axis only.
        """
        assert calculate_distance((0, 0), (0, 10)) == 10
        assert calculate_distance((0, 5), (0, 0)) == 5
    
    def test_diagonal_distance(self):
        """Test diagonal distance using Pythagorean theorem.

        Uses 3-4-5 and 6-8-10 right triangles to verify calculation.
        """
        assert calculate_distance((0, 0), (3, 4)) == 5
        assert calculate_distance((0, 0), (6, 8)) == 10
    
    def test_negative_coordinates(self):
        """Test distance calculation with negative coordinates.

        Verifies that negative coordinates are handled correctly.
        """
        assert calculate_distance((-5, -5), (0, 0)) == pytest.approx(math.sqrt(50))


class TestCalculateDirection:
    """Tests for calculate_direction function."""
    
    def test_zero_distance(self):
        """Test direction when points are the same.

        Verifies that direction is (0, 0) when both points are identical.
        """
        assert calculate_direction((0, 0), (0, 0)) == (0.0, 0.0)
    
    def test_right_direction(self):
        """Test direction to the right.

        Verifies that direction vector points right with unit magnitude.
        """
        direction = calculate_direction((0, 0), (10, 0))
        assert direction[0] == pytest.approx(1.0)
        assert direction[1] == pytest.approx(0.0)
    
    def test_up_direction(self):
        """Test direction upward.

        Verifies that direction vector points up with unit magnitude.
        """
        direction = calculate_direction((0, 0), (0, -10))
        assert direction[0] == pytest.approx(0.0)
        assert direction[1] == pytest.approx(-1.0)
    
    def test_diagonal_direction(self):
        """Test diagonal direction is normalized.

        Verifies that the returned direction vector has unit magnitude.
        """
        direction = calculate_direction((0, 0), (10, 10))
        magnitude = math.sqrt(direction[0]**2 + direction[1]**2)
        assert magnitude == pytest.approx(1.0)


class TestApplyGravity:
    """Tests for apply_gravity function."""
    
    def test_normal_state_applies_gravity(self):
        """Test gravity is applied in normal state.

        Verifies that gravity constant is added to velocity when not sticking.
        """
        velocity = apply_gravity(0, MAGNETIC_STATE_NORMAL)
        assert velocity == GRAVITY
    
    def test_sticking_state_no_gravity(self):
        """Test gravity is not applied when sticking.

        Verifies that velocity is zeroed when magnetically attached to surface.
        """
        velocity = apply_gravity(5, MAGNETIC_STATE_STICKING)
        assert velocity == 0.0
    
    def test_max_fall_speed(self):
        """Test velocity is capped at max fall speed.

        Verifies that terminal velocity is enforced.
        """
        velocity = apply_gravity(MAX_FALL_SPEED, MAGNETIC_STATE_NORMAL)
        assert velocity == MAX_FALL_SPEED
    
    def test_cumulative_gravity(self):
        """Test gravity accumulates over time.

        Verifies that gravity is added each frame for acceleration effect.
        """
        velocity = 0
        for _ in range(5):
            velocity = apply_gravity(velocity, MAGNETIC_STATE_NORMAL)
        assert velocity == 5 * GRAVITY


class TestApplyFriction:
    """Tests for apply_friction function."""
    
    def test_ground_friction(self):
        """Test friction on ground.

        Verifies that ground friction coefficient is applied when grounded.
        """
        velocity = apply_friction(10, on_ground=True)
        assert velocity == 10 * FRICTION
    
    def test_air_resistance(self):
        """Test air resistance when not on ground.

        Verifies that air resistance coefficient is applied when airborne.
        """
        velocity = apply_friction(10, on_ground=False)
        assert velocity == 10 * AIR_RESISTANCE
    
    def test_zero_velocity(self):
        """Test friction on zero velocity.

        Verifies that zero velocity remains zero after friction is applied.
        """
        assert apply_friction(0, on_ground=True) == 0
        assert apply_friction(0, on_ground=False) == 0


class TestCalculateMagneticForce:
    """Tests for calculate_magnetic_force function."""
    
    def test_out_of_range(self):
        """Test no force when out of range.

        Verifies that magnetic force is zero when distance exceeds range.
        """
        force = calculate_magnetic_force((0, 0), (200, 0), 100, 1.0, POLARITY_ATTRACT)
        assert force == (0.0, 0.0)
    
    def test_attract_force(self):
        """Test attract force direction.

        Verifies that attraction force pulls object toward the magnet.
        """
        force = calculate_magnetic_force((0, 0), (50, 0), 100, 1.0, POLARITY_ATTRACT)
        assert force[0] > 0  # Should be pulled right toward magnet
        assert force[1] == pytest.approx(0.0)
    
    def test_repel_force(self):
        """Test repel force direction.

        Verifies that repulsion force pushes object away from the magnet.
        """
        force = calculate_magnetic_force((0, 0), (50, 0), 100, 1.0, POLARITY_REPEL)
        assert force[0] < 0  # Should be pushed left away from magnet
        assert force[1] == pytest.approx(0.0)
    
    def test_force_decreases_with_distance(self):
        """Test force is stronger when closer.

        Verifies inverse relationship between distance and force magnitude.
        """
        close_force = calculate_magnetic_force((0, 0), (20, 0), 100, 1.0, POLARITY_ATTRACT)
        far_force = calculate_magnetic_force((0, 0), (80, 0), 100, 1.0, POLARITY_ATTRACT)
        assert abs(close_force[0]) > abs(far_force[0])
    
    def test_zero_distance(self):
        """Test force at zero distance.

        Verifies that force is zero when object and magnet are at same position.
        """
        force = calculate_magnetic_force((50, 50), (50, 50), 100, 1.0, POLARITY_ATTRACT)
        assert force == (0.0, 0.0)


class TestCheckRectCollision:
    """Tests for check_rect_collision function."""
    
    def test_no_collision(self):
        """Test non-overlapping rectangles.

        Verifies that separated rectangles do not register as colliding.
        """
        assert not check_rect_collision((0, 0, 10, 10), (20, 20, 10, 10))
    
    def test_collision(self):
        """Test overlapping rectangles.

        Verifies that overlapping rectangles are detected as colliding.
        """
        assert check_rect_collision((0, 0, 20, 20), (10, 10, 20, 20))
    
    def test_touching_not_collision(self):
        """Test rectangles touching edges don't collide.

        Verifies that edge-adjacent rectangles are not considered overlapping.
        """
        assert not check_rect_collision((0, 0, 10, 10), (10, 0, 10, 10))
    
    def test_contained(self):
        """Test one rectangle inside another.

        Verifies that a fully contained rectangle is detected as colliding.
        """
        assert check_rect_collision((0, 0, 100, 100), (25, 25, 10, 10))


class TestResolveCollision:
    """Tests for resolve_collision function."""
    
    def test_resolve_top_collision(self):
        """Test collision from top (landing on platform).

        Verifies that player landing on platform is resolved correctly with
        floor orientation and zeroed vertical velocity.
        """
        player_rect = (50, 90, 20, 20)  # Player just above platform
        platform_rect = (0, 100, 200, 20)
        velocity = (0, 5)
        
        new_pos, new_vel, side = resolve_collision(player_rect, platform_rect, velocity)
        assert side == ORIENTATION_FLOOR
        assert new_vel[1] == 0
    
    def test_resolve_bottom_collision(self):
        """Test collision from bottom (hitting ceiling).

        Verifies that player hitting ceiling is resolved correctly with
        ceiling orientation and zeroed vertical velocity.
        """
        player_rect = (50, 20, 20, 20)
        platform_rect = (0, 0, 200, 20)
        velocity = (0, -5)
        
        new_pos, new_vel, side = resolve_collision(player_rect, platform_rect, velocity)
        assert side == ORIENTATION_CEILING
        assert new_vel[1] == 0


class TestGetSurfaceNormal:
    """Tests for get_surface_normal function."""
    
    def test_floor_normal(self):
        """Test floor surface normal points up.

        Verifies that floor orientation returns upward normal vector.
        """
        assert get_surface_normal(ORIENTATION_FLOOR) == (0, -1)
    
    def test_ceiling_normal(self):
        """Test ceiling surface normal points down.

        Verifies that ceiling orientation returns downward normal vector.
        """
        assert get_surface_normal(ORIENTATION_CEILING) == (0, 1)
    
    def test_wall_left_normal(self):
        """Test left wall normal points right.

        Verifies that left wall orientation returns rightward normal vector.
        """
        assert get_surface_normal(ORIENTATION_WALL_LEFT) == (1, 0)
    
    def test_wall_right_normal(self):
        """Test right wall normal points left.

        Verifies that right wall orientation returns leftward normal vector.
        """
        assert get_surface_normal(ORIENTATION_WALL_RIGHT) == (-1, 0)
    
    def test_unknown_orientation(self):
        """Test unknown orientation defaults to floor.

        Verifies that unrecognized orientations fall back to floor normal.
        """
        assert get_surface_normal("unknown") == (0, -1)


class TestApplySurfaceGravity:
    """Tests for apply_surface_gravity function."""
    
    def test_floor_gravity(self):
        """Test gravity on floor surface.

        Verifies that gravity pulls downward on floor orientation.
        """
        velocity = apply_surface_gravity((0, 0), ORIENTATION_FLOOR)
        assert velocity[1] > 0  # Falls down
    
    def test_ceiling_gravity(self):
        """Test gravity on ceiling surface (inverted).

        Verifies that gravity pulls upward on ceiling orientation.
        """
        velocity = apply_surface_gravity((0, 0), ORIENTATION_CEILING)
        assert velocity[1] < 0  # Falls up
    
    def test_wall_left_gravity(self):
        """Test gravity on left wall.

        Verifies that gravity pulls leftward on left wall orientation.
        """
        velocity = apply_surface_gravity((0, 0), ORIENTATION_WALL_LEFT)
        assert velocity[0] < 0  # Falls left
    
    def test_wall_right_gravity(self):
        """Test gravity on right wall.

        Verifies that gravity pulls rightward on right wall orientation.
        """
        velocity = apply_surface_gravity((0, 0), ORIENTATION_WALL_RIGHT)
        assert velocity[0] > 0  # Falls right


class TestClamp:
    """Tests for clamp function."""
    
    def test_clamp_below_min(self):
        """Test value below minimum is clamped.

        Verifies that values below minimum are raised to minimum.
        """
        assert clamp(-10, 0, 100) == 0
    
    def test_clamp_above_max(self):
        """Test value above maximum is clamped.

        Verifies that values above maximum are lowered to maximum.
        """
        assert clamp(150, 0, 100) == 100
    
    def test_clamp_in_range(self):
        """Test value in range is unchanged.

        Verifies that values within range are returned unmodified.
        """
        assert clamp(50, 0, 100) == 50
    
    def test_clamp_at_boundaries(self):
        """Test values at boundaries.

        Verifies that boundary values are returned unmodified.
        """
        assert clamp(0, 0, 100) == 0
        assert clamp(100, 0, 100) == 100
