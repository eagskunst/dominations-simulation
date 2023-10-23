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
    
    def update_historics(self, simulation):
        self.not_worked_space.append(simulation.nation.not_worked_space)
        self.used_space.append(simulation.nation.used_space)
        self.roads_count.append(simulation.nation.roads_count)
        self.population_count.append(simulation.nation.population_count)
        self.busy_population_count.append(simulation.nation.current_busy_population_count)
        self.houses_count.append(simulation.nation.houses_count)
        self.animals.append(len(simulation.nation.animals))
        self.gold_mines.append(simulation.nation.gold_mines)
        self.food_count.append(simulation.resources.food_count)
        self.gold_count.append(simulation.resources.gold_count)
        self.attack_units.append(simulation.combat.attack_units_count)
        self.defense_units.append(simulation.combat.defense_units_count)
        self.attack_force_rate.append(simulation.combat.attack_force_rate)
        self.resting.append(simulation.combat.resting)
        self.attack_risk_rate.append(simulation.enemy_nation.attacks_risk_rate)
        self.gold_per_combat.append(simulation.enemy_nation.gold_per_combat)
        self.food_per_combat.append(simulation.enemy_nation.food_per_combat)
        self.units_per_combat.append(simulation.enemy_nation.units_per_combat)

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