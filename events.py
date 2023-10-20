from models import Nation, Resources, Combat, ResearchAndDevelopment, EnemyNation
from entities import Animal, BuildingFactory, Building, GoldBuilding, HouseBuilding, FoodBuilding

class Event:

    def __init__(self) -> None:
        self.thicks = 0

    def thick(self):
        pass

    def is_finished(self) -> bool:
        return self.thicks <= 0

class MineGoldEvent(Event):

    GOLD_PER_MINE = 300
    NEEDED_WORKERS = 2

    def __init__(self, nation: Nation, resources: Resources):
        #todo verificar si hay minas
        super().__init__()
        self.nation = nation
        self.thicks = nation.mine_time
        self.resources = resources
        if (nation.current_busy_population_count 
            + MineGoldEvent.NEEDED_WORKERS >= nation.population_count):
            print("Can not start mine gold event because there is not enough available population")
            self.thicks = 0
        nation.current_busy_population_count += MineGoldEvent.NEEDED_WORKERS
    
    def thick(self):
        self.thicks -= 1
        if self.thicks > 0:
            return
        print("Gold mined. Disposing resources.")
        self.nation.current_busy_population_count -= MineGoldEvent.NEEDED_WORKERS
        self.resources.gold_count += MineGoldEvent.GOLD_PER_MINE
        self.finished = True

class CollectRoadGold(Event):

    def __init__(self, nation: Nation, resources: Resources):
        super().__init__()
        self.nation = nation
        self.resource = resources
        self.thicks = nation.roads_count
        self.resources = resources
        self.gold_earned = 0
        if self.nation.roads_count <= 0:
            print("No hay caminos para recolectar")
            self.thicks = 0
    
    def thick(self):
        self.thicks -= 1
        if self.thicks <= 0:
            print("Terminada la recolección de caminos")
            print(f"Oro generado: {self.gold_earned}")
            return
        self.gold_earned += self.nation.road_gold_generation
        self.resources.gold_count += self.nation.road_gold_generation

class BuildRoadEvent(Event):

    def __init__(self, nation: Nation):
        super().__init__()
        self.thicks = 1
        self.nation = nation
        if nation.roads_count + 4 > nation.buildings_count * 4:
            print("You must build more buildings before building more roads")
            self.is_finished = True
            self.thicks = 0
    
    def thick(self):
        self.thicks -= 1
        if self.thicks > 0:
            return
        self.nation.roads_count += 4
        print("Roads built")

class OpenSpaceEvent(Event):

    SPACE_THICKS = 5
    NEEDED_WORKERS = 3

    def __init__(self, nation: Nation):
        super().__init__()
        self.nation = nation
        self.thicks = OpenSpaceEvent.SPACE_THICKS
        if nation.not_worked_space < 0:
            print("There is no space for new buildings")
            self.thicks = 0
        elif (nation.current_busy_population_count +
              OpenSpaceEvent.NEEDED_WORKERS > nation.population_count):
            print("There is not enough population for doing this work")
            self.thicks = 0
        self.nation.current_busy_population_count += OpenSpaceEvent.NEEDED_WORKERS
    
    def thick(self):
        self.thicks -= 1
        if self.thicks > 0:
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
            self.thicks = 0
        else:
            if nation.current_busy_population_count + animal.workers_needed() > nation.population_count:
                print("There is not enough population for doing this work")
                self.thicks = 0
            else:
                self.thicks = animal.hunt_time()
                self.animal = animal
                self.nation.current_busy_population_count += self.animal.workers_needed()
                self.nation.animals.remove(animal)
    
    def thick(self):
        self.thicks -= 1
        if self.thicks > 0:
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
        building = BuildingFactory().create(building_type)
        if nation.current_busy_population_count + building.workers_needed() > nation.population_count:
            print("There is not enough population for doing this work")
            self.thicks = -1
        gold_cost, food_cost = rd.calculate_building_cost(building_type, seed) 
        if food_cost > res.food_count:
            print("There is not enough food for doing this work")
            self.thicks = -1
        elif gold_cost > res.gold_count:
            print("There is not enough gold for doing this work")
            self.thicks = -1
        
        if self.thicks == -1:
            self.thicks = 0
        else:
            res.food_count -= food_cost
            res.gold_count -= gold_cost
            nation.current_busy_population_count += building.workers_needed()
            self.thicks = rd.bulding_build_time
            self.nation = nation
            self.res = res
            self.building = building
    
    def thick(self):
        self.thicks -= 1
        if self.thicks > 0:
            return
        self.nation.current_busy_population_count -= self.building.workers_needed()
        if type(self.building) is HouseBuilding:
            self.nation.houses_count += 1
            self.nation.population_count += 2
        elif type(self.building) is FoodBuilding or type(self.building) is GoldBuilding:
            self.res.gold_food_buidings.append(self.building)

class ImproveBuilding(Event):

    def __init__(self, rd: ResearchAndDevelopment, nation: Nation, res: Resources, building: Building, seed):
        if type(building) is HouseBuilding:
            print("You can't improve houses")
        building.level += 1
        if nation.current_busy_population_count + building.workers_needed() > nation.population_count:
            print("There is not enough population for doing this work")
            self.thicks = -1
            building.level -= 1
        elif building.level > rd.max_building_improvements:
            print("You can not upgrade this building to the next level before changing eras")
            self.thicks = -1
            building.level -= 1
        gold_cost, food_cost = rd.calculate_improvement_cost(building.type, seed) 
        if food_cost > res.food_count:
            print("There is not enough food for doing this work")
            self.thicks = -1
            building.level -= 1
        elif gold_cost > res.gold_count:
            print("There is not enough gold for doing this work")
            self.thicks = -1
            building.level -= 1
        if self.thicks == -1:
            self.thicks = 0
        else:
            res.food_count -= food_cost
            res.gold_count -= gold_cost
            nation.current_busy_population_count += building.workers_needed()
            self.thicks = rd.building_improvement_time
            self.nation = nation
            self.res = res
            self.building = building
            building.improving = True
    
    def thick(self):
        self.thicks -= 1
        if self.thicks > 0:
            return
        self.nation.current_busy_population_count -= self.building.workers_needed()
        self.building.improving = False
