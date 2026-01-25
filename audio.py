"""Audio synthesis engine using numpy and pygame."""

import logging
import numpy as np
from typing import Optional, Literal
from dataclasses import dataclass

logger = logging.getLogger(__name__)

WaveformType = Literal['sine', 'square', 'triangle', 'sawtooth']


@dataclass
class AudioParams:
    """Current audio parameters."""
    frequency: float = 440.0      # Hz
    volume: float = 0.5           # 0.0 - 1.0
    pan: float = 0.5              # 0.0 (left) - 1.0 (right)
    waveform: WaveformType = 'sine'


class AudioEngine:
    """
    Real-time audio synthesis using pygame.mixer.
    
    Generates waveforms based on current parameters, updated each frame.
    
    Usage:
        audio = AudioEngine(sample_rate=44100, buffer_size=512)
        audio.start()
        
        # Update parameters from gesture input
        audio.params.frequency = 440.0
        audio.params.volume = 0.7
        
        # In main loop
        audio.update()
        
        audio.stop()
    """
    
    def __init__(
        self,
        sample_rate: int = 44100,
        buffer_size: int = 512,
        channels: int = 2
    ):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.channels = channels
        self.params = AudioParams()
        
        self._phase = 0.0
        self._running = False
        self._sound: Optional['pygame.mixer.Sound'] = None
        self._channel: Optional['pygame.mixer.Channel'] = None
    
    def start(self):
        """Initialise pygame mixer and start audio."""
        import pygame
        
        # Pre-init mixer with low latency settings
        pygame.mixer.pre_init(
            frequency=self.sample_rate,
            size=-16,  # 16-bit signed
            channels=self.channels,
            buffer=self.buffer_size
        )
        pygame.mixer.init()
        
        # Reserve a channel for our continuous tone
        pygame.mixer.set_num_channels(8)
        self._channel = pygame.mixer.Channel(0)
        
        self._running = True
        logger.info(
            f"Audio engine started: {self.sample_rate}Hz, "
            f"buffer={self.buffer_size}"
        )
        
        # Generate initial sound
        self._update_sound()
    
    def stop(self):
        """Stop audio and clean up."""
        import pygame
        
        self._running = False
        if self._channel:
            self._channel.stop()
        pygame.mixer.quit()
        logger.info("Audio engine stopped")
    
    def update(self):
        """
        Update the playing sound with current parameters.
        
        Call this regularly (e.g., every frame) for responsive audio.
        """
        if not self._running:
            return
        
        self._update_sound()
    
    def _update_sound(self):
        """Generate and play new audio buffer."""
        import pygame
        
        # Generate waveform
        samples = self._generate_waveform(
            self.params.frequency,
            self.params.waveform,
            self.buffer_size * 4  # Generate a bit more for smooth looping
        )
        
        # Apply volume
        samples = samples * self.params.volume
        
        # Apply panning (for stereo)
        if self.channels == 2:
            left_vol = 1.0 - self.params.pan
            right_vol = self.params.pan
            stereo = np.column_stack([
                samples * left_vol,
                samples * right_vol
            ])
            samples = stereo.flatten()
        
        # Convert to 16-bit integers
        samples = (samples * 32767).astype(np.int16)
        
        # Create pygame Sound object
        self._sound = pygame.mixer.Sound(buffer=samples.tobytes())
        
        # Play with looping
        if self._channel and not self._channel.get_busy():
            self._channel.play(self._sound, loops=-1)
    
    def _generate_waveform(
        self,
        frequency: float,
        waveform: WaveformType,
        num_samples: int
    ) -> np.ndarray:
        """Generate waveform samples."""
        # Time array
        t = np.arange(num_samples) / self.sample_rate
        
        # Phase continuity for smooth transitions
        phase_increment = 2 * np.pi * frequency / self.sample_rate
        phases = self._phase + np.cumsum(np.full(num_samples, phase_increment))
        self._phase = phases[-1] % (2 * np.pi)
        
        if waveform == 'sine':
            return np.sin(phases)
        
        elif waveform == 'square':
            return np.sign(np.sin(phases))
        
        elif waveform == 'triangle':
            return 2 * np.abs(2 * (phases / (2 * np.pi) % 1) - 1) - 1
        
        elif waveform == 'sawtooth':
            return 2 * (phases / (2 * np.pi) % 1) - 1
        
        else:
            logger.warning(f"Unknown waveform: {waveform}, using sine")
            return np.sin(phases)
    
    def set_frequency(self, freq: float):
        """Set frequency with bounds checking."""
        self.params.frequency = max(20.0, min(20000.0, freq))
    
    def set_volume(self, vol: float):
        """Set volume with bounds checking."""
        self.params.volume = max(0.0, min(1.0, vol))
    
    def set_pan(self, pan: float):
        """Set stereo pan with bounds checking."""
        self.params.pan = max(0.0, min(1.0, pan))
    
    def set_waveform(self, waveform: WaveformType):
        """Set waveform type."""
        self.params.waveform = waveform


class MockAudioEngine(AudioEngine):
    """Mock audio engine for testing without sound output."""
    
    def start(self):
        self._running = True
        logger.info("Mock audio engine started (no sound)")
    
    def stop(self):
        self._running = False
        logger.info("Mock audio engine stopped")
    
    def update(self):
        pass  # No-op


def create_audio_engine(use_mock: bool = False, **kwargs) -> AudioEngine:
    """Factory function to create appropriate audio engine."""
    if use_mock:
        return MockAudioEngine(**kwargs)
    return AudioEngine(**kwargs)
