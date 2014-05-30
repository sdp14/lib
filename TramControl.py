#-------------------------------------------------------------------------------
# Name:        TramControl
# Purpose:
#
# Author:      NP
#
# Created:     15/01/2014
# Copyright:   (c) NP 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# StateMachine/TramControl.py
# Autonomous and directed control of tram operation
import string, sys, time, serial
import minimalmodbus
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
from Tracking import Tracking


class StateT(State):

    def __init__(self):
        self.transitions = None
    def next(self, input):
        if(input in self.transitions):
            print "Tramaccel info is: ", TramAction.accel_result
            print "Emergeny info is: ", TramAction.emergency

            return self.transitions[input]
        else:
            print ("Input %s not supported for current state" % input)
            return self
##            raise RuntimeError("Input %s not supported for current state" % input)


class Wait(StateT):

    def run(self, param):
        if(param[0]!='wait' or len(param)<2):
            return
        dur = int(param[1])
        print("Tram: Waiting %i Second(s)" % dur)
        time.sleep(dur)
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


class Move(StateT):

    def run(self, param):
        if(param[0]!='move'):
            return
        if(len(param)<2):
            print "tram direction ",TramControl.direction
            if(TramControl.direction>0):
                motormove = 9 - TramControl.cable
                dist = 100
            else:
                motormove = 8 + TramControl.cable
                dist = -100
            if(TramControl.direction>TramControl.minrange and TramControl.position+dist > TramControl.maxrange):
                TramControl.direction=-1
            if(TramControl.direction<TramControl.minrange and TramControl.position+dist < TramControl.minrange):
                TramControl.direction=1
            if(dist==100):
                if(TramControl.position+dist>TramControl.maxrange):
                    print("Move exceeds transact range!")
                    return

            if(dist==-100):
                if(TramControl.position+dist<TramControl.minrange):
                    print("Move exceeds transact range!")
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

        if(dist>TramControl.maxrange or dist<TramControl.minrange):
            print("Move exceeds transact range!")
            return

        while(TramControl.position!=dist):
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
            print("Tram: Moving %i centimeter(s) " % location + "to position %i" % (TramControl.position+location))
            if(motor_move(motormove)):
                TramControl.position+=location
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


class Measure(StateT):

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

        try:
            print('Sending connection test')
            TramControl.sock.send('Connection test')
            print repr(TramAction.response)
        except Exception, e:
            # whatever you need to do when the connection is dropped
            print('Attempting reconnect to server')
            connect()

        if(TramControl.sock):
            print("Tram: Sending Wait.")
            reset = ['wait',0,0,0,0,0,TramAction.measurement_tolerance,TramAction.acceleration_sensitivity,TramAction.acceleration_tolerance]
            TramConnect().send(TramControl.sock, reset)
            time.sleep(1)

            print("Tram: Taking Measurements.")
            TramConnect().send(TramControl.sock, param)

            time.sleep(2)
            if(param[1] or param[2] or param[3]):
                print "Tram: Downloading Data."
                TramConnect().FTP(param)
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


class Upload(StateT):

    def run(self, param):
        if(param[0]!='upload'):
            return

        recs = {}
        for lines in open(r'.\lib\imagerecord.txt').readlines():
            cur_line = lines.split(" ")
            recs[cur_line[0]]=int(cur_line[1])

        if(param[1]=='1'):
            print("Base: Uploading Data.")
            TramControl.datalogger = ParseData().parse_data()
            WebSite().upload_website(TramControl.datalogger, '/data/json_upload/', 1)

        if(param[1]=='2'):
            print("Base: Uploading Excel.")
            ParseData().make_excel_file()
            WebSite().upload_website('Excel', '/articles/file_upload/', 2)

        if(param[1]=='3'):
            if(recs['trampics']>0):
                print("Base: Uploading Tram Picture.")
                WebSite().upload_website(r'.\tram_pictures\trampic{:>05}.ppm'.format(recs['trampics']-1), '/articles/file_upload/', 3)
            else:
                return False

        if(param[1]=='4'):
            if(recs['basepics']>0):
                print("Base: Uploading Base Picture.")
                WebSite().upload_website(r'.\base_pictures\basepic{:>05}.jpg'.format(recs['basepics']-1), '/articles/file_upload/', 3)
            else:
                return False

        if(param[1]=='5'):
            if(recs['vids']>0):
                print("Base: Uploading Tram Video.")
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


