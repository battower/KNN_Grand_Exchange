#pre-digests data for KNN Grand Exchange consumption
import GE_Data_Access as ge
import myKNN 
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import ge_data_funcs as gef


SECS_PER_DAY  = 86400
SECS_PER_HOUR = 3600
SECS_HALF_HOUR = 1800

class GEData_Muncher(object):

    #returns datax, datay matrices as lists of lists, for KNN_GrandExchange 
    #hours_a is a measure of the variance over the past amount of hours, 
    #hours_b is a second measure of the various over some other amount of hours
    #future_mins is the number of minutes into the future to predict
    #data in normalized into the feature space(0,1), days_normd is the number of days used to calculate this value 
    def munch(self, domain_df=None, training_df=None, hours_a=0, hours_b=0, future_mins=0, days_normd=1):

        len_dom = len(domain_df.index)
        len_train = len(training_df.index)

        datax = [ [0.0, 0.0, 0.0] for i in range(len_train)]
        datay = [ 0.0 for i in range(len_train) ]
        scalars = [ [0.0, 0.0] for i in range(len_train) ]

        for i in range(len_train):

            cur_ts = int(training_df.iloc[i]['timestamp'])

            a_ts = self._subtract_hours(cur_ts, hours_a)
            b_ts = self._subtract_hours(cur_ts, hours_b)
            future_ts = self._add_minutes( cur_ts, future_mins )
            norm_ts = self._subtract_days( cur_ts, days_normd)

            hist_a = self._rows_between(domain_df, a_ts, cur_ts)
            hist_b = self._rows_between(domain_df, b_ts, cur_ts)
            future = self._rows_between(domain_df,cur_ts,future_ts)
            norm = self._rows_between(domain_df,norm_ts,cur_ts)

            hist_a = hist_a['buy_average'].values
            hist_b = hist_b['buy_average'].values
            future = future['buy_average'].values
            norm = norm['buy_average'].values
            
            norm = norm.reshape( len(norm), 1)
            min = np.nanmin(norm)
            max = np.nanmax(norm)

            hist_a = self._scale( hist_a.reshape( len(hist_a), 1), min, max)
            hist_b = self._scale( hist_b.reshape( len(hist_b), 1), min, max)
            future = self._scale( future.reshape( len(future), 1), min, max)

            #hist_a = hist_a.reshape( len(hist_a), 1)
            #hist_b = hist_b.reshape( len(hist_b), 1)
            #future = future.reshape( len(future), 1)

            lena = len(hist_a)
            lenb = len(hist_b)
            lenf = len(future)

            cur_val = hist_a[len(hist_a)-1] #future[0]
            fut_val = future[lenf-1]
          
            var_a = np.nanvar(hist_a[0:lena-1])
            var_b = np.nanvar(hist_b[0:lenb-1])

            datax[i][0] = cur_val
            datax[i][1] = var_a
            datax[i][2] = var_b

            datay[i] = [fut_val]

            scalars[i][0] = min
            scalars[i][1] = max

        return datax, datay, scalars

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
        temp = np.zeros(lend)
        for i in range(lend):
            temp[i] = (ndarray[i] - min)/(max-min)

        return temp

    def _rows_between(self, df=None, start=0, end=0):
        return  df[ (df['timestamp'] >= start ) & ( df['timestamp'] <= end )]

    def _subtract_days(self, unix_time, days=0):
        return self._subtract_times(unix_time, days*SECS_PER_DAY)

    def _add_minutes(self, unix_time, mins=0):
        return self._add_times(unix_time, mins*60)

    def _subtract_hours(self, unix_time=0, hours=0):
        return self._subtract_times( unix_time, (hours * SECS_PER_HOUR))

    def _subtract_times(self, a=0, b=0):
        return a-b

    def _add_times(self, a=0, b=0):
        return a+b