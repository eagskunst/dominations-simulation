from handlers import EventHandler
from models import Nation, Resources

def main():
    nation = Nation(
        name="Wiwaland",
        current_time=0,
        available_space=10,
        not_worked_space=10,
        used_space=0,
        animal_spawn_rate=0.4,
        gold_mine_spawn_rate=0.4,
        roads_count=10,
        population_count=10,
        road_gold_generation=0.4,
        hunt_time=5,
        mine_time=2,
        current_busy_population_count=0
    )
    resources = Resources(
        food_count=10,
        gold_count=100,
        gold_buildings_count=2,
        food_buildings_count=2
    )
    handler = EventHandler(nation)
    nation.mine_gold(handler, resources)
    while True:
        print("new thick")
        handler.advance_time()
        input()

if __name__ == "__main__":
    main()