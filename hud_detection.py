import cv2
import numpy as np
import pytesseract
import time
import pygetwindow as gw
import mss
import json
import os
from collections import deque

# Set up Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
ocr_config = "--psm 6 -c tessedit_char_whitelist=0123456789 --oem 3"

# Define max values for coins, laps, and position
MAX_COINS = 10
MIN_LAPS = 1
MAX_LAPS = 3
MIN_POSITION = 1
MAX_POSITION = 12  # Maximum number of players in a Mario Kart 8 race

# Rolling window history for stabilization
coin_history = deque(maxlen=5)
lap_history = deque(maxlen=5)
position_history = deque(maxlen=5)

# JSON output file
json_filename = "hud_data.json"

# Directories for saving debug images
debug_folders = {
    "coins": "coin_debug_images",
    "laps": "lap_debug_images",
    "position": "position_debug_images"
}

# Create debug folders if they don't exist
for folder in debug_folders.values():
    if not os.path.exists(folder):
        os.makedirs(folder)

# Frame counter for debug image saving
frame_counter = 0

# Template images directory
template_dir = "template_images"
position_templates = {}


# Load position templates and apply separate dark processing
def load_and_process_templates():
    """Loads position templates and applies grayscale + darkening."""
    for i in range(1, 13):  # 1st to 12th place
        position_text = f"{i}{'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'}"
        template_path = os.path.join(template_dir, f"{position_text}_place_template.png")

        if os.path.exists(template_path):
            template_img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            darkened_template = cv2.convertScaleAbs(template_img, alpha=0.17, beta=0)  # Darken template
            position_templates[position_text] = darkened_template
        else:
            print(f"[⚠️] Warning: Template {template_path} not found!")


# Load templates at the start
load_and_process_templates()


# Find OBS Fullscreen Projector Window
def get_obs_fullscreen_window():
    for window in gw.getWindowsWithTitle("Fullscreen Projector (Source) - MK8 Capture"):
        return window
    return None


# Capture OBS Fullscreen Projector Window
def capture_obs_window():
    obs_window = get_obs_fullscreen_window()
    if obs_window is None:
        return None

    with mss.mss() as sct:
        monitor = {
            "top": obs_window.top,
            "left": obs_window.left,
            "width": obs_window.width,
            "height": obs_window.height
        }
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame


# Preprocessing: Grayscale + Lower Exposure for Coins & Laps
def preprocess_image(image):
    """Applies grayscale conversion and lowers exposure before OCR."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    darker = cv2.convertScaleAbs(gray, alpha=0.17, beta=0)  # Lower exposure
    return darker


# Preprocessing: Grayscale + Lower Exposure for Position ONLY
def preprocess_position(image):
    """Applies grayscale conversion and lowers exposure for position tracking."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    darker = cv2.convertScaleAbs(gray, alpha=0.17, beta=0)  # Lower exposure
    return darker


# Extract & Verify OCR Text (For Coins & Laps Only)
def extract_text(image):
    """Runs OCR on the preprocessed grayscale & lowered exposure image."""
    text = pytesseract.image_to_string(image, config=ocr_config).strip()
    return ''.join(filter(str.isdigit, text))  # Keep only numbers


# Fix OCR Misreading & Apply Caps
def fix_ocr_values(text, min_value, max_value, history):
    """Ensures OCR values are within valid range and corrects misreads."""
    if not text:
        return history[-1] if history else min_value  # Use last valid value if available

    try:
        num = int(text)
        num = max(min_value, min(num, max_value))  # Ensure within valid range

        # Store in rolling history
        history.append(num)

        # Apply stabilization by averaging the last few values
        stabilized_value = round(sum(history) / len(history))

        return str(stabilized_value).zfill(2)

    except ValueError:
        return history[-1] if history else str(min_value).zfill(2)  # Use last valid value if available


# Template Matching for Position Detection
def match_position(frame):
    """Matches the position counter image against darkened templates and returns the closest match."""
    best_match = None
    best_score = float("-inf")  # The higher the score, the better the match

    for position, template in position_templates.items():
        if template is None:
            continue

        # Resize the template to match the position counter size
        template_resized = cv2.resize(template, (frame.shape[1], frame.shape[0]))

        # Match template (TM_CCOEFF_NORMED gives the best match as higher value)
        result = cv2.matchTemplate(frame, template_resized, cv2.TM_CCOEFF_NORMED)
        _, score, _, _ = cv2.minMaxLoc(result)

        # Find best match
        if score > best_score:
            best_match = position
            best_score = score

    return best_match if best_match else "Unknown"


# Save data to JSON
def save_to_json(lap, coins, position):
    """Saves lap count, coin count, and player position to a JSON file."""
    data = {
        "Lap": lap,
        "Coins": coins,
        "Position": position
    }
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, indent=4)


# Main Loop
while True:
    start_time = time.time()
    frame = capture_obs_window()
    if frame is None:
        continue

    h, w, _ = frame.shape

    # Define HUD crop areas
    coin_counter = frame[-140:-60, 172:257]  # Coins
    lap_counter = frame[-140:-60, 340:390]  # Laps (Corrected)
    position_counter = frame[-220:-60, 1610:1840]  # Player Position (Bottom Right)

    # Apply grayscale + lower exposure processing **ONLY FOR POSITION**
    processed_position = preprocess_position(position_counter)

    # Apply grayscale + lower exposure processing for Coins & Laps
    processed_coin = preprocess_image(coin_counter)
    processed_lap = preprocess_image(lap_counter)

    # Save debug images every **7 frames**
    if frame_counter % 7 == 0:
        coin_debug_filename = os.path.join(debug_folders["coins"], f"coin_frame_{frame_counter:05d}.png")
        lap_debug_filename = os.path.join(debug_folders["laps"], f"lap_frame_{frame_counter:05d}.png")

        cv2.imwrite(coin_debug_filename, processed_coin)
        cv2.imwrite(lap_debug_filename, processed_lap)

        print(f"[✅] Debug images saved: {coin_debug_filename}, {lap_debug_filename}")

    # Run OCR on processed images
    raw_coins = extract_text(processed_coin)
    raw_laps = extract_text(processed_lap)

    # Fix OCR misreads and enforce caps
    coins = fix_ocr_values(raw_coins, 0, MAX_COINS, coin_history)
    laps = fix_ocr_values(raw_laps, MIN_LAPS, MAX_LAPS, lap_history)

    # Match position using **darkened** template matching
    position = match_position(processed_position)

    # Save to JSON
    save_to_json(laps, coins, position)

    # Print Results
    print(f"[🏎️] Lap: {laps} | [💰] Coins: {coins} | [📍] Position: {position}")

    frame_counter += 1  # Increment frame counter
    time.sleep(0.05)  # Reduce CPU Load
