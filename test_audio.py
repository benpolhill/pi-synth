#!/usr/bin/env python3
"""
Test audio synthesis independently.

Run this to verify audio output is working before integrating.

Usage:
    python test_audio.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from audio import create_audio_engine


def main():
    print("Testing audio synthesis")
    print("=" * 40)
    
    audio = create_audio_engine(
        sample_rate=44100,
        buffer_size=512
    )
    
    try:
        audio.start()
        print("\nYou should hear test tones...")
        
        # Test different waveforms
        waveforms = ['sine', 'square', 'triangle', 'sawtooth']
        
        for waveform in waveforms:
            audio.set_waveform(waveform)
            print(f"\n{waveform.upper()} wave:")
            
            # Sweep frequency
            for freq in [220, 330, 440, 550, 660]:
                audio.set_frequency(freq)
                audio.set_volume(0.5)
                print(f"  {freq} Hz", end='', flush=True)
                
                # Give time for sound to play
                for _ in range(10):
                    audio.update()
                    time.sleep(0.05)
                
                print(" ✓")
        
        print("\n\nTesting pan (put on headphones):")
        audio.set_frequency(440)
        audio.set_waveform('sine')
        
        # Pan left to right
        for i in range(21):
            pan = i / 20
            audio.set_pan(pan)
            pos = "LEFT" if pan < 0.3 else "RIGHT" if pan > 0.7 else "CENTER"
            print(f"\r  Pan: {pan:.1f} [{pos:^7s}]", end='', flush=True)
            
            for _ in range(5):
                audio.update()
                time.sleep(0.03)
        
        print("\n\nTesting volume:")
        audio.set_pan(0.5)
        
        for i in range(11):
            vol = i / 10
            audio.set_volume(vol)
            bar = '█' * int(vol * 20)
            print(f"\r  Volume: {vol:.1f} [{bar:20s}]", end='', flush=True)
            
            for _ in range(5):
                audio.update()
                time.sleep(0.05)
        
        print("\n\nAudio test complete!")
        print("Press Ctrl+C to exit")
        
        while True:
            audio.update()
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    
    finally:
        audio.stop()


if __name__ == '__main__':
    main()
