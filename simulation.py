from historics import StatsCache
from handlers import EventHandler

class Simulation:
    def __init__(self, nation, resources, combat, research_and_dev, enemy_nation):
        self.nation = nation
        self.resources = resources
        self.combat = combat
        self.research_and_dev = research_and_dev
        self.enemy_nation = enemy_nation
        self.stats_cache = StatsCache()
    
    def run_simulation(self):
        # Your simulation logic here
        print("Running simulation with the following data:")
        print("Nation:", self.nation)
        print("Resources:", self.resources)
        print("Combat:", self.combat)
        print("Research and Development:", self.research_and_dev)
        print("Enemy Nation:", self.enemy_nation)
        event_handler = EventHandler(self.nation)
        while True:
            print("1. Add a new event")
            print("2. Check status")
            print("3. Continue simulation")
            print("4. End simulation")
            choice = input("Enter your choice: ")
            if choice == "1":
                # Add a new event based on user input (you can customize this based on the available event types)
                event_type = input("Enter the type of event (e.g., MineGoldEvent): ")
            elif choice == "2":
                print("Status: ")
                # TODO print status from all components
            elif choice == "3":
                # Advance the simulation by one time step
                event_handler.advance_time()
                self.stats_cache.update_historics(self)  # Update historical data
                print("Simulation advanced by one time step.")
            elif choice == "4":
                # End the simulation loop
                print("Simulation ended.")
                break
            else:
                print("Invalid choice. Please try again.")
        print("Showing graphs")
        self.stats_cache.plot_all_attributes()