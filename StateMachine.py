# StateMachine/StateMachine.py
# Takes a list of Inputs to move from State to
# State using a template method.

from TramAction import TramAction
from WebSite import WebSite

global last_command_id
last_command_id = int(WebSite().get_html_data('/articles/last_id/'))


def get_server_command(self):
    global last_command_id
    next_command_id = int(WebSite().get_html_data('/articles/last_id/'))
    if(next_command_id>last_command_id):
        last_command_id = next_command_id
        command = []
        command = str(WebSite().get_html_data('/articles/last/')).lower().split(" ")
        print 'Server:', command

        exe_command = map(TramAction, command)

        if("autonomous" not in command[0]):
            self.currentState = self.currentState.next(exe_command[0])
            if(len(command)>1):
                self.currentState.run(command)

        return command

    else:
        return ['none', 0]


def update_auto():
    commands = str(WebSite().get_html_data('/articles/get_tram_file/'))
    f = open('./lib/TramMoves.txt','w')
    f.write(commands)
    f.close()


def update_acc(server_command):
    if(server_command[0]=="msr_tol"):
        TramAction.measurement_tolerance=server_command[1]
        print 'updated measurement_tolerance = ',TramAction.measurement_tolerance
    if(server_command[0]=="acc_sen"):
        TramAction.acceleration_sensitivity=server_command[1]
        print 'updated acceleration_sensitivity = ',TramAction.acceleration_sensitivity
    if(server_command[0]=="acc_tol"):
        TramAction.acceleration_tolerance=server_command[1]
        print 'updated acceleration_tolerance = ',TramAction.acceleration_tolerance


class StateMachine():
    def __init__(self, initialState):
        self.currentState = initialState
##        self.currentState.run(["wait",10])

    # Template method:
    def runAll(self, inputs, params):
        global last_command_id
        c = 0
        user_disable=0
        interrupt=0


        for i in inputs:
            server_command=get_server_command(self)

            if(TramAction.emergency==1 or not TramAction.run):
                self.currentState = self.currentState.next(TramAction.move)
                self.currentState.run(["move",0])
                disable=1

            if("msr_tol" in server_command or "acc_sen" in server_command or "acc_tol" in server_command):
                update_acc(server_command)

            if(server_command[0]=='update_autonomous'):
                update_auto()
                print("UPDATING")
                interrupt=1

            if(server_command[0]=='shutdown_autonomous'):
                print("SHUTTING DOWN")
                self.currentState = self.currentState.next(TramAction.move)
                self.currentState.run(["move",0])
                TramAction.run = False
                disable=0

            if(server_command[0]=='disable_autonomous'):
                user_disable=1
                disable=1

                while(disable==1):
                    server_command=get_server_command(self)
                    if(server_command[0]=='enable_autonomous'):
                        print("ENABLING")
                        disable=0
                        user_disable=0
                    if(server_command[0]=='update_autonomous'):
                        print("UPDATING")
                        update_auto()
                        interrupt=1
                    if(server_command[0]=='shutdown_autonomous'):
                        print("SHUTTING DOWN")
                        TramAction.run = False
                        disable=0
                        user_disable=0
                    if("msr_tol" in server_command or "acc_sen" in server_command or "acc_tol" in server_command):
                        update_acc(server_command)
                    if(user_disable==0 and TramAction.emergency==0):
                        disable=0

            if(interrupt==1):
                break

            print(i)
            print(params[c])
            self.currentState = self.currentState.next(i)
            self.currentState.run(params[c])
            c+=1