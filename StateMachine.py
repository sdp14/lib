# StateMachine/StateMachine.py
# Takes a list of Inputs to move from State to
# State using a template method.

from TramAction import TramAction
from WebSite import WebSite
from TramConnect import TramConnect
import TramConnect
from thread import start_new_thread
import threading
import time
import datetime

global last_command_id # E keeps track of last thing 
global Endflag
Endflag=0
last_command_id = int(WebSite().get_html_data('/articles/last_id/'))

def connect():
    print("Base Station: Trying to connect to tram")

    StateMachine.sock = TramConnect.TramConnect().connect()
    StateMachine.response = ''
    if(StateMachine.sock):
        print('Starting new thread')
        try:
            print '1'
            start_new_thread(TramConnect.TramConnect().make_thread, (StateMachine.sock,StateMachine.response,))
            print '2'
            print(StateMachine.sock)
            print('Sending connection test')
            #print(socket.connInfo[1])
            StateMachine.sock.send('Connection test')
        except Exception ,e:
            print("Thread error: "+ str(e))
            return False

    else:
        print('Failure connecting to tram')
        return False

def get_server_command(self): # E 
    global last_command_id
    next_command_id = int(WebSite().get_html_data('/articles/last_id/')) 
    if(next_command_id>last_command_id): # E check to see if something new has happened 
        last_command_id = next_command_id 
        command = []
        command = str(WebSite().get_html_data('/articles/last/')).lower().split(" ")
        print 'Server:', command # E print the command you got from the website 

        exe_command = map(TramAction, command) # E update state, 

        if("autonomous" not in command[0]): # E if not autonomous, set next command to 
            self.currentState = self.currentState.next(exe_command[0])
            if(len(command)>1):
                self.currentState.run(command)

        return command

    else:
        return ['none', 0]


def update_auto(): # E go to get tram file, open tram moves, take everything and write it to the file and save it locally 
    commands = str(WebSite().get_html_data('/articles/get_tram_file/')) 
    f = open('./lib/TramMoves.txt','w')
    f.write(commands)
    f.close()


def update_acc(server_command): # E give it a command, and it will update the variable 
    if(server_command[0]=="msr_tol"): # E If give msr_tol it will update measurement tolerance, print to screen with new value 
        TramAction.measurement_tolerance=server_command[1]
        print 'updated measurement_tolerance = ',TramAction.measurement_tolerance
    if(server_command[0]=="acc_sen"):
        TramAction.acceleration_sensitivity=server_command[1]
        print 'updated acceleration_sensitivity = ',TramAction.acceleration_sensitivity
    if(server_command[0]=="acc_tol"):
        TramAction.acceleration_tolerance=server_command[1]
        print 'updated acceleration_tolerance = ',TramAction.acceleration_tolerance


class StateMachine(): # E
    def __init__(self, initialState): # E initial state 
        self.currentState = initialState
##        self.currentState.run(["wait",10])

    # Template method:
    def runAll(self, inputs, params): # E will take a list of inputs 
        global last_command_id
        global Endflag
        global AddAday
        c = 0
        jump = 0
        user_disable=0
        interrupt=0
        timeflag=0
        for i in inputs: # E go one-by-one through inputs 
            server_command=get_server_command(self) # E ask website for new command 

            if(TramAction.emergency==1 or not TramAction.run): # E emergency situation has occured, stop moving
                self.currentState = self.currentState.next(TramAction.move) # Move to home and disable (0)
                self.currentState.run(["move",0])
                self.sock.send('StopRpt')
                print('sending StopRpt')
                disable=1
                c+=1# C Need to look at next commoand
                if(':' not in params[c][1]): #C need to go back to position 0 as soon as in shutdown mode. Ignore other commands until next measurement time
                    c-=1
                    c+=1
                    jump=1
                if(':' in params[c][1] or 'end' in params[c][1]):
                    c-=1
                    TramAction.emergency=0
                    print('emergency=0')
                    jump=0
            if("msr_tol" in server_command or "acc_sen" in server_command or "acc_tol" in server_command): # E if told to update a value then you call update acc 
                update_acc(server_command)

            if(server_command[0]=='update_autonomous'): # E run update auto 
                update_auto()
                print("UPDATING")
                interrupt=1

            if(server_command[0]=='shutdown_autonomous'): # E move back to 0 
                print("SHUTTING DOWN")
                self.currentState = self.currentState.next(TramAction.move)
                self.currentState.run(["move",0])
                TramAction.run = False
                disable=0

            if(server_command[0]=='disable_autonomous'): # E disable and keep waiting for a new command 
                user_disable=1 # E waitng to get reenabled after being disabled 
                disable=1

                while(disable==1):
                    server_command=get_server_command(self) # wait for new comamnd 
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

            if(interrupt==1): # E if interrupt is 1 then stop list of actions 
                break

            if(":" in params[c][1]):#C time management section
                while 1:
                    t=datetime.datetime.now()
                    timeinfo1=t.strftime('%d %b %y ')+params[c][1]
                    timeinfo2=t.strftime('%d %b %y %H:%M:%S')
                    print timeinfo1
                    print timeinfo2 #C timeinfo is str        
                    t1=datetime.datetime.strptime(timeinfo1, "%d %b %y %H:%M:%S") # Time set in control.txt  
                    t2=datetime.datetime.strptime(timeinfo2, "%d %b %y %H:%M:%S") #  Present time  
                    print t1
                    print t2
                    print 'timeflag',timeflag
                    print params[c]
                    if (Endflag ==1 ):
                        Endflag=0
                        t1+=datetime.timedelta(days=1) #C Adding 24 hours
                    if (t1<=t2 and timeflag==1): #C Make Measurement
                        print 'Go!'            
                        timeflag=0
                        c+=1 # E increment to use next parameter
                        print(i) # E print command that was given 
                        print(params[c]) # E print parameters recieved 
                        self.currentState = self.currentState.next(i) # E changes state to be the next one 
                        self.currentState.run(params[c]) # E run the next state 
                        c-=1 # C To make i and params[c] sychronized
                        break
                    
                    if (t1>=t2 and timeflag==0): #C If not passing the measurement time, then wait unil next measurement time
                        #connect()#C Connect again
                        Tdiff=t1-t2
                        Tremain=Tdiff.total_seconds()
                        #asfd=threading.thread()
                        #a=asfd.is_alive()
                        print 'wait',Tremain, 'seconds'
                        while Tremain > 0:
                            Tremain=Tremain-1
                            print Tremain
                            time.sleep(1)
                        timeflag=1
                        connect()
                        #a=asdf.is_alive()
                        #print a

                    if (t1<t2 and timeflag==0): #C When measurement meets time stamp, 'c' and 'i' need to be same command
                        c+=1
                        print 'Catching up command in "i"'
                        break 
                    else:
                        print 'Time Setting Error'
            if(":" not in params[c][1] and jump == 0 and Endflag == 0):
                if(i.action != params[c][0]):
                    c+=1
                    print(i) # E print command that was given 
                    print(params[c]) # E print parameters recieved 
                    self.currentState = self.currentState.next(i) # E changes state to be the next one 
                    self.currentState.run(params[c]) # E run the next state 
                    c+=1 # E increment to use next parameter
                else:
                    print(i) # E print command that was given 
                    print(params[c]) # E print parameters recieved 
                    self.currentState = self.currentState.next(i) # E changes state to be the next one 
                    self.currentState.run(params[c]) # E run the next state 
                    c+=1 # E increment to use next parameter
            
            if ("end" in params[c][1]):
                Endflag=1