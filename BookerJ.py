import os
import json
import csv
import numpy as np
import pandas as pd
import myKNN

class BookerJ(object):

    #jdir directory of json_logs, ddir is the data directory for the items in the given list, items: a list of items to buy and sell
    def __init__(self, jdir=None, ddir=None, items=None):

        self.jdir = jdir
        self.ddir = ddir
        self.items = items
        self.files = [ [ddir + i + '_x.csv', ddir + i + '_y.csv'] for i in items ]
        self.idata = None
        self.knn = myKNN.KNN()

        self.curprices = None
        self.predprices = None

        #OWN(1/0), LASTPAIDPRICE, AVGBUYPRICE, NUMTIMESBOUGHT, LASTSOLDPRICE, AVGSELLPRICE, NUMTIMESSOLD,TOTPROFT, AVGPROFT
        self.ledger = { k : [0,0,0.0,0,0.0,0,0.0,0,0] for k in self.items}

    
    #reads the last num json logs generated by ge data scraper 1 log is generated per half hour
    def readlogs(self, num=48):
        self.idata = self.read_idata(num)
        return self.idata

    #analyzes the data read from the log files
    def analyze(self):
       
        if self.idata is None: raise ValueError('must read log files before analysis')

        curprices = { k : 0.0 for k in self.items}
        predprices = { k : 0.0 for k in self.items}
      
        #loop through each tracked item
        leni = len(self.items)
        for i in range(leni):

            #read in item data, training data for the ith item
            datax = self._readfile(self.files[i][0]) 
            datay = self._readfile(self.files[i][1])
            
            #reshape datay
            for j in range(len(datay)): datay[j] = datay[j][0] #its a single value in a list, reshape

            #munch the current data for input into knn algorithm
            munched_point = self.munch_point(self.items[i], self.idata)

            #scaled between 0-1 for min-max price of last 24 hours
            curprices[ self.items[i] ] = munched_point[0]
            predprices[self.items[i] ] = self.knn.knn_on_point([25],datax,datay,munched_point)

            self.curprices = curprices
            self.predprices = predprices

        return predprices, curprices

    #returns buy and sell dictionary of items, higher sense the greater a difference in pred and cur prices required before recommending buying or selling
    def recommend(self, sens=0.2):

        buyitems = {}
        sellitems = {}

        for i in self.items:

            #get the various prices for the item
            curprice = self.curprices[i]
            predprice = self.predprices[i]

            nonscaled = self.idata.iloc[0][i]#cur price on grand exchange

            diff = predprice - curprice

            if diff > sens:
                buyitems[i] = [nonscaled, curprice, predprice]
            elif diff < (-1)*sens:
                sellitems[i] = [nonscaled, curprice, predprice]

        return buyitems, sellitems

   # IN_STOCK(Y/N), LAST BUY_PRICE, AVERAGE_BUY_PRICE, NUMBER_TIMES BOUGHT, LAST_SELL_PRICE, AVERAGE_SELL_PRICE,  NUMBER_TIMES SOLD,
   # TOTAL_PROFITLOSS, AVG_PROFITLOSS

    #booker simulates buying and selling based on the given dictionaries produced by booker.recommend
    def buysell(self, buy=None, sell=None):

        items_bought = []
        items_sold = []

        #try to buy recommended items
        for i, prices in buy.items():

            ldata = self.ledger[i]

            if ldata[0] < 1: #do not have this item, so buy one
                
                items_bought.append(i)

                ldata[3] += 1 #number of times item has been bought

                curavg = ldata[2]
                numbought = ldata[3]

                ldata[0] = 1 
                ldata[1] = prices[0] #current price in gold
                ldata[2] = (prices[0]/numbought) +  curavg #calc average buy price
                ldata[7] -= prices[0] #subtract purchase amount from tally
                
                #update ledger
                self.ledger[i] = ldata
        
        #try tosell recommended items
        for i, prices in sell.items():

           ldata = self.ledger[i]

           if ldata[0] > 0: #have item to sell, sell it

               items_sold.append(i)

               ldata[6] += 1 #increase count sold

               curavg = ldata[5]
               numsold = ldata[6]

               ldata[0] = 0
               ldata[4] = prices[0]
               ldata[5] = (prices[0]/numsold) + curavg #calc average sell price

               ldata[7] += prices[0] #add sale price to tally

               ldata[8] = ((ldata[4] - ldata[1])/numsold) + ldata[8] #calc avg profit

               #update ledger
               self.ledger[i] = ldata

        return items_bought, items_sold
      
    def display_ledger(self,num_items = 10):

        #sort ledger by average profit
        s = sorted(self.ledger.items(), key=lambda e: e[1][8], reverse=True)

        out = ''
        #display top num_items
        count = 0
        for k,v in s:
            if num_items > count:
                out += k + ' +/ ' + str(self.ledger[k][8]) + '\n'
                print(k + ' +/- ' + str(self.ledger[k][8]))
                count += 1
            else: break;

        return out
        
    
    #read the item data from json files and convert to dataframe and replace 0 with nan
    def read_idata(self, num_logs):

        jdata = self.read_json_data( num_logs )
        idata = pd.DataFrame.from_dict(jdata)
        idata.replace(0,np.nan, inplace=True)
 
        return idata


    #reads the latest num_files of json ge summary data for the given items
    def read_json_data(self, num_files=48):

        jlogs = os.listdir(self.jdir)
        lenj = len(jlogs)
        jfiles = list(jlogs[ lenj-(num_files+1) : lenj-1])

        jdata = self.read_buy_averages(jfiles)

        return jdata

    #returns a dictionary whos keys are the item names and whos values are a list of buy averages as recorded in each of the json_logs being read.
    def read_buy_averages(self, files=None):
    
        dvals= { k : [] for k in self.items }

        for fn in files:
            f = open(self.jdir + fn, mode='r')
            d = json.load(f)
            for e in d:
                item = d[e]['name'].replace(' ','_')
                if item in self.items: 
                    dvals[item].append( d[e]['buy_average'] )
        
            f.close()

        return dvals


    def _readfile(self, filename=None):
        
        data = []
        file = open(filename, mode='r', newline='')

        reader = csv.reader(file)
        for row in reader: data.append( [float(elem) for elem in row ] )
        
        file.close()
    
        return data


    #munch point 24h, 4h
    def munch_point(self,item, data):

        pastday_vals = data[item].values
        lenv = len(pastday_vals)
        pastday_vals.reshape(lenv,1)

        min = np.nanmin(pastday_vals)
        max = np.nanmax(pastday_vals)

        scaled_vals = self._scale(pastday_vals,min,max)

        cur_val = scaled_vals[0]

        var_a = np.nanvar(scaled_vals[0:9]) #variance past 4H
        var_b = np.nanvar(scaled_vals) #variance past 24H
        
        return [cur_val,var_a,var_b]


    #Xi = (Xi - Xmin)/(Xmax-Xmin)
    def _scale(self, ndarray=None, min=None, max=None):
        
        lend = len(ndarray)
        temp = [0.0 for i in range(lend)]

        for i in range(lend):
            temp[i] = (ndarray[i] - min)/(max-min)

        return temp

