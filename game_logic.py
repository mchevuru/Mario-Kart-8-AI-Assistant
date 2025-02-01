class MarioKartDriftAnalyzer:
    def __init__(self, mt_stat):
        """
        Initialize the analyzer with the vehicle's Mini-Turbo (MT) stat.
        """
        self.mt_stat = mt_stat
        self.mt_threshold, self.smt_threshold, self.umt_threshold = self._calculate_mini_turbo_thresholds()

    def _calculate_mini_turbo_thresholds(self):
        """
        Calculate the Mini-Turbo thresholds based on the vehicle's MT stat.
        """
        mt_threshold = 280 - (self.mt_stat - 1.00) * 2.4
        smt_threshold = 590 - (self.mt_stat - 1.00) * 4.8
        umt_threshold = 900 - (self.mt_stat - 1.00) * 6.0
        return mt_threshold, smt_threshold, umt_threshold

    def _calculate_accumulation_rate(self, stick_angle):
        """
        Determine the Mini-Turbo accumulation rate based on the control stick angle.
        """
        if stick_angle > 45:
            return 5  # Optimal rate (units per frame)
        else:
            return 2  # Non-optimal rate (units per frame)

    def simulate_drift(self, stick_angle, drift_duration):
        """
        Simulate the drift to calculate Mini-Turbo charge and provide feedback.
        """
        accumulation_rate = self._calculate_accumulation_rate(stick_angle)
        mini_turbo_counter = 0

        for frame in range(int(drift_duration * 60)):  # Convert duration to frames (60 FPS)
            mini_turbo_counter += accumulation_rate
            if mini_turbo_counter >= self.umt_threshold:
                return "Achieved Ultra Mini-Turbo (UMT)"
            elif mini_turbo_counter >= self.smt_threshold:
                return "Achieved Super Mini-Turbo (SMT)"
            elif mini_turbo_counter >= self.mt_threshold:
                return "Achieved Mini-Turbo (MT)"

        return "No Mini-Turbo achieved"

    def critique_drift(self, stick_angle, drift_duration):
        """
        Provide feedback based on the drift simulation.
        """
        result = self.simulate_drift(stick_angle, drift_duration)
        if "No Mini-Turbo achieved" in result:
            if stick_angle <= 45:
                return f"{result}. Suggestion: Increase control stick angle to above 45° for optimal Mini-Turbo accumulation."
            else:
                return f"{result}. Suggestion: Extend drift duration to achieve at least a Mini-Turbo."
        else:
            return f"{result}. Well done!"
