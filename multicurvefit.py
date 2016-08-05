import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from curvefit import *
class multicurvefit(curvefit):
    '''The curve in a loglog plane can be decomposed in several picewise . 
       
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
        Save the fit data to a json file with colums:
        coeffs,xmin,xmax
        where coeffs are used to build the poly1d objects
        '''
        self.polys.to_json(jsonfile)
                
    def read_json(self,jsonfile):
        '''
        Recover fitted data from a  json file with colums:
        coeffs,xmin,xmax
        where coeffs are used to build the poly1d objects
        '''
        #http://stackoverflow.com/questions/20603925/label-based-indexing-pandas-loc
        self.polys=pd.read_json(jsonfile,dtype=object)
        for i in range(self.polys.shape[0]):
            self.polys.loc[i,'coeffs']=np.asarray(self.polys.ix[i].coeffs)
            
        self.polys=self.polys.reset_index(drop=True)
        
    def __call__(self,x,verbose=True):
        '''
        Given a set of coefficients for  xmin<=x<xmax,
        built the proper poly1d an evalute it in that point
        '''
        x=np.asarray(x)
        fout=np.array([])

        if not x.shape:
            x=np.asarray([x])
        
        ordered=True
        n=self.polys.shape[0]
        if np.unique(x==np.sort(x)).tolist()==[True]:
            self.polys['p']=[np.poly1d(self.polys.coeffs[i]) for i in range(self.polys.shape[0])]
            if n>1: #if n==1 -> ramge: (-oo,+oo)
                xx=x[x<self.polys.xmax[0]]
                fout=np.append(fout,( 10**( self.polys.p[0]( np.log10(xx) ) ) ) )
                if n>2: 
                    for i in range(n-2):
                        xx=x[np.logical_and(x>=self.polys.xmax[i], x<self.polys.xmax[i+1] )]
                        fout=np.append(fout, 10**( self.polys.p[i+1]( np.log10(xx) ) ) )
     
                xx=x[x>=self.polys.xmax[n-2]]
                fout=np.append(fout, 10**( self.polys.p[n-1]( np.log10(xx) ) ) )
        else:
            warnings.warn('Input array no ordered. Going into slow mode ')
            ordered=False
     
        if n==1:
            fout=np.append(fout, 10**( np.poly1d(self.polys.coeffs[0])( np.log10(x) ) ) )        
        if not ordered:
            for xx in x:
     
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
                        warnings.warn('WARNING: Out of fitted range: %g' %xx)
     
     
                coeffs=coeffs.coeffs.reset_index(drop=True)[0]
                if len(coeffs)>0:
                    p=np.poly1d(coeffs)
                    fout=np.append( fout,10.**( p( np.log10(xx) ) ) )
                else:
                    sys.exit('ERROR: Out of range')

        if fout.shape[0]==1:
            fout=fout[0]
        return fout
