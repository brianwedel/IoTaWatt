class Event:
    # Event types
    TIME = 0
    POWER = 1

    def events():
        return [TIME, POWER]

class TimeTickEvent(Event):
    def __init__(self, source, timestamp):
        self.source = source
        self.value = timestamp
        self.type = Event.TIME

class PowerEvent(Event):
    def __init__(self, source, power_value_watts):
        self.source = source
        self.value = power_value_watts
        self.type = Event.POWER

class EventCallback:
    def__init__(self, event_type, dest, callback):
        self.event_type = event_type
        self.dest = dest
        self.callback = callback

class Sim:
    def __init__(self):
        # list of nodes registered with simulator
        self.nodes = []

        # dictionary of event_type -> list of callbacks
        self.event_callbacks = {}
        for e in Event.events()
            self.event_callbacks[e] = []

    def add_event_callback(self, event_type, dest_node, callback):
       self.event_callbacks[event_Type].append(EventCallback(event_type, dest_node, callback))

    def add_node(self, node):
        self.nodes.append(node)
        node.register(self)

    def generate_event(self, event):
        self.pending_events.append(event)

    def _run_events(self):
        for cb in self.event_callbacks[event.type]:
            cb.callback(event)

    def run(self, duration_sec):
        for t in range(0, duration_sec):
            # Simulator generated time tick
            time_tick = TimeTickEvent(self, t)
            self.generate_event(time_tick)

            # Service all other generated events (from other nodes)
            

class HouseLoad:
    def register(self, sim):
        self.sim = sim
        self.sim.add_event_callback(Event.TIME, self, self.time_tick_callback)

    def time_tick_callback(self, event):
        self.sim.generate_event(EventPower(self, 1000.0))

if __name__ == "__main__":
    house = HouseLoad()
    sim = Sim()
    sim.add_node(house)

    sim.run(100.0)
