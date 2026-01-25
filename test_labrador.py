#!/usr/bin/env python3
"""
Test EspoTek Labrador connection.

This is a basic connectivity test. Full Labrador integration is 
an enhancement - the main synth works without it.

Usage:
    python test_labrador.py
"""

import sys
import time
from pathlib import Path

# Labrador doesn't have official pip packages, so this is a 
# placeholder showing how to structure the integration.


def check_labrador_connection():
    """Check if Labrador is connected via USB."""
    import os
    
    # Common USB serial ports on Linux
    potential_ports = [
        '/dev/ttyACM0',
        '/dev/ttyACM1',
        '/dev/ttyUSB0',
        '/dev/ttyUSB1',
    ]
    
    found_ports = []
    for port in potential_ports:
        if os.path.exists(port):
            found_ports.append(port)
    
    return found_ports


def test_serial_communication(port: str):
    """Test basic serial communication with Labrador."""
    try:
        import serial
        
        print(f"Attempting to open {port}...")
        
        ser = serial.Serial(
            port=port,
            baudrate=115200,
            timeout=1
        )
        
        print(f"Opened {port} successfully!")
        
        # The Labrador protocol is documented in the EspoTek repo
        # This is a placeholder - actual commands depend on firmware
        
        ser.close()
        return True
        
    except ImportError:
        print("pyserial not installed. Run: pip install pyserial")
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("Testing EspoTek Labrador connection")
    print("=" * 40)
    
    # Check for USB devices
    print("\nChecking for USB serial ports...")
    ports = check_labrador_connection()
    
    if not ports:
        print("No serial ports found.")
        print("\nTroubleshooting:")
        print("1. Is the Labrador plugged in via USB?")
        print("2. Check 'dmesg | tail' after plugging in")
        print("3. You may need to add your user to the 'dialout' group:")
        print("   sudo usermod -a -G dialout $USER")
        print("   (then log out and back in)")
        return
    
    print(f"Found ports: {ports}")
    
    for port in ports:
        print(f"\nTesting {port}...")
        if test_serial_communication(port):
            print(f"✓ {port} appears to be working")
        else:
            print(f"✗ {port} test failed")
    
    print("\n" + "=" * 40)
    print("Note: Full Labrador integration requires the Labrador")
    print("desktop software or building Python bindings from source.")
    print("See: https://github.com/EspoTek/Labrador")
    print("\nThe main synth works without Labrador integration.")
    print("Labrador adds optional waveform output and scope display.")


if __name__ == '__main__':
    main()
