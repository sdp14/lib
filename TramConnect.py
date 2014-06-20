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


def mytimeout(arg): # E If you want to see if 20 seconds has gone by, call mytimeout(0) then call mytimeout 30 it will return True if it has been more than 30 seconds. Less will return false 

    if(arg==0): # E If it is it sets it's own variable to the current time. I want the current time to be time zero. Zero sets the time
        TramConnect.mytime = time.clock()
        return False

    if(arg!=0): # E If anything else, it will check to see if that many seconds has gone by. A number will return True is that time has passed (since it was set)
        return (abs(time.clock()-TramConnect.mytime) >= arg)


def get_address(): # E Sets port and host from config file. Will set it for you. 
##    host = '192.168.2.103'
##    port = 52000
    recs = {}
    for lines in open(r'.\lib\tramconfig.txt').readlines(): # E opens tramconfig file. # E Need this file, expects it to be in lib folder 
        cur_line = lines.split(" ") # E splits it based on a space. Takes a string and makes an array of strings. Basef on (" ") which is a space. 
        recs[cur_line[0]]=cur_line[1]

    global host # E reads in host and port. 
    global port # E Called oon line 55, sets host and port equal (allows it to be changed in the file without digging through code)
    host = recs['host'].replace("\n", "")
    port = int(recs['port'])


class TramConnect():

    def connect(self): # E ln 51-57 reads config file and sets variable. once done this is goes in a try: block which attempts to start connection

        global host # E makes variables, calls and prints ln. 56, 57 
        global port
        ##host = '10.100.4.76' # '127.0.0.1' can also be used
        ##port = 52000
        get_address()
        print "host = "+repr(host)
        print "port = "+repr(port)

        try:
            sock = socket() # E Make a socket (allows to talk to BB)
        #Disable this to make it work with the tram server
            sock.settimeout(1) # E comment this out to work w/o BB, eliminates timeouts # E Try to connect for 1 second and if not possible let me know something went wrong 
            sock.connect((host, port)) #Connect takes tuple of host and port # E connects socket to host/port
            return sock # E once previous line successfully allows use of this connection later on 

        except Exception, e: # E if something goes wrong (wrong IP, port, host etc.) exception thrown
            print "Something's wrong with %s. Exception type is %s" % (host, e) # E Host will be printed, will give a little bit of information
            return False # E Will immediately stop program from running. 

       # sock.close()


    def make_thread(self, sock, data): # E Continually try and recieve data and process it 

        self.sock = sock # E give it a socket, will recieve data, slipt into numbers and update stuff depending on numbers given 
        self.data = data # E overwritten in line 85? 
        #Connecting to socket

        #Infinite loop to keep client running.

        while 1: # E infinitely looping, try catch, because we are doing something over the network which can fail.

            #data_to_send = raw_input("Enter command to send to server:   ")
            try: # E Necessary for if something goes wrong 
                data = sock.recv(1024) # E I have connection and I want you wait for some data. Something will be told over the connection 1024 is the maximum size willing to receive in bytes 
                if not data: # E makes sure data is given and it is not empty 
                    break # E If none, the loop will be broken. When messages stop being recieved, end this function 
                print data # E Print data to screen 
             #   print "break" 
                TramAction.response = data # E setting a variable 
                if(data.isdigit()): # E Checks to see if is number (True) if not then (False)
                    emergency = 0 
                    nums = [int(i) for i in data] # E will go through numbers. If given ten numbers, each loop wull contain one 
                    for j in nums: 
                        if(j<3): # E Dirty switch statement (numbers are cryptic, less efficeint but more readable like strings)
                            TramAction.accel_result = j # E depending on what number is recieved, will do different things
                        if(j==5 or j==6): # E Possibily forward and backward? 
                            TramAction.motor_switch = j
                        if(j==4 or j==7): # E 7 is low battery, 
                            TramAction.battery = j 
                        if(j==3 or j==8):
                            TramAction.temperature = j
                        if(j==2): # E or j==7 or j==8:  Will cause an emergency state 
                            emergency = 1 
                        # E To implment more checks if(j==2 or j==7 or j==8):  
                        # 2 related to accelerometer, 7 to low battery, 8 to high temp in tram 
                        TramAction.emergency = emergency

            except Exception ,e: # E if something goes wrong on connect it will exit the function. 
                print("Serial communication error: "+ str(e)+"   --> TramConnect")
                break


    def send(self, s, param): # E This table tells you what everything is. 
        ## param 1 = take datalogger measurements
        ## param 2 = take ten pictures
        ## param 3 = record video
        ## param 4 = streaming vid on
        ## param 5 = streaming vid off
        ## param 6 = measurement tolerance 10
        ## param 7 = acceleration sensitivity 180
        ## param 8 = acceleration tolerance 20

        self.s = s # E Socket? number 2? To somewhere else. 
        self.param = param # E an array of integers 
        try: # E same a usual 
            print 'Sending to tram: ' + str(param[0])+" "+str(param[1])+" "+str(param[2])+" "+str(param[3])+" "+str(param[4])+" "+str(param[5])+" "+str(param[6])+" "+str(param[7])+" "+str(param[8]) # E prints out all the things to the screen 
            s.send(str(param[0])+" "+str(param[1])+" "+str(param[2])+" "+str(param[3])+" "+str(param[4])+" "+str(param[5])+" "+str(param[6])+" "+str(param[7])+" "+str(param[8])) # E sending message to socket
            data = ''
            mytimeout(0) # E sets clock to time zero 
            while ('done' not in TramAction.response and param[0]!='wait'): # E in make_thread ln 90, waiting for other func to recieve a response that is done. Tram saying it is done
                if(data != TramAction.response): # E if something has come in, will show what is recieved prints what is being told 
                    print 'Received: ', TramAction.response
                    data = TramAction.response
                if(mytimeout(300)): # E if time out 300 (will wait 300 sec?) If it waits and it hasn't gotten back, you leave the function 
                    print 'Timing out connection'
                    break

        except Exception, e: # E if something weird happens prints an exception 
            print("Something's wrong with server. Exception type is %s" % (e))
            return False


    def FTP(self, param): # EB Transfer files from the tram computer to the control computer. Open config file, get address set host and port. Print a message
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

        print 'Trying to connect to FTP server' # EB Tries to connect to tram computer 
        print param[1], param[2], param[3] # EB param[1]=1 transfers data, param[2]=1 transfers photos, param[3]=1 transfers video
        try: # E over network so something could go wrong 
            ftp=FTP(host, timeout=2) # E create a connection, specialized to move files back and forth 
            ftp.login('logger','zz58j8bnQcFPSawhnN8YGtFT') #B Logger account and password
            ftp.cwd('/upload/')  # E current working directory, for the FTP any file given will be in there. 
            if(int(param[1])==1): # E if param 1 is set to 1, data download 
                print 'download data' 
                filetram = open("tramData.dat", 'wb') # E Open file 
                try: # E try to connect taking data from Tram and downloading (copy/paste somewhere to somewhere else)
                    ftp.retrbinary("RETR " + "tramData.dat", lambda data: filetram.write(data))
                    ##ftp.retrbinary('RETR %s' % "tramData.dat", filetram.write)
                    ##ftp.retrbinary("RETR " + "tramData.dat", open(filetram, 'wb').write)
                except Exception ,e: # EB print error if the try fails 
                    print "FTP Error %s" %e


                filetram.close() # E close the connection that was made 
            if(int(param[2])==1): # E if the second one is set, try another file (trampic)
