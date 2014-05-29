#-------------------------------------------------------------------------------
# Name:        ParseData
# Purpose:
#
# Author:      Arsid
#
# Created:     24/01/2014
# Copyright:   (c) Arsid 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!usr/bin/python
import xlsxwriter
import time, datetime
from WebSite import WebSite


#returns the number of different data recordings

def number_of_data():
    f = open(".\dat_file\MDR.dat", "r")

    cur_line = 0
    data = 0

    #Tile of the data at a certain column is at cur_line == 1
    #Data starts when cur_line > 3 i.e. cur_line >= 4
    for line in f:
        newl = line.split(",")

        it = 0
        for word in newl:
            it += 1

        if(cur_line == 1):
            data = it
            break

        cur_line += 1

    return data



def form_JSON(cur_data_set):

    #append_text = open("tramData.dat", 'r').read()


##    file_to_get = open("tramData.dat", 'r')
##    append_text = ""
##
##    for line in file_to_get:
##    	append_text = line
##        break
##
##
##    myfile = open(".\dat_file\MDR.dat", "a")
##
##    print(append_text)
##    myfile.write(append_text)


    f = open(".\dat_file\MDR.dat", "r")

    json_data = {}
    #data stores the data for the current column
    data = []

    cur_line = 0
    #Tile of the data at a certain column is at cur_line == 1
    #Data starts when cur_line > 3 i.e. cur_line >= 4
    for line in f:
        newl = line.split(",")

        it = 0
        for word in newl:

            #get the name for the current data position and place it in the dict
            if(cur_line == 1 and cur_data_set == it):

                json_data["name"] = word.replace('"', '')
                json_data["data"] = []

            #get the units for the current data set
            if(cur_line == 2 and cur_data_set == it):
                json_data['units'] = word.replace('"', '')

            #get the data
            if(cur_line > 3 and it == cur_data_set):

                if(cur_data_set > 0 and str(word) != " " and str(word) != "\n"):
                    ##print(cur_data_set)
                    data.append(float(word.replace('"', '')))
                    #uncomment for test data that is all 1's
                    #data.append(1)

                elif (cur_data_set == 0 and str(word) != " " and str(word) != "\n"):


                    word.replace("\n", "")
                    time_list = word.replace('"', '').split(" ") #split the day and the hours of the day into 2 data points
							                                     #time_list[0] gives the year, month and day data
							                                     #time_list[1] has hour, minute and seconds

                    day = time_list[0].split("-") # day[0] = year, day[1] = month, day[2] = day
                    hour = time_list[1].split(":") #hour[0] = hour, hour[1]= minute, hour[2] = seconds

##                    print day
                    day = map(int, day)
                    hour = map(int, hour)

                    cur_time = int(time.mktime(datetime.datetime(day[0], day[1], day[2], hour[0], hour[1], hour[2]).timetuple())*1000)

                    data.append(str(cur_time))


            it += 1

        cur_line += 1


    f.close()
    json_data['data'] = data
    return json_data


class ParseData():

    def append_data(self):

        file_to_get = open("tramData.dat", 'r')
        append_text = ""

        for line in file_to_get:
        	append_text = line

        myfile = open(".\dat_file\MDR.dat", "a")

#        print(append_text + "\n")
        myfile.write(append_text + "\n")



    def parse_data(self):

        json_data = {}

        for x in range(0, number_of_data()):
            json_data['id_'+str(x+1)] = form_JSON(x)
           # print json_data['id_'+str(x+1)]['name']

        #clear the file of old data
        f = open('data.json', 'w').close()
        #store new data to the file
##        json.dump(json_data, open('data.json', 'w'))

#        print"done"

        return json_data


    def make_excel_file(self):
		f = open(".\dat_file\MDR.dat", "r")

		name_of_excel_file = "data_file"
		workbook = xlsxwriter.Workbook('excel_file/' + str(name_of_excel_file) + ".xlsx")
		worksheet = workbook.add_worksheet()

		cur_line = 0
		for line in f:
			newl = line.split(",")

			it = 0
			for word in newl:
				worksheet.write(cur_line, it, word.replace('"', ''))
				it += 1

			cur_line += 1


		f.close()
		workbook.close()

