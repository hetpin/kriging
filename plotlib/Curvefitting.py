import scipy.optimize as optimize
import numpy as np

A = np.array([(19,20,24), (10,40,28), (10,50,31)])

def func(data, a, b, c):
    return a*data[:,0]+ b*data[:,1] + c
A[:,2] = func(A[:,:2], 100.5,3,4)
print A
guess = (1,1,1)
params, pcov = optimize.curve_fit(func, A[:,:2], A[:,2], guess)
print(params)