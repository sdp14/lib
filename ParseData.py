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
#import xlsxwriter
import csv
import time, datetime
from WebSite import WebSite


#returns the number of different data recordings

def number_of_data(): # E returns of data recordings = overall function 
    f = open(".\dat_file\MDR.dat", "r") # E opens file 

    cur_line = 0 # E current lime
    data = 0 # E number of diffrent data recoring 

    #Tile of the data at a certain column is at cur_line == 1
    #Data starts when cur_line > 3 i.e. cur_line >= 4
    for line in f: # E goes line by line in data file 
        newl = line.split(",") # E spilts lines with commas 

        it = 0
        for word in newl: # E goes through everyword in array and counts the number of words. Counts how many after splitting
            it += 1

        if(cur_line == 1): # E if on first line, count how many data points and leave loop 
            data = it
            break

        cur_line += 1

    return data # counting how many words in cur line equals one 



def form_JSON(cur_data_set): # E JSON is a universal formatting. A way to format data that is common 
# E Overall open file, format the data, tell it the column and it will make a json object, then return it 
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


    f = open(".\dat_file\MDR.dat", "r") # E Will open data file 

    json_data = {} # E where JSON stuff will be stored 
    #data stores the data for the current column
    data = []

    cur_line = 0
    #Tile of the data at a certain column is at cur_line == 1
    #Data starts when cur_line > 3 i.e. cur_line >= 4
    for line in f: # E read in data line by line 
        newl = line.split(",") # E splits it with commas 

        it = 0
        for word in newl: # E goes word by word in your array 

            #get the name for the current data position and place it in the dict
            if(cur_line == 1 and cur_data_set == it): # E if cur_line is 1 (would be name) it stores that info for later 

                json_data["name"] = word.replace('"', '') #E Do not know what data is yet 
                json_data["data"] = []

            #get the units for the current data set
            if(cur_line == 2 and cur_data_set == it): #  E For units (ln 1 is name, ln 2 is units)
                json_data['units'] = word.replace('"', '')

            #get the data
            if(cur_line > 3 and it == cur_data_set): # E ln 4 and beyond will be data # E Where is ln 3 

                if(cur_data_set > 0 and str(word) != " " and str(word) != "\n"): # E ln 91-114 are formatting the data, splitting data to make pretty
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


            it += 1 # E updates number 

        cur_line += 1 # E updates current line 


    f.close() # E close file 
    json_data['data'] = data # E put data in the json data structure 
    return json_data 


class ParseData(): # E 

    def append_data(self): # E open tram data and updating so it has the last line 

        file_to_get = open("tramData.dat", 'r')
        append_text = ""

        for line in file_to_get:
        	append_text = line

        myfile = open(".\dat_file\MDR.dat", "a") # E writes the last line to the end of that file, "a" means append 

#        print(append_text + "\n")
        myfile.write(append_text + "\n")



    def parse_data(self): # E json data use the functions. Read, format pretty and return 

        json_data = {}

        for x in range(0, number_of_data()): # E loop through the data and call form json 
            json_data['id_'+str(x+1)] = form_JSON(x) 
           # print json_data['id_'+str(x+1)]['name']

        #clear the file of old data
        f = open('data.json', 'w').close() # E open a file and write whole chunk to it
        #store new data to the file
##        json.dump(json_data, open('data.json', 'w'))

#        print"done"

        return json_data # E return the data point 


  #   def make_excel_file(self): # E Makes excel file 
		# f = open(".\dat_file\MDR.dat", "r") # E open data # E Is this working?

		# name_of_excel_file = "data_file" # E Copy paste into excel 
		# workbook = xlsxwriter.Workbook('excel_file/' + str(name_of_excel_file) + ".xlsx")
		# worksheet = workbook.add_worksheet()

		# cur_line = 0
		# for line in f: # E go line by line 
		# 	newl = line.split(",") 

		# 	it = 0
		# 	for word in newl: # E word by work writing by worksheet 
		# 		worksheet.write(cur_line, it, word.replace('"', ''))
		# 		it += 1

		# 	cur_line += 1


		# f.close() # E Close both 
		# workbook.close()

    def make_csv_file(input_name, output_name):
        f = open(input_name, "r") # E open data 
        c = open(output_name, "wb")
        writer = csv.writer(c)
        writer.writerows(f)


    make_csv_file(".\dat_file\MDR.dat", ".\csv_file\data_file.csv")
