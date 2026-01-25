"""Utility functions for smoothing, mapping, and signal processing."""

import math
from typing import Tuple, Optional


class Smoother:
    """Exponential moving average smoother for reducing jitter."""
    
    def __init__(self, factor: float = 0.7, initial: float = 0.0):
        """
        Args:
            factor: Smoothing factor 0.0-0.99. Higher = smoother but laggier.
            initial: Initial value.
        """
        self.factor = factor
        self.value = initial
        self._initialised = False
    
    def update(self, new_value: float) -> float:
        """Update with new reading and return smoothed value."""
        if not self._initialised:
            self.value = new_value
            self._initialised = True
        else:
            self.value = (self.factor * self.value) + ((1 - self.factor) * new_value)
        return self.value
    
    def reset(self, value: float = 0.0):
        """Reset the smoother."""
        self.value = value
        self._initialised = False


class Position3D:
    """Smoothed 3D position tracker."""
    
    def __init__(self, smoothing: float = 0.7):
        self.x = Smoother(smoothing)
        self.y = Smoother(smoothing)
        self.z = Smoother(smoothing)
    
    def update(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Update all coordinates and return smoothed position."""
        return (
            self.x.update(x),
            self.y.update(y),
            self.z.update(z)
        )
    
    def get(self) -> Tuple[float, float, float]:
        """Get current smoothed position."""
        return (self.x.value, self.y.value, self.z.value)


def map_range(
    value: float,
    in_min: float,
    in_max: float,
    out_min: float,
    out_max: float,
    clamp: bool = True
) -> float:
    """
    Map a value from one range to another (linear).
    
    Args:
        value: Input value
        in_min, in_max: Input range
        out_min, out_max: Output range
        clamp: If True, clamp output to range
    """
    # Avoid division by zero
    if in_max == in_min:
        return out_min
    
    result = (value - in_min) / (in_max - in_min) * (out_max - out_min) + out_min
    
    if clamp:
        result = max(out_min, min(out_max, result))
    
    return result


def map_exponential(
    value: float,
    in_min: float,
    in_max: float,
    out_min: float,
    out_max: float,
    exponent: float = 2.0
) -> float:
    """
    Map with exponential curve - useful for audio frequency/volume.
    
    Args:
        exponent: 2.0 = quadratic, 3.0 = cubic, etc.
    """
    # Normalise to 0-1
    normalised = (value - in_min) / (in_max - in_min)
    normalised = max(0.0, min(1.0, normalised))
    
    # Apply curve
    curved = normalised ** exponent
    
    # Map to output range
    return curved * (out_max - out_min) + out_min


def map_logarithmic(
    value: float,
    in_min: float,
    in_max: float,
    out_min: float,
    out_max: float
) -> float:
    """
    Map with logarithmic curve - useful for perceived loudness.
    """
    # Normalise to 0-1
    normalised = (value - in_min) / (in_max - in_min)
    normalised = max(0.001, min(1.0, normalised))  # Avoid log(0)
    
    # Apply log curve (using log10, scaled)
    curved = (math.log10(normalised) + 3) / 3  # Maps ~0.001-1 to ~0-1
    curved = max(0.0, min(1.0, curved))
    
    return curved * (out_max - out_min) + out_min


def apply_deadzone(value: float, deadzone: float = 0.05) -> float:
    """
    Apply deadzone at edges of 0-1 range.
    
    Useful for Skywriter which can be noisy at extremes.
    """
    if value < deadzone:
        return 0.0
    elif value > (1.0 - deadzone):
        return 1.0
    else:
        # Rescale middle section to full range
        return (value - deadzone) / (1.0 - 2 * deadzone)


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """
    Convert HSV to RGB.
    
    Args:
        h: Hue (0-360)
        s: Saturation (0-1)
        v: Value (0-1)
    
    Returns:
        Tuple of (r, g, b) in range 0-255
    """
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (
        int((r + m) * 255),
        int((g + m) * 255),
        int((b + m) * 255)
    )


def interpolate_colour(
    colour1: Tuple[int, int, int],
    colour2: Tuple[int, int, int],
    t: float
) -> Tuple[int, int, int]:
    """Linearly interpolate between two RGB colours."""
    t = max(0.0, min(1.0, t))
    return (
        int(colour1[0] + (colour2[0] - colour1[0]) * t),
        int(colour1[1] + (colour2[1] - colour1[1]) * t),
        int(colour1[2] + (colour2[2] - colour1[2]) * t)
    )
