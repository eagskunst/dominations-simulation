from __future__ import annotations  # <-- Additional import.
import typing
if typing.TYPE_CHECKING:
    from models import Nation, Resources, Combat, ResearchAndDevelopment, EnemyNation
from entities import Animal, BuildingFactory, Building, GoldBuilding, HouseBuilding, FoodBuilding, AnimalFactory, animal_types, AttackBuilding, DefenseBuilding
import numpy as np
import sys
from utils import EventAdditionError

class Event:
    """
    Base class for all events in the game.

    Attributes:
        ticks (int): The number of ticks for the event.

    Methods:
        tick(): Advance the event by one tick.
        is_finished(): Check if the event has finished.
    """
    def __init__(self) -> None:
        self.ticks = 0

    def tick(self):
        pass

    def is_finished(self) -> bool:
        return self.ticks <= 0

class MineGoldEvent(Event):
    """
    Represents an event where the nation mines gold.

    Attributes:
        GOLD_PER_MINE (int): The amount of gold generated per mine.
        NEEDED_WORKERS (int): The number of workers needed for the event.

    Methods:
        tick(): Advance the event by one tick.
    """
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
            nation.current_busy_population_count += MineGoldEvent.NEEDED_WORKERS
    
    def tick(self):
        self.ticks -= 1
        if self.ticks > 0:
            return
        print("Gold mined. Disposing resources.")
        self.nation.current_busy_population_count -= MineGoldEvent.NEEDED_WORKERS
        self.resources.gold_count += MineGoldEvent.GOLD_PER_MINE
        self.nation.gold_mines -= 1
        if self.nation.gold_mines < 0:
            self.nation.gold_mines = 0

class CollectRoadGold(Event):
    """
    Represents an event where the nation collects gold from roads.

    Attributes:
        nation (Nation): The nation collecting road gold.
        resources (Resources): The nation's resources.

    Methods:
        tick(): Advance the event by one tick.
    """

    def __init__(self, nation: Nation, resources: Resources):
        super().__init__()
        self.nation = nation
        self.resource = resources
        self.ticks = nation.roads_count
        self.resources = resources
        self.gold_earned = 0
        if self.nation.roads_count <= 0:
            raise EventAdditionError("No hay caminos para recolectar")
    
    def tick(self):
        self.ticks -= 1
        if self.ticks <= 0:
            print("Terminada la recolección de caminos")
            print(f"Oro generado: {self.gold_earned}")
            return
        self.gold_earned += self.nation.road_gold_generation
        self.resources.gold_count += self.nation.road_gold_generation

class BuildRoadEvent(Event):
    """
    Represents an event to build roads in the nation.

    Attributes:
        nation (Nation): The nation building roads.

    Methods:
        tick(): Advance the event by one tick.
    """

    def __init__(self, nation: Nation):
        super().__init__()
        self.ticks = 1
        self.nation = nation
        if nation.roads_count + 4 > nation.buildings_count * 4:
            raise EventAdditionError("You must build more buildings before building more roads")
    
    def tick(self):
        self.ticks -= 1
        if self.ticks > 0:
            return
        self.nation.roads_count += 4
        print("Roads built")

class OpenSpaceEvent(Event):
    """
    Represents an event to open up new space for building.

    Attributes:
        nation (Nation): The nation opening new space.

    Methods:
        tick(): Advance the event by one tick.
    """

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
    
    def find_first_occurrence(lst, predicate):
        try:
            return next(x for x in lst if predicate(x))
        except StopIteration:
            return None

class BuildBuilding(Event):
    """
    Represents an event to build a new building in the nation.

    Attributes:
        nation (Nation): The nation where the building is constructed.
        rd (ResearchAndDevelopment): Information about research and development.
        res (Resources): The nation's resources.
        building_type (str): The type of building to be constructed.
        seed (int): Random seed for cost calculation.

    Methods:
        tick(): Advance the event by one tick.
    """
    def __init__(self, nation: Nation, rd: ResearchAndDevelopment, res: Resources, combat: Combat, building_type: str, seed: int):
        super().__init__()
        building = BuildingFactory().create(building_type)
        if nation.current_busy_population_count + building.workers_needed() > nation.population_count:
            raise EventAdditionError("There is not enough population for doing this work")
        gold_cost, food_cost = rd.calculate_building_cost(building_type, seed) 
        if food_cost > res.food_count:
            raise EventAdditionError("There is not enough food for doing this work")
        elif gold_cost > res.gold_count:
            raise EventAdditionError("There is not enough gold for doing this work")
    
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
        elif type(self.building) is AttackBuilding:
            self.combat.attack_buildings_count += 1
            self.combat.max_attack_units_count += 20
            self.combat.training_time += 1
            self.combat.calculate_attack_and_defense_rates()
        elif type(self.building) is DefenseBuilding:
            self.combat.defense_buildings_count += 1
            self.combat.max_defense_units_count += 20
            self.combat.training_time += 1
            self.combat.calculate_attack_and_defense_rates()
        
        self.nation.available_space -= 1
        if self.nation.available_space < 0:
            self.nation.available_space = 0
        self.nation.used_space += 1

class ImproveBuilding(Event):
    """
    Represents an event to improve a building in the nation.

    Attributes:
        rd (ResearchAndDevelopment): Information about research and development.
        nation (Nation): The nation where the building is improved.
        res (Resources): The nation's resources.
        building (Building): The building to be improved.
        seed (int): Random seed for cost calculation.

    Methods:
        tick(): Advance the event by one tick.
    """
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
    """
    Represents an event where the nation attacks enemies.

    Attributes:
        enemy_nation (EnemyNation): The enemy nation being attacked.
        combat (Combat): Information about the nation's combat capabilities.
        res (Resources): The nation's resources.

    Methods:
        tick(): Advance the event by one tick.
    """
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
    """
    Represents an event where the nation's troops rest after an attack.

    Attributes:
        combat (Combat): Information about the nation's combat capabilities.

    Methods:
        tick(): Advance the event by one tick.
    """
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
    """
    Represents an event where the nation defends against enemy attacks.

    Attributes:
        enemy_nation (EnemyNation): The enemy nation launching the attack.
        combat (Combat): Information about the nation's combat capabilities.
        res (Resources): The nation's resources.

    Methods:
        tick(): Advance the event by one tick.
    """
    def __init__(self, enemy_nation: EnemyNation, combat: Combat, res: Resources):
        super().__init__()
        print("Enemy nation attack")
        self.enemy_nation = enemy_nation
        self.combat = combat
        self.res = res
        self.ticks = 1
    
    def tick(self):
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
    """
    Represents an event where a gold mine spawns in the nation.

    Attributes:
        nation (Nation): The nation where the mine spawns.

    Methods:
        tick(): Advance the event by one tick.
    """
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
    """
    Represents an event to update random values in the enemy nation.

    Attributes:
        enemy_nation (EnemyNation): The enemy nation to update.
        res (Resources): The resources of the player's nation.

    Methods:
        tick(): Advance the event by one tick.
    """
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
        