# StateMachine/tram/TramAction.py

class TramAction():
    def __init__(self, action):
        self.action = action
    def __str__(self): return self.action
    def __cmp__(self, other):
        return cmp(self.action, other.action)
    # Necessary when __cmp__ or __eq__ is defined
    # in order to make this class usable as a
    # dictionary key:
    def __hash__(self):
        return hash(self.action)

# Static fields; an enumeration of instances:
TramAction.wait = TramAction("wait")
TramAction.move = TramAction("move")
TramAction.measure = TramAction("measure")
TramAction.upload = TramAction("upload")
TramAction.picture = TramAction("picture")
TramAction.response = ''
TramAction.location = 0
TramAction.measurement_tolerance=10
TramAction.acceleration_sensitivity=500
TramAction.acceleration_tolerance=20
TramAction.accel_result = 0
TramAction.motor_switch = 0
TramAction.battery = 0
TramAction.temperature = 0
TramAction.emergency = 0
TramAction.run = True