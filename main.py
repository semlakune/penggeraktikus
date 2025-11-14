#!/usr/bin/env python3
"""
Penggerak Tikus - Automatic Cursor Mover
Keeps your computer active by moving the cursor when idle is detected.
"""

import threading
import random
import time
import math
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import pyautogui
from pynput import mouse, keyboard
from pynput.keyboard import Key, KeyCode

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install it with: pip install pyyaml")
    sys.exit(1)

try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw

    TRAY_AVAILABLE = True
except ImportError:
    Icon = None  # type: ignore[assignment]
    Menu = None  # type: ignore[assignment]
    MenuItem = None  # type: ignore[assignment]
    Image = None  # type: ignore[assignment]
    ImageDraw = None  # type: ignore[assignment]
    TRAY_AVAILABLE = False


# ============================================================================
# GLOBAL STATE
# ============================================================================


class AppState:
    """Global application state"""

    def __init__(self):
        self.last_activity_time = time.time()
        self.cursor_movement_active = False
        self.script_moving_cursor = False
        self.movement_count = 0
        self.total_distance: float = 0.0
        self.session_start_time = time.time()
        self.paused = False
        self.should_exit = False
        self.pattern_step = 0
        self.last_position: Optional[Tuple[int, int]] = None


state = AppState()


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_CONFIG = {
    "idle_timeout": 300,
    "movement_interval": 0.5,
    "movement_range": 100,
    "status_update_interval": 30,
    "movement_pattern": "random",
    "verbosity": "normal",
    "use_emoji": True,
    "work_hours_only": False,
    "work_hours_start": "09:00",
    "work_hours_end": "18:00",
    "work_days": [0, 1, 2, 3, 4],
    "pause_when_locked": True,
    "adaptive_intervals": True,
    "multi_monitor": True,
    "preferred_monitor": -1,
    "enable_pause_hotkey": True,
    "pause_hotkey": "ctrl+shift+p",
    "enable_system_tray": True,
    "start_minimized": False,
    "pattern_settings": {
        "circle": {"radius": 50, "steps": 20},
        "figure8": {"width": 100, "height": 80, "steps": 30},
        "smooth": {"amplitude": 50, "frequency": 0.1},
        "jiggle": {"max_distance": 10},
        "human": {"min_distance": 20, "max_distance": 150, "acceleration": 0.3},
    },
    "adaptive_settings": {
        "short_idle": {"threshold": 600, "interval": 30},
        "medium_idle": {"threshold": 1800, "interval": 60},
        "long_idle": {"interval": 120},
    },
}

config = DEFAULT_CONFIG.copy()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def load_config(config_path="config.yaml"):
    """Load configuration from YAML file"""
    global config

    if Path(config_path).exists():
        try:
            with open(config_path, "r") as f:
                user_config = yaml.safe_load(f) or {}
                config.update(user_config)
            return True
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            print("Using default configuration.")
            return False
    return False


def get_current_time():
    """Get formatted current time"""
    return datetime.now().strftime("%H:%M:%S - %B %d, %Y")


