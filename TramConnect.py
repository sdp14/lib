#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Arsid
#
# Created:     24/01/2014
# Copyright:   (c) Arsid 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import time
from socket import *
from ftplib import FTP
#Importing all from thread
from thread import *
from TramAction import TramAction

global host
global port


def mytimeout(arg):

    if(arg==0):
        TramConnect.mytime = time.clock()
        return False

    if(arg!=0):
        return (abs(time.clock()-TramConnect.mytime) >= arg)


def get_address():
##    host = '192.168.2.103'
##    port = 52000
    recs = {}
    for lines in open(r'.\lib\tramconfig.txt').readlines():
        cur_line = lines.split(" ")
        recs[cur_line[0]]=cur_line[1]

    global host
    global port
    host = recs['host'].replace("\n", "")
    port = int(recs['port'])


class TramConnect():

    def connect(self):

        global host
        global port
        ##host = '10.100.4.76' # '127.0.0.1' can also be used
        ##port = 52000
        get_address()
        print "host = "+repr(host)
        print "port = "+repr(port)

        try:
            sock = socket()
        #Disable this to make it work with the tram server
            sock.settimeout(1) # E comment this out to work w/o BB, eliminates timeouts
            sock.connect((host, port)) #Connect takes tuple of host and port
            return sock

        except Exception, e:
            print "Something's wrong with %s. Exception type is %s" % (host, e)
            return False

       # sock.close()


    def make_thread(self, sock, data):

        self.sock = sock
        self.data = data
        #Connecting to socket

        #Infinite loop to keep client running.

        while 1:

            #data_to_send = raw_input("Enter command to send to server:   ")
            try:
                data = sock.recv(1024)
                if not data:
                    break
                print data
             #   print "break"
                TramAction.response = data
                if(data.isdigit()):
                    emergency = 0
                    nums = [int(i) for i in data]
                    for j in nums:
                        if(j<3):
                            TramAction.accel_result = j
                        if(j==5 or j==6):
                            TramAction.motor_switch = j
                        if(j==4 or j==7):
                            TramAction.battery = j
                        if(j==3 or j==8):
                            TramAction.temperature = j
                        if(j==2):
                            emergency = 1
                        # E To implment more checks if(j==2 or j==7 or j==8):
                        # 2 related to accelerometer, 7 to low battery, 8 to high temp in tram 
                        TramAction.emergency = emergency

            except Exception ,e:
                print("Serial communication error: "+ str(e))
                break


    def send(self, s, param):
        ## param 1 = take datalogger measurements
        ## param 2 = take ten pictures
        ## param 3 = record video
        ## param 4 = streaming vid on
        ## param 5 = streaming vid off
        ## param 6 = measurement tolerance 10
        ## param 7 = acceleration sensitivity 180
        ## param 8 = acceleration tolerance 20

        self.s = s
        self.param = param
        try:
            print 'Sending to tram: ' + str(param[0])+" "+str(param[1])+" "+str(param[2])+" "+str(param[3])+" "+str(param[4])+" "+str(param[5])+" "+str(param[6])+" "+str(param[7])+" "+str(param[8])
            s.send(str(param[0])+" "+str(param[1])+" "+str(param[2])+" "+str(param[3])+" "+str(param[4])+" "+str(param[5])+" "+str(param[6])+" "+str(param[7])+" "+str(param[8]))
            data = ''
            mytimeout(0)
            while ('done' not in TramAction.response and param[0]!='wait'):
                if(data != TramAction.response):
                    print 'Received: ', TramAction.response
                    data = TramAction.response
                if(mytimeout(300)):
                    print 'Timing out connection'
                    break

        except Exception, e:
            print("Something's wrong with server. Exception type is %s" % (e))
            return False


    def FTP(self, param):
        self.param = param

        recs = {}
        for lines in open(r'.\lib\imagerecord.txt').readlines():
            cur_line = lines.split(" ")
            recs[cur_line[0]]=int(cur_line[1])
##        print "Current picture number = ", recs['pics']
##        print "Current video number = ", recs['vids']
        global host
        global port
        get_address()

        print 'Trying to connect to FPT server'
        print param[1], param[2], param[3]
        try:
            ftp=FTP(host, timeout=2)
            ftp.login('logger','zz58j8bnQcFPSawhnN8YGtFT')
            ftp.cwd('/upload/')
            if(int(param[1])==1):
                print 'download data'
                filetram = open("tramData.dat", 'wb')
                try:
                    ftp.retrbinary("RETR " + "tramData.dat", lambda data: filetram.write(data))
                    ##ftp.retrbinary('RETR %s' % "tramData.dat", filetram.write)
                    ##ftp.retrbinary("RETR " + "tramData.dat", open(filetram, 'wb').write)
                except Exception ,e:
                    print "FTP Error %s" %e


                filetram.close()
            if(int(param[2])==1):
##                i=0
##                while (i<10):
                filetram = open(r'.\tram_pictures\trampic{:>05}.ppm'.format(recs['trampics']), 'wb')
##                    filetram = open(r'.\pics\picture'+str(recs['pics']+1)+'.ppm', 'wb')
                try:
##                    print("grabber00"+str(i)+".ppm")
##                    filename = "grabber00"+str(i)+".ppm"
                    filename = "grabber000.ppm"
                    ftp.retrbinary("RETR " + str(filename), lambda data: filetram.write(data))
                    filetram.close()
                    recs['trampics']=recs['trampics']+1
                except Exception ,e:
                    print "FTP Error %s" %e
##                i+=1

            if(int(param[3])==1):
                filetram = open(r'.\tram_video\video{:>05}.mp4'.format(recs['vids']), 'wb')
                try:
    ##                filetram = open(r'.\video\video'+str(recs['vids']+1)+'.mp4', 'wb')
                    gettext(ftp,"output.mp4",filetram)
                    filetram.close()
                    recs['vids']=recs['vids']+1
                except Exception ,e:
                    print "FTP Error %s" %e
            ftp.quit()
##            f = open(r'.\lib\imagerecord.txt','w').close()
            f = open(r'.\lib\imagerecord.txt','w')
            for items in recs:
                f.write(str(items)+" "+str(recs[items])+'\n')
            f.close()

        except Exception ,e:
            print 'Unable to connect exception: %s'%e
            return


    def timeout(self, arg):

        self.arg = arg
        if(arg==0):
            TramConnect.time = time.clock()
            return False

        if(arg!=0):
            return (abs(time.clock()-TramConnect.time) >= arg)


