# Magnet Boots Mayhem

A 2D side-scrolling platformer with magnetic traversal mechanics built with Python and Pygame.

## 🎮 Features

- **Magnetic Boots**: Walk on walls and ceilings by sticking to magnetic surfaces
- **Magnetic Fields**: Interact with attract and repel magnets to solve puzzles
- **Physics-Based Gameplay**: Realistic magnetic force calculations and momentum
- **Multiple Levels**: Tutorial and demo levels showcasing game mechanics
- **Modular Design**: Clean, well-documented codebase for easy extension

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd magnet-boots-mayhem

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Game

```bash
python run.py
```

## 🎯 Controls

| Action | Keys |
|--------|------|
| Move | Arrow Keys / WASD |
| Jump | Space |
| Toggle Magnetic Boots | M |
| Pause | Escape |
| Restart Level | R |

## 📁 Project Structure

```
magnet-boots-mayhem/
├── run.py                 # Entry point
├── requirements.txt       # Dependencies
├── src/                   # Source code
│   ├── game.py           # Main game loop
│   ├── player.py         # Player mechanics
│   ├── physics.py        # Physics engine
│   ├── platforms.py      # Platform classes
│   ├── magnets.py        # Magnet system
│   ├── enemies.py        # Enemy classes
│   ├── level.py          # Level management
│   ├── input_handler.py  # Input system
│   └── renderer.py       # Rendering
├── tests/                 # Test suite
├── docs/                  # Documentation
└── .github/workflows/     # CI/CD
```

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📖 Documentation

- [Architecture](docs/ARCHITECTURE.md) - Technical design and system overview
- [Usage Guide](docs/USAGE.md) - How to play and configure the game
- [Suggestions](docs/SUGGESTIONS.md) - Future improvement ideas

## 🔧 Development

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Linting

```bash
flake8 src/ tests/
mypy src/
```

## 📜 License

MIT License - see LICENSE for details.

## 🙏 Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
