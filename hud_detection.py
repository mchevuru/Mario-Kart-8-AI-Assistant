import cv2
import numpy as np
import pytesseract
import time
import pygetwindow as gw
import mss
import os
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

# Create output directories for debug images
os.makedirs("debug_images", exist_ok=True)
os.makedirs("ocr_debug_images", exist_ok=True)

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

# Preprocessing: Apply Step-by-Step Image Modifications
def preprocess_image(image, label, frame_counter):
    """Applies grayscale, exposure reduction, and brightness mask, saving each step."""

    # **Step 1: Original Crop**
    cv2.imwrite(f"debug_images/{label}_step1_original.png", image)

    # **Step 2: Convert to Grayscale**
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f"debug_images/{label}_step2_grayscale.png", gray)

    # **Step 3: Lower Exposure (Alpha = 0.17, DO NOT CHANGE)**
    darker = cv2.convertScaleAbs(gray, alpha=0.17, beta=0)
    cv2.imwrite(f"debug_images/{label}_step3_lower_exposure.png", darker)

    # **Step 4: Create Brightness Mask (Detects Bright Digits)**
    bright_mask = cv2.inRange(darker, 180, 255)
    cv2.imwrite(f"debug_images/{label}_step4_brightness_mask.png", bright_mask)

    # **Step 5: Boost Brightness of Detected Digits**
    enhanced = cv2.addWeighted(darker, 1, bright_mask, 6.0, 0)
    cv2.imwrite(f"debug_images/{label}_step5_brightness_boost.png", enhanced)

    # **Save the final image OCR will read**
    ocr_image_path = f"ocr_debug_images/{label}_{frame_counter:05d}.png"
    cv2.imwrite(ocr_image_path, enhanced)

    return enhanced

# Extract & Verify OCR Text
def extract_text(image):
    """Runs OCR directly on the preprocessed image."""
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

# Main Loop
frame_counter = 0
while True:
    start_time = time.time()
    frame = capture_obs_window()
    if frame is None:
        continue

    h, w, _ = frame.shape

    # Define HUD crop areas (Corrected Lap Counter)
    coin_counter = frame[-140:-60, 172:257]  # Coins
    lap_counter = frame[-140:-60, 340:390]   # Laps (Corrected)

    # Apply preprocessing (Grayscale + Lower Exposure + Brightness Mask)
    processed_coin = preprocess_image(coin_counter, "coin", frame_counter)
    processed_lap = preprocess_image(lap_counter, "lap", frame_counter)

    # Run OCR on processed images
    raw_coins = extract_text(processed_coin)
    raw_laps = extract_text(processed_lap)

    # Fix OCR misreads and enforce caps
    coins = fix_ocr_values(raw_coins, 0, MAX_COINS, coin_history)
    laps = fix_ocr_values(raw_laps, MIN_LAPS, MAX_LAPS, lap_history)

    # Print OCR Results
    print(f"[🏎️] Lap: {laps} | [💰] Coins: {coins}")

    # FPS Calculation
    elapsed_time = time.time() - start_time
    fps = 1 / elapsed_time
    print(f"[⚡] FPS: {fps:.2f}")

    frame_counter += 1
    time.sleep(0.05)  # Reduce CPU Load
