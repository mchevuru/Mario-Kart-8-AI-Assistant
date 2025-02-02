import json

class MarioKartDriftAnalyzer:
    def init(self, total_laps, hud_data):
        """
        Initialize the analyzer with the total number of laps and the HUD data file path.
        """
        self.total_laps = total_laps
        self.hud_data = hud_data

    def read_hud_data(self):
        """
        Read the current lap and coin count from the HUD data JSON file.
        """
        try:
            with open(self.hud_data, 'r') as file:
                hud_data = json.load(file)
                current_lap = hud_data.get('Lap', 1)
                current_coins = hud_data.get('Coins', 0)
                return current_lap, current_coins
        except FileNotFoundError:
            print(f"Error: The file {self.hud_data} was not found.")
            return None, None
        except json.JSONDecodeError:
            print(f"Error: The file {self.hud_data} contains invalid JSON.")
            return None, None
def determine_strategy(self):
        """
        Provide real-time advice based on the current lap and coin count.
        """
        current_lap, current_coins = self.read_hud_data()
        if current_lap is None or current_coins is None:
            return "Unable to provide strategy due to missing HUD data."

        if current_lap == 1:
            if current_coins < 10:
                return ("Lap 1: Focus on collecting coins to reach 10. "
                        "Consider slight deviations from the racing line to gather coins, "
                        "as having 10 coins increases your kart's top speed.")
            else:
                return ("Lap 1: You've collected 10 coins. "
                        "Maintain the optimal racing line to maximize speed.")
        else:
            if current_coins < 10:
                return (f"Lap {current_lap}: You have {current_coins} coins. "
                        "Aim to collect more coins when possible without compromising your position. "
                        "Maintaining 10 coins ensures maximum speed.")
            else:
                return (f"Lap {current_lap}: With 10 coins, focus on the optimal racing line. "
                        "Prioritize maintaining your position and speed.")

