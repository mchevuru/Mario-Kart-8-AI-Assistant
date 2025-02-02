import json
import time

class GameState:
    def __init__(self):
        self.lap_count = 1
        self.coin_count = 0
        self.position_count = 12

    def update_from_json(self, json_file):
        try:
            with open(json_file, "r") as file:
                ocr_data = json.load(file)

            self.lap_count = ocr_data.get("Lap", self.lap_count)
            self.coin_count = ocr_data.get("Coins", self.coin_count)
            self.position_count = ocr_data.get("Position", self.position_count)

            return True

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f" Error reading JSON: {e}")
            return False

    def display_game_state(self):
        print("\n Updated Game State:")
        print(f" Lap: {self.lap_count}")
        print(f" Coin: {self.coin_count}")
        print(f" Position: {self.position_count}")

game_state = GameState()

json_file = "game_data.json"

def get_lap_count(self):
    return self.lap_count

def get_position(self):
    return self.position_count

def get_coint_count(self):
    return self.coin_count

while True:
    updated = game_state.update_from_json(json_file)

    if updated:
        game_state.display_game_state()

    time.sleep(1 / 2)