from events import Event
from models import Nation

class EventHandler():

    def __init__(self, nation: Nation, current_events: list[Event] = []):
        self.nation = nation
        self.current_events = current_events
    
    def advance_time(self):
        removable_events = []
        self.nation.advance_time()
        for event in self.current_events:
            event.thick()
            if event.is_finished():
                removable_events.append(event)
        for event in removable_events:
            self.current_events.remove(event)
    
    def add_event(self, event: Event):
        self.current_events.append(event)