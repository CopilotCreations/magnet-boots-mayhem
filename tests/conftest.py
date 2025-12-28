"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import MagicMock, patch
import sys


# Mock pygame for testing
@pytest.fixture(autouse=True)
def mock_pygame():
    """Auto-mock pygame for all tests."""
    pygame_mock = MagicMock()
    pygame_mock.K_LEFT = 276
    pygame_mock.K_RIGHT = 275
    pygame_mock.K_UP = 273
    pygame_mock.K_DOWN = 274
    pygame_mock.K_SPACE = 32
    pygame_mock.K_ESCAPE = 27
    pygame_mock.K_m = 109
    pygame_mock.K_r = 114
    pygame_mock.K_a = 97
    pygame_mock.K_d = 100
    pygame_mock.K_w = 119
    pygame_mock.K_s = 115
    pygame_mock.K_LSHIFT = 304
    pygame_mock.KEYDOWN = 768
    pygame_mock.KEYUP = 769
    pygame_mock.QUIT = 256
    pygame_mock.SRCALPHA = 65536
    pygame_mock.key.name = lambda k: {
        32: 'space',
        276: 'left',
        275: 'right',
        273: 'up',
        274: 'down',
        27: 'escape',
        109: 'm',
        114: 'r'
    }.get(k, str(k))
    
    pygame_mock.Surface = MagicMock
    pygame_mock.Rect = lambda x, y, w, h: MagicMock(x=x, y=y, width=w, height=h)
    pygame_mock.font.Font = MagicMock
    pygame_mock.display.set_mode = MagicMock(return_value=MagicMock(get_width=lambda: 800, get_height=lambda: 600, get_size=lambda: (800, 600)))
    
    with patch.dict(sys.modules, {'pygame': pygame_mock}):
        yield pygame_mock


@pytest.fixture
def sample_platform():
    """Create a sample platform for testing."""
    from src.platforms import Platform
    from src.constants import ORIENTATION_FLOOR
    return Platform(100, 200, 150, 30, is_magnetic=True, orientation=ORIENTATION_FLOOR)


@pytest.fixture
def sample_magnet():
    """Create a sample magnet for testing."""
    from src.magnets import Magnet
    from src.constants import POLARITY_ATTRACT
    return Magnet(100, 100, POLARITY_ATTRACT, range_=150, strength=1.0)


@pytest.fixture
def sample_player():
    """Create a sample player for testing."""
    from src.player import Player
    return Player(100, 200)


@pytest.fixture
def sample_enemy():
    """Create a sample enemy for testing."""
    from src.enemies import Enemy
    return Enemy(100, 200)


@pytest.fixture
def sample_level():
    """Create a sample level for testing."""
    from src.level import Level
    from src.platforms import Platform
    
    level = Level(name="Test Level")
    level.add_platform(Platform(0, 550, 800, 50))
    level.set_player_start(100, 500)
    level.set_goal(700, 500, 50, 50)
    
    return level
