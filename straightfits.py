import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
class straightfits(object):
    '''The curve in a loglog plane can be decomposed in approximately straight lines. 
       In the $(\log x,\log y)$-plane one straight line is described by $y = Ae^{Bx}$ for some $A$ and $B$.

       From: http://stackoverflow.com/a/3433503/2268280:

       For fitting $y = Ae^{Bx}$, take the logarithm of both side gives $\log y = \log A + Bx$. 
       So just fit $\log y$ against $x$.
    '''
    A=np.array(0)
    B=np.array(0)
    corners=np.array([])
    def __init__(self,x=[],y=[]):
        self.x=np.asarray(x)
        self.y=np.asarray(y)
        if self.x.shape[0]>0:
            self.corners=np.append(self.corners,self.x[0])
    def add_segment(self,xmin,xmax,ShowPlot=True,verbose=False):
        '''Add one straight segment to the logarhitmic fit
           between xmin and xmax,
           WARNING: xmax not inclued in the range of the fit
           ShowPlot to check the fit
        '''
        df=pd.DataFrame()
        df['x']=self.x
        df['y']=self.y
        self.corners=np.append(self.corners,xmax)
        d=df[np.logical_and(df.x>=xmin,df.x<=xmax)]
        z = np.polyfit(d.x, np.log(d.y), 1)
        p = np.poly1d(z)
        if verbose:
            print 'logy=',p
        self.A=np.append( self.A,np.exp(p[0]) )
        self.B=np.append( self.B,p[1])
        if ShowPlot:
            xlin=np.linspace(xmin,xmax)
            plt.semilogy(d.x,d.y,'ro')
            plt.semilogy(xlin,self.A[-1]*np.exp(self.B[-1]*xlin))
        return self.A[-1],self.B[-1]
    def delete_last_segment(self):
        '''Delete tha last saved straight segment'''
        self.A=self.A[:-1]
        self.B=self.B[:-1]
        self.corners=self.corners[:-1]
    
    def to_csv(self,csvfile):
        '''
        Save the fit data to a csv file with colums:
        A,B,corners
        where: $y = Ae^{Bx}$
        '''
        df=pd.DataFrame()
        df['A']=self.A
        df['B']=self.B
        df['corners']=self.corners
        df.to_csv(csvfile,index=False)
        
    def read_csv(self,csvfile):
        '''
        Recover fitted data from a csv file with colums:
        A,B,corners
        where: $y = Ae^{Bx}$
        '''
        df=pd.read_csv(csvfile)
        self.A=df.A
        self.B=df.B
        self.corners=df.corners
        
    def __call__(self,x):
        '''
        Given an array A and another array B defined by the
        values of x in corners, obtain the several values
        of $y = Ae^{Bx}$ for any x.
        x can be a float or an array of floats
        '''
        xa=np.asarray(x)
        if not np.asarray(x).shape:
            xa=np.asarray([x])
        
        limit=np.array([])
        imax=self.corners.shape[0]-1
        for xx in xa:
            for i in range(1,imax+1):
                if xx>=self.corners[i-1] and xx<self.corners[i]:
                    limit = np.append( limit,self.A[i]*np.exp(self.B[i]*xx) )
                if xx<self.corners[0] or xx>=self.corners[imax]:
                    limit = np.append( limit,0.0 )	
                    sys.exit('ERROR: Out of range')
                   
        if limit.shape[0]==1:
            limit=limit[0]
        return limit
        