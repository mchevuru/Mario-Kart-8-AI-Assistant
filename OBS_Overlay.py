import pygame
import json
import time
import os
from collections import deque
import win32gui
import win32api
import win32con

# Constants
HUD_JSON_FILE = "hud_data.json"
STABILITY_THRESHOLD = 5  # How many consecutive readings before confirming a lap change
lap_readings = deque(maxlen=STABILITY_THRESHOLD)

# Variables for lap timing
start_time = None
lap_times = {}

# Load previous lap times from JSON file
if os.path.exists(HUD_JSON_FILE):
    with open(HUD_JSON_FILE, "r") as f:
        try:
            lap_times = json.load(f)
        except json.JSONDecodeError:
            lap_times = {}

def update_lap_time(lap):
    """Updates lap time when a confirmed lap change occurs"""
    global start_time

    if start_time is None:  # Start timing from Lap 1
        start_time = time.time()
        return

    if lap > 1:  # Only update when moving to Lap 2 or 3
        elapsed_time = time.time() - start_time
        lap_times[f"Lap {lap - 1}"] = round(elapsed_time, 2)  # Store previous lap time
        start_time = time.time()  # Reset timer for next lap

        # Save to JSON file
        with open(HUD_JSON_FILE, "w") as f:
            json.dump(lap_times, f, indent=4)

        print(f"[🕒] Lap {lap - 1} time recorded: {elapsed_time:.2f} sec")

def process_lap(lap_ocr):
    """Processes the lap count and only updates it when stable for 5 readings"""
    global lap_readings

    lap_readings.append(lap_ocr)

    # Confirm lap change if detected 5 times in a row
    if len(lap_readings) == STABILITY_THRESHOLD and all(l == lap_ocr for l in lap_readings):
        update_lap_time(lap_ocr)

# ** Pygame Setup for Overlay **
pygame.init()
overlay_width, overlay_height = 300, 150
screen = pygame.display.set_mode((overlay_width, overlay_height), pygame.NOFRAME)

# Find the OBS window
def get_obs_window():
    return win32gui.FindWindow(None, "Fullscreen Projector (Source) - MK8 Capture")

# Move overlay on top of OBS
def set_overlay_topmost(hwnd):
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 50, 50, overlay_width, overlay_height, win32con.SWP_SHOWWINDOW)

def load_hud_data():
    try:
        with open(HUD_JSON_FILE, "r") as json_file:
            data = json.load(json_file)
        return data.get("Lap", "00"), data.get("Coins", "00")
    except:
        return "00", "00"
    
# Main loop
running = True
while running:
    screen.fill((0, 0, 0, 0))  # Transparent background

    # Load the latest HUD data
    if os.path.exists(HUD_JSON_FILE):
        with open(HUD_JSON_FILE, "r") as f:
            try:
                lap_times = json.load(f)
            except json.JSONDecodeError:
                lap_times = {}

    # Display lap times
    font = pygame.font.Font(None, 32)
    # Get updated lap & coin data
    lap, coins = load_hud_data()

    if (lap > 1 & coins >= 8):
        screen.blit("Some message that makes sense", (100, 150))
    elif (lap > 2 & coins <= 3):
        screen.blit("Some message that makes sense", (100, 150))
    # elif ()
    #     screen.blit("Some message that makes sense", (100, 150))
    # elif ()
    #     screen.blit("Some message that makes sense", (100, 150))
    # elif ()
    #     screen.blit("Some message that makes sense", (100, 150))
    # elif ()
    #     screen.blit("Some message that makes sense", (100, 150))

    # Render text
    # lap_text = font.render(f"Lap: {lap}", True, (255, 255, 255))
    # coin_text = font.render(f"Coins: {coins}", True, (255, 255, 0))

    # Positioning on screen (adjust as needed)
    # screen.blit(lap_text, (50, HEIGHT - 150))  # Bottom left
    # screen.blit(coin_text, (50, HEIGHT - 100))  # Slightly above bottom left
    
    
    # y_offset = 20
    # screen.blit(font.render("Lap Times:", True, (255, 255, 255)), (10, 10))
    # for lap, time_value in lap_times.items():
    #     screen.blit(font.render(f"{lap}: {time_value} sec", True, (255, 255, 255)), (10, y_offset))
    #     y_offset += 30

    pygame.display.update()

    # Attach overlay to OBS
    obs_window = get_obs_window()
    if obs_window:
        set_overlay_topmost(win32gui.GetForegroundWindow())

    # Handle exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()