#-------------------------------------------------------------------------------
# Name:        TramControl
# Purpose:
#
# Author:      NoahP
#
# Created:     15/01/2014
# Copyright:   (c) NP 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# StateMachine/TramControl.py
# Autonomous and directed control of tram operation
import string, sys, time, serial
import minimalmodbus
import pdb
sys.path += [r'.\lib']
from ctypes import *
from thread import *
from socket import *
from datetime import datetime

import cv2

from State import State
from StateMachine import StateMachine
from TramAction import TramAction
from TramConnect import TramConnect
from WebSite import WebSite
from ParseData import ParseData
#from Tracking import Tracking



class StateT(State): # E Takes info from TramAction.py. If the input is self.transitions report results 
# E Prints accel and if it is an emergency or not. 
    def __init__(self):
        self.transitions = None
    def next(self, input):
        if(input in self.transitions):
            print "Tramaccel info is: ", TramAction.accel_result # E TramAction.accel_result = 0
            print "Emergency info is: ", TramAction.emergency # E TramAction.emergency = 0

            return self.transitions[input]
        else:
            print ("Input %s not supported for current state" % input)
            return self
##            raise RuntimeError("Input %s not supported for current state" % input)

class Command(StateT)
    def run(self, param):
        if(param[0]!='move'):
            return
        if(param[0]=='returnhome'):
            
    def next(self, input):
        # Supported transition initialization:
        if not self.transitions:
            self.transitions = {
                TramAction.wait : TramControl.wait,
                TramAction.move : TramControl.move,
                TramAction.measure : TramControl.measure,
                TramAction.upload : TramControl.upload,
                TramAction.picture : TramControl.picture
            }
        return StateT.next(self, input)

class Wait(StateT): # E takes in a number of seconds wait 

    def run(self, param):
        if(param[0]!='wait' or len(param)<2):
            return
        duration = int(param[1])
        print("Tram: Waiting %i Second(s)" % duration) # E prints number of seconds waiting 
        time.sleep(duration) # B time.sleep(duration) suspends the program (on only the control computer) for the length 'duration' in seconds
        WebSite().tram_info(int(TramControl.position/100), param[0], 'success', int(TramControl.position/50), TramAction.accel_result) # Updates website 

    def next(self, input):
        # Supported transition initialization:
        if not self.transitions:
            self.transitions = {
                TramAction.wait : TramControl.wait,
                TramAction.move : TramControl.move,
                TramAction.measure : TramControl.measure,
                TramAction.upload : TramControl.upload,
                TramAction.picture : TramControl.picture
            }
        return StateT.next(self, input)


class Move(StateT): # E handles going forawrd and backward and makes sure you don't go too far 

    def run(self, param):
        if(param[0]!='move'):
            return
        if(len(param)<2):
            print "tram direction ",TramControl.direction
            if(TramControl.direction>0):
                motormove = 9 - TramControl.cable #E TramControl.cable initially set to 0 
                dist = 100 # E This will be changed if stopping distance need be changed 
            else:
                motormove = 8 + TramControl.cable
                dist = -100
            if(TramControl.direction>TramControl.minrange and TramControl.position+dist > TramControl.maxrange):
                TramControl.direction=-1
            if(TramControl.direction<TramControl.minrange and TramControl.position+dist < TramControl.minrange):
                TramControl.direction=1
            if(dist==100): # E prevents tram from moving too far away 
                if(TramControl.position+dist>TramControl.maxrange):
                    print("Move exceeds cable length!")
                    return

            if(dist==-100): # E prevents tram from getting too close 
                if(TramControl.position+dist<TramControl.minrange):
                    print("Move exceeds cable length!")
                    return

            print("Tram: Moving %i centimeter(s) " % dist + "to position %i" % (TramControl.position+dist))
            if(motor_move(motormove)):
                TramControl.position+=dist

