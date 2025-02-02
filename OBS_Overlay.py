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
        return data.get("Lap", "00"), data.get("Coins", "00"), data.get("Position", "00")
    except:
        return "00", "00", "00"
    
# Main loop
running = True
while running:
    screen.fill((0, 0, 0, 0))  # Transparent background



    # Display lap times
    font = pygame.font.Font(None, 32)
    # Get updated lap & coin data
    lap, coins, pos = load_hud_data()

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