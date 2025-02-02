import cv2
import numpy as np
import pytesseract
import time
import pygetwindow as gw
import mss
import json
from collections import deque

# Set up Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
ocr_config = "--psm 6 -c tessedit_char_whitelist=0123456789 --oem 3"

# Define max values for coins & laps
MAX_COINS = 10
MIN_LAPS = 1
MAX_LAPS = 3

# Rolling window history for stabilization
coin_history = deque(maxlen=5)
lap_history = deque(maxlen=5)

# JSON output file
json_filename = "hud_data.json"

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

# Preprocessing: Grayscale + Lower Exposure
def preprocess_image(image):
    """Applies grayscale conversion and lowers exposure before OCR."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    darker = cv2.convertScaleAbs(gray, alpha=0.17, beta=0)  # Lower exposure
    return darker

# Extract & Verify OCR Text
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

# Save data to JSON
def save_to_json(lap, coins):
    """Saves lap count and coin count to a JSON file."""
    data = {
        "Lap": lap,
        "Coins": coins
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

    # Define HUD crop areas (Corrected Lap Counter)
    coin_counter = frame[-140:-60, 172:257]  # Coins
    lap_counter = frame[-140:-60, 340:390]   # Laps (Corrected)

    # Apply grayscale + lower exposure processing
    processed_coin = preprocess_image(coin_counter)
    processed_lap = preprocess_image(lap_counter)

    # Run OCR on processed images
    raw_coins = extract_text(processed_coin)
    raw_laps = extract_text(processed_lap)

    # Fix OCR misreads and enforce caps
    coins = fix_ocr_values(raw_coins, 0, MAX_COINS, coin_history)
    laps = fix_ocr_values(raw_laps, MIN_LAPS, MAX_LAPS, lap_history)

    # Save to JSON
    save_to_json(laps, coins)

    # Print OCR Results
    print(f"[🏎️] Lap: {laps} | [💰] Coins: {coins}")

    # FPS Calculation
    elapsed_time = time.time() - start_time
    fps = 1 / elapsed_time
    print(f"[⚡] FPS: {fps:.2f}")

    time.sleep(0.05)  # Reduce CPU Load