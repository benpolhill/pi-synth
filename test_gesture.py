#!/usr/bin/env python3
"""
Test Skywriter gesture input independently.

Run this to verify the Skywriter HAT is working before integrating.

Usage:
    python test_gesture.py          # Real hardware
    python test_gesture.py --mock   # Simulated input
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from gesture_input import create_gesture_input


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mock', action='store_true')
    args = parser.parse_args()
    
    print("Testing Skywriter gesture input")
    print("=" * 40)
    
    def on_position(x, y, z):
        # Clear line and print position
        bar_x = '█' * int(x * 20)
        bar_y = '█' * int(y * 20)
        bar_z = '█' * int(z * 20)
        print(f"\rX: {x:.2f} [{bar_x:20s}] | Y: {y:.2f} [{bar_y:20s}] | Z: {z:.2f} [{bar_z:20s}]", end='')
    
    def on_touch(zone):
        print(f"\n*** TOUCH: {zone} ***")
    
    def on_flick(direction):
        print(f"\n>>> FLICK: {direction} >>>")
    
    gesture = create_gesture_input(
        use_mock=args.mock,
        smoothing=0.7,
        on_position=on_position,
        on_touch=on_touch,
        on_flick=on_flick
    )
    
    try:
        gesture.start()
        print("\nWave your hand over the Skywriter...")
        print("Touch the surface to test touch zones")
        print("Flick across the surface to test gestures")
        print("Press Ctrl+C to exit\n")
        
        if args.mock:
            # Simulate some movement for mock mode
            import math
            t = 0
            while True:
                x = 0.5 + 0.4 * math.sin(t)
                y = 0.5 + 0.4 * math.cos(t * 0.7)
                z = 0.5 + 0.3 * math.sin(t * 0.3)
                gesture.set_mock_position(x, y, z)
                t += 0.05
                time.sleep(0.02)
        else:
            # Real hardware - just wait
            while True:
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    
    finally:
        gesture.stop()


if __name__ == '__main__':
    main()
