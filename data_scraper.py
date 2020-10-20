#updated ge_scraper module.  Plan to take over ops at midnight from ge_scraper

#retrieves json summary of items on grand exchnage from rsbuddy.com,
#and appends the data to the appropriate files.

#the script is intended to be run every half-hour as data is not updated any earlier. scheduled with task manager

#day 0 = 1597881600 = Midnight Aug 20 2020 - start of data collection
#d0_buy_average.csv = buy averages for every item day 0

import time
import datetime
import os.path
import requests
import json
import csv

TIME_ZERO = 1597881600 #00:00:00 Aug 20 
TIME_END = 1599780600 # sep 10 330 #1599523200 #sept 8 12 am 20 20 #1599091200
SECS_DAY = 86400
SECS_HALF_HOUR = 1800

out_dir = 'data/out/'

ba_dir = 'ge/buy_average/'
bq_dir = 'ge/buy_quantity/'
sa_dir = 'ge/sell_average/'
sq_dir = 'ge/sell_quantity/'
oa_dir = 'ge/overall_average/'
oq_dir = 'ge/overall_quantity/'

ba_file = 'buy_avg_d'
bq_file = 'buy_qua_d'
sa_file = 'sell_avg_d'
sq_file = 'sell_qua_d'
oa_file = 'ovr_avg_d'
oq_file = 'ovr_qua_d'

#data extracted from rsbuddy
buy_avg = []
sell_avg =[]
buy_qua = []
sell_qua = []
tot_avg = []
tot_qua = []
names = []

out_dirs = [ba_dir, bq_dir, sa_dir, sq_dir, oa_dir, oq_dir]
out_files = [ba_file, bq_file, sa_file, sq_file, oa_file, oq_file]
out_data = [buy_avg, buy_qua, sell_avg, sell_qua, tot_avg, tot_qua]

rsbuddy = 'https://rsbuddy.com/exchange/summary.json'

#return number of whole days since midnight aug 20 2020
def get_day(time_secs):
    day_zero = TIME_ZERO #1597881600 #00:00:00 Aug 20
    secs_day = 86400
    return int( (time_secs-day_zero)/secs_day )

#creates a new file named filename, writes headers [timestamp, datetime, item1, item2,....]
def create_csv(filename, itemnames):
    added_headers = ['timestamp', 'datetime']
    added_headers.extend(itemnames)

    file = open(filename, mode='w', newline='')
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(added_headers)

    file.close()

#appends data to csv file of filename
def write_csv(filename, data, cur_time, cur_datetime):
    
    data_out =[cur_time, cur_datetime]
    data_out.extend(data)

    file_out = open(filename, mode='a', newline='')
    writer = csv.writer(file_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(data_out)

    file_out.close()

#determine todays number
cur_time = int(time.time())
day  = get_day( cur_time ) #day since time zero 00:00:00 Aug 20 2020 

cur_datetime = datetime.datetime.utcfromtimestamp(cur_time).strftime('%Y-%m-%d %H:%M:%S')

#sends http request to rs buddy for a summary of the grand exchange state.
data_req = requests.get(rsbuddy)
data = json.loads(data_req.text)

#collect the data
for item in data:

    names.append(data[item]['name'].replace(" ", "_")) #item name, replace spaces in column names with '_', keep this format for compatability
    buy_avg.append(data[item]['buy_average'])
    buy_qua.append(data[item]['buy_quantity'])
    sell_avg.append(data[item]['sell_average'])
    sell_qua.append(data[item]['sell_quantity'])
    tot_avg.append(data[item]['overall_average'])
    tot_qua.append(data[item]['overall_quantity'])

#write the data to the proper files.
num_files = len(out_files)
for i in range(num_files):

    #eg = 'data/out/buy_average/buy_avg_d10.csv'
    filename = out_dir + out_dirs[i] + out_files[i] + str(day) + '.csv'
    if not os.path.isfile(filename):
        create_csv(filename,names)
    write_csv(filename,out_data[i], cur_time, cur_datetime)

#back up json data just in case needed
filename = out_dir + 'json_data/ge_summary_'+ cur_datetime.replace(' ', '_').replace(':','_') + '.json'
file = open(filename, mode='w')

json.dump(data,file)

file.close()