##                i=0
##                while (i<10):
                filetram = open(r'.\tram_pictures\trampic{:>05}.ppm'.format(recs['trampics']), 'wb') # E open connection 
##                    filetram = open(r'.\pics\picture'+str(recs['pics']+1)+'.ppm', 'wb')
                try: # E try to transfer file 
##                    print("grabber00"+str(i)+".ppm")
##                    filename = "grabber00"+str(i)+".ppm"
                    filename = "grabber000.ppm"
                    ftp.retrbinary("RETR " + str(filename), lambda data: filetram.write(data))
                    filetram.close()
                    recs['trampics']=recs['trampics']+1
                except Exception ,e:
                    print "FTP Error %s" %e
##                i+=1

            if(int(param[3])==1): # E Similar situation for video 
                filetram = open(r'.\tram_video\video{:>05}.mp4'.format(recs['vids']), 'wb')
                try:
    ##                filetram = open(r'.\video\video'+str(recs['vids']+1)+'.mp4', 'wb')
                    gettext(ftp,"output.mp4",filetram)
                    filetram.close()
                    recs['vids']=recs['vids']+1
                except Exception ,e:
                    print "FTP Error %s" %e
            ftp.quit() # E Closes FTP connection 
##            f = open(r'.\lib\imagerecord.txt','w').close()
            f = open(r'.\lib\imagerecord.txt','w')
            for items in recs: # E Probably a record 
                f.write(str(items)+" "+str(recs[items])+'\n')
            f.close()

        except Exception ,e: # E if FTP connection doesn't work, catch exception and print 
            print 'Unable to connect exception: %s'%e
            return


    def timeout(self, arg): # E exactly as above, zero sets the clock, anything else will return T or F

        self.arg = arg
        if(arg==0):
            TramConnect.time = time.clock()
            return False

        if(arg!=0):
            return (abs(time.clock()-TramConnect.time) >= arg)


