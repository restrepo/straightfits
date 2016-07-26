import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from curvefit import *
class multicurvefit(curvefit):
    '''The curve in a loglog plane can be decomposed in approximately straight lines. 
       In the $(\log x,\log y)$-plane one straight line is described by $y = Ae^{Bx}$ for some $A$ and $B$.

       From: http://stackoverflow.com/a/3433503/2268280:

       For fitting $y = Ae^{Bx}$, take the logarithm of both side gives $\log y = \log A + Bx$. 
       So just fit $\log y$ against $x$.
    '''
    polys=pd.DataFrame()
    def __init__(self,x=[],y=[]):# *args, **kwargs):
        #super(multicurvefit, self).__init__(*args, **kwargs)
        self.x=np.asarray(x)
        self.y=np.asarray(y)
 
    def __getitem__(self, key):
        if key=='x':
            return self.x
        elif key=='y': 
            return self.y
        else:
            sys.exit('Not key: %s' %key)
            
    def add_curve(self,xmin,xmax,poly_order=1,ShowPlot=True,verbose=False):
        '''Add one straight segment to the logarhitmic fit
           between xmin and xmax,
           WARNING: xmax not inclued in the range of the fit
           ShowPlot to check the fit
        '''
        df=pd.DataFrame()
        ps=pd.Series()
        df['x']=self.x
        df['y']=self.y
        d=df[np.logical_and(df.x>=xmin,df.x<=xmax)]
        c=curvefit(d.x.values,d.y.values)
        c.add_fit(poly_order) #poulates c object
        ps['coeffs']=c.coeffs
        ps['xmin']=xmin
        ps['xmax']=xmax
        self.polys=self.polys.append(ps,ignore_index=True)
        
    def delete_last_curve(self):
        '''Delete tha last saved straight segment'''
        self.polys=self.polys[:-1]
    
    def to_json(self,jsonfile):
        '''
        Save the fit data to a csv file with colums:
        A,B,corners
        where: $y = Ae^{Bx}$
        '''
        self.polys.to_json('lux2016.json')
                
    def read_json(self,jsonfile):
        '''
        Recover fitted data from a csv file with colums:
        A,B,corners
        where: $y = Ae^{Bx}$
        '''
        self.polys=pd.read_json(jsonfile).reset_index(drop=True)
        for i in range(self.polys.shape[0]):
            self.polys['coeffs'][i]=np.asarray(self.polys.ix[i].coeffs)
            
        self.polys=self.polys.reset_index(drop=True)
        
    def __call__(self,x,verbose=True):
        '''
        Given an array A and another array B defined by the
        values of x in corners, obtain the several values
        of $y = Ae^{Bx}$ for any x.
        x can be a float or an array of floats
        '''
        xa=np.asarray(x)
        
        limit=np.array([])
        if not np.asarray(x).shape:
            xa=np.asarray([x])
        for xx in xa:

            wrng=False
            if xx<self.polys.xmin.min():
                wrng=True
                coeffs=self.polys[:1]
            elif xx>=self.polys.xmax.max(): 
                wrng=True
                coeffs=self.polys[-1:]
            else:
                coeffs=self.polys[np.logical_and(self.polys.xmin<=xx,self.polys.xmax>xx)]        

            if wrng:
                if verbose:
                    print('WARNING: Out of fitted range:',xx)


            coeffs=coeffs.coeffs.reset_index(drop=True)[0]
            if len(coeffs)>0:
                p=np.poly1d(coeffs)
                limit=np.append( limit,10.**( p( np.log10(xx) ) ) )
            else:
                sys.exit('ERROR: Out of range')

        if limit.shape[0]==1:
            limit=limit[0]
        return limit
            