##                print "Tracking result: ", TramAction.location 
                WebSite().tram_info(int(TramControl.position/100), 'move', 'success', int(TramControl.position/50), TramAction.accel_result)
            else:
                WebSite().tram_info(int(TramControl.position/100), 'move', 'failure', int(TramControl.position/50), TramAction.accel_result)

            return

        dist = int(param[1])

        if(dist>TramControl.maxrange or dist<TramControl.minrange): # E Prevents movement out of the length range min and max 
            print("Move exceeds cable length!")
            return

        while(TramControl.position!=dist): # E moves motor (how are these distances working?)
            if (dist-TramControl.position>0 and dist-TramControl.position<=5):
                motormove=11 - TramControl.cable
                location=1
            if (dist-TramControl.position>5 and dist-TramControl.position<=50):
                motormove=13 - TramControl.cable
                location=10
            if (dist-TramControl.position>50):
                motormove=9 - TramControl.cable
                location=100
            if (dist-TramControl.position<0 and dist-TramControl.position>=-5):
                motormove=10 + TramControl.cable
                location=-1
            if (dist-TramControl.position<-5 and dist-TramControl.position>-50):
                motormove=12 + TramControl.cable
                location=-10
            if (dist-TramControl.position<=-50):
                motormove=8 + TramControl.cable
                location=-100
            print("Tram: Moving %i centimeter(s) " % location + "to position %i" % (TramControl.position+location)) # E Prints how far moving and where tram will end up
            if(motor_move(motormove)): # E Prints whether the correct distance was moved # E Actually do the movment. before is just calculates
                TramControl.position+=location # E 136 - 139 updates the website 
                WebSite().tram_info(int(TramControl.position/100), 'move', 'success', int(TramControl.position/50), TramAction.accel_result)
            else:
                WebSite().tram_info(int(TramControl.position/100), 'move', 'failure', int(TramControl.position/50), TramAction.accel_result)

##                while (TramControl.position%100==0 and TramAction.location!=0):
##                    if(TramAction.location==2):
##                        break
##                    if(TramAction.location==1):
##                        if(not motor_move(10+motormove%2)):
##                            break
##                    if(TramAction.location==3):
##                        if(not motor_move(11-motormove%2)):
##                            break

##                print "Tracking result: ", TramAction.location

    def next(self, input):
        # Supported transition initialization:
        if not self.transitions:
            self.transitions = {
                TramAction.wait : TramControl.wait,
                TramAction.move : TramControl.move,
                TramAction.measure : TramControl.measure,
                TramAction.upload : TramControl.upload,
                TramAction.picture : TramControl.picture
            }
        return StateT.next(self, input)


class Measure(StateT):  # E Ends up calling the FTP stuff, takes file and copies to our local space 

    def run(self, param):
        ## param 1 = take datalogger measurements
        ## param 2 = take ten pictures
        ## param 3 = record video
        ## param 4 = streaming vid on
        ## param 5 = streaming vid off
        ## param 6 = measurement tolerance 10
        ## param 7 = acceleration sensitivity 180
        ## param 8 = acceleration tolerance 20
        param.extend([TramAction.measurement_tolerance])
        param.extend([TramAction.acceleration_sensitivity])
        param.extend([TramAction.acceleration_tolerance])

        if(param[0]!='measure' or len(param)<6):
            return
        if(int(param[4]) or int(param[5])):
            param[0]='videoStream'

