# Gesture-Controlled Audiovisual Synth

A Raspberry Pi project combining the Pimoroni Skywriter HAT (3D gesture sensing) with the EspoTek Labrador (oscilloscope/waveform generator) to create an interactive audiovisual instrument.

## Concept

Wave your hand above the Skywriter to control both visuals and sound simultaneously:

- **X position** → Visual hue / Audio pan
- **Y position** → Visual shape/pattern / Audio pitch  
- **Z position (height)** → Visual intensity/scale / Audio volume
- **Touch zones** → Trigger effects or change modes

The Labrador generates audio waveforms and can also display the output on its oscilloscope for a secondary visual feedback loop.

## Hardware Required

- Raspberry Pi 3 Model B (or newer)
- Pimoroni Skywriter HAT
- EspoTek Labrador
- Speakers or headphones (3.5mm or USB audio)
- Optional: HDMI display for visuals

## Software Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Main Controller                         │
│                      (main.py)                               │
└─────────────────┬───────────────────────┬───────────────────┘
                  │                       │
                  ▼                       ▼
┌─────────────────────────┐   ┌─────────────────────────────┐
│   Gesture Input         │   │   Output Manager            │
│   (gesture_input.py)    │   │   (output_manager.py)       │
│                         │   │                             │
│   - Skywriter interface │   │   - Coordinates audio/visual│
│   - Position smoothing  │   │   - Parameter mapping       │
│   - Gesture detection   │   │   - Mode switching          │
└─────────────────────────┘   └──────────┬──────────────────┘
                                         │
                      ┌──────────────────┼──────────────────┐
                      │                  │                  │
                      ▼                  ▼                  ▼
          ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
          │ Audio Engine  │  │ Visual Engine │  │ Labrador I/O  │
          │ (audio.py)    │  │ (visuals.py)  │  │ (labrador.py) │
          │               │  │               │  │               │
          │ - Waveform gen│  │ - Pygame/GL   │  │ - Waveform out│
          │ - Effects     │  │ - Shapes      │  │ - Scope display│
          └───────────────┘  └───────────────┘  └───────────────┘
```

## Project Structure

```
gesture-av-synth/
├── README.md
├── requirements.txt
├── config.yaml              # Tunable parameters
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── gesture_input.py     # Skywriter interface
│   ├── audio.py             # Sound synthesis
│   ├── visuals.py           # Visual rendering
│   ├── labrador.py          # Labrador communication
│   ├── output_manager.py    # Coordinates outputs
│   └── utils.py             # Smoothing, mapping helpers
├── tests/
│   ├── test_gesture.py      # Test Skywriter independently
│   ├── test_audio.py        # Test audio output
│   └── test_labrador.py     # Test Labrador connection
└── docs/
    └── WIRING.md            # Hardware setup notes
```

## Setup Instructions

### 1. Enable I2C on the Pi

```bash
sudo raspi-config
# Interface Options → I2C → Enable
```

### 2. Install system dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-venv python3-pygame libsdl2-mixer-2.0-0
```

### 3. Create virtual environment

```bash
cd gesture-av-synth
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Install Labrador software

Follow instructions at: https://github.com/EspoTek/Labrador

### 6. Test components individually

```bash
python tests/test_gesture.py   # Wave hand over Skywriter
python tests/test_audio.py     # Should hear test tones
python tests/test_labrador.py  # Check USB connection
```

### 7. Run the synth

```bash
python src/main.py
```

## Configuration

Edit `config.yaml` to adjust:

- Frequency ranges for audio
- Colour palettes for visuals
- Smoothing factors for gesture input
- Mapping curves (linear, exponential, etc.)

## Development Notes for Claude Code

### Priority order for implementation:

1. **gesture_input.py** - Get Skywriter data flowing first
2. **utils.py** - Smoothing is essential; raw data is jittery
3. **audio.py** - Basic tone generation 
4. **visuals.py** - Simple shapes responding to input
5. **output_manager.py** - Wire it all together
6. **labrador.py** - Enhancement, not critical path

### Known challenges:

- Skywriter can be noisy at edges of detection range
- Audio latency on Pi needs `pygame.mixer` pre-init tuning
- Labrador Python bindings may need building from source

### Testing approach:

Each module should work standalone with mock inputs before integration.

## License

MIT
