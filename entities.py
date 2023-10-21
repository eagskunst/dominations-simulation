animal_types = ["Bunny", "Fox", "Deer", "Bear"]
building_types = ["Gold", "Food", "House", "Attack", "Defense"]

class Animal:
    
    def name() -> str:
        pass

    def hunt_time() -> int:
        pass

    def food_given() -> int:
        pass

    def workers_needed() -> int:
        pass

class Bunny(Animal):

    def name() -> str:
        return "Bunny"
    
    def hunt_time() -> int:
        return 2
    
    def food_given() -> int:
        return 4
    
    def workers_needed() -> int:
        return 1

class Fox(Animal):
    
    def name() -> str:
        return "Fox"
    
    def hunt_time() -> int:
        return 3
    
    def food_given() -> int:
        return 10
    
    def workers_needed() -> int:
        return 2

class Deer(Animal):
    
    def name() -> str:
        return "Deer"
    
    def hunt_time() -> int:
        return 5
    
    def food_given() -> int:
        return 30
    
    def workers_needed() -> int:
        return 3

class Bear(Animal):

    def name() -> str:
        return "Bear"
    
    def hunt_time() -> int:
        return 8
    
    def food_given() -> int:
        return 70
    
    def workers_needed() -> int:
        return 4

class AnimalFactory:

    def create(name: str) -> Animal:
        if name == "Bunny":
            return Bunny()
        elif name == "Fox":
            return Fox()
        elif name == "Deer":
            return Deer()
        elif name == "Bear":
            return Bear()
        else:
            raise RuntimeError()

class Building:

    def __init__(self, type: str, level: int=1) -> None:
        self.type = type
        self.level = level
        self.improving = False
        pass

    def workers_needed() -> int:
        pass

class GoldBuilding(Building):

    def workers_needed(self) -> int:
        return self.level * 2
    
class FoodBuilding(Building):

    def workers_needed(self) -> int:
        return self.level * 3

class HouseBuilding(Building):

    def workers_needed(self) -> int:
        return self.level
    
class BuildingFactory:

    def create(building_type: str) -> Building:
        if building_type == "Gold":
            return GoldBuilding(building_type)
        elif building_type == "Food":
            return FoodBuilding(building_type)
        elif building_type == "House":
            return HouseBuilding(building_type)