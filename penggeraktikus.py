import threading
import random
import time
from datetime import datetime
import pyautogui
from pynput import mouse, keyboard

# Global variables to track activity
last_activity_time = time.time()
cursor_movement_active = False
script_moving_cursor = False

# Sensitivity for idle time in seconds
IDLE_TIME = 300  # Time required to be idle before starting cursor movement
MOVE_INTERVAL = 0.5  # Time interval between each cursor move for smoother movement
MAX_MOVE_RANGE = 10  # Maximum range for random cursor movement

def get_current_time():
    return datetime.now().strftime("%H:%M:%S - %B %d, %Y")

def update_last_activity():
    global last_activity_time, cursor_movement_active
    if not script_moving_cursor:
        last_activity_time = time.time()
        if cursor_movement_active:
            print(f"{get_current_time()} - Activity detected. Stopping cursor movement.")
            cursor_movement_active = False

def on_move(x, y):
    update_last_activity()

def on_click(x, y, button, pressed):
    update_last_activity()

def on_scroll(x, y, dx, dy):
    update_last_activity()

def on_press(key):
    update_last_activity()

def on_release(key):
    update_last_activity()

def move_cursor_randomly():
    global cursor_movement_active, script_moving_cursor
    while True:
        time_since_last_activity = time.time() - last_activity_time
        if not cursor_movement_active and time_since_last_activity >= IDLE_TIME:
            cursor_movement_active = True
            print(f"{get_current_time()} - No activity for {IDLE_TIME} seconds. Starting cursor movement.")

        if cursor_movement_active:
            script_moving_cursor = True
            x, y = pyautogui.position()
            new_x = x + random.randint(-MAX_MOVE_RANGE, MAX_MOVE_RANGE)
            new_y = y + random.randint(-MAX_MOVE_RANGE, MAX_MOVE_RANGE)
            pyautogui.moveTo(new_x, new_y, duration=MOVE_INTERVAL)
            script_moving_cursor = False

        time.sleep(0.1)

# Set up listeners
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

# Start listeners
mouse_listener.start()
keyboard_listener.start()

# Start cursor movement thread
cursor_thread = threading.Thread(target=move_cursor_randomly)
cursor_thread.start()

try:
    # Keep the program running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    # Stop listeners and thread
    mouse_listener.stop()
    keyboard_listener.stop()
    cursor_movement_active = False
    cursor_thread.join()
