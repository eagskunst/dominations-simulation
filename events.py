from __future__ import annotations  # <-- Additional import.
import typing
if typing.TYPE_CHECKING:
    from models import Nation, Resources, Combat, ResearchAndDevelopment, EnemyNation
from entities import Animal, BuildingFactory, Building, GoldBuilding, HouseBuilding, FoodBuilding, AnimalFactory, animal_types
import numpy as np
import sys
from utils import EventAdditionError, get_buildings_count

class Event:

    def __init__(self) -> None:
        self.ticks = 0

    def tick(self):
        pass

    def is_finished(self) -> bool:
        return self.ticks <= 0

class MineGoldEvent(Event):

    GOLD_PER_MINE = 300
    NEEDED_WORKERS = 2

    def __init__(self, nation: Nation, resources: Resources):
        super().__init__()
        self.nation = nation
        self.ticks = nation.mine_time
        self.resources = resources
        if nation.gold_mines <= 0:
            raise EventAdditionError("There is no gold mines")
        elif (nation.current_busy_population_count 
            + MineGoldEvent.NEEDED_WORKERS >= nation.population_count):
            raise EventAdditionError("Can not start mine gold event because there is not enough available population")
        else:
            nation.gold_mines -= 1
            if self.nation.gold_mines < 0:
                self.nation.gold_mines = 0
            nation.current_busy_population_count += MineGoldEvent.NEEDED_WORKERS
    
    def tick(self):
        self.ticks -= 1
        if self.ticks > 0:
            return
        print("Gold mined. Disposing resources.")
        self.nation.current_busy_population_count -= MineGoldEvent.NEEDED_WORKERS
        self.resources.gold_count += MineGoldEvent.GOLD_PER_MINE

class CollectRoadGold(Event):

    def __init__(self, nation: Nation, resources: Resources, event_handler):
        super().__init__()
        self.nation = nation
        self.resource = resources
        self.ticks = nation.roads_count
        self.resources = resources
        if event_handler.collecting_gold:
            raise EventAdditionError("Cannot collect gold if already collecting")
        event_handler.collecting_gold = True
        self.event_handler = event_handler
        if self.nation.roads_count <= 0:
            raise EventAdditionError("No roads to collect")
        self.gold_earned = self.nation.road_gold_generation * self.nation.roads_count
    
    def tick(self):
        self.ticks -= 1
        if self.ticks <= 0:
            print(f"Gold collected from roads. Gold earned: {self.gold_earned}")
            return
        self.resources.gold_count += self.gold_earned
        self.event_handler.collecting_gold = False

class BuildRoadEvent(Event):

    def __init__(self, nation: Nation, res: Resources, combat: Combat):
        super().__init__()
        self.ticks = 1
        self.nation = nation
        buildings_count = get_buildings_count(nation, res, combat)
        if nation.roads_count + 4 > buildings_count * 4:
            raise EventAdditionError("You must build more buildings before building more roads")
    
    def tick(self):
        self.ticks -= 1
        if self.ticks > 0:
            return
        self.nation.roads_count += 4
        print("Roads built")

class OpenSpaceEvent(Event):

    SPACE_TICKS = 5
    NEEDED_WORKERS = 3

    def __init__(self, nation: Nation):
        super().__init__()
        self.nation = nation
        self.ticks = OpenSpaceEvent.SPACE_TICKS
        if nation.not_worked_space <= 0:
            raise EventAdditionError("There is no space for new buildings")
        elif (nation.current_busy_population_count +
              OpenSpaceEvent.NEEDED_WORKERS > nation.population_count):
            raise EventAdditionError("There is not enough population for doing this work")
        self.nation.current_busy_population_count += OpenSpaceEvent.NEEDED_WORKERS
    
    def tick(self):
        self.ticks -= 1
        if self.ticks > 0:
            return
        self.nation.available_space += 1
        self.nation.current_busy_population_count -= OpenSpaceEvent.NEEDED_WORKERS
        if (self.nation.current_busy_population_count < 0):
            self.nation.current_busy_population_count = 0
        self.nation.not_worked_space -= 1
        if (self.nation.not_worked_space < 0):
            self.nation.not_worked_space = 0

