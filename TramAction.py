# StateMachine/tram/TramAction.py
# E outlines the fields 
class TramAction():
    def __init__(self, action): 
        self.action = action
    def __str__(self): return self.action # E turns to a string 
    def __cmp__(self, other): # E compare function, < > 
        return cmp(self.action, other.action)
    # Necessary when __cmp__ or __eq__ is defined
    # in order to make this class usable as a
    # dictionary key:
    def __hash__(self): # E can put in a dictionary 
        return hash(self.action)

# Static fields; an enumeration of instances: # E variables 
TramAction.wait = TramAction("wait")
TramAction.move = TramAction("move")
TramAction.measure = TramAction("measure")
TramAction.upload = TramAction("upload")
TramAction.picture = TramAction("picture")
TramAction.command = TramAction("command")
TramAction.response = ''
TramAction.location = 0
TramAction.measurement_tolerance=10
TramAction.acceleration_sensitivity=2000 # C Hiher value for worse sensitivity. The original value was 500.
TramAction.acceleration_tolerance=15
TramAction.accel_result = 0
TramAction.motor_switch = 0
TramAction.battery = 0
TramAction.temperature = 0  
TramAction.emergency = 0
TramAction.run = True