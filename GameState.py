import json
import time

class GameState:
    def __init__(self):
        self.speed = 0
        self.lap = 1
        self.position = 12
        self.current_item = None
        self.enemy_items = []
        self.boost_available = False
        self.track_name = ""

    def update_from_json(self, json_file):
        try:
            with open(json_file, "r") as file:
                ocr_data = json.load(file)

            self.speed = ocr_data.get("speed", self.speed)
            self.lap = ocr_data.get("lap", self.lap)
            self.position = ocr_data.get("position", self.position)
            self.current_item = ocr_data.get("current_item", self.current_item)
            self.enemy_items = ocr_data.get("enemy_items", self.enemy_items)
            self.boost_available = ocr_data.get("boost_available", self.boost_available)
            self.track_name = ocr_data.get("track_name", self.track_name)

            return True

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️ Error reading JSON: {e}")
            return False

    def display_game_state(self):
        print("\n🔄 Updated Game State:")
        print(f"🚗 Speed: {self.speed} km/h")
        print(f"🏁 Lap: {self.lap}")
        print(f"📍 Position: {self.position}")
        print(f"🎯 Current Item: {self.current_item}")
        print(f"⚠️ Enemy Items: {', '.join(self.enemy_items) if self.enemy_items else 'None'}")
        print(f"🚀 Boost Available: {'Yes' if self.boost_available else 'No'}")
        print(f"🛣 Track: {self.track_name}")
        print("-" * 40)

game_state = GameState()

json_file = "game_data.json"

while True:
    updated = game_state.update_from_json(json_file)

    if updated:
        game_state.display_game_state()

    time.sleep(1 / 30)