def format_duration(seconds):
    """Format seconds into human-readable duration"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def is_work_hours():
    """Check if current time is within work hours"""
    if not config["work_hours_only"]:
        return True

    now = datetime.now()

    # Check if today is a work day
    if now.weekday() not in config["work_days"]:
        return False

    # Parse work hours
    start_time = datetime.strptime(config["work_hours_start"], "%H:%M").time()
    end_time = datetime.strptime(config["work_hours_end"], "%H:%M").time()
    current_time = now.time()

    return start_time <= current_time <= end_time


def get_screen_bounds():
    """Get screen boundaries, considering multi-monitor setup"""
    screen_width, screen_height = pyautogui.size()

    if config["multi_monitor"] and config["preferred_monitor"] == -1:
        # Use all monitors - get total screen size
        # For simplicity, we use the primary screen bounds
        # In a real multi-monitor setup, you'd query all screens
        return 0, 0, screen_width, screen_height
    else:
        return 0, 0, screen_width, screen_height


def constrain_to_screen(x, y):
    """Constrain coordinates to screen boundaries"""
    min_x, min_y, max_x, max_y = get_screen_bounds()

    x = max(min_x, min(x, max_x - 1))
    y = max(min_y, min(y, max_y - 1))

    return int(x), int(y)


def log(message, level="normal"):
    """Print message based on verbosity level"""
    verbosity = config["verbosity"]

    if verbosity == "quiet" and level != "important":
        return

    if verbosity == "normal" and level == "verbose":
        return

    print(message)


def emoji(char, fallback=""):
    """Return emoji if enabled, otherwise return fallback"""
    if config["use_emoji"]:
        return char
    return fallback


# ============================================================================
# MOVEMENT PATTERNS
# ============================================================================


class MovementPattern:
    """Base class for movement patterns"""

    @staticmethod
    def get_next_position(current_x, current_y):
        """Get next position based on pattern. Return (dx, dy)"""
        raise NotImplementedError


class RandomPattern(MovementPattern):
    """Random movement pattern"""

    @staticmethod
    def get_next_position(current_x, current_y):
        movement_range = config["movement_range"]
        dx = random.randint(-movement_range, movement_range)
        dy = random.randint(-movement_range, movement_range)
        return dx, dy


class CirclePattern(MovementPattern):
    """Circular movement pattern"""

    @staticmethod
    def get_next_position(current_x, current_y):
        settings = config["pattern_settings"]["circle"]
        radius = settings["radius"]
        steps = settings["steps"]

        angle = (state.pattern_step * 2 * math.pi) / steps
        state.pattern_step = (state.pattern_step + 1) % steps

        if state.last_position is None:
            state.last_position = (current_x, current_y)
            center_x, center_y = current_x, current_y
        else:
            center_x, center_y = state.last_position

        dx = int(radius * math.cos(angle))
        dy = int(radius * math.sin(angle))

        return dx, dy


class Figure8Pattern(MovementPattern):
    """Figure-8 movement pattern"""

    @staticmethod
    def get_next_position(current_x, current_y):
        settings = config["pattern_settings"]["figure8"]
        width = settings["width"]
        height = settings["height"]
        steps = settings["steps"]

        t = (state.pattern_step * 2 * math.pi) / steps
        state.pattern_step = (state.pattern_step + 1) % steps

        # Lissajous curve for figure-8
        dx = int(width * math.sin(t))
        dy = int(height * math.sin(2 * t) / 2)

        return dx, dy


class SmoothPattern(MovementPattern):
    """Smooth wave movement pattern"""

    @staticmethod
    def get_next_position(current_x, current_y):
        settings = config["pattern_settings"]["smooth"]
        amplitude = settings["amplitude"]
        frequency = settings["frequency"]

        t = state.pattern_step * frequency
        state.pattern_step += 1

        dx = int(amplitude * math.sin(t))
        dy = int(amplitude * math.cos(t * 0.7))  # Different frequency for y

        return dx, dy


class JigglePattern(MovementPattern):
    """Small jiggle movement in place"""

    @staticmethod
    def get_next_position(current_x, current_y):
        max_dist = config["pattern_settings"]["jiggle"]["max_distance"]

        dx = random.randint(-max_dist, max_dist)
        dy = random.randint(-max_dist, max_dist)

        return dx, dy


class HumanPattern(MovementPattern):
    """Human-like movement with varying distances"""

    @staticmethod
    def get_next_position(current_x, current_y):
        settings = config["pattern_settings"]["human"]
        min_dist = settings["min_distance"]
        max_dist = settings["max_distance"]

        # Random distance
        distance = random.randint(min_dist, max_dist)

        # Random angle
        angle = random.uniform(0, 2 * math.pi)

        dx = int(distance * math.cos(angle))
        dy = int(distance * math.sin(angle))

        return dx, dy


PATTERNS = {
    "random": RandomPattern,
    "circle": CirclePattern,
    "figure8": Figure8Pattern,
    "smooth": SmoothPattern,
    "jiggle": JigglePattern,
    "human": HumanPattern,
}


def get_movement_pattern():
    """Get the current movement pattern class"""
    pattern_name = config["movement_pattern"]
    return PATTERNS.get(pattern_name, RandomPattern)


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================


def print_header():
    """Print startup header with configuration"""
    log("=" * 70, "important")
    log(f"  {emoji('🖱️  ', '')}PENGGERAK TIKUS - Automatic Cursor Mover", "important")
    log("=" * 70, "important")
    log(f"Started at: {get_current_time()}", "important")
    log("\nConfiguration:", "important")
    log(
        f"  - Idle timeout: {config['idle_timeout']} seconds ({config['idle_timeout'] // 60} minutes)",
        "important",
    )
    log(f"  - Movement pattern: {config['movement_pattern']}", "important")
    log(f"  - Movement interval: {config['movement_interval']} seconds", "important")
    log(f"  - Movement range: ±{config['movement_range']} pixels", "important")
    log(f"  - Verbosity: {config['verbosity']}", "important")

    if config["work_hours_only"]:
        log(
            f"  - Work hours: {config['work_hours_start']} - {config['work_hours_end']}",
            "important",
        )

    if config["adaptive_intervals"]:
        log("  - Adaptive intervals: enabled", "important")

    if config["enable_pause_hotkey"]:
        log(f"  - Pause hotkey: {config['pause_hotkey']}", "important")

    log("\nStatus: Monitoring user activity...", "important")
    log("=" * 70, "important")
    log("\nPress Ctrl+C to stop the program", "important")
    if config["enable_pause_hotkey"]:
        log(f"Press {config['pause_hotkey']} to pause/resume\n", "important")
    else:
        log("")


def print_statistics():
    """Print current statistics"""
    session_duration = time.time() - state.session_start_time
    log(f"\n{'─' * 70}", "important")
    log(f"{emoji('📊', '')} Session Statistics:", "important")
    log(f"  - Session duration: {format_duration(session_duration)}", "important")
    log(f"  - Total cursor movements: {state.movement_count}", "important")
    log(f"  - Total distance traveled: {int(state.total_distance)} pixels", "important")
    if state.movement_count > 0:
        log(
            f"  - Average distance per move: {int(state.total_distance / state.movement_count)} pixels",
            "important",
        )
    log(f"{'─' * 70}\n", "important")


# ============================================================================
# INPUT HANDLERS
# ============================================================================


def update_last_activity():
    """Update last activity time"""
    if not state.script_moving_cursor and not state.paused:
        state.last_activity_time = time.time()
        if state.cursor_movement_active:
            log(f"\n{emoji('✋', '[STOP]')} {get_current_time()}", "normal")
            log(
                "   User activity detected! Stopping automatic cursor movement.",
                "normal",
            )
            log(f"   Total movements in this session: {state.movement_count}", "normal")
            state.cursor_movement_active = False
            state.pattern_step = 0  # Reset pattern
            state.last_position = None


def on_move(x, y):
    """Mouse move handler"""
    update_last_activity()


def on_click(x, y, button, pressed):
    """Mouse click handler"""
    update_last_activity()


def on_scroll(x, y, dx, dy):
    """Mouse scroll handler"""
    update_last_activity()


def on_press(key):
    """Keyboard press handler"""
    update_last_activity()
    on_hotkey_press(key)


def on_release(key):
    """Keyboard release handler"""
    update_last_activity()
    on_hotkey_release(key)


# Hotkey state tracking
hotkey_pressed = set()
expected_hotkey = set()


def refresh_hotkey_binding():
    """Cache the parsed hotkey combination for faster comparison"""
    global expected_hotkey

    hotkey_pressed.clear()
    if not config.get("enable_pause_hotkey"):
        expected_hotkey = set()
        return

    expected_hotkey = parse_hotkey(config["pause_hotkey"])


def parse_hotkey(hotkey_string):
    """Parse hotkey string like 'ctrl+shift+p' into key components"""
    parts = hotkey_string.lower().split("+")
    keys = []

    for part in parts:
        if part == "ctrl":
            keys.append(Key.ctrl)
        elif part == "shift":
            keys.append(Key.shift)
        elif part == "alt":
            keys.append(Key.alt)
        elif part == "cmd":
            keys.append(Key.cmd)
        else:
            # Regular character key
            keys.append(KeyCode.from_char(part))

    return set(keys)


def on_hotkey_press(key):
    """Handle hotkey press for pause/resume"""
    global hotkey_pressed

    if config["enable_pause_hotkey"] and expected_hotkey:
        try:
            hotkey_pressed.add(key)

            # Normalize the pressed keys
            normalized_pressed = set()
            for k in hotkey_pressed:
                if hasattr(k, "char"):
                    if k.char:
                        normalized_pressed.add(KeyCode.from_char(k.char.lower()))
                else:
                    normalized_pressed.add(k)

            # Check if hotkey matches
            if normalized_pressed >= expected_hotkey:
                toggle_pause()
                hotkey_pressed.clear()
        except AttributeError:
            pass


def on_hotkey_release(key):
    """Handle hotkey release"""
    global hotkey_pressed
    try:
        hotkey_pressed.discard(key)
    except KeyError:
        pass


def toggle_pause():
    """Toggle pause state"""
    state.paused = not state.paused

    if state.paused:
        log(f"\n{emoji('⏸️ ', '[PAUSED]')} {get_current_time()}", "important")
        log(
            f"   Program paused. Press {config['pause_hotkey']} to resume.", "important"
        )
        state.cursor_movement_active = False
    else:
        log(f"\n{emoji('▶️ ', '[RESUMED]')} {get_current_time()}", "important")
        log("   Program resumed. Monitoring activity...", "important")
        state.last_activity_time = time.time()  # Reset idle timer


# ============================================================================
# CURSOR MOVEMENT
# ============================================================================


def get_adaptive_interval():
    """Get movement interval based on idle time"""
    if not config["adaptive_intervals"]:
        return config["movement_interval"]

    time_since_last_activity = time.time() - state.last_activity_time
    adaptive = config["adaptive_settings"]

    if time_since_last_activity < adaptive["short_idle"]["threshold"]:
        return adaptive["short_idle"]["interval"]
    elif time_since_last_activity < adaptive["medium_idle"]["threshold"]:
        return adaptive["medium_idle"]["interval"]
    else:
        return adaptive["long_idle"]["interval"]


def move_cursor_randomly():
    """Main cursor movement loop"""
    last_status_update = time.time()

    while not state.should_exit:
        # Skip if paused
        if state.paused:
            time.sleep(0.5)
            continue

        # Skip if outside work hours
        if not is_work_hours():
            if not state.cursor_movement_active:
                current_time = time.time()
                if (current_time - last_status_update) >= config[
                    "status_update_interval"
                ]:
                    log(
                        f"{emoji('⏰', '[TIME]')} Outside work hours. Sleeping...",
                        "verbose",
                    )
                    last_status_update = current_time
            time.sleep(60)  # Check every minute
            continue

        current_time = time.time()
        time_since_last_activity = current_time - state.last_activity_time

        # Show periodic status updates when user is active
        if (
            not state.cursor_movement_active
            and (current_time - last_status_update) >= config["status_update_interval"]
        ):
            idle_percentage = (time_since_last_activity / config["idle_timeout"]) * 100
            remaining = config["idle_timeout"] - time_since_last_activity

            if idle_percentage < 100:
                log(
                    f"{emoji('⏱️ ', '[IDLE]')} Idle: {format_duration(time_since_last_activity)} / {format_duration(config['idle_timeout'])} "
                    f"({min(idle_percentage, 100):.0f}%) - {format_duration(remaining)} until auto-movement",
                    "normal",
                )

            last_status_update = current_time

        # Start cursor movement when idle threshold is reached
        if (
            not state.cursor_movement_active
            and time_since_last_activity >= config["idle_timeout"]
        ):
            state.cursor_movement_active = True
            log(f"\n{emoji('🚀', '[START]')} {get_current_time()}", "normal")
            log(
                f"   Idle timeout reached ({format_duration(config['idle_timeout'])})!",
                "normal",
            )
            log(
                f"   Starting automatic cursor movement with pattern: {config['movement_pattern']}\n",
                "normal",
            )

        # Move cursor if active
        if state.cursor_movement_active:
            state.script_moving_cursor = True
            x, y = pyautogui.position()

            # Get movement from pattern
            pattern_class = get_movement_pattern()
            dx, dy = pattern_class.get_next_position(x, y)

            new_x, new_y = constrain_to_screen(x + dx, y + dy)

            # Calculate actual distance
            actual_dx = new_x - x
            actual_dy = new_y - y
            distance = math.sqrt(actual_dx**2 + actual_dy**2)

            # Move cursor with adaptive interval
            interval = (
                get_adaptive_interval()
                if config["adaptive_intervals"]
                else config["movement_interval"]
            )

            try:
                pyautogui.moveTo(new_x, new_y, duration=interval)
            except pyautogui.FailSafeException:
                log(
                    f"\n{emoji('⚠️ ', '[WARNING]')} Failsafe triggered! Cursor in corner.",
                    "important",
                )
                state.cursor_movement_active = False
                state.script_moving_cursor = False
                continue

            # Update statistics
            state.movement_count += 1
            state.total_distance += distance

            # Print movement info
            log(
                f"{emoji('🖱️ ', '[MOVE]')} Move #{state.movement_count}: ({x}, {y}) → ({new_x}, {new_y}) | "
                f"Distance: {int(distance)}px | Total: {int(state.total_distance)}px",
                "normal",
            )

            state.script_moving_cursor = False

            # Use adaptive interval for sleep
            time.sleep(interval)
        else:
            time.sleep(0.1)


# ============================================================================
# SYSTEM TRAY
# ============================================================================


def create_tray_icon():
    """Create system tray icon"""
    if (
        not TRAY_AVAILABLE
        or not config["enable_system_tray"]
        or Icon is None
        or Menu is None
        or MenuItem is None
        or Image is None
        or ImageDraw is None
    ):
        return None

    # Create a simple icon
    width = 64
    height = 64
    image = Image.new("RGB", (width, height), "white")
    dc = ImageDraw.Draw(image)

    # Draw a simple mouse cursor icon
    dc.rectangle([16, 16, 48, 48], fill="blue", outline="black")
    dc.polygon([(32, 20), (28, 32), (36, 32)], fill="white")

    def on_quit(icon, item):
        """Quit from tray"""
        state.should_exit = True
        icon.stop()

    def on_pause_resume(icon, item):
        """Toggle pause from tray"""
        toggle_pause()

    def on_show_stats(icon, item):
        """Show statistics"""
        print_statistics()

    menu = Menu(
        MenuItem("Pause/Resume", on_pause_resume),
        MenuItem("Show Statistics", on_show_stats),
        MenuItem("Quit", on_quit),
    )

    icon = Icon("PenggerakTikus", image, "Penggerak Tikus", menu)
    return icon


# ============================================================================
# MAIN
# ============================================================================


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Penggerak Tikus - Automatic Cursor Mover",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Run with default config
  %(prog)s --idle-time 180              # Set idle timeout to 3 minutes
  %(prog)s --pattern circle --quiet     # Use circle pattern in quiet mode
  %(prog)s --work-hours-only            # Only run during work hours
  %(prog)s --config myconfig.yaml       # Use custom config file
        """,
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)",
    )
    parser.add_argument("--idle-time", type=int, help="Idle timeout in seconds")
    parser.add_argument(
        "--pattern",
        type=str,
        choices=list(PATTERNS.keys()),
        help="Movement pattern to use",
    )
    parser.add_argument("--range", type=int, help="Movement range in pixels")
    parser.add_argument(
        "--quiet", action="store_true", help="Quiet mode (only show important messages)"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Verbose mode (show all messages)"
    )
    parser.add_argument(
        "--work-hours-only",
        action="store_true",
        help="Only run during configured work hours",
    )
    parser.add_argument(
        "--no-tray", action="store_true", help="Disable system tray icon"
    )
    parser.add_argument(
        "--no-emoji", action="store_true", help="Disable emoji in output"
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    global config

    # Parse command line arguments
    args = parse_arguments()

    # Load configuration file
    load_config(args.config)

    # Override config with command line arguments
    if args.idle_time:
        config["idle_timeout"] = args.idle_time
    if args.pattern:
        config["movement_pattern"] = args.pattern
    if args.range:
        config["movement_range"] = args.range
    if args.quiet:
        config["verbosity"] = "quiet"
    if args.verbose:
        config["verbosity"] = "verbose"
    if args.work_hours_only:
        config["work_hours_only"] = True
    if args.no_tray:
        config["enable_system_tray"] = False
    if args.no_emoji:
        config["use_emoji"] = False

    refresh_hotkey_binding()

    # Print startup header
    print_header()

    # Set up input listeners
    mouse_listener = mouse.Listener(
        on_move=on_move, on_click=on_click, on_scroll=on_scroll
    )

    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

    # Start input listeners
    mouse_listener.start()
    keyboard_listener.start()

    # Start cursor movement thread
    cursor_thread = threading.Thread(target=move_cursor_randomly, daemon=True)
    cursor_thread.start()

    # Create system tray icon
    tray_icon = None
    tray_thread = None
    if config["enable_system_tray"] and TRAY_AVAILABLE:
        tray_icon = create_tray_icon()
        if tray_icon:
            if sys.platform == "darwin" and hasattr(tray_icon, "run_detached"):
                tray_icon.run_detached()
            else:
                tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
                tray_thread.start()
            log(f"{emoji('✅', '[OK]')} System tray icon enabled", "normal")

    log(f"{emoji('✅', '[OK]')} All systems active. Monitoring started!\n", "important")

    try:
        # Keep the program running
        while not state.should_exit:
            time.sleep(1)
    except KeyboardInterrupt:
        log(
            f"\n\n{emoji('🛑', '[STOP]')} Shutdown initiated by user (Ctrl+C)\n",
            "important",
        )
        print_statistics()
        log(f"Final session ended at: {get_current_time()}", "important")
        log(f"\nThank you for using Penggerak Tikus! {emoji('👋', '')}", "important")
    finally:
        # Cleanup
        state.should_exit = True
        mouse_listener.stop()
        keyboard_listener.stop()
        if tray_icon:
            tray_icon.stop()
        if tray_thread and tray_thread.is_alive():
            tray_thread.join(timeout=1)


if __name__ == "__main__":
    main()
