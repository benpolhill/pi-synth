"""Interface for Pimoroni Skywriter HAT gesture input."""

import logging
from typing import Callable, Optional, Tuple
from dataclasses import dataclass, field
from threading import Lock

from utils import Position3D, map_range, apply_deadzone

logger = logging.getLogger(__name__)


@dataclass
class GestureState:
    """Current state of gesture input."""
    # Raw position (0.0 - 1.0 normalised)
    x: float = 0.5
    y: float = 0.5
    z: float = 0.5
    
    # Is a hand currently detected?
    active: bool = False
    
    # Touch zones (Skywriter has north, south, east, west, center)
    touch_north: bool = False
    touch_south: bool = False
    touch_east: bool = False
    touch_west: bool = False
    touch_center: bool = False
    
    # Detected gestures
    last_flick: Optional[str] = None  # 'north', 'south', 'east', 'west'
    last_airwheel: float = 0.0        # Rotation delta
    
    # Lock for thread safety (Skywriter uses callbacks)
    _lock: Lock = field(default_factory=Lock)
    
    def get_position(self) -> Tuple[float, float, float]:
        """Thread-safe position getter."""
        with self._lock:
            return (self.x, self.y, self.z)
    
    def set_position(self, x: float, y: float, z: float):
        """Thread-safe position setter."""
        with self._lock:
            self.x = x
            self.y = y
            self.z = z


class GestureInput:
    """
    Manages Skywriter HAT input with smoothing and normalisation.
    
    Usage:
        gesture = GestureInput(smoothing=0.7)
        gesture.start()
        
        # In main loop:
        x, y, z = gesture.get_position()
        if gesture.state.touch_center:
            # Handle touch
    """
    
    def __init__(
        self,
        smoothing: float = 0.7,
        deadzone: float = 0.05,
        on_position: Optional[Callable] = None,
        on_touch: Optional[Callable] = None,
        on_flick: Optional[Callable] = None
    ):
        """
        Args:
            smoothing: Position smoothing factor (0.0-0.99)
            deadzone: Edge deadzone (0.0-0.2)
            on_position: Callback(x, y, z) for position updates
            on_touch: Callback(zone) for touch events
            on_flick: Callback(direction) for flick gestures
        """
        self.smoothing = smoothing
        self.deadzone = deadzone
        self.state = GestureState()
        self._position_tracker = Position3D(smoothing)
        
        # User callbacks
        self._on_position = on_position
        self._on_touch = on_touch
        self._on_flick = on_flick
        
        self._running = False
        self._skywriter = None
    
    def start(self):
        """Initialise and start reading from Skywriter."""
        try:
            import skywriter
            self._skywriter = skywriter
        except ImportError:
            logger.error(
                "skywriter module not found. Install with: pip install skywriter"
            )
            raise
        
        # Register callbacks
        @skywriter.move()
        def move(x, y, z):
            self._handle_move(x, y, z)
        
        @skywriter.touch()
        def touch(position):
            self._handle_touch(position)
        
        @skywriter.flick()
        def flick(start, finish):
            self._handle_flick(start, finish)
        
        @skywriter.airwheel()
        def airwheel(delta):
            self._handle_airwheel(delta)
        
        self._running = True
        logger.info("Skywriter gesture input started")
    
    def stop(self):
        """Stop reading from Skywriter."""
        self._running = False
        # Note: skywriter library doesn't have explicit cleanup
        logger.info("Skywriter gesture input stopped")
    
    def get_position(self) -> Tuple[float, float, float]:
        """Get current smoothed, normalised position."""
        return self.state.get_position()
    
    def _handle_move(self, x: float, y: float, z: float):
        """Handle raw position update from Skywriter."""
        # Skywriter gives x, y in 0.0-1.0, z is larger range
        # Normalise z (typical range seems to be 0-65535)
        z_normalised = map_range(z, 0, 65535, 0.0, 1.0)
        
        # Apply smoothing
        sx, sy, sz = self._position_tracker.update(x, y, z_normalised)
        
        # Apply deadzone
        sx = apply_deadzone(sx, self.deadzone)
        sy = apply_deadzone(sy, self.deadzone)
        sz = apply_deadzone(sz, self.deadzone)
        
        # Update state
        self.state.set_position(sx, sy, sz)
        self.state.active = True
        
        # User callback
        if self._on_position:
            self._on_position(sx, sy, sz)
    
    def _handle_touch(self, position: str):
        """Handle touch event."""
        logger.debug(f"Touch: {position}")
        
        with self.state._lock:
            # Reset all touches
            self.state.touch_north = position == 'north'
            self.state.touch_south = position == 'south'
            self.state.touch_east = position == 'east'
            self.state.touch_west = position == 'west'
            self.state.touch_center = position == 'center'
        
        if self._on_touch:
            self._on_touch(position)
    
    def _handle_flick(self, start: str, finish: str):
        """Handle flick gesture."""
        # Determine direction from start/finish
        direction = finish  # Simplified; could be smarter
        logger.debug(f"Flick: {start} -> {finish}")
        
        with self.state._lock:
            self.state.last_flick = direction
        
        if self._on_flick:
            self._on_flick(direction)
    
    def _handle_airwheel(self, delta: float):
        """Handle airwheel (circular) gesture."""
        logger.debug(f"Airwheel delta: {delta}")
        
        with self.state._lock:
            self.state.last_airwheel = delta


class MockGestureInput(GestureInput):
    """
    Mock gesture input for testing without hardware.
    
    Uses mouse position in a pygame window or manual updates.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mock_x = 0.5
        self._mock_y = 0.5
        self._mock_z = 0.5
    
    def start(self):
        """No-op for mock."""
        self._running = True
        logger.info("Mock gesture input started (no hardware)")
    
    def set_mock_position(self, x: float, y: float, z: float):
        """Manually set position for testing."""
        self._handle_move(x, y, z)
    
    def simulate_touch(self, zone: str):
        """Simulate a touch event."""
        self._handle_touch(zone)
    
    def simulate_flick(self, direction: str):
        """Simulate a flick gesture."""
        self._handle_flick('center', direction)


def create_gesture_input(use_mock: bool = False, **kwargs) -> GestureInput:
    """
    Factory function to create appropriate gesture input.
    
    Args:
        use_mock: If True, create mock input for testing
        **kwargs: Passed to GestureInput constructor
    """
    if use_mock:
        return MockGestureInput(**kwargs)
    return GestureInput(**kwargs)
