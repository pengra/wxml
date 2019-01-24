# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 22:22:28 2018

@author: Langley
"""
import numpy as np
from scipy.stats import chisquare

# This performs a chisquared test for indpependance on a
# sequence of integegers. This is test will output the p-value
# of a chisquared test done on the sequnce. This test is good
# for a sequnce of integers with a relativly small number of 
# possible values that reoccur many times. A small p-value
# indicates that the sequnce is not indpependant, while a large
# value tells you that it could be indpendant.
 
def chisquare_independence_test(sequence, step_size):
    
    x=[]
    for j in range(0,step_size):
        seq=[]
        for i in range(j,len(sequence),step_size):
            seq.append(int(sequence[i]))
        x.append(seq)
            
    idx = {}
    for seq in x:
        for val in seq:
            if not val in idx:
                idx[val]= len(idx)
    
    
    catagories = [[0 for j in range(len(idx))]for i in range(len(idx))]
    
    for seq in x:
        for i in range(1,len(seq)):
         catagories[idx[seq[i]]][idx[seq[i-1]]] += 1;
    
    freqs =  np.array(catagories)/np.sum(catagories)
    
    expected = np.array([[0 for j in range(len(idx))]for i in range(len(idx))])
    
    for i in range(len(freqs)):
        for j in range(len(freqs[i])):
            expected[i][j]= np.sum(catagories)*np.sum(freqs[i,:])*np.sum(freqs[:,j])
    
    exp = []
    cat = []
    
    for i in range(len(catagories)):
        for j in range(len(catagories[i])):
            if catagories[i][j]>0 and expected[i][j]>0:
                cat.append(catagories[i][j])
                exp.append(expected[i][j])
            else:
                cat.append(1)
                exp.append(1)
    return chisquare(cat, f_exp=exp).pvalue


# This method calculates that coefficient of correlation 
# of the elements of the sequnce compared the the elements
# that are step_size indecies ahead in the sequnce. An output 
# with magnitude close to 1 indicates that the values are corrilated
# and an output close to 0 indicates that they are not.

def r_value_independence_test(sequence, step_size):
    v=[]
    for i in range(len(sequence)-step_size):
        v.append([sequence[i],sequence[i+step_size]])
    v=np.array(v)
    x = v[:,0]
    y = v[:,1]
    print(v)
    return np.corrcoef(x,y)[1,0]
