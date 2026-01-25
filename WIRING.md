# Hardware Wiring Guide

## Components

1. **Raspberry Pi 3 Model B** (or newer)
2. **Pimoroni Skywriter HAT**
3. **EspoTek Labrador** (optional)
4. Audio output (3.5mm speakers, HDMI audio, or USB audio)
5. HDMI display (for visuals)

## Skywriter HAT

The Skywriter is a HAT (Hardware Attached on Top) so it simply plugs directly onto the Pi's 40-pin GPIO header.

```
┌─────────────────────────────────────┐
│          Skywriter HAT              │
│                                     │
│    ┌───────────────────────┐        │
│    │   Sensing Area        │        │
│    │   (wave hand here)    │        │
│    │                       │        │
│    │   N                   │        │
│    │ W   C   E             │        │
│    │   S                   │        │
│    └───────────────────────┘        │
│                                     │
│ ████████████████████████████████████│ ← 40-pin header
└─────────────────────────────────────┘
         ↓ plugs onto ↓
┌─────────────────────────────────────┐
│         Raspberry Pi                │
│ ████████████████████████████████████│ ← GPIO header
│                                     │
│  [USB] [USB] [ETH]    [HDMI] [PWR]  │
└─────────────────────────────────────┘
```

### I2C Connection

The Skywriter uses I2C, which must be enabled on the Pi:

```bash
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

Verify the connection:
```bash
sudo i2cdetect -y 1
```

You should see a device at address `0x42`:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- 42 -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --
```

## EspoTek Labrador

The Labrador connects via USB.

```
┌──────────────┐       USB Cable        ┌─────────────────┐
│   Labrador   │◄──────────────────────►│  Raspberry Pi   │
│              │                        │  USB Port       │
│  [micro-USB] │                        │                 │
└──────────────┘                        └─────────────────┘
```

### Check Connection

```bash
# After plugging in, check dmesg
dmesg | tail

# Look for ttyACM device
ls -la /dev/ttyACM*
```

You should see something like `/dev/ttyACM0`.

### Permissions

Add your user to the `dialout` group for serial access:

```bash
sudo usermod -a -G dialout $USER
# Log out and back in for this to take effect
```

## Audio Output

### Option 1: 3.5mm Jack (Default)

Just plug speakers or headphones into the Pi's 3.5mm audio jack.

Force audio output to 3.5mm if needed:
```bash
sudo raspi-config
# Advanced Options → Audio → Force 3.5mm
```

### Option 2: HDMI Audio

Audio can go through HDMI to a TV/monitor with speakers.

```bash
sudo raspi-config
# Advanced Options → Audio → Force HDMI
```

### Option 3: USB Audio

For better quality, use a USB audio adapter:

```bash
# List audio devices
aplay -l

# Set USB as default in ~/.asoundrc:
defaults.pcm.card 1
defaults.ctl.card 1
```

## Display

Connect an HDMI display for the visual output. The pygame window will appear there.

For headless operation (no display), run with `--no-visual` flag.

## Complete Setup Diagram

```
                    ┌────────────────────────────────┐
                    │         Skywriter HAT          │
                    │      (plugged on top of Pi)    │
                    └──────────────┬─────────────────┘
                                   │ (GPIO/I2C)
                                   ▼
┌──────────────┐    USB     ┌─────────────────────────────────────┐
│   Labrador   │◄──────────►│          Raspberry Pi 3B            │
│              │            │                                     │
└──────────────┘            │  [USB]  [USB]  [USB]  [USB]  [ETH]  │
                            │                                     │
                            │  [HDMI]────────►  Display           │
                            │                                     │
                            │  [3.5mm]───────►  Speakers          │
                            │                                     │
                            │  [PWR]◄─────────  5V Power          │
                            └─────────────────────────────────────┘
```

## Troubleshooting

### Skywriter not detected

1. Check I2C is enabled: `sudo raspi-config`
2. Check wiring with `i2cdetect -y 1`
3. Try reseating the HAT
4. Check for bent GPIO pins

### Labrador not detected

1. Try different USB cable (data, not charge-only)
2. Check `dmesg` after plugging in
3. Ensure dialout group membership
4. Try different USB port

### No audio output

1. Check volume: `alsamixer`
2. Test with: `speaker-test -t wav`
3. Check audio routing in `raspi-config`

### Display issues

1. Check HDMI cable connection
2. Try forcing HDMI resolution in `/boot/config.txt`:
   ```
   hdmi_force_hotplug=1
   hdmi_group=1
   hdmi_mode=16  # 1080p 60Hz
   ```
