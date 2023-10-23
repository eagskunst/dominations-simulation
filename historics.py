import matplotlib.pyplot as plt

class StatsCache:
    def __init__(self):
        self.not_worked_space = []
        self.used_space = []
        self.roads_count = []
        self.population_count = []
        self.busy_population_count = []
        self.houses_count = []
        self.animals = []
        self.gold_mines = []
        self.food_count = []
        self.gold_count = []
        self.attack_units = []
        self.defense_units = []
        self.attack_force_rate = []
        self.resting = []
        self.attack_risk_rate = []
        self.gold_per_combat = []
        self.food_per_combat = []
        self.units_per_combat = []
        self.attack_wins = []
        self.attack_losts = []
        self.defense_wins = []
        self.defense_losts = []

    def plot_attribute(self, attribute_name, title):
        values = getattr(self, attribute_name)
        time = list(range(1, len(values) + 1))

        plt.figure(figsize=(10, 6))
        plt.plot(time, values, marker='o', linestyle='-', label=attribute_name)
        plt.title(title)
        plt.xlabel("Minutes (Time)")
        plt.ylabel("Value")
        plt.grid(True)
        plt.legend()
        plt.show()

    def plot_all_attributes(self):
        for attribute_name in dir(self):
            if not attribute_name.startswith("__") and not callable(getattr(self, attribute_name)):
                self.plot_attribute(attribute_name, f"{attribute_name} over Time")