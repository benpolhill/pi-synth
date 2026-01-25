"""Output manager - coordinates audio and visual outputs based on gesture input."""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from utils import map_range, map_exponential

logger = logging.getLogger(__name__)


@dataclass
class MappingConfig:
    """Configuration for parameter mapping."""
    # Audio frequency range (Hz)
    freq_min: float = 110.0
    freq_max: float = 880.0
    
    # Use exponential curve for frequency (more musical)
    freq_exponential: bool = True
    
    # Visual size range (0-1, mapped to pixels in visual engine)
    size_min: float = 0.1
    size_max: float = 1.0
    
    # What X controls
    x_to_hue: bool = True       # Colour hue
    x_to_pan: bool = True       # Audio stereo position
    
    # What Y controls  
    y_to_pitch: bool = True     # Audio frequency
    
    # What Z controls
    z_to_volume: bool = True    # Audio volume
    z_to_size: bool = True      # Visual size
    z_to_brightness: bool = True  # Visual brightness


class OutputManager:
    """
    Maps gesture input to audio and visual parameters.
    
    This is the central coordinator that takes normalised gesture data
    and updates both the audio and visual engines appropriately.
    
    Usage:
        manager = OutputManager(audio_engine, visual_engine)
        
        # In main loop:
        x, y, z = gesture.get_position()
        manager.update(x, y, z)
    """
    
    def __init__(
        self,
        audio_engine,
        visual_engine,
        config: Optional[MappingConfig] = None
    ):
        self.audio = audio_engine
        self.visual = visual_engine
        self.config = config or MappingConfig()
        
        # Current mode (can be changed by touch gestures)
        self.mode = 'default'
        
        # Available waveforms for cycling
        self.waveforms = ['sine', 'square', 'triangle', 'sawtooth']
        self._waveform_index = 0
        
        # Available shapes for cycling
        self.shapes = ['circle', 'square', 'triangle', 'blob']
        self._shape_index = 0
    
    def update(self, x: float, y: float, z: float):
        """
        Update audio and visual parameters based on gesture position.
        
        Args:
            x, y, z: Normalised position (0.0 - 1.0)
        """
        # --- Audio mapping ---
        
        if self.config.y_to_pitch:
            if self.config.freq_exponential:
                freq = map_exponential(
                    y, 0.0, 1.0,
                    self.config.freq_min, self.config.freq_max,
                    exponent=2.0
                )
            else:
                freq = map_range(
                    y, 0.0, 1.0,
                    self.config.freq_min, self.config.freq_max
                )
            self.audio.set_frequency(freq)
        
        if self.config.z_to_volume:
            # Z = height, higher = louder
            volume = map_range(z, 0.0, 1.0, 0.0, 0.8)
            self.audio.set_volume(volume)
        
        if self.config.x_to_pan:
            self.audio.set_pan(x)
        
        # --- Visual mapping ---
        
        # Position on screen
        self.visual.params.x = x
        self.visual.params.y = y
        
        if self.config.x_to_hue:
            # Map x to full colour wheel
            self.visual.params.hue = map_range(x, 0.0, 1.0, 0.0, 360.0)
        
        if self.config.z_to_size:
            size = map_range(
                z, 0.0, 1.0,
                self.config.size_min, self.config.size_max
            )
            self.visual.params.size = size
        
        if self.config.z_to_brightness:
            brightness = map_range(z, 0.0, 1.0, 0.3, 1.0)
            self.visual.params.brightness = brightness
    
    def handle_touch(self, zone: str):
        """
        Handle touch zone events - change modes or cycle options.
        
        Args:
            zone: 'north', 'south', 'east', 'west', or 'center'
        """
        logger.info(f"Touch: {zone}")
        
        if zone == 'north':
            # Cycle waveform forward
            self._waveform_index = (self._waveform_index + 1) % len(self.waveforms)
            waveform = self.waveforms[self._waveform_index]
            self.audio.set_waveform(waveform)
            logger.info(f"Waveform: {waveform}")
        
        elif zone == 'south':
            # Cycle waveform backward
            self._waveform_index = (self._waveform_index - 1) % len(self.waveforms)
            waveform = self.waveforms[self._waveform_index]
            self.audio.set_waveform(waveform)
            logger.info(f"Waveform: {waveform}")
        
        elif zone == 'east':
            # Cycle shape forward
            self._shape_index = (self._shape_index + 1) % len(self.shapes)
            shape = self.shapes[self._shape_index]
            self.visual.params.shape = shape
            logger.info(f"Shape: {shape}")
        
        elif zone == 'west':
            # Cycle shape backward
            self._shape_index = (self._shape_index - 1) % len(self.shapes)
            shape = self.shapes[self._shape_index]
            self.visual.params.shape = shape
            logger.info(f"Shape: {shape}")
        
        elif zone == 'center':
            # Toggle trail effect
            self.visual._trail_enabled = not self.visual._trail_enabled
            self.visual._trail.clear()
            logger.info(f"Trail: {self.visual._trail_enabled}")
    
    def handle_flick(self, direction: str):
        """
        Handle flick gestures.
        
        Args:
            direction: Flick direction
        """
        logger.info(f"Flick: {direction}")
        
        # Could use for larger jumps in frequency, rapid mode changes, etc.
        if direction == 'north':
            # Jump up an octave
            current_freq = self.audio.params.frequency
            self.audio.set_frequency(current_freq * 2)
        
        elif direction == 'south':
            # Jump down an octave
            current_freq = self.audio.params.frequency
            self.audio.set_frequency(current_freq / 2)
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get current state for debug display."""
        return {
            'freq': self.audio.params.frequency,
            'volume': self.audio.params.volume,
            'waveform': self.audio.params.waveform,
            'hue': self.visual.params.hue,
            'shape': self.visual.params.shape,
            'size': self.visual.params.size,
            'fps': self.visual.get_fps(),
            'mode': self.mode
        }
