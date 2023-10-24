from historics import StatsCache
from handlers import EventHandler
from utils import EventAdditionError
import events
import numpy as np
import random

class Simulation:
    def __init__(self, nation, resources, combat, research_and_dev, enemy_nation):
        self.nation = nation
        self.resources = resources
        self.combat = combat
        self.research_and_dev = research_and_dev
        self.enemy_nation = enemy_nation
        self.not_worked_space_for_new_era = self.nation.not_worked_space * 2
        self.stats_cache = StatsCache()
        self.seed = random.getrandbits(100)
    
    def run(self):
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
            print("5. Show event list")
            print("6. End simulation")
            choice = input("Enter your choice: ")
            if choice == "1":
                user_event_choice = input("Enter the type of event you want to add: ")
                try:
                    self.create_events_based_on_input(user_event_choice, event_handler)
                    print(f"{user_event_choice} added")
                    input()
                except EventAdditionError as e:
                    print(e)
                    input()
            elif choice == "2":
                print("Status: ")
                print(self.resources.show_status())
                print(self.combat.show_status())
                print(self.research_and_dev.show_status())
                print(self.enemy_nation.show_status())
                input()
            elif choice == "3":
                # Advance the simulation by one time step
                self.roll_for_enemy_attack(event_handler)
                event_handler.advance_time()
                self.stats_cache.update_historics(self)  # Update historical data
                print("Simulation advanced by one time step.")
                input()
            elif choice == "4":
                if self.nation.not_worked_space > 0:
                    print("You have to used all available space first.")
                else:
                    self.research_and_dev.era_level += 1
                    self.nation.not_worked_space = self.not_worked_space_for_new_era
                    self.not_worked_space_for_new_era *= 2
                    self.research_and_dev.max_building_improvements += 5
                    print("Nation era advanced")
            elif choice == "5":
                self.show_event_list()
            elif choice == "6":
                # End the simulation loop
                print("Simulation ended.")
                break
            else:
                print("Invalid choice. Please try again.")
                input()
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
    
    def create_events_based_on_input(self, user_input, event_handler):
        if user_input == "MineGold":
            self.nation.mine_gold(event_handler, self.resources)
        elif user_input == "CollectRoadGold":
            self.nation.collect_gold_from_roads(event_handler, self.resources)
        elif user_input == "BuildRoad":
            self.nation.build_road(event_handler)
        elif user_input == "OpenSpace":
            self.nation.open_space(event_handler)
        elif user_input == "HuntAnimal":
            animal_name = input("Enter the animal name: ")
            self.nation.hunt_animal(event_handler, animal_name, self.resources)
        elif user_input == "BuildBuilding":
            building_type = input("Enter the building type: ")
            self.research_and_dev.create_building(event_handler, self.nation, self.resources, building_type, self.seed)
        elif user_input == "ImproveBuilding":
            building_name = input("Enter the building to improve: ")
            self.research_and_dev.improve_building(event_handler, self.nation, self.resources, building_name, self.seed)
        elif user_input == "AttackEnemies":
            self.enemy_nation.update_attacks_risk_rate(self.resources)
            event = events.AttackEnemiesEvent(self.enemy_nation, self.combat, self.resources)
            event_handler.add_event(event)
        else:
            print("Invalid event name. Please try again.")
    
    def show_event_list(self):
        events = {
            "MineGold": "Mine gold from available gold mines.",
            "CollectRoadGold": "Collect gold from the roads.",
            "BuildRoad": "Build new roads for the nation.",
            "OpenSpace": "Open up new space for building.",
            "HuntAnimal": "Hunt animals for resources.",
            "BuildBuilding": "Construct new buildings for the nation.",
            "ImproveBuilding": "Improve the level of existing buildings.",
            "AttackEnemiesEvent": "Initiate an attack on enemy nation.",
        }

        print("List of Events:")
        for event, description in events.items():
            print(f"{event}: {description}")
