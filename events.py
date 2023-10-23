from models import Nation, Resources, Combat, ResearchAndDevelopment, EnemyNation
from entities import Animal, BuildingFactory, Building, GoldBuilding, HouseBuilding, FoodBuilding, AnimalFactory, animal_types
import numpy as np
import sys

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
            print("There is no gold mines")
        elif (nation.current_busy_population_count 
            + MineGoldEvent.NEEDED_WORKERS >= nation.population_count):
            print("Can not start mine gold event because there is not enough available population")
            self.ticks = 0
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

class CollectRoadGold(Event):

    def __init__(self, nation: Nation, resources: Resources):
        super().__init__()
        self.nation = nation
        self.resource = resources
        self.ticks = nation.roads_count
        self.resources = resources
        self.gold_earned = 0
        if self.nation.roads_count <= 0:
            print("No hay caminos para recolectar")
            self.ticks = 0
    
    def tick(self):
        self.ticks -= 1
        if self.ticks <= 0:
            print("Terminada la recolección de caminos")
            print(f"Oro generado: {self.gold_earned}")
            return
        self.gold_earned += self.nation.road_gold_generation
        self.resources.gold_count += self.nation.road_gold_generation

class BuildRoadEvent(Event):

    def __init__(self, nation: Nation):
        super().__init__()
        self.ticks = 1
        self.nation = nation
        if nation.roads_count + 4 > nation.buildings_count * 4:
            print("You must build more buildings before building more roads")
            self.is_finished = True
            self.ticks = 0
    
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
        if nation.not_worked_space < 0:
            print("There is no space for new buildings")
            self.ticks = 0
        elif (nation.current_busy_population_count +
              OpenSpaceEvent.NEEDED_WORKERS > nation.population_count):
            print("There is not enough population for doing this work")
            self.ticks = 0
        self.nation.current_busy_population_count += OpenSpaceEvent.NEEDED_WORKERS
    
    def tick(self):
        self.ticks -= 1
        if self.ticks > 0:
            return
        self.nation.available_space += 1
        self.nation.current_busy_population_count -= OpenSpaceEvent.NEEDED_WORKERS

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
            print(f"There is no {animal_name} in the nation currently. Animals: {nation.animals}")
            self.ticks = 0
        else:
            if nation.current_busy_population_count + animal.workers_needed() > nation.population_count:
                print("There is not enough population for doing this work")
                self.ticks = 0
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

    def __init__(self, nation: Nation, rd: ResearchAndDevelopment, res: Resources, building_type: str, seed: int):
        super().__init__()
        building = BuildingFactory().create(building_type)
        if nation.current_busy_population_count + building.workers_needed() > nation.population_count:
            print("There is not enough population for doing this work")
            self.ticks = -1
        gold_cost, food_cost = rd.calculate_building_cost(building_type, seed) 
        if food_cost > res.food_count:
            print("There is not enough food for doing this work")
            self.ticks = -1
        elif gold_cost > res.gold_count:
            print("There is not enough gold for doing this work")
            self.ticks = -1
        
        if self.ticks == -1:
            self.ticks = 0
        else:
            res.food_count -= food_cost
            res.gold_count -= gold_cost
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
            self.res.gold_food_buidings.append(self.building)

class ImproveBuilding(Event):

    def __init__(self, rd: ResearchAndDevelopment, nation: Nation, res: Resources, building: Building, seed):
        super().__init__()
        if type(building) is HouseBuilding:
            print("You can't improve houses")
        building.level += 1
        if nation.current_busy_population_count + building.workers_needed() > nation.population_count:
            print("There is not enough population for doing this work")
            self.ticks = -1
            building.level -= 1
        elif building.level > rd.max_building_improvements:
            print("You can not upgrade this building to the next level before changing eras")
            self.ticks = -1
            building.level -= 1
        gold_cost, food_cost = rd.calculate_improvement_cost(building.type, seed) 
        if food_cost > res.food_count:
            print("There is not enough food for doing this work")
            self.ticks = -1
            building.level -= 1
        elif gold_cost > res.gold_count:
            print("There is not enough gold for doing this work")
            self.ticks = -1
            building.level -= 1
        if self.ticks == -1:
            self.ticks = 0
        else:
            res.food_count -= food_cost
            res.gold_count -= gold_cost
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
            print("You don't have troops")
            self.ticks = -1
        elif combat.is_resting:
            print("Your troops are resting")
            self.ticks = -1
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
        self.enemy_nation = enemy_nation
        self.combat = combat
        self.res = res
        self.ticks = 1
    
    def tick(self):
        if self.combat.defense_units_count >= self.enemy_nation.attack_coefficient:
            print("Defend success!")
            self.combat.defense_units_count = np.random.randint(low=1, high=self.combat.defense_units_count - 1)
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