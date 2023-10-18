animal_types = ["Bunny", "Fox", "Deer", "Bear"]

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