class HuntAnimalEvent(Event):

    def __init__(self, nation: Nation, animal_name: str, resources: Resources):
        super().__init__()
        self.nation = nation
        self.resources = resources
        animal: Animal = self.find_first_occurrence(
            nation.animals, 
            lambda animal: animal.name() == animal_name
        )
        if animal == None:
            raise EventAdditionError(f"There is no {animal_name} in the nation currently. Animals: {nation.animals}")
        else:
            if nation.current_busy_population_count + animal.workers_needed() > nation.population_count:
                raise EventAdditionError("There is not enough population for doing this work")
            else:
                self.ticks = animal.hunt_time()
                self.animal = animal
                self.nation.current_busy_population_count += self.animal.workers_needed()
                self.nation.animals.remove(animal)
    
    def tick(self):
        self.ticks -= 1
        if self.ticks > 0:
            return
        #todo revisar si puede almacenar mas comida
        self.resources.food_count += self.animal.food_given()
        self.nation.current_busy_population_count -= self.animal.workers_needed()
        print(f"Animal {self.animal.name()} hunted, added {self.animal.food_given()} food")
    
    def find_first_occurrence(self, lst, predicate):
        try:
            return next(x for x in lst if predicate(x))
        except StopIteration:
            return None

class BuildBuilding(Event):

    def __init__(self, nation: Nation, rd: ResearchAndDevelopment, res: Resources, building_type: str, seed: int):
        super().__init__()
        building = BuildingFactory().create(building_type)
        if nation.current_busy_population_count + building.workers_needed() > nation.population_count:
            people_needed = nation.current_busy_population_count + building.workers_needed()
            raise EventAdditionError(f"There is not enough population for doing this work. Needs: {people_needed} people")
        gold_cost, food_cost = rd.calculate_building_cost(building_type, seed) 
        if food_cost > res.food_count:
            raise EventAdditionError(f"There is not enough food for doing this work. Needs {food_cost} food")
        elif gold_cost > res.gold_count:
            raise EventAdditionError(f"There is not enough gold for doing this work. Needs {gold_cost} gold")
    
        res.food_count -= food_cost
        if res.food_count < 0:
            res.food_count = 0
        res.gold_count -= gold_cost
        if res.gold_count < 0:
            res.gold_count = 0
        nation.current_busy_population_count += building.workers_needed()
        self.ticks = rd.bulding_build_time
        self.nation = nation
        self.res = res
        self.building = building
    
    def tick(self):
        self.ticks -= 1
        if self.ticks > 0:
            return
        self.nation.current_busy_population_count -= self.building.workers_needed()
        if type(self.building) is HouseBuilding:
            self.nation.houses_count += 1
            self.nation.population_count += 2
        elif type(self.building) is FoodBuilding or type(self.building) is GoldBuilding:
            self.res.gold_food_buildings.append(self.building)
        self.nation.available_space -= 1
        if self.nation.available_space < 0:
            self.nation.available_space = 0
        self.nation.used_space += 1
        print(f"{self.building.type} building built.")

class ImproveBuilding(Event):

    def __init__(self, rd: ResearchAndDevelopment, nation: Nation, res: Resources, building_name: str, seed):
        super().__init__()
        building: Building = None
        for b in res.gold_food_buildings:
            if b.type == building_name:
                building = b
                if b.level + 1 > rd.max_building_improvements or b.improving:
                    continue
                else:
                    break
        if building is None:
            raise EventAdditionError(f"There is no {building_name} in the nation currently.")

        if building.improving:
            raise EventAdditionError(f"The {building.type} is already being improved.")

        if building.level >= rd.max_building_improvements:
            raise EventAdditionError("The building cannot be improved further before changing eras.")

        if nation.current_busy_population_count + building.workers_needed() > nation.population_count:
            raise EventAdditionError("There is not enough population for doing this work.")

        gold_cost, food_cost = rd.calculate_improvement_cost(building.type, seed)
        if food_cost > res.food_count:
            raise EventAdditionError("There is not enough food for doing this work.")
        elif gold_cost > res.gold_count:
            raise EventAdditionError("There is not enough gold for doing this work.")

        res.food_count -= food_cost
        if res.food_count < 0:
            res.food_count = 0
        res.gold_count -= gold_cost
        if res.gold_count < 0:
            res.gold_count = 0

        nation.current_busy_population_count += building.workers_needed()
        self.ticks = rd.building_improvement_time
        self.nation = nation
        self.res = res
        self.building = building
        building.improving = True
    
    def tick(self):
        self.ticks -= 1
        if self.ticks > 0:
            return
        self.nation.current_busy_population_count -= self.building.workers_needed()
        self.building.improving = False

