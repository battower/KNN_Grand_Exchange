#same as BrokerBooker, except meant to to run automatically.  Makes simulated purchases and makes recommendations based on results as well.

#Buys one of any item KNN analysis says is low price and will rise.  If item is not already owned buy one item at buy price and record to buy+sell tally, record avg price payed
#last price paid, and number of times item was purchased.

#Sells any item KNN says price is high and will fall.  It item has been purchased, sell item, remove from stock, record price sold at, average profit,
#and sell price to current buy+sell tally

#"Location: {0:20} Revision {1}".format(Location,Revision)

import BookerScript_Utils as ut
import BookerJ
import time
import datetime

import warnings
warnings.filterwarnings("ignore")

scriptlog = 'bookerscript_log.txt'

starttime = int(time.time())

#get the items to observe and trade
tracked_items = ut.read_items_file('live_items.csv')

#get last 48 files, (24 hour period)
jdir = '../../osrs_ge/scrapers/Grand Exchange Data Scraper/scraper.py/data/out/json_data/'
ddir = 'data/'

bkr = BookerJ.BookerJ(jdir, ddir, tracked_items)

curtime = starttime
cycletime = starttime
haschecked = False

while True:

    if not haschecked:

        bkr.readlogs(48)
        bkr.analyze()
        buy,sell = bkr.recommend(sens=0.2)
        bought, sold = bkr.buysell(buy,sell)

        dispstring = ut.display_info(curtime,buy,sell,bought,sold)
        ledgerstring = bkr.display_ledger(10)

        ut.writelog(scriptlog,dispstring,ledgerstring)

        cycletime = int(time.time())
        haschecked = True

    else:#wait for 30 mins
        
        waiting = (curtime - cycletime)/60
        if (waiting > 30):
            haschecked=False

    curtime = int(time.time())



