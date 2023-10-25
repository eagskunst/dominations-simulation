import matplotlib.backends.backend_pdf as mpdf
import matplotlib.pyplot as plt

class StatsCache:
    """
    Stores historical statistics over time for various attributes of a simulation run.
    
    Methods:
        - update_historics: Updates the historical data based on the current state of the simulation.
        - plot_attribute: Plots the historical data for a single attribute over time.
        - plot_all_attributes: Plots the historical data for all attributes.
    """
    
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
        """
        Pulls the current data from the simulation and appends it to the historical lists.
        
        Args:
            simulation (object): The current state of the simulation.
        """
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

    def plot_attribute(self, pdf_pages, attribute_name, title):
        """
        Plots a specific attribute's historical data.
        
        Args:
            attribute_name (str): The attribute to plot.
            title (str): Title for the plot.
        """
        values = getattr(self, attribute_name)
        time = list(range(1, len(values) + 1))

        plt.figure(figsize=(10, 6))
        plt.plot(time, values, marker='o', linestyle='-', label=attribute_name)
        plt.title(title)
        plt.xlabel("Minutes (Time)")
        plt.ylabel("Value")
        plt.grid(True)
        plt.legend()
        pdf_pages.savefig()
        plt.close()

    def plot_all_attributes(self):
        """
        Iterates over all attributes and plots their historical data.
        """
        pdf_pages = mpdf.PdfPages('simulation_plots.pdf')  # PDF file to save the plots
        for attribute_name in dir(self):
            if not attribute_name.startswith("__") and not callable(getattr(self, attribute_name)):
                self.plot_attribute(pdf_pages, attribute_name, f"{attribute_name} over Time")
        pdf_pages.close()  # Close the PDF after saving all the plots