class AttackEnemiesEvent(Event):

    def __init__(self, enemy_nation: EnemyNation, combat: Combat, res: Resources):
        super().__init__()
        if combat.attack_units_count <= 0 or combat.attack_buildings_count <= 0:
            raise EventAdditionError("You don't have troops")
        elif combat.resting:
            raise EventAdditionError("Your troops are resting")
        else:
            self.ticks = 1
            self.enemy_nation = enemy_nation
            self.combat = combat
            self.res = res
    
    def tick(self):
        self.ticks -= 1
        if self.ticks > 0 or self.ticks <= -1:
            return
        print("Starting attack to enemy nation")
        defense_rate = (self.enemy_nation.defense_units_coefficient + self.enemy_nation.defense_units_coefficient) / 2
        if defense_rate >= self.combat.attack_force_rate:
            print("Attack failed. Enemy nation won.")
            self.combat.attack_units_count = 0
        else:
            print("Attack success. Our nation won!")
            max_attack_lost = max(1, self.combat.attack_units_count - 1)
            lost_units = np.random.randint(low=1, high=max_attack_lost)
            print(f"Our nation lost {lost_units} unit/s")
            self.combat.attack_units_count -= lost_units
            self.combat.resting = True
            new_food = self.enemy_nation.food_per_combat
            new_gold = self.enemy_nation.gold_per_combat
            self.res.food_count += new_food
            self.res.gold_count += new_gold
            print(f"Added {new_food} food and {new_gold} gold")

class RestFromAttackEvent(Event):

    REST_TICKS = 20

    def __init__(self, combat: Combat):
        super().__init__()
        self.ticks = RestFromAttackEvent.REST_TICKS
        self.combat = combat
    
    def tick(self):
        self.ticks -= 1
        if self.ticks > 0:
            return
        print("Your troops are not longer resting. You can attack again")
        self.combat.resting = False

class DefendFromEnemiesEvent(Event):

    def __init__(self, enemy_nation: EnemyNation, combat: Combat, res: Resources):
        super().__init__()
        print("Enemy nation attack")
        self.enemy_nation = enemy_nation
        self.combat = combat
        self.res = res
        self.ticks = 1
    
    def tick(self):
        self.ticks -= 1
        if self.ticks != 0:
            return
        if self.combat.defense_units_count >= self.enemy_nation.attack_coefficient:
            print("Defend success!")
            try:
                self.combat.defense_units_count = np.random.randint(low=1, high=self.combat.defense_units_count - 1)
            except ValueError: # for low >= high error
                self.combat.defense_units_count = 1
        else:
            print("Defense failed")
            self.combat.defense_units_count = 0
            lost_food = min(self.res.food_count, self.enemy_nation.food_per_combat)
            lost_gold = min(self.res.gold_count, self.enemy_nation.gold_per_combat)
            self.res.food_count -= lost_food
            self.res.gold_count -= lost_gold
            print(f"We lost {lost_food} food and {lost_gold} gold")

class SpawnMineEvent(Event):

    def __init__(self, nation: Nation):
        super().__init__()
        self.ticks = sys.maxsize
        self.nation = nation
    
    def tick(self):
        self.ticks -= 1
        if self.ticks <= 0:
            self.ticks = sys.maxsize
        random_prob = np.random.random()
        if random_prob >= self.nation.gold_mine_spawn_rate:
            print("Gold mine spawned")
            self.nation.gold_mines += 1

class SpawnAnimalEvent(Event):

    def __init__(self, nation: Nation):
        super().__init__()
        self.ticks = sys.maxsize
        self.nation = nation
    
    def tick(self):
        self.ticks -= 1
        if self.ticks <= 0:
            self.ticks = sys.maxsize
        random_prob = np.random.random()
        if random_prob >= self.nation.animal_spawn_rate:
            animal_name = np.random.choice(animal_types)
            animal = AnimalFactory().create(animal_name)
            self.nation.animals.append(animal)
            print(f"{animal_name} spawned")

class UpdateRandomValuesEvent(Event):

    def __init__(self, enemy_nation: EnemyNation, res: Resources):
        super().__init__()
        self.ticks = sys.maxsize
        self.enemy_nation = enemy_nation
        self.res = res
    
    def tick(self):
        self.ticks -= 1
        if self.ticks <= 0:
            self.ticks = sys.maxsize
        self.enemy_nation.update_attacks_risk_rate(self.res)
        self.enemy_nation.update_food_per_combat()
        self.enemy_nation.update_gold_per_combat()
        self.enemy_nation.update_units_per_combat()
        