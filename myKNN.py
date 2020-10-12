

import math

class KNN(object):

    #returns a list of prediction values for the datapoint for each k in kvals, based on the given training data.
    def knn_on_point(self, kvals, trainingx, trainingy, datapoint ):

 
        lenk = len(kvals)
        knn = [0.0 for k in range(lenk)]
        dists = self._sort_dists(datapoint, trainingx)

        for i in range(lenk):
            k = kvals[i]
            if k == 0: raise ValueError('k cannot be zero.')
            val = 0.0
            for j in range(k):
                idx = dists[j][1]
                val += trainingy[idx]
       
            knn[i] = val/k
    
        return knn

    #returns a matrix as nested lists, the ith row represents the prediction values for datapoints[i]and each column a different k value
    def knn_on_set(self,kvals,trainingx,trainingy,datapoints ):

        lenx = len(trainingx)
        lend = len(datapoints)
        if lenx != len(trainingy): raise ValueError('training sets x and y need to be same length')

        preds = [ [0.0 for k in kvals] for i in range(lend) ]

        for i in range(lend):
            preds[i] = self.knn_on_point(kvals,trainingx,trainingy, datapoints[i])
    
        return preds

    #performs knn leave one out cross validation on the training data for the given values of k
    #returns a matrix as nested lists columns for each k value, and rows for each training data point
    def knn_cv(self,kvals,trainingx,trainingy):

        lenx = len(trainingx)
        if lenx != len(trainingy): raise ValueError("x and y datasets must be same length")

        cv = [ [0.0 for k in kvals] for i in range(lenx) ]

        for i in range(lenx):

            x = self._leave_one_out(trainingx, i)
            y = self._leave_one_out(trainingy, i)
            datapoint = trainingx[i]

            cv[i] =  self.knn_on_point(kvals,x,y,datapoint)

        return cv

    #returns a matrix as nested lists where the ith row represents the squared error for the ith prediction, and each column represents a different k value
    def error_matrix(self,predictions=None, reality=None):
    
        lenp = len(predictions)
        lenr = len(reality)
        if (lenp and lenr) == False: raise ValueError('zero vectors are forbidden')
        if lenp != lenr: raise ValueError('prediction and reality vectors need to be equal length')

        #There should be something here at index 0. The number of values here represents the number of k values tested.
        lenk = len(predictions[0])
        error_mtx = [ [0.0 for i in range(lenk)] for j in range(lenr)] #num_rows = lenr, #num_cols = lenk

        for i in range(lenr):
            real_val = reality[i]

            for j in range(lenk):
                pred_val = predictions[i][j]
                error_mtx[i][j] = (real_val - pred_val)**2 #squared error between predicted value and actual value

        return error_mtx

    #determine the best value of k based on the least avgerage squared error
    def avg_error(self,error_mtx=None):

        num_rows = len(error_mtx)
        num_cols = len(error_mtx[0])
        if num_cols and num_rows == 0: raise ValueError('zero vectors are forbidden')
        lenk = num_cols
        err_avg = [ [0.0,i] for i in range(lenk) ]

        #sum up the squared error for each k
        for i in range(num_rows):

            for j in range(lenk):
                err_avg[j][0] += error_mtx[i][j]
   
        #calculate the mean for each k
        for i in range(lenk): err_avg[i][0] = err_avg[i][0]/num_rows

        return err_avg
    #return a list with the i'th element of x removed
    def _leave_one_out(self,x, i):

        lenx = len(x)
        y = []
        for j in range(lenx):
            if j==i:
                pass
            else:
                y.append(x[j])
        return y

    #euclidian distance between two points
    def _euclid(self,xpoint,ypoint):
    
        lenx = len(xpoint)
        if lenx != len(ypoint): raise ValueError( 'x and y must have same length to measure distance' )

        s = 0.0
        for i in range(lenx):
            s += (xpoint[i] - ypoint[i])**2
        return math.sqrt(s)

    #returns an ordered list of (dist, idx) of points closest to the datapoint.  
    def _sort_dists(self,datapoint, xs):
        lenx = len(xs)
        dist = [(0.0,0) for i in range(lenx)]

        for i in range(lenx):
            dist[i] = (self._euclid(datapoint,xs[i]), i)
    
        dist.sort()
        return dist






