from models import Nation, Resources, Combat, ResearchAndDevelopment, EnemyNation

class Event:
    def thick(self):
        pass

    def is_finished(self) -> bool:
        pass

class MineGoldEvent(Event):

    GOLD_PER_MINE = 300

    def __init__(self, nation: Nation, resources: Resources):
        self.nation = nation
        self.finished = False
        self.thicks = nation.mine_time
        self.resources = resources
        if nation.current_busy_population_count + 2 >= nation.population_count:
            print("Can not start mine gold event because there is not enough available population")
            self.finished = True
        nation.current_busy_population_count += 2
    
    def thick(self):
        self.thicks -= 1
        if self.thicks >= 0:
            return
        print("Gold mined. Disposing resources.")
        self.nation.current_busy_population_count -= 2
        self.resources.gold_count += MineGoldEvent.GOLD_PER_MINE
        self.finished = True

    def is_finished(self) -> bool:
        return self.finished
