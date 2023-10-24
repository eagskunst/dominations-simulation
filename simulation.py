from historics import StatsCache
from handlers import EventHandler
from utils import EventAdditionError
import events
import numpy as np

class Simulation:
    def __init__(self, nation, resources, combat, research_and_dev, enemy_nation):
        self.nation = nation
        self.resources = resources
        self.combat = combat
        self.research_and_dev = research_and_dev
        self.enemy_nation = enemy_nation
        self.not_worked_space_for_new_era = self.nation.not_worked_space * 2
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
        self.add_default_events(event_handler)
        while True:
            print(self.nation.show_status())
            print("1. Add a new event")
            print("2. Check status")
            print("3. Continue simulation")
            print("4. Advance era")
            print("5. End simulation")
            choice = input("Enter your choice: ")
            if choice == "1":
                # Add a new event based on user input (you can customize this based on the available event types)
                event_type = input("Enter the type of event (e.g., MineGoldEvent): ")
                try:
                    print("call add event function")
                except EventAdditionError as e:
                    print(e)
            elif choice == "2":
                print("Status: ")
                print(self.resources.show_status())
                print(self.combat.show_status())
                print(self.research_and_dev.show_status())
                print(self.enemy_nation.show_status())
            elif choice == "3":
                # Advance the simulation by one time step
                self.roll_for_enemy_attack(event_handler)
                event_handler.advance_time()
                self.stats_cache.update_historics(self)  # Update historical data
                print("Simulation advanced by one time step.")
            elif choice == "4":
                if self.nation.not_worked_space > 0:
                    print("You have to used all available space first.")
                else:
                    self.research_and_dev.era_level += 1
                    self.nation.not_worked_space = self.not_worked_space_for_new_era
                    self.not_worked_space_for_new_era *= 2
            elif choice == "5":
                # End the simulation loop
                print("Simulation ended.")
                break
            else:
                print("Invalid choice. Please try again.")
        print("Showing graphs")
        self.stats_cache.plot_all_attributes()
    
    def add_default_events(self, event_handler: EventHandler):
        event_handler.add_event(events.SpawnMineEvent(self.nation))
        event_handler.add_event(events.SpawnAnimalEvent(self.nation))
        event_handler.add_event(events.UpdateRandomValuesEvent(self.enemy_nation, self.resources))

    def roll_for_enemy_attack(self, event_handler: EventHandler):
        if event_handler.attack_running:
            return
        random_prob = np.random.rand()
        if random_prob < self.enemy_nation.attacks_risk_rate:
            event_handler.add_event(events.DefendFromEnemiesEvent(self.enemy_nation, self.combat, self.resources))
