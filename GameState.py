import json

class GameState:
    def __init__(self):
        self.speed = 0
        self.lap = 1
        self.position = 12
        self.current_item = None
        self.enemy_items = []
        self.boost_available = False
        self.track_name = ""

    def update_from_ocr(self, ocr_data):
        self.speed = ocr_data.get("speed", self.speed)
        self.lap = ocr_data.get("lap", self.lap)
        self.position = ocr_data.get("position", self.position)
        self.current_item = ocr_data.get("current_item", self.current_item)
        self.enemy_items = ocr_data.get("enemy_items", self.enemy_items)
        self.boost_available = ocr_data.get("boost_available", self.boost_available)
        self.track_name = ocr_data.get("track_name", self.track_name)

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

# Simulate loading OCR data from a JSON file (this would come from Team 1's OCR system)
with open("game_data.json", "r") as file:
    ocr_data = json.load(file)

# Create a GameState instance and update it with OCR data
game_state = GameState()
game_state.update_from_ocr(ocr_data)

# Display the stored game state
game_state.display_game_state()