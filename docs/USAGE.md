# Magnet Boots Mayhem - User Guide

## Introduction

Magnet Boots Mayhem is a 2D side-scrolling platformer where you use magnetic boots to traverse walls, ceilings, and interact with magnetic fields. Navigate through levels by mastering the unique magnetic mechanics!

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the repository**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

Start the game from the project root directory:

```bash
python run.py
```

## Controls

### Movement
| Action | Primary Key | Alternate Key |
|--------|-------------|---------------|
| Move Left | ← (Arrow Left) | A |
| Move Right | → (Arrow Right) | D |
| Move Up (on walls) | ↑ (Arrow Up) | W |
| Move Down (on walls) | ↓ (Arrow Down) | S |

### Actions
| Action | Key |
|--------|-----|
| Jump | Space |
| Toggle Magnetic Boots | M |
| Sprint | Left Shift |

### Game Controls
| Action | Key |
|--------|-----|
| Pause/Resume | Escape |
| Restart Level | R |

## Game Mechanics

### Magnetic Boots

Your character is equipped with magnetic boots that can attach to specially marked magnetic surfaces.

- **Activating**: Boots are active by default. Press **M** to toggle them on/off.
- **Sticking**: Walk onto a magnetic surface (shown in blue/purple) to automatically stick.
- **Walking**: While stuck, you can walk along the surface in any direction.
- **Jumping Off**: Press **Space** to launch perpendicular to the surface.

### Surfaces

| Surface Type | Color | Magnetic |
|--------------|-------|----------|
| Normal Platform | Gray | No |
| Magnetic Platform | Blue/Purple | Yes |
| Ceiling | Same as above | Depends |
| Wall | Same as above | Depends |

### Magnets

Environmental magnets create force fields that affect you and some enemies:

| Magnet Type | Color | Effect |
|-------------|-------|--------|
| Attract | Blue glow | Pulls you toward it |
| Repel | Red glow | Pushes you away |

**Tips:**
- Use attract magnets to help reach high platforms
- Use repel magnets to boost your jumps
- Magnets only affect you when boots are active and you're not stuck

### Enemies

| Enemy Type | Behavior |
|------------|----------|
| Basic | Walks in one direction |
| Patrol | Moves back and forth |
| Flying | Moves in a wave pattern |

Enemies can be avoided by:
- Jumping over them
- Using walls/ceilings to bypass
- Letting magnets push them away

## Gameplay Tips

### Beginner Tips

1. **Start with the tutorial** - It introduces mechanics gradually
2. **Watch the boot indicator** - Blue boots = active, gray = inactive
3. **Don't rush** - Plan your magnetic paths
4. **Use double jump** - You can jump twice in the air

### Advanced Techniques

1. **Wall Running**
   - Stick to a wall while moving up to "run" up it
   - Jump off at the top for extra height

2. **Ceiling Traverse**
   - Walk along ceilings to skip entire sections
   - Remember you're upside down - controls feel reversed!

3. **Magnet Slingshotting**
   - Turn off boots near an attract magnet
   - Get pulled toward it
   - Turn boots on to stick to a nearby surface

4. **Magnet Bouncing**
   - Use repel magnets to boost jumps
   - Chain multiple magnets for long distances

## Levels

### Tutorial
A simple introduction level that teaches:
- Basic movement
- Magnetic wall climbing
- Goal completion

### Demo Level
A full level showcasing:
- Walls and ceiling platforms
- Attract and repel magnets
- Complex traversal paths

## Menu Navigation

### Main Menu
- Use **↑/↓** to select options
- Press **Space** to confirm selection

### Options
1. **Start Game** - Begin the demo level
2. **Tutorial** - Play the tutorial level
3. **Quit** - Exit the game

### Pause Menu
Press **Escape** during gameplay to pause.
- Press **Escape** again to resume
- Press **R** to restart the level

## Troubleshooting

### Game won't start
- Ensure Python 3.9+ is installed
- Verify pygame is installed: `pip install pygame`
- Check for error messages in the console

### Performance issues
- Close other applications
- Reduce screen resolution (modify constants.py)
- Ensure graphics drivers are updated

### Controls not responding
- Click on the game window to focus it
- Check if keys are bound correctly
- Restart the game

## Configuration

### Environment Variables (.env)

Copy `.env.example` to `.env` and customize:

```ini
# Display settings
SCREEN_WIDTH=800
SCREEN_HEIGHT=600
FULLSCREEN=false

# Debug settings
DEBUG_MODE=false
SHOW_FPS=false
SHOW_HITBOXES=false

# Audio settings
MUSIC_VOLUME=0.7
SFX_VOLUME=1.0
```

### Modifying Constants

Edit `src/constants.py` to change:
- Screen dimensions
- Player speed and jump strength
- Gravity and physics values
- Colors and visual settings

## Creating Custom Levels

Levels are stored as JSON files. Create a new level:

```python
from src.level import Level
from src.platforms import Platform
from src.magnets import Magnet

level = Level(name="My Level")

# Add ground
level.add_platform(Platform(0, 550, 800, 50))

# Add magnetic wall
level.add_platform(Platform(300, 300, 30, 250, is_magnetic=True, orientation="wall_left"))

# Add magnet
level.add_magnet(Magnet(400, 400, "attract", range_=150))

# Set spawn and goal
level.set_player_start(50, 500)
level.set_goal(700, 500)

# Save
level.save("levels/my_level.json")
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Running with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

## Credits

- Built with [Pygame](https://www.pygame.org/)
- Developed as a demonstration project

## License

MIT License - See LICENSE file for details.
