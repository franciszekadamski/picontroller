# Pico Controller - Device Management System

This system runs on a Raspberry Pi Pico and provides network-based control for multiple hardware devices (sensors, servos, LEDs) through a simple command protocol.

## Architecture Overview

The system consists of four main modules that work together to provide remote device control:

```
┌─────────────┐
│   main.py   │  ← Entry point & main loop
└──────┬──────┘
       │
       ├──→ ┌──────────────────┐
       │    │ network_tools.py │  ← WiFi & socket setup
       │    └──────────────────┘
       │
       ├──→ ┌────────────────────┐
       │    │ device_creation.py │  ← Device factory
       │    └─────────┬──────────┘
       │              │
       └──────────────┴──→ ┌────────────┐
                           │ devices.py │  ← Device classes
                           └────────────┘
```

## File Descriptions

### 1. `devices.py` - Device Classes

Defines all hardware device classes with a unified interface:

**Base Class: `Device`**
- Provides common interface for all devices
- Command dispatch system using handler maps
- State management via `update_states()` method

**Device Types:**
- **`Sensor`**: Reads analog values from ADC pins with calibration (y = ax + b)
  - Commands: `read`
  - Returns calibrated sensor readings
  
- **`Servo`**: Controls PWM servo motors with timed swing operations
  - Commands: `up`, `down`, `swing`
  - Non-blocking swing timing via state machine
  
- **`BuiltinLED`**: Controls onboard LED with non-blocking blink
  - Commands: `on`, `off`, `blink`
  - Non-blocking blink timing via state machine

**Key Features:**
- Non-blocking operations (no `time.sleep()` in command handlers)
- State machines for timed operations (servo swing, LED blink)
- Unified command interface via `__call__` method

### 2. `device_creation.py` - Device Factory

Factory pattern for creating device instances from configuration:

**Functions:**
- `create_single_device()`: Creates one device from its specification
- `create_devices()`: Loads configuration JSON and creates all devices for a board
- `read_ip()`: Reads board IP from configuration file

**Configuration Format:**
```json
{
  "boards": {
    "192.168.1.100": [
      {
        "type": "sensor",
        "name": "humidity_sensor",
        "sensor_pin_number": 26,
        "power_pin_number_3_3_v": 15,
        "a": 0.001,
        "b": 0.0
      }
    ]
  }
}
```

### 3. `network_tools.py` - Network Setup

Manages WiFi connection and socket server creation:

**Class: `NetworkServer`**
- Configures static IP from configuration file
- Connects to WiFi with retry logic
- Creates TCP socket server on port 1234 (default)
- Handles connection failures gracefully

**Configuration Format:**
```json
{
  "network": {
    "ssid": "your_wifi_name",
    "password": "your_password",
    "subnet": "255.255.255.0",
    "gateway": "192.168.1.1",
    "dns": "8.8.8.8"
  }
}
```

**Key Features:**
- Static IP configuration
- Automatic reconnection on bind failures
- Returns connection status for validation

### 4. `main.py` - Main Controller Loop

Main application entry point that orchestrates everything:

**Flow:**
1. **Initialization:**
   - Reads board IP from `board_ip.json`
   - Connects to WiFi via `NetworkServer`
   - Creates all devices from `configuration.json`

2. **Main Loop:**
   ```
   Loop:
     ├─ Update all device states (non-blocking timers)
     ├─ Accept incoming connection (1s timeout)
     ├─ Receive command: "device_name:command"
     ├─ Execute command on device
     ├─ Send response: "device_name:result"
     └─ Handle errors and reconnect if needed
   ```

**Protocol:**
- **Request Format:** `device_name:command`
- **Response Format:** `device_name:result`
- **Error Format:** `ERROR:message`

**Example Commands:**
```
humidity_sensor:read     → humidity_sensor:45.2
servo1:swing            → servo1:swinged
led:blink               → led:blinked
```

## Communication Protocol

### Command Structure
```
CLIENT → PICO: "device_name:command"
PICO → CLIENT: "device_name:result"
```

### Error Handling
- **Unknown device:** `ERROR:Unknown device <name>`
- **Invalid format:** `ERROR:Invalid command format`
- **Unknown command:** Returns device-specific failure result (`failed`)

## State Management

The system uses non-blocking state machines for timed operations:

**Servo Swing States:**
- `idle`: Ready for command
- `triggered`: Command received, moving up
- `busy`: Waiting for timer, then moves down

**LED Blink States:**
- `idle`: Ready for command
- `busy`: LED on, waiting for timer to turn off

State is updated on every main loop iteration via `update_states()`, ensuring the system remains responsive to new commands.

## Configuration Files

Two JSON files must be present on the Pico:

1. **`board_ip.json`**: Board's IP address
   ```json
   {
     "board_ip": "192.168.1.100"
   }
   ```

2. **`configuration.json`**: Network and device configuration
   ```json
   {
     "network": {
       "ssid": "WiFi_Name",
       "password": "password",
       "subnet": "255.255.255.0",
       "gateway": "192.168.1.1",
       "dns": "8.8.8.8"
     },
     "boards": {
       "192.168.1.100": [
         // device specifications
       ]
     }
   }
   ```

## Type System

All code includes comprehensive type hints for:
- Function parameters and return types
- Inline variable annotations
- Generic types (Dict, Mapping, Sequence)

This ensures better code clarity and helps catch errors during development.

## Design Patterns

**Factory Pattern** (`device_creation.py`):
- Centralizes device instantiation
- Maps device types to classes via dictionary

**Command Pattern** (`devices.py`):
- Each device has command handlers dictionary
- Unified execution interface across all devices

**State Machine Pattern** (`Servo`, `BuiltinLED`):
- Non-blocking timed operations
- State transitions managed in `update_states()`

**Error Recovery** (`main.py`, `network_tools.py`):
- Socket timeout allows continuous state updates
- Automatic socket recreation on connection failures
- Graceful handling of malformed commands

## Adding New Device Types

1. Create new class in `devices.py` inheriting from `Device`
2. Define `_command_handlers` dictionary in `__init__`
3. Implement command methods with return values
4. Add to `DEVICE_CLASS_MAP` in `device_creation.py`
5. Add device type to `DEVICE_TYPES` list
6. Add device specification to `configuration.json`

Example:
```python
class NewDevice(Device):
    def __init__(self, device_specification: dict):
        super().__init__(unknown_command_result='failed')
        self._command_handlers = {
            'action': self.action,
        }
    
    def action(self) -> str:
        # Implement action
        return 'done'
```
