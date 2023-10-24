animal_types = ["Bunny", "Fox", "Deer", "Bear"]
building_types = ["Gold", "Food", "House", "Attack", "Defense"]

class Animal:
    """ 
    Abstract class for animals. Each animal type should provide implementations 
    for these methods.
    """
    def name() -> str:
        pass

    def hunt_time() -> int:
        pass

    def food_given() -> int:
        pass

    def workers_needed() -> int:
        pass

class Bunny(Animal):
    """ Specific class for a Bunny type animal with its characteristics. """
    def name() -> str:
        return "Bunny"
    
    def hunt_time() -> int:
        return 2
    
    def food_given() -> int:
        return 4
    
    def workers_needed() -> int:
        return 1

class Fox(Animal):
    """ Specific class for a Fox type animal with its characteristics. """
    def name() -> str:
        return "Fox"
    
    def hunt_time() -> int:
        return 3
    
    def food_given() -> int:
        return 10
    
    def workers_needed() -> int:
        return 2

class Deer(Animal):
    """ Specific class for a Deer type animal with its characteristics. """
    def name() -> str:
        return "Deer"
    
    def hunt_time() -> int:
        return 5
    
    def food_given() -> int:
        return 30
    
    def workers_needed() -> int:
        return 3

class Bear(Animal):
    """ Specific class for a Bear type animal with its characteristics. """
    def name() -> str:
        return "Bear"
    
    def hunt_time() -> int:
        return 8
    
    def food_given() -> int:
        return 70
    
    def workers_needed() -> int:
        return 4

class AnimalFactory:
    """
    Factory class for creating Animal instances based on their names.
    
    Raises:
        RuntimeError: When trying to create an animal type that isn't supported.
    """
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
    """ 
    Base class for buildings with common attributes and methods. Specific building 
    types will inherit from this.
    """
    def __init__(self, type: str, level: int=1) -> None:
        self.type = type
        self.level = level
        self.improving = False
        pass

    def workers_needed() -> int:
        pass

class GoldBuilding(Building):
    """ Specific class for a Gold-type building with its characteristics. """
    def workers_needed(self) -> int:
        return self.level * 2
    
class FoodBuilding(Building):
    """ Specific class for a Food-type building with its characteristics. """
    def workers_needed(self) -> int:
        return self.level * 3

class HouseBuilding(Building):
    """ Specific class for a House-type building with its characteristics. """
    def workers_needed(self) -> int:
        return self.level
    
class BuildingFactory:
    """
    Factory class for creating Building instances based on their types.
    """
    def create(building_type: str) -> Building:
        if building_type == "Gold":
            return GoldBuilding(building_type)
        elif building_type == "Food":
            return FoodBuilding(building_type)
        elif building_type == "House":
            return HouseBuilding(building_type)