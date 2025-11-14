# Penggerak Tikus 🖱️

**Automatic Cursor Mover** - Keep your computer active by automatically moving the cursor when idle is detected.

## Features

### Core Features
- ⏱️ **Idle Detection** - Automatically detects when you're away
- 🖱️ **Automatic Cursor Movement** - Moves cursor to keep system active
- 📊 **Real-time Statistics** - Track movements, distance, and session duration
- ⚙️ **Highly Configurable** - YAML configuration file + CLI arguments

### Movement Patterns
Choose from 6 different movement patterns:
- **random** - Random movements (default)
- **circle** - Smooth circular motion
- **figure8** - Figure-8 pattern (Lissajous curve)
- **smooth** - Smooth wave pattern
- **jiggle** - Small movements in place
- **human** - Human-like random movements with varying distances

### Advanced Features
- 🛡️ **Screen Boundary Protection** - Cursor never goes off-screen
- ⏸️ **Pause/Resume Hotkey** - Ctrl+Shift+P to pause/resume
- 🕐 **Smart Scheduling** - Only run during work hours
- 🔄 **Adaptive Intervals** - Movement frequency adapts to idle time
- 🖥️ **Multi-Monitor Support** - Works across multiple displays
- 🔔 **System Tray Icon** - Easy access from system tray (macOS/Windows)
- 🔇 **Quiet/Verbose Modes** - Control output verbosity
- 🌐 **No Emoji Mode** - Disable emojis for cleaner output

## Installation

### Requirements
- Python 3.7+
- macOS, Windows, or Linux

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install pyautogui pynput pyyaml pystray pillow
```

## Quick Start

### Basic Usage

```bash
# Run with default settings
python penggeraktikus.py

# Run with custom idle timeout (3 minutes)
python penggeraktikus.py --idle-time 180

# Use circle pattern in quiet mode
python penggeraktikus.py --pattern circle --quiet

# Only run during work hours
python penggeraktikus.py --work-hours-only

# Disable system tray and emojis
python penggeraktikus.py --no-tray --no-emoji
```

### Configuration File

Edit `config.yaml` to customize settings:

```yaml
# Basic settings
idle_timeout: 300          # 5 minutes
movement_interval: 0.5     # 0.5 seconds between moves
movement_range: 100        # ±100 pixels
movement_pattern: random   # Pattern to use

# Display settings
verbosity: normal          # quiet, normal, verbose
use_emoji: true           # Enable/disable emoji

# Smart scheduling
work_hours_only: false
work_hours_start: "09:00"
work_hours_end: "18:00"
work_days: [0, 1, 2, 3, 4]  # Monday-Friday

# Advanced features
adaptive_intervals: true
multi_monitor: true
enable_pause_hotkey: true
pause_hotkey: "ctrl+shift+p"
enable_system_tray: true
```

## Command Line Arguments

```
usage: penggeraktikus.py [-h] [--config CONFIG] [--idle-time IDLE_TIME]
                         [--pattern {random,circle,figure8,smooth,jiggle,human}]
                         [--range RANGE] [--quiet] [--verbose]
                         [--work-hours-only] [--no-tray] [--no-emoji]

Options:
  --config CONFIG       Path to configuration file (default: config.yaml)
  --idle-time SECONDS   Idle timeout in seconds
  --pattern PATTERN     Movement pattern to use
  --range PIXELS        Movement range in pixels
  --quiet              Quiet mode (only show important messages)
  --verbose            Verbose mode (show all messages)
  --work-hours-only    Only run during configured work hours
  --no-tray            Disable system tray icon
  --no-emoji           Disable emoji in output
```

## Movement Patterns

### Random (Default)
Random movements within specified range. Unpredictable and natural.

```bash
python penggeraktikus.py --pattern random --range 100
```

### Circle
Smooth circular motion. Continuous and visually appealing.

```yaml
pattern_settings:
  circle:
    radius: 50
    steps: 20
```

### Figure-8
Creates a figure-8 pattern using Lissajous curves.

```yaml
pattern_settings:
  figure8:
    width: 100
    height: 80
    steps: 30
```

### Smooth
Smooth wave pattern with sinusoidal movement.

```yaml
pattern_settings:
  smooth:
    amplitude: 50
    frequency: 0.1
