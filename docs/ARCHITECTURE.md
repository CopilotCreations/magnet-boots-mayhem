# Magnet Boots Mayhem - Architecture

## Overview

Magnet Boots Mayhem is a 2D side-scrolling platformer built with Python and Pygame. The game features unique magnetic traversal mechanics that allow the player to walk on walls and ceilings using magnetic boots.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Game Loop                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Input     │  │   Update    │  │        Render           │  │
│  │  Handler    │──│   Logic     │──│       System            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                 │                      │
         ▼                 ▼                      ▼
┌─────────────┐   ┌─────────────┐         ┌─────────────┐
│  Keyboard   │   │   Physics   │         │   Camera    │
│  Mappings   │   │   Engine    │         │   System    │
└─────────────┘   └─────────────┘         └─────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐   ┌──────────┐
   │  Player  │  │ Platforms│   │  Magnets │
   └──────────┘  └──────────┘   └──────────┘
```

## Module Descriptions

### Core Modules

#### `game.py`
The main game controller that manages:
- Game state machine (Menu, Playing, Paused, Level Complete, Game Over)
- Main game loop (events → update → render)
- Level management and transitions
- Integration of all game systems

**Key Classes:**
- `GameState` (Enum): Defines all possible game states
- `Game`: Main game class with run loop

#### `player.py`
Player entity with magnetic boot mechanics:
- Position, velocity, and physics properties
- Magnetic state management (normal, sticking)
- Movement on floors, walls, and ceilings
- Collision detection and response
- Double jump capability

**Key Methods:**
- `move()`: Handle directional input
- `jump()`: Execute jump or wall-jump
- `toggle_magnetic_state()`: Toggle magnetic boots
- `stick_to_surface()`: Attach to magnetic platforms
- `update()`: Main physics update

#### `physics.py`
Physics engine handling:
- Gravity application (normal and surface-relative)
- Friction and air resistance
- Magnetic force calculations (inverse square law)
- Collision detection (AABB)
- Collision resolution with direction

**Key Functions:**
- `calculate_magnetic_force()`: Compute attraction/repulsion
- `check_rect_collision()`: AABB collision test
- `resolve_collision()`: Position and velocity correction
- `apply_surface_gravity()`: Gravity relative to surface orientation

### Game Objects

#### `platforms.py`
Platform entities for level geometry:
- Static platforms (floors, walls, ceilings)
- Moving platforms with start/end positions
- Magnetic property for boot interaction
- Orientation-aware surface detection

**Classes:**
- `Platform`: Static platform
- `MovingPlatform`: Animated platform

#### `magnets.py`
Magnetic field generators:
- Attract/repel polarity
- Configurable range and strength
- Force calculation for objects in range
- Visual representation with field indicators

#### `enemies.py`
Enemy entities:
- Basic enemies affected by gravity
- Patrol enemies with back-and-forth movement
- Flying enemies with sinusoidal patterns
- Magnetic interaction support

**Classes:**
- `Enemy`: Base enemy class
- `PatrolEnemy`: Ground patroller
- `FlyingEnemy`: Aerial enemy

#### `level.py`
Level data management:
- Platform, magnet, and enemy storage
- Player spawn and goal positions
- JSON serialization/deserialization
- Magnetic force aggregation
- Demo level generation

### Systems

#### `input_handler.py`
Input abstraction layer:
- Key binding management
- Action-based input queries
- Movement vector calculation
- Support for alternate key bindings

**Key Features:**
- `is_action_pressed()`: Continuous input
- `is_action_just_pressed()`: Edge-triggered input
- `get_movement_vector()`: Normalized movement

#### `renderer.py`
Rendering system:
- Camera with smooth following
- Level drawing (platforms, magnets, enemies)
- Player rendering with state indicators
- HUD display
- Menu and overlay rendering

**Classes:**
- `Camera`: Viewport management
- `Renderer`: Drawing operations

## Data Flow

### Input → Player Movement

```
InputHandler.update()
    │
    ▼
InputHandler.get_movement_vector()
    │
    ▼
Player.move(horizontal, vertical)
    │
    ▼
Player.velocity_x/y updated
```

### Physics Update Cycle

```
Player.apply_gravity()
    │
    ▼
Level.get_total_magnetic_force()
    │
    ▼
Player.apply_magnetic_force()
    │
    ▼
Player.update() → position += velocity
    │
    ▼
