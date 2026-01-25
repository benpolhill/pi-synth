# CLAUDE.md - Instructions for Claude Code

This file provides context for Claude Code when working on this project.

## Project Overview

A gesture-controlled audiovisual synthesiser for Raspberry Pi using:
- **Pimoroni Skywriter HAT** - 3D gesture sensing (I2C)
- **EspoTek Labrador** - Optional waveform generator/scope (USB)
- **Pygame** - Audio synthesis and visual rendering

## Architecture

```
gesture_input.py  →  output_manager.py  →  audio.py
                          ↓                    ↓
                     visuals.py          [labrador.py]
```

The `output_manager.py` is the central coordinator that maps gesture input to audio and visual parameters.

## Development Environment

This runs on a Raspberry Pi 3B. When testing locally (not on Pi):
- Use `--mock` flag to simulate Skywriter input
- Use `--no-audio` if no speakers available

```bash
# On Pi with hardware
python src/main.py --debug

# On dev machine without hardware
python src/main.py --mock --debug
```

## Key Files to Modify

| Task | File(s) |
|------|---------|
| Add new parameter mapping | `output_manager.py`, `config.yaml` |
| New visual shapes | `visuals.py` |
| New waveforms/audio effects | `audio.py` |
| Gesture smoothing/sensitivity | `utils.py`, `gesture_input.py` |
| Labrador integration | `labrador.py` (create if needed) |

## Current Status

- [x] Project structure
- [x] Gesture input with smoothing
- [x] Basic audio synthesis (sine, square, triangle, saw)
- [x] Visual rendering (circle, square, triangle, blob)
- [x] Parameter mapping (position → freq/colour/size)
- [x] Touch zone handling (mode switching)
- [ ] Labrador waveform output
- [ ] Labrador scope input
- [ ] More advanced visual effects
- [ ] MIDI output option
- [ ] Recording/playback

## Known Issues / TODOs

1. **Audio latency**: Pygame mixer has some latency. If problematic, consider:
   - Reducing buffer_size in config (increases CPU)
   - Using `simpleaudio` or `sounddevice` instead
   - Pre-generating wavetables

2. **Skywriter edge noise**: The sensor gets noisy at edges of detection. The deadzone helps but could be improved with more sophisticated filtering.

3. **Labrador Python bindings**: No official pip package. Options:
   - Use PySerial with raw protocol
   - Build bindings from EspoTek repo
   - Control via subprocess calling the CLI tools

## Testing Approach

Test each module independently before integration:

```bash
python tests/test_gesture.py --mock  # Simulated gesture
python tests/test_gesture.py         # Real Skywriter

python tests/test_audio.py           # Audio output

python tests/test_labrador.py        # USB connection check
```

## Configuration

All tuneable parameters are in `config.yaml`. Avoid hardcoding values in Python files.

## Code Style

- Type hints on function signatures
- Docstrings on classes and public methods
- Logging instead of print() in library code
- Factory functions (`create_*`) for dependency injection

## Useful Commands

```bash
# Enable I2C on Pi
sudo raspi-config  # Interface Options → I2C

# Check Skywriter is detected
sudo i2cdetect -y 1  # Should show device at 0x42

# Check Labrador USB
dmesg | grep -i acm
ls -la /dev/ttyACM*

# Run with verbose logging
python src/main.py --debug 2>&1 | tee debug.log
```

## References

- Skywriter library: https://github.com/pimoroni/skywriter-hat
- Labrador repo: https://github.com/EspoTek/Labrador
- Pygame audio: https://www.pygame.org/docs/ref/mixer.html
