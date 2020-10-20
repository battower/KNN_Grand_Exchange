
import BookerScript_Utils as ut
import BookerJ
import time
import datetime

#denial is always good.
import warnings
warnings.filterwarnings("ignore")


#text log of script's output
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

#Loop forever, offering tips every half hour
while True:

    if not haschecked:

        bkr.readlogs(48)
        bkr.analyze()
        buy,sell = bkr.recommend(sens=0.2) #any price change greater that 0.2
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



