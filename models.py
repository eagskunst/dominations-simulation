from dataclasses import dataclass
import events
from entities import Animal, building_types, Building
import numpy as np

@dataclass
class Nation():
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
    animals: list[Animal] = []

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
        
        

@dataclass
class Resources():
    food_count: int
    gold_count: int
    gold_food_buidings: list[Building]

@dataclass
class Combat():
    attack_units_count: int
    defense_units_count: int
    max_combat_units_count: int
    attack_buildings_count: int
    attack_force_rate: float
    training_time: int

@dataclass
class ResearchAndDevelopment():
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
    
    def create_building(self, event_handler, nation, res, building_type: str, seed: int):
        event = events.BuildBuilding(nation, self, res, building_type, seed)
        event_handler.add_event(event)
    
    def improve_building(self, event_handler, nation, res, building, seed: int):
        event = events.ImproveBuilding(self, nation, res, building, seed)
        event_handler.add_event(event)

@dataclass
class EnemyNation():
    attack_coefficient: float
    defense_units_coefficient: float
    defense_buildings_coefficient: float
    gold_per_combat: float
    food_per_combat: float
    units_per_combat: int
    attacks_risk_rate: float