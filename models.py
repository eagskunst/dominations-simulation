from dataclasses import dataclass
import events
from entities import  building_types, Building
import numpy as np

@dataclass
class Nation():
    """
    Represents a nation in the game.

    Attributes:
        name (str): The name of the nation.
        current_time (int): The current time in the game.
        available_space (int): Available space in the nation.
        not_worked_space (int): Space not currently in use.
        used_space (int): Space currently in use.
        animal_spawn_rate (float): Rate of animal spawn.
        gold_mine_spawn_rate (float): Rate of gold mine spawn.
        roads_count (int): Number of roads in the nation.
        population_count (int): Total population count.
        road_gold_generation (int): Gold generation from roads.
        hunt_time (int): Time required for hunting.
        mine_time (int): Time required for mining.
        current_busy_population_count (int): Count of population currently engaged.
        houses_count (int): Number of houses in the nation.
        animals (list): List of animals in the nation.
        gold_mines (int): Number of gold mines in the nation.

    Methods:
        advance_time(): Increment the current time by 1.
        mine_gold(event_handler, resources): Schedule a gold mining event.
        collect_gold_from_roads(event_handler, resources): Schedule a gold collection event from roads.
        build_road(event_handler): Schedule a road building event.
        open_space(event_handler): Schedule an event to open more space.
        hunt_animal(event_handler, animal_name, resources): Schedule a hunting event.
        show_status(): Display the status of the nation.
    """
    name: str
    current_time: int
    available_space: int
    not_worked_space: int
    used_space: int
    animal_spawn_rate: float
    gold_mine_spawn_rate: float
    roads_count: int
    population_count: int
    road_gold_generation: int
    hunt_time: int
    mine_time: int
    current_busy_population_count: int
    houses_count: int
    animals = []
    gold_mines: int = 0

    def advance_time(self):
        self.current_time += 1
    
    def mine_gold(self, event_handler, resources):
        event = events.MineGoldEvent(self, resources)
        event_handler.add_event(event)
    
    def collect_gold_from_roads(self, event_handler, resources):
        event = events.CollectRoadGold(self, resources)
        event_handler.add_event(event)
    
    def build_road(self, event_handler):
        event = events.BuildRoadEvent(self)
        event_handler.add_event(event)
    
    def open_space(self, event_handler):
        event = events.OpenSpaceEvent(self)
        event_handler.add_event(event)
    
    def hunt_animal(self, event_handler, animal_name: str, resources):
        event = events.HuntAnimalEvent(self, animal_name, resources)
        event_handler.add_event(event)
    
    def show_status(self):
        status = f"Name: {self.name}\n"
        status += f"Current Time: {self.current_time}\n"
        status += f"Available Space: {self.available_space}\n"
        status += f"Not Worked Space: {self.not_worked_space}\n"
        status += f"Used Space: {self.used_space}\n"
        status += f"Roads Count: {self.roads_count}\n"
        status += f"Population Count: {self.population_count}\n"
        status += f"Current Busy Population Count: {self.current_busy_population_count}\n"
        status += f"Houses Count: {self.houses_count}\n"
        status += f"Animals: {self.animals}\n"
        status += f"Gold Mines: {self.gold_mines}\n"
        return status
        

@dataclass
class Resources():
    """
    Represents the resources in the game.

    Attributes:
        food_count (int): The count of available food.
        gold_count (int): The count of available gold.
        gold_food_buidings (list[Building]): List of buildings related to gold and food.

    Methods:
        show_status(): Display the status of resources.
    """
    food_count: int
    gold_count: int
    gold_food_buildings: list[Building]

    def show_status(self):
        status = "Resources\n"
        status += f"Food Count: {self.food_count}\n"
        status += f"Gold Count: {self.gold_count}\n"
        status += f"Gold Food Buildings: {self.gold_food_buildings}\n"
        return status

@dataclass
class Combat():
    """
    Represents the combat statistics and capabilities of a nation.

    Attributes:
        attack_units_count (int): Count of attack units.
        defense_units_count (int): Count of defense units.
        max_combat_units_count (int): Maximum combat units count.
        attack_buildings_count (int): Count of buildings related to attack.
        attack_force_rate (float): Attack force rate.
        training_time (int): Time required for training.
        resting (bool): Whether the units are resting.

    Methods:
        show_status(): Display the combat status of the nation.
    """
    attack_units_count: int
    defense_units_count: int
    max_attack_units_count: int
    max_defense_units_count: int
    attack_buildings_count: int
    defense_buildings_count: int
    attack_force_rate: float
    defense_force_rate: float
    training_time: int
    resting: bool = False
    attack_buildings: list[Building]
    defense_buildings: list[Building]

    def show_status(self):
        status = "Combat\n"
        status += f"Attack Units Count: {self.attack_units_count}\n"
        status += f"Defense Units Count: {self.defense_units_count}\n"
        status += f"Max Attack Units Count: {self.max_attack_units_count}\n"
        status += f"Max Defense Units Count: {self.max_defense_units_count}\n"
        status += f"Attack Buildings Count: {self.attack_buildings_count}\n"
        status += f"Defense Buildings Count: {self.defense_buildings_count}\n"
        status += f"Attack Force Rate: {self.attack_force_rate}\n"
        status += f"Defense Force Rate: {self.defense_force_rate}\n"
        status += f"Training Time: {self.training_time}\n"
        status += f"Resting: {self.resting}\n"
        return status
    
    def calculate_attack_and_defense_rates(self):
        self.attack_force_rate = (self.attack_units_count * 1.5) + (self.attack_buildings_count * 10)
        self.defense_force_rate = (self.defense_units_count * 0.8) + (self.defense_buildings * 12)

