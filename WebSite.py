#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      NP
#
# Created:     20/02/2014
# Copyright:   (c) NP 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import xlsxwriter
import time, datetime
import json, urllib, urllib2
import mechanize
from TramAction import TramAction


def main():
    pass


def get_address():
##    address = 'http://192.168.2.104:8000'
    recs = {}
    for lines in open(r'.\lib\tramconfig.txt').readlines():
        cur_line = lines.split(" ")
        recs[cur_line[0]]=cur_line[1]

    return recs['server'].replace("\n", "")


class WebSite():
   # data = {'position': '5 meters', 'command_info': {'status': 'success', 'current_command': 'move'}, 'pos_percentage': '60', 'battery_info': '2 hours'}
   # upload_JSON(data)
    def get_html_data(self, website):
        ##print ('connenting to: '+ get_address()+website)
        try:
            req = urllib2.Request(get_address()+website)
            response = urllib2.urlopen((req), timeout=2)
            the_page = response.read()
            return the_page
        except Exception, e:
            print "URL error(%s)" % (e)
            return False


    def login(self, br):
        self.br = br

        try:
            br.open(get_address()+'/accounts/login/', timeout=2)
            br.select_form(nr=0)
            br.form['username'] = "tram"
            br.form['password'] = "tramisfam"
            br.submit()

##        except urllib2.HTTPError:
##            pass
        except Exception, e:
            print "Mechanize error %s" % str(e)
            return False


    #uploads the json file to the website
    def upload_website(self, data, mywebsite, filetype):
        #url of website to upload the json
        mywebsite = get_address()+mywebsite
        print mywebsite
        #Mechanize methods to select the right form to submit
        br = mechanize.Browser()
        self.login(br)
        try:
            br.open((mywebsite), timeout=2)
            br.select_form(nr=0)
            if(filetype == 0):
                try:
                    br.form['tram_info'] = ""
                    br.form['tram_info'] = json.dumps(data)
                except Exception, e:
                    return False
            elif(filetype == 1):
                try:
                    br.form['json_model'] = ""
                    br.form['json_model'] = json.dumps(data)
                except Exception, e:
                    return False
            elif(filetype == 2):
                try:
                    br.form.add_file(open("excel_file/data_file.xlsx", "rb"), 'multipart/form-data', "data_file.xlsx")
                    br.form.set_all_readonly(False)
                except Exception, e:
                    return False
            elif(filetype == 3):
                try:
                    br.form.add_file(open(data, "rb"), 'multipart/form-data', data[16:])
                    br.form.set_all_readonly(False)
                except Exception, e:
                    return False
            elif(filetype == 4):
                try:
                    br.form.add_file(open(data, "rb"), 'multipart/form-data', data[14:])
                    br.form.set_all_readonly(False)
                except Exception, e:
                    return False

            #adding the json data to the form
            #json.dumps needed to make the data a json type such that it can
            #be validated on the server

            #submitting the form
            try:
                br.submit()
            except Exception, e:
                return False

        except Exception, e:
            print "Mechanize error %s" % str(e)
            return False


    def tram_info(self, position, current_command, status, pos_percentage, accelerometer):
        self.position =position
        self.current_command = current_command
        self.status = status
        self.pos_percentage = pos_percentage
        self.accelerometer = accelerometer
        data = {}
        data['position'] = str(position) + ' meters'
        data['command_info'] = {}
        data['command_info']['status'] = status
        data['command_info']['current_command'] = current_command
        data['pos_percentage'] = pos_percentage
        accel=''
        emergency = TramAction.accel_result
        if (TramAction.accel_result==2):
            accel='Accelerometer is experiencing a lot of turbulance: '
            emergency=2
        if(TramAction.temperature == 3):
            accel+='Temperature too high: '
            emergency=2
        if(TramAction.battery == 4):
            accel+='Battery is low: '
            emergency=2
        accel+='shutting down.'
        data['shutdown_info'] = accel
        if (TramAction.battery==4):
            bat='Battery Low'
        else:
            bat='Battery Charged'
        data['battery_info'] = bat
        data['accelerometer'] = str(emergency)
        timestamp = str(time.localtime().tm_mon) +"/" + str(time.localtime().tm_mday) + "/" + str(time.localtime().tm_year) + " " + str(time.localtime().tm_hour) + ":" + str(time.localtime().tm_min) + ":" + str(time.localtime().tm_sec)
        data['timestamp'] = timestamp

        self.upload_website(data, '/data/tram_data_upload/', 0)


    def image_upload(self, filename, mywebsite):

        #url of website to upload the json
        mywebsite = get_address()+mywebsite
        print mywebsite
        #Mechanize methods to select the right form to submit
        br = mechanize.Browser()
        self.login(br)

        try:
            br.open(mywebsite, timeout=2)
            br.select_form(nr=0)

##            filepath = '%s' % (str(filename)+str(recs['pics'])+".jpg")
##            print filepath
##            br.form.add_file(open(filepath, "rb"), 'multipart/form-data', str(filename+str(recs['pics'])+".jpg"))
            br.form.add_file(open(filename, "rb"), 'multipart/form-data', filename[16:])
            br.form.set_all_readonly(False)

            br.submit()
            print "Image Uploaded"
        except Exception, e:
            print "Mechanize error %s" % str(e)
            return False

        # br.submit()
