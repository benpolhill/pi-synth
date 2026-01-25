#!/usr/bin/env python3
"""
Gesture-Controlled Audiovisual Synth

Main entry point - initialises all components and runs the main loop.

Usage:
    python main.py                    # Normal mode
    python main.py --mock             # Mock mode (no hardware)
    python main.py --no-audio         # Visual only
    python main.py --config my.yaml   # Custom config
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import yaml

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from gesture_input import create_gesture_input
from audio import create_audio_engine
from visuals import create_visual_engine
from output_manager import OutputManager, MappingConfig

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return {}
    
    with open(path) as f:
        return yaml.safe_load(f)


def setup_logging(level: str = 'INFO'):
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Gesture-controlled AV synth')
    parser.add_argument('--mock', action='store_true', 
                        help='Use mock inputs (no hardware)')
    parser.add_argument('--no-audio', action='store_true',
                        help='Disable audio output')
    parser.add_argument('--no-visual', action='store_true',
                        help='Disable visual output')
    parser.add_argument('--config', type=str, default='../config.yaml',
                        help='Path to config file')
    parser.add_argument('--debug', action='store_true',
                        help='Show debug overlay')
    args = parser.parse_args()
    
    # Load config
    config_path = Path(__file__).parent / args.config
    config = load_config(config_path)
    
    # Setup logging
    log_level = config.get('debug', {}).get('log_level', 'INFO')
    setup_logging(log_level)
    
    logger.info("Starting Gesture AV Synth")
    logger.info(f"Mock mode: {args.mock}")
    
    # Extract config sections
    audio_config = config.get('audio', {})
    visual_config = config.get('visuals', {})
    gesture_config = config.get('gesture', {})
    mapping_config = config.get('mapping', {})
    
    # Create components
    gesture = create_gesture_input(
        use_mock=args.mock,
        smoothing=gesture_config.get('smoothing', 0.7),
        deadzone=gesture_config.get('edge_deadzone', 0.05)
    )
    
    audio = create_audio_engine(
        use_mock=args.mock or args.no_audio,
        sample_rate=audio_config.get('sample_rate', 44100),
        buffer_size=audio_config.get('buffer_size', 512)
    )
    
    visual = create_visual_engine(
        use_mock=args.mock or args.no_visual,
        width=visual_config.get('window_width', 800),
        height=visual_config.get('window_height', 600),
        fullscreen=visual_config.get('fullscreen', False),
        fps=visual_config.get('fps', 60),
        bg_color=tuple(visual_config.get('bg_color', [10, 10, 20]))
    )
    
    # Create mapping config
    mapping = MappingConfig(
        freq_min=audio_config.get('freq_min', 110),
        freq_max=audio_config.get('freq_max', 880),
        x_to_hue=mapping_config.get('x_to_hue', True),
        x_to_pan=mapping_config.get('x_to_pan', True),
        y_to_pitch=mapping_config.get('y_to_pitch', True),
        z_to_volume=mapping_config.get('z_to_volume', True),
        z_to_size=mapping_config.get('z_to_size', True),
        z_to_brightness=mapping_config.get('z_to_brightness', True)
    )
    
    # Create output manager
    manager = OutputManager(audio, visual, mapping)
    
    # Wire up gesture callbacks
    gesture._on_touch = manager.handle_touch
    gesture._on_flick = manager.handle_flick
    
    # Start components
    try:
        gesture.start()
        audio.start()
        visual.start()
        
        logger.info("All components started. Wave your hand to play!")
        logger.info("Press ESC or close window to quit")
        logger.info("Touch zones: N/S=waveform, E/W=shape, Center=trail")
        
        # Main loop
        show_debug = args.debug or config.get('debug', {}).get('show_gesture_data', False)
        running = True
        
        while running:
            # Handle pygame events (window close, keyboard)
            if not visual.handle_events():
                running = False
                break
            
            # Get gesture position
            x, y, z = gesture.get_position()
            
            # Update outputs
            manager.update(x, y, z)
            
            # Update and render
            audio.update()
            visual.update()
            
            debug_info = manager.get_debug_info() if show_debug else None
            visual.render(show_debug=show_debug, debug_info=debug_info)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    
    finally:
        # Clean up
        logger.info("Shutting down...")
        gesture.stop()
        audio.stop()
        visual.stop()
        logger.info("Goodbye!")


if __name__ == '__main__':
    main()