Collision Detection (platforms)
    │
    ▼
Collision Resolution
    │
    ▼
Magnetic Sticking Check
```

### Magnetic Force Calculation

```
Object Position
    │
    ▼
For each Magnet:
    │
    ├─ Calculate distance
    │
    ├─ Check if in range
    │
    ├─ Apply inverse square falloff
    │
    └─ Determine direction (attract/repel)
    │
    ▼
Sum all forces → Total magnetic force
```

## State Machine

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌────────┐     Start Game     ┌─────────┐                  │
│  │  MENU  │ ──────────────────▶│ PLAYING │                  │
│  └────────┘                    └─────────┘                  │
│       ▲                            │ │                       │
│       │                    ESC     │ │  Goal                │
│       │                     │      │ │  Reached             │
│       │                     ▼      │ │                       │
│       │               ┌─────────┐  │ │  ┌───────────────┐   │
│       │               │ PAUSED  │  │ └─▶│LEVEL_COMPLETE │   │
│       │               └─────────┘  │    └───────────────┘   │
│       │                     │      │           │             │
│       │               ESC   │      │     Next Level         │
│       │                     ▼      │           │             │
│       │                 Resume     │           ▼             │
│       │                     │      │    ┌─────────┐         │
│       │                     └──────┼───▶│ PLAYING │         │
│       │                            │    └─────────┘         │
│       │                            │                         │
│       │                     Fall   │                         │
│       │                     Off    │                         │
│       │                            ▼                         │
│       │                    ┌────────────┐                   │
│       └────────────────────│ GAME_OVER  │                   │
│              ESC           └────────────┘                   │
│                                  │                           │
│                              R   │                           │
│                                  ▼                           │
│                            Restart Level                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Magnetic Physics Model

### Force Calculation

The magnetic force follows an inverse square relationship:

```
F = strength × (1 - distance/range)²
```

Where:
- `strength`: Magnet power multiplier
- `distance`: Distance from magnet center to object
- `range`: Maximum effective range

### Direction

- **Attract**: Force vector points toward magnet
- **Repel**: Force vector points away from magnet

### Surface Sticking

When player contacts a magnetic surface:
1. Player state changes to `STICKING`
2. Gravity is suspended
3. Movement becomes surface-relative
4. Jump launches perpendicular to surface

## Collision System

### Detection

Uses Axis-Aligned Bounding Box (AABB) collision:

```python
collision = (rect1.x < rect2.x + rect2.w and
             rect1.x + rect1.w > rect2.x and
             rect1.y < rect2.y + rect2.h and
             rect1.y + rect1.h > rect2.y)
```

### Resolution

1. Calculate overlap on each axis
2. Find minimum overlap direction
3. Push player out of collision
4. Zero velocity in collision direction
5. Trigger magnetic sticking if applicable

## File Structure

```
magnet-boots-mayhem/
├── run.py                 # Entry point
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore patterns
│
├── src/                  # Source code
│   ├── __init__.py
│   ├── constants.py      # Game constants
│   ├── game.py           # Main game loop
│   ├── player.py         # Player entity
│   ├── physics.py        # Physics engine
│   ├── platforms.py      # Platform classes
│   ├── magnets.py        # Magnet system
│   ├── enemies.py        # Enemy classes
│   ├── level.py          # Level management
│   ├── input_handler.py  # Input system
│   └── renderer.py       # Rendering system
│
├── tests/                # Test suite
│   ├── conftest.py       # Pytest fixtures
│   ├── test_physics.py
│   ├── test_player.py
│   ├── test_platforms.py
│   ├── test_magnets.py
│   ├── test_enemies.py
│   ├── test_level.py
│   ├── test_input_handler.py
│   └── test_game.py
│
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md   # This file
│   ├── USAGE.md          # User guide
│   └── SUGGESTIONS.md    # Future improvements
│
└── .github/workflows/    # CI/CD
    └── ci.yml            # GitHub Actions
```

## Dependencies

- **pygame**: Game framework (rendering, input, audio)
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **mypy**: Static type checking
- **black**: Code formatting
- **flake8**: Linting

## Performance Considerations

1. **Collision Optimization**: Only check collisions with nearby platforms
2. **Magnetic Force Caching**: Recalculate only when positions change
3. **Render Culling**: Only draw objects within camera viewport
4. **Object Pooling**: Reuse enemy instances for respawning
