# penggeraktikus - Random Cursor Movement Script

This Python script simulates mouse activity by moving the cursor randomly after a period of inactivity. It's designed to keep your computer active or simulate user presence.

## Features

- Detects user inactivity (no mouse movement or keyboard input)
- Moves the cursor randomly after a set idle time
- Stops cursor movement when user activity is detected
- Customizable idle time and movement parameters

## Requirements

- Python 3.6+
- pyautogui
- pynput

## Installation

1. Clone this repository or download the script.
2. Install the required libraries:

```
pip install -r requirements.txt
```

## Usage

Run the script using Python:

```
python penggeraktikus.py
```

To stop the script, press Ctrl+C in the terminal where it's running.

## Configuration

You can adjust the following parameters in the script:

- `IDLE_TIME`: Time (in seconds) of inactivity before cursor movement starts (default: 5 seconds)
- `MOVE_INTERVAL`: Time interval between each cursor move (default: 0.5 seconds)
- `MAX_MOVE_RANGE`: Maximum range for random cursor movement (default: 10 pixels)

## Note

This script is for educational purposes only. Be aware of your organization's policies regarding the use of automation tools.

## License

[MIT License](https://opensource.org/licenses/MIT)