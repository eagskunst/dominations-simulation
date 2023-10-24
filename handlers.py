from events import Event, RestFromAttackEvent
from models import Nation

class EventHandler():
    """
    Manages and processes events for a nation.
    
    Attributes:
        nation (Nation): The nation instance this handler is managing events for.
        current_events (list[Event]): The current active events for the nation.
        attack_running (bool): A flag to determine if an attack event is running.
    """
    def __init__(self, nation: Nation, current_events: list[Event] = []):
        self.nation = nation
        self.current_events = current_events
        self.attack_running = False
    
    def advance_time(self):
        """
        Progresses the simulation by one time unit, processing all ongoing events
        and updating the nation's state accordingly.
        """
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
        """
        Adds a new event to the current events list for the nation.
        
        Args:
            event (Event): The event instance to be added.
        """
        self.current_events.append(event)
        self.attack_running = type(event).__name__ == 'AttackEnemiesEvent'