class Picture(StateT):

    def run(self, param):
        if(param[0]!='picture'):
            return
        print("Base Station: Taking Picture")
        take_picture()
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


class TramControl(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, TramControl.wait)


def main():
    pass


def motor_move(pos):

    try:
        instrument = minimalmodbus.Instrument('COM6', 1)
        instrument.serial.port = 'COM6'         # this is the serial port name
        instrument.serial.baudrate = 9600   # Baud
        instrument.serial.bitsize = 8
        instrument.serial.parity   = serial.PARITY_EVEN
        instrument.serial.stopbits = 1
        instrument.serial.timeout  = 0.1   # seconds
        instrument.address = 1     # this is the slave address number

        docking = False
        if((pos==8+TramControl.cable and TramControl.position<=100) or (pos==10+TramControl.cable and TramControl.position<=1) or (pos==12+TramControl.cable and TramControl.position<=10)):
            docking = True

        instrument.write_register(385, 0)
        instrument.write_register(385, 1)
        instrument.write_register(125, 0)
        instrument.write_register(125, pos)
        val = int(instrument.read_register(127))
        TramConnect().timeout(0)
        while ((val & 0x4000) == 0):
            if (TramAction.location != 0 and (pos==8 or pos==9)):
                if(TramConnect().timeout(2)):
                    instrument.write_register(125, 0)
                    instrument.write_register(125, 32)
                    print 'Tracking triggered - motor returned: ', instrument.read_register(127)
            if(TramControl.sock):
                if (TramAction.motor_switch==5 and docking):
                    instrument.write_register(125, 0)
                    instrument.write_register(125, 32)
                    print 'Switch triggered - motor returned: ', instrument.read_register(127)
            if (val != int(instrument.read_register(127))):
                val = int(instrument.read_register(127))
                print 'motor value returned: ', hex(val)

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
    camcapture = cv.CaptureFromCAM(0)
    if(~camcapture.isOpened()):
        return False

    recs = {}
    for lines in open(r'.\lib\imagerecord.txt').readlines():
        cur_line = lines.split(" ")
        recs[cur_line[0]]=int(cur_line[1])

    img = cv.QueryFrame(camcapture)
    cv.SaveImage(r'.\base_pictures\pic{:>05}.jpg'.format(recs['basepics']), img)
    recs['basepics']=recs['basepics']+1

    f = open(r'.\lib\imagerecord.txt','w')
    for items in recs:
        f.write(str(items)+" "+str(recs[items])+'\n')
    f.close()


def connect():
    print("Base Station: Trying to connect to tram")

    TramControl.sock = TramConnect().connect()
    if(TramControl.sock):
        print('Starting new thread')
        try:
            start_new_thread(TramConnect().make_thread, (TramControl.sock,TramControl.response,))
            print(TramControl.sock)
            print('Sending connection test')
            TramControl.sock.send('Connection test')
        except Exception ,e:
            print("Thread error: "+ str(e))
            return False

    else:
        print('Failure connecting to tram')
        return False


def tracking():
    print("Base Station: Starting tracking")
    try:
        t=Tracking()
        if(t):
            start_new_thread(t.tracking,())
    except Exception ,e:
        print("Thread error: "+ str(e))
        return False



if __name__ == '__main__':

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

    tracking()
    connect()


    while(TramAction.run):

##        if(datetime.now().time().hour==9):
##            TramAction.accel_result = 0

        while (datetime.now().time().hour > 0 and datetime.now().time().hour < 24):
            # E > 0 is when tram set to begin operations, < 24 is when tram cease operations
            if(not TramAction.run):
                print "Entering shutdown state"
                break

            command = []
            params = []
            print "Current hour: " + str(datetime.now().time().hour)
            for lines in open(r'.\control.txt').readlines():
                command.append(lines.replace("\n", "").split(" ")[0])
                params.append(lines.replace("\n", "").split(" "))
            command = map(string.strip, command)
            command = map(TramAction, command)

            TramControl().runAll(command, params)

            if(TramAction.emergency!=0):
                print "Entering emerg0ency state"
