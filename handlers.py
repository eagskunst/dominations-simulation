from events import Event, RestFromAttackEvent
from models import Nation

class EventHandler():

    def __init__(self, nation: Nation, current_events: list[Event] = []):
        self.nation = nation
        self.current_events = current_events
        self.attack_running = False
        self.collecting_gold = False
    
    def advance_time(self):
        removable_events = []
        self.nation.advance_time()
        for event in self.current_events:
            event.tick()
            if event.is_finished():
                removable_events.append(event)
        for event in removable_events:
            self.current_events.remove(event)
            if type(event).__name__ == 'AttackEnemiesEvent':
                self.attack_running = False
                self.add_event(RestFromAttackEvent(event.combat))
            
    
    def add_event(self, event: Event):
        self.current_events.append(event)
        self.attack_running = type(event).__name__ == 'AttackEnemiesEvent'