```

### Jiggle
Small movements in place. Minimal but effective.

```yaml
pattern_settings:
  jiggle:
    max_distance: 10
```

### Human
Human-like movements with varying distances and random angles.

```yaml
pattern_settings:
  human:
    min_distance: 20
    max_distance: 150
    acceleration: 0.3
```

## Adaptive Intervals

When enabled, movement frequency adapts based on how long you've been idle:

- **Short idle** (< 10 min): Move every 30 seconds
- **Medium idle** (< 30 min): Move every 60 seconds
- **Long idle** (> 30 min): Move every 120 seconds

Configure in `config.yaml`:

```yaml
adaptive_intervals: true
adaptive_settings:
  short_idle:
    threshold: 600
    interval: 30
  medium_idle:
    threshold: 1800
    interval: 60
  long_idle:
    interval: 120
```

## Smart Scheduling

Automatically pause outside of work hours:

```yaml
work_hours_only: true
work_hours_start: "09:00"
work_hours_end: "18:00"
work_days: [0, 1, 2, 3, 4]  # 0=Monday, 6=Sunday
```

## Keyboard Shortcuts

- **Ctrl+C** - Stop the program
- **Ctrl+Shift+P** - Pause/Resume (configurable)

Change pause hotkey in `config.yaml`:
```yaml
pause_hotkey: "ctrl+alt+p"  # or any combination
```

## System Tray

When enabled, you'll see a tray icon with:
- Pause/Resume option
- Show Statistics
- Quit

Disable with `--no-tray` or in config:
```yaml
enable_system_tray: false
```

## Examples

### Keep computer awake during presentation
```bash
python penggeraktikus.py --idle-time 60 --pattern jiggle --quiet
```

### Work hours automation
```bash
python penggeraktikus.py --work-hours-only --pattern human
```

### Minimal output
```bash
python penggeraktikus.py --quiet --no-emoji --no-tray
```

### Test different patterns quickly
```bash
# Try circle pattern for 2 minutes
python penggeraktikus.py --pattern circle --idle-time 120

# Try figure-8 pattern
python penggeraktikus.py --pattern figure8 --idle-time 120
```

## Troubleshooting

### Cursor not moving?
- Check if you're within work hours (if enabled)
- Verify idle timeout has been reached
- Check if program is paused (Ctrl+Shift+P to resume)

### System tray not showing?
Install required dependencies:
```bash
pip install pystray pillow
```

### Permission errors?
On macOS, grant accessibility permissions:
1. System Preferences → Security & Privacy → Privacy
2. Accessibility → Add Terminal/Python

### Hotkey not working?
- Verify the hotkey format in config
- Some key combinations may be reserved by OS
- Try a different combination

## Output Examples

### Normal Mode
```
======================================================================
  🖱️  PENGGERAK TIKUS - Automatic Cursor Mover
======================================================================
Started at: 14:30:45 - January 14, 2025

Configuration:
  - Idle timeout: 300 seconds (5 minutes)
  - Movement pattern: random
  - Movement interval: 0.5 seconds
  - Movement range: ±100 pixels
  - Verbosity: normal
  - Pause hotkey: ctrl+shift+p

Status: Monitoring user activity...
======================================================================

⏱️  Idle: 2m 30s / 5m 0s (50%) - 2m 30s until auto-movement

🚀 14:35:45 - January 14, 2025
   Idle timeout reached (5m 0s)!
   Starting automatic cursor movement with pattern: random

🖱️  Move #1: (500, 300) → (550, 380) | Distance: 94px | Total: 94px
🖱️  Move #2: (550, 380) → (480, 320) | Distance: 89px | Total: 183px
```

### Quiet Mode
```
======================================================================
  PENGGERAK TIKUS - Automatic Cursor Mover
======================================================================
All systems active. Monitoring started!
```

## Performance

- **CPU Usage**: < 1% when idle monitoring
- **Memory Usage**: ~20-30 MB
- **Battery Impact**: Minimal

## Security & Privacy

- No data collection or logging
- All processing happens locally
- No network connections
- Open source - inspect the code yourself

## Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

Built with:
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - GUI automation
- [pynput](https://pynput.readthedocs.io/) - Input monitoring
- [PyYAML](https://pyyaml.org/) - Configuration management
- [pystray](https://pystray.readthedocs.io/) - System tray support

---

Made with ❤️ for keeping your computer awake during important moments!
