"""Visual rendering engine using pygame."""

import logging
import math
from typing import Tuple, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class VisualParams:
    """Current visual parameters."""
    # Position (0.0 - 1.0)
    x: float = 0.5
    y: float = 0.5
    
    # Size and intensity
    size: float = 0.5           # 0.0 - 1.0, mapped to pixel size
    brightness: float = 1.0     # 0.0 - 1.0
    
    # Colour
    hue: float = 0.0            # 0 - 360
    saturation: float = 1.0     # 0.0 - 1.0
    
    # Shape: 'circle', 'square', 'triangle', 'blob'
    shape: str = 'circle'


class VisualEngine:
    """
    Visual rendering using pygame.
    
    Usage:
        visuals = VisualEngine(width=800, height=600)
        visuals.start()
        
        # Update parameters from gesture input
        visuals.params.x = 0.5
        visuals.params.hue = 180.0
        
        # In main loop
        visuals.update()
        visuals.render()
        
        visuals.stop()
    """
    
    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        fullscreen: bool = False,
        fps: int = 60,
        bg_color: Tuple[int, int, int] = (10, 10, 20)
    ):
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.target_fps = fps
        self.bg_color = bg_color
        
        self.params = VisualParams()
        
        # Size range in pixels
        self.min_size = 20
        self.max_size = 300
        
        self._screen = None
        self._clock = None
        self._running = False
        self._font = None
        
        # Trail effect (optional)
        self._trail: List[Tuple[float, float, float]] = []
        self._trail_enabled = False
        self._trail_length = 20
    
    def start(self):
        """Initialise pygame display."""
        import pygame
        
        pygame.init()
        
        flags = 0
        if self.fullscreen:
            flags = pygame.FULLSCREEN
        
        self._screen = pygame.display.set_mode(
            (self.width, self.height),
            flags
        )
        pygame.display.set_caption("Gesture AV Synth")
        
        self._clock = pygame.time.Clock()
        self._font = pygame.font.Font(None, 24)
        
        self._running = True
        logger.info(f"Visual engine started: {self.width}x{self.height}")
    
    def stop(self):
        """Clean up pygame."""
        import pygame
        pygame.quit()
        self._running = False
        logger.info("Visual engine stopped")
    
    def update(self):
        """Update any animated state."""
        # Add current position to trail
        if self._trail_enabled:
            self._trail.append((
                self.params.x,
                self.params.y,
                self.params.size
            ))
            # Limit trail length
            if len(self._trail) > self._trail_length:
                self._trail.pop(0)
    
    def render(self, show_debug: bool = False, debug_info: dict = None):
        """Render current frame."""
        import pygame
        
        if not self._running or not self._screen:
            return
        
        # Clear screen
        self._screen.fill(self.bg_color)
        
        # Draw trail (if enabled)
        if self._trail_enabled and len(self._trail) > 1:
            self._draw_trail()
        
        # Calculate screen position
        screen_x = int(self.params.x * self.width)
        screen_y = int((1.0 - self.params.y) * self.height)  # Flip Y
        
        # Calculate size
        size = int(
            self.min_size + 
            self.params.size * (self.max_size - self.min_size)
        )
        
        # Get colour from HSV
        colour = self._hsv_to_rgb(
            self.params.hue,
            self.params.saturation,
            self.params.brightness
        )
        
        # Draw shape
        if self.params.shape == 'circle':
            self._draw_circle(screen_x, screen_y, size, colour)
        elif self.params.shape == 'square':
            self._draw_square(screen_x, screen_y, size, colour)
        elif self.params.shape == 'triangle':
            self._draw_triangle(screen_x, screen_y, size, colour)
        elif self.params.shape == 'blob':
            self._draw_blob(screen_x, screen_y, size, colour)
        else:
            self._draw_circle(screen_x, screen_y, size, colour)
        
        # Debug overlay
        if show_debug and debug_info:
            self._draw_debug(debug_info)
        
        # Flip display
        pygame.display.flip()
        
        # Cap framerate
        self._clock.tick(self.target_fps)
    
    def _draw_circle(self, x: int, y: int, size: int, colour: Tuple[int, int, int]):
        """Draw a filled circle with glow effect."""
        import pygame
        
        # Outer glow
        glow_colour = tuple(max(0, c - 100) for c in colour)
        pygame.draw.circle(self._screen, glow_colour, (x, y), size + 10)
        
        # Main circle
        pygame.draw.circle(self._screen, colour, (x, y), size)
        
        # Inner highlight
        highlight = tuple(min(255, c + 50) for c in colour)
        pygame.draw.circle(self._screen, highlight, (x, y), size // 2)
    
    def _draw_square(self, x: int, y: int, size: int, colour: Tuple[int, int, int]):
        """Draw a filled square."""
        import pygame
        
        rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
        pygame.draw.rect(self._screen, colour, rect)
        
        # Border
        border_colour = tuple(min(255, c + 50) for c in colour)
        pygame.draw.rect(self._screen, border_colour, rect, 3)
    
    def _draw_triangle(self, x: int, y: int, size: int, colour: Tuple[int, int, int]):
        """Draw an equilateral triangle."""
        import pygame
        
        # Calculate vertices
        height = size * math.sqrt(3)
        points = [
            (x, y - height * 0.6),           # Top
            (x - size, y + height * 0.4),    # Bottom left
            (x + size, y + height * 0.4)     # Bottom right
        ]
        
        pygame.draw.polygon(self._screen, colour, points)
    
    def _draw_blob(self, x: int, y: int, size: int, colour: Tuple[int, int, int]):
        """Draw an organic blob shape using overlapping circles."""
        import pygame
        import time
        
        # Animate blob slightly
        t = time.time()
        
        for i in range(6):
            angle = (i / 6) * 2 * math.pi + t * 0.5
            offset = size * 0.3
            bx = x + math.cos(angle) * offset
            by = y + math.sin(angle) * offset
            blob_size = size * (0.6 + 0.2 * math.sin(t * 2 + i))
            pygame.draw.circle(self._screen, colour, (int(bx), int(by)), int(blob_size))
    
    def _draw_trail(self):
        """Draw fading trail of past positions."""
        import pygame
        
        for i, (tx, ty, ts) in enumerate(self._trail):
            alpha = i / len(self._trail)
            screen_x = int(tx * self.width)
            screen_y = int((1.0 - ty) * self.height)
            size = int(self.min_size + ts * (self.max_size - self.min_size))
            
            # Fade colour
            colour = self._hsv_to_rgb(
                self.params.hue,
                self.params.saturation,
                self.params.brightness * alpha * 0.5
            )
            
            pygame.draw.circle(
                self._screen, colour,
                (screen_x, screen_y),
                int(size * alpha)
            )
    
    def _draw_debug(self, info: dict):
        """Draw debug information overlay."""
        import pygame
        
        y_offset = 10
        for key, value in info.items():
            if isinstance(value, float):
                text = f"{key}: {value:.3f}"
            else:
                text = f"{key}: {value}"
            
            surface = self._font.render(text, True, (255, 255, 255))
            self._screen.blit(surface, (10, y_offset))
            y_offset += 20
    
    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB."""
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
    
    def get_fps(self) -> float:
        """Get current FPS."""
        if self._clock:
            return self._clock.get_fps()
        return 0.0
    
    def handle_events(self) -> bool:
        """
        Process pygame events.
        
        Returns:
            False if should quit, True otherwise.
        """
        import pygame
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_f:
                    # Toggle fullscreen
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_t:
                    # Toggle trail
                    self._trail_enabled = not self._trail_enabled
                    self._trail.clear()
        
        return True


class MockVisualEngine(VisualEngine):
    """Mock visual engine for testing without display."""
    
    def start(self):
        self._running = True
        logger.info("Mock visual engine started (no display)")
    
    def stop(self):
        self._running = False
        logger.info("Mock visual engine stopped")
    
    def update(self):
        pass
    
    def render(self, show_debug: bool = False, debug_info: dict = None):
        pass
    
    def handle_events(self) -> bool:
        return True


def create_visual_engine(use_mock: bool = False, **kwargs) -> VisualEngine:
    """Factory function to create appropriate visual engine."""
    if use_mock:
        return MockVisualEngine(**kwargs)
    return VisualEngine(**kwargs)