@dataclass
class ResearchAndDevelopment():
    """
    Represents the research and development capabilities of a nation.

    Attributes:
        era_level (int): The level of the era.
        max_building_improvements (int): Maximum building improvement level.
        bulding_build_time (int): Time required to build a building.
        building_improvement_time (int): Time required for building improvement.

    Methods:
        calculate_building_cost(building_type, seed): Calculate the cost of building construction.
        calculate_improvement_cost(building_type, seed): Calculate the cost of building improvement.
        create_building(event_handler, nation, res, building_type, seed): Schedule a building construction event.
        improve_building(event_handler, nation, res, building, seed): Schedule a building improvement event.
        show_status(): Display the research and development status of the nation.
    """
    era_level: int
    max_building_improvements: int
    bulding_build_time: int             # todo se debe cambiar por exponencial segun la era
    building_improvement_time: int             # todo se debe cambiar por exponencial segun la era

    """
    Returns (gold_cost, food_cost)
    """
    def calculate_building_cost(self, building_type: str, seed: int) -> tuple[int]:
        rng = np.random.default_rng(seed)
        type_cost = (0, 0)
        for building in building_types:
            food_cost = rng.uniform(50, 200)
            gold_cost = rng.uniform(50, 200)
            if building_type == building:
                type_cost = (gold_cost, food_cost)
        return type_cost
    """
    Returns (gold_cost, food_cost)
    """
    def calculate_improvement_cost(self, building_type: str, seed: int) -> tuple[int]:
        rng = np.random.default_rng(seed)
        type_cost = (0, 0)
        for building in building_types:
            food_cost = rng.uniform(300, 500)
            gold_cost = rng.uniform(300, 500)
            if building_type == building:
                type_cost = (int(gold_cost), int(food_cost))
        return type_cost
    
    def create_building(self, event_handler, nation, res, combat: Combat, building_type: str, seed: int):
        event = events.BuildBuilding(nation, self, res, combat, building_type,  seed)
        event_handler.add_event(event)
    
    def improve_building(self, event_handler, nation, res, combat, building_name, seed: int):
        event = events.ImproveBuilding(self, nation, res, combat, building_name, seed)
        event_handler.add_event(event)
    
    def show_status(self):
        status = "R&D\n"
        status += f"Era Level: {self.era_level}\n"
        status += f"Max Building Improvements: {self.max_building_improvements}\n"
        status += f"Building Build Time: {self.bulding_build_time}\n"
        status += f"Building Improvement Time: {self.building_improvement_time}\n"
        return status

@dataclass
class EnemyNation():
    """
    Represents an enemy nation in the game.

    Attributes:
        attack_coefficient (float): Attack coefficient.
        defense_units_coefficient (float): Defense units coefficient.
        defense_buildings_coefficient (float): Defense buildings coefficient.
        gold_per_combat_mean (int): Mean gold per combat.
        gold_per_combat_std (int): Standard deviation of gold per combat.
        food_per_combat_mean (int): Mean food per combat.
        food_per_combat_std (int): Standard deviation of food per combat.
        units_per_combat_mean (int): Mean units per combat.
        units_per_combat_std (int): Standard deviation of units per combat.
        attacks_risk_rate (float): Risk rate of attacks.
        food_per_combat (int): Food cost per combat.
        gold_per_combat (int): Gold cost per combat.
        units_per_combat (int): Units per combat.

    Methods:
        update_attacks_risk_rate(resources): Update the risk rate of attacks based on available resources.
        update_gold_per_combat(): Update the gold cost per combat.
        update_food_per_combat(): Update the food cost per combat.
        update_units_per_combat(): Update the units per combat.
        show_status(): Display the status of the enemy nation.
    """
    attack_coefficient: float
    defense_units_coefficient: float
    defense_buildings_coefficient: float
    gold_per_combat_mean: int
    gold_per_combat_std: int
    food_per_combat_mean: int
    food_per_combat_std: int
    units_per_combat_mean: int
    units_per_combat_std: int
    attacks_risk_rate: float
    food_per_combat: int = 0
    gold_per_combat: int = 0
    units_per_combat: int = 0

    def update_attacks_risk_rate(self, resources):
        if resources.food_count <= 0 or resources.gold_count <= 0:
            self.attacks_risk_rate += 0.01
        else:
            self.attacks_risk_rate = max(0.01, self.attacks_risk_rate - (resources.food_count + resources.gold_count) * 0.0001)
    
    def update_gold_per_combat(self):
        self.gold_per_combat = int(np.random.normal(self.gold_per_combat_mean, self.gold_per_combat_std))
    
    def update_food_per_combat(self):
        self.food_per_combat = int(np.random.normal(self.food_per_combat_mean, self.food_per_combat_std))
    
    def update_units_per_combat(self):
        self.units_per_combat = int(np.random.normal(self.units_per_combat_mean, self.units_per_combat_std))
    
    def show_status(self):
        status = "Enemy nation\n"
        status += f"Attack Coefficient: {self.attack_coefficient}\n"
        status += f"Defense Units Coefficient: {self.defense_units_coefficient}\n"
        status += f"Defense Buildings Coefficient: {self.defense_buildings_coefficient}\n"
        status += f"Attacks Risk Rate: {self.attacks_risk_rate}\n"
        status += f"Food Per Combat: {self.food_per_combat}\n"
        status += f"Gold Per Combat: {self.gold_per_combat}\n"
        status += f"Units Per Combat: {self.units_per_combat}\n"
        return status