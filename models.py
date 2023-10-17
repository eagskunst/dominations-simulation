from dataclasses import dataclass
import events

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
    road_gold_generation: float
    hunt_time: int
    mine_time: int
    current_busy_population_count: int

    def advance_time(self):
        self.current_time += 1
    
    def mine_gold(self, event_handler, resources):
        event = events.MineGoldEvent(self, resources)
        event_handler.add_event(event)

@dataclass
class Resources():
    food_count: int
    gold_count: int
    gold_buildings_count: int
    food_buildings_count: int

@dataclass
class Combat():
    attack_units_count: int
    defense_units_count: int
    max_attack_units_count: int
    attack_buildings_count: int
    attack_force_rate: float
    training_time: int

@dataclass
class ResearchAndDevelopment():
    era_level: int
    building_build_cost: int
    max_building_improvements: int
    improvement_cost: int
    bulding_build_time: int
    building_improvement_time: int

@dataclass
class EnemyNation():
    attack_coefficient: float
    defense_units_coefficient: float
    defense_buildings_coefficient: float
    gold_per_combat: float
    food_per_combat: float
    units_per_combat: int
    attacks_risk_rate: float