##        if(TramAction.emergency==1):
##            param = ['wait',0,0,0,0,0,TramAction.measurement_tolerance,TramAction.acceleration_sensitivity,TramAction.acceleration_tolerance]
##            TramConnect().send(TramControl.sock, param)
##            TramAction.emergency=0

        try: # E try and except are for if an error occurs 
            print('Sending connection test')
            TramControl.sock.send('Connection test')
            print repr(TramAction.response)
        except Exception, e: # E do we need to add something for when the connection is dropped??
            #  S whatever you need to do when the connection is dropped
            print('Attempting reconnect to server')
            connect()

        if(TramControl.sock): # E How information is sent over the connection (.sock)
            print("Tram: Sending Wait.") # E Prints message
            reset = ['wait',0,0,0,0,0,TramAction.measurement_tolerance,TramAction.acceleration_sensitivity,TramAction.acceleration_tolerance] # E makes what to send 
            TramConnect().send(TramControl.sock, reset) # E sends over connection
            time.sleep(1) # E wait time 

            print("Tram: Taking Measurements.")
            TramConnect().send(TramControl.sock, param) # E measurement taken 

            time.sleep(2)
            if(param[1] or param[2] or param[3]):
                print "Tram: Downloading Data." # E once measurement is done 
                TramConnect().FTP(param) # E download onto local  
                ParseData().append_data()
    ##            print("Tram: Uploading Results.")
    ##            ParseData().upload('/data/json_upload/')
    ##        if(param[2]=='1'):
    ##            print("Tram: Downloading Pictures.")
    ##            TramConnect().FTP(2)
    ##            print("Tram: Uploading Results.")
    ##            image_upload(r'.\pics\picture')

    ##        if(param[3]=='1'):
    ##            print("Tram: Downloading Video.")
    ##            TramConnect().FTP(3)
    ##            print("Tram: Uploading Results.")
    ##            image_upload(r'.\pics\picture')

        WebSite().tram_info(int(TramControl.position/100), param[0], 'success', int(TramControl.position/50), TramAction.accel_result) # E Copy paste to update website 

    def next(self, input):
        # Supported transition initialization:
        if not self.transitions:
            self.transitions = {
                TramAction.wait : TramControl.wait,
                TramAction.move : TramControl.move,
                TramAction.measure : TramControl.measure,
                TramAction.upload : TramControl.upload,
                TramAction.picture : TramControl.picture
            }
        return StateT.next(self, input)


class Upload(StateT): # E If param one, call this upload function etc... 

    def run(self, param):
        if(param[0]!='upload'): # if the param isn't upload then just return 
            return

        recs = {}
        for lines in open(r'.\lib\imagerecord.txt').readlines():
            cur_line = lines.split(" ")
            recs[cur_line[0]]=int(cur_line[1])

        if(param[1]=='1'):
            print("Base status: Uploading Data...")
            TramControl.datalogger = ParseData().parse_data()
            WebSite().upload_website(TramControl.datalogger, '/data/json_upload/', 1)

        if(param[1]=='2'):

            print("Base status: Uploading Excel...")
            ParseData().make_excel_file()

            WebSite().upload_website('Excel', '/articles/file_upload/', 2)

        if(param[1]=='3'):
            if(recs['trampics']>0):
                print("Base status: Uploading Tram Picture...")
                WebSite().upload_website(r'.\tram_pictures\trampic{:>05}.ppm'.format(recs['trampics']-1), '/articles/file_upload/', 3)
            else:
                return False

        if(param[1]=='4'):
            if(recs['basepics']>0):
                print("Base status: Uploading Base Picture...")
                WebSite().upload_website(r'.\base_pictures\basepic{:>05}.jpg'.format(recs['basepics']-1), '/articles/file_upload/', 3)
            else:
                return False

        if(param[1]=='5'):
            if(recs['vids']>0):
                print("Base status: Uploading Tram Video...")
                WebSite().upload_website(r'.\tram_videos\tramvid{:>05}.jpg'.format(recs['vids']-1), '/articles/file_upload/', 4)
            else:
                return False

        WebSite().tram_info(int(TramControl.position/100), param[0], 'success', int(TramControl.position/50), TramAction.accel_result)

    def next(self, input):
        # Supported transition initialization:
        if not self.transitions:
            self.transitions = {
                TramAction.wait : TramControl.wait,
                TramAction.move : TramControl.move,
                TramAction.measure : TramControl.measure,
                TramAction.upload : TramControl.upload,
                TramAction.picture : TramControl.picture
            }
        return StateT.next(self, input)


class Picture(StateT): # E takes a picture. Possibily need an error catch # E calls take picture function then 307 updates website 

    def run(self, param):
        if(param[0]!='picture'):
            return
        print("Base Station: Taking Picture")
        take_picture()
        WebSite().tram_info(int(TramControl.position/100), param[0], 'success', int(TramControl.position/50), TramAction.accel_result)

    def next(self, input): # E make sure you go to one of these commands 
        # Supported transition initialization:
        if not self.transitions:
            self.transitions = {
                TramAction.wait : TramControl.wait,
                TramAction.move : TramControl.move,
                TramAction.measure : TramControl.measure,
                TramAction.upload : TramControl.upload,
                TramAction.picture : TramControl.picture
            }
        return StateT.next(self, input)


