# StateMachine/State.py
# A State has an operation, and can be moved
# into the next State given an Input:

class State: # E can run or next 
    def run(self): # E safety feature 
        assert 0, "run not implemented"
    def next(self, input): # E will fail assertion 
        assert 0, "next not implemented"

# E will override 