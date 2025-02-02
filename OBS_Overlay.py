import pygame
import json
import time
import pygetwindow as gw
import win32gui
import win32con

# JSON file containing lap & coin data
json_filename = "hud_data.json"

# Pygame initialization
pygame.init()

# Font settings
pygame.font.init()
font = pygame.font.Font(None, 50)  # Default Pygame font, size 50

# Get OBS Fullscreen Window Position
def get_obs_window():
    for window in gw.getWindowsWithTitle("Fullscreen Projector (Source) - MK8 Capture"):
        return window
    return None

# Create Transparent Pygame Window
obs_window = get_obs_window()
if obs_window is None:
    print("[❌] OBS Fullscreen window not found!")
    exit()

# Set window size & position to match OBS
WIDTH, HEIGHT = obs_window.width, obs_window.height
pygame.display.set_caption("MK8 HUD Overlay")
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME | pygame.SRCALPHA)

# Get the Pygame window handle and make it always on top
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT)
win32gui.SetLayeredWindowAttributes(hwnd, win32gui.RGB(0, 0, 0), 255, win32con.LWA_ALPHA)

# Function to load data from JSON
def load_hud_data():
    try:
        with open(json_filename, "r") as json_file:
            data = json.load(json_file)
        return data.get("Lap", "00"), data.get("Coins", "00")
    except:
        return "00", "00"

# Main Loop
running = True
while running:
    screen.fill((0, 0, 0, 0))  # Fully transparent background

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

    pygame.display.update()

    # Close if ESC is pressed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    time.sleep(0.05)  # Small delay for performance

pygame.quit()