class TramControl(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, TramControl.wait)


def main():
    pass


def motor_move(pos): # E move the motor to position you are looking for 

    try:
        instrument = minimalmodbus.Instrument('COM6', 1) # E setting all the values 
        instrument.serial.port = 'COM6'         # this is the serial port name
        instrument.serial.baudrate = 9600   # Baud # E (symbols per second)baudbaud
        instrument.serial.bitsize = 8 
        instrument.serial.parity   = serial.PARITY_EVEN
        instrument.serial.stopbits = 1 # E Used to indicate the end of data transmission
        instrument.serial.timeout  = 0.1   # seconds
        instrument.address = 1     # this is the slave address number

        docking = False # E see if you're docking or not 
        if((pos==8+TramControl.cable and TramControl.position<=100) or (pos==10+TramControl.cable and TramControl.position<=1) or (pos==12+TramControl.cable and TramControl.position<=10)):
            docking = True

        instrument.write_register(385, 0) # E writing over the serial 
        instrument.write_register(385, 1)
        instrument.write_register(125, 0)
        instrument.write_register(125, pos) # E telling where you want to go
        val = int(instrument.read_register(127)) # E in value 
        TramConnect().timeout(0) 
        while ((val & 0x4000) == 0): # E checking to see if bit is set. While it is not, message will be sent to update it 
            if (TramAction.location != 0 and (pos==8 or pos==9)):
                if(TramConnect().timeout(2)):
                    instrument.write_register(125, 0)
                    instrument.write_register(125, 32)
                    print 'Tracking triggered - motor returned: ', instrument.read_register(127) # E camera tracking, if it sees something 
            if(TramControl.sock):
                if (TramAction.motor_switch==5 and docking):
                    instrument.write_register(125, 0)
                    instrument.write_register(125, 32)
                    print 'Switch triggered - motor returned: ', instrument.read_register(127) # E If you bump into something? 
            if (val != int(instrument.read_register(127))): # E val is what it told you last time, if what you are reading now is not equal, then set val to new reading 
                val = int(instrument.read_register(127))
                print 'motor value returned: ', hex(val) # E if the motor is at a new postion, print what the value is. #  This prints new reading

        TramAction.location = 0  # E following code removed because of the use of the camera 
##        if(TramControl.sock): # E For use of backing tram slowly into station 
##            TramConnect().timeout(0)
##            if (TramAction.motor_switch!=5 and docking):
##                time.sleep(5)
##                while(TramAction.motor_switch!=5):
##                    instrument.write_register(125, 0)
##                    instrument.write_register(125, 10+TramControl.cable)
##                    time.sleep(5)
##                    if(TramConnect().timeout(30)):
##                        return False
##
        return True 

##        ser = serial.Serial(
##            port='COM6',
##            baudrate=9600,
##            timeout=100,
##            parity=serial.PARITY_EVEN,
##            stopbits=serial.STOPBITS_ONE,
##            bytesize=serial.EIGHTBITS)
##
##        ser.write("\x01\x06\x00\x7d\x00\x00\x19\xd2")
##        time.sleep(1)
##        if(pos==8):
##            ser.write("\x01\x06\x00\x7d\x00\x08\x18\x14")
##        if(pos==9):
##            ser.write("\x01\x06\x00\x7d\0x00\x09\xd9\xd4")
##        if(pos==10):
##            ser.write("\x01\x06\x00\x7d\x00\x0a\x99\xd5")
##        if(pos==11):
##            ser.write("\x01\x06\x00\x7d\x00\x0b\x58\x15")
##        if(pos==12):
##            ser.write("\x01\x06\x00\x7d\x00\x0c\x19\xd7")
##        if(pos==13):
##            ser.write("\x01\x06\x00\x7d\x00\x0d\xd8\x17")
##        s = ser.read(10)
##        print repr(s)
##        ser.close()             # close port
##        return True

    except Exception ,e:
        print("Serial communication error: "+ str(e))
        return False


def take_picture(): 
    camcapture = cv.CaptureFromCAM(0) # E uses cv to take a pic from webcam 
    if(~camcapture.isOpened()): # E if it can't take a picture, return false 
        return False

    recs = {} 
    for lines in open(r'.\lib\imagerecord.txt').readlines(): # E 421-423 goes through record of pictures 
        cur_line = lines.split(" ")
        recs[cur_line[0]]=int(cur_line[1])

    img = cv.QueryFrame(camcapture) # E 425-427 save pic to end of record 
    cv.SaveImage(r'.\base_pictures\pic{:>05}.jpg'.format(recs['basepics']), img) 
    recs['basepics']=recs['basepics']+1

    f = open(r'.\lib\imagerecord.txt','w') # E save record with new picture inside 
    for items in recs:
        f.write(str(items)+" "+str(recs[items])+'\n')
    f.close()


def connect(): # E Call all connect functions 
    print("Base Station: Trying to connect to tram")

    TramControl.sock = TramConnect().connect()
    if(TramControl.sock): # E checks connection 
        print('Starting new thread')
        try: 
            start_new_thread(TramConnect().make_thread, (TramControl.sock,TramControl.response,)) # E makes running in background that waits for data (earlier)
            print(TramControl.sock)
            print('Sending connection test') # E sends little message 
            TramControl.sock.send('Connection test')
        except Exception ,e:
            print("Thread error: "+ str(e))
            return False

    else: # E if you fail to set up socket 
        print('Failure connecting to tram')
        return False


# def tracking(): # E Does camera, runs the tracking function 
#     print("Base Station: Starting tracking")
#     try:
#         t=Tracking()
#         if(t):
#             start_new_thread(t.tracking,())
#     except Exception ,e:
#         print("Thread error: "+ str(e))
#         return False



if __name__ == '__main__': # E main function, run your code. sets up states 

    main()
    ##LabVIEWCode = cdll.LoadLibrary(r'.\lib\SharedLib.dll')
    # Static variable initialization:
    TramControl.wait = Wait()
    TramControl.move = Move()
    TramControl.measure = Measure()
    TramControl.picture = Picture()
    TramControl.upload = Upload()
    TramControl.response = ''
    TramControl.position=0 # E defines starting position as distance from base station
    TramControl.direction=1 
    TramControl.maxrange=500 # E allowable length of travel in cm. Never above distance in cm of length of cable - x
    TramControl.minrange=0 # E closest distance allowed to base station
    TramControl.datalogger={} 
    TramControl.track_pos=0
    TramControl.cable=0 # E cable orientation. if over tram = 0, if under tram = 1. 

##    TramConnect().timeout(0)
##    while 1:
##        if(TramConnect().timeout(30)):
##            break

#    ParseData().append_data()
#    sys.exit(0)

    # tracking() # E Calls all the tracking, sets up camera 
    connect() # E Calsl connect, thing runnign in background to recieve data, runs connection test 


    while(TramAction.run): # E assuming the other two have worked, it continues on to this main 

##        if(datetime.now().time().hour==9):
##            TramAction.accel_result = 0

        while (datetime.now().time().hour > 0 and datetime.now().time().hour < 24): # E sets when you want it to run for. In this case 1 am to midnight
            # E > 0 is when tram set to begin operations, < 24 is when tram cease operations
            if(not TramAction.run): # E if you don't have an action, you shut down 
                print "Entering shutdown state"
                break

            command = []
            params = []
            print "Current time: " + str(datetime.now().time()) # E print out time 
            for lines in open(r'.\control.txt').readlines(): # E open control.txt which is a list of commands you want it to run, for every command you will add to command array and paramenters 
                command.append(lines.replace("\n", "").split(" ")[0])
                params.append(lines.replace("\n", "").split(" "))
            command = map(string.strip, command) # E turn name inside into a func (what python recognizes)
            command = map(TramAction, command)

            TramControl().runAll(command, params) # E Call run all, which loops through statemachine 

            if(TramAction.emergency!=0): # E if your emergency is not equal to zero, youre entering the emergency state 
                print "Entering emergency state"