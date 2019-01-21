
#Need to figure out how to pass in arguments 
from rakan import PyRakan as BaseRakan
import random
import math

class MarcovChainMonteCarlo(BaseRakan):
    """
    A MCMC method for the state of Iowa
    We hope to generalize code for any state

    """
    #declare variables
    float CompactEnergy 
    float PopEnergy
    int alpha
    int beta

#initialize starting point at random precinct 
    startPoint = random.randint(0, precinct)

#Calculate current energies
    currentCompac = self.getcompactness(startPoint)
    currentPopEng = self.getpopenergy(startPoint)

#propose move 
	precinct, district = self.propose_random_move(startPoint)

#calculate candidate energies
	candCompac = self.getcompactness(precinct)
	candEnergy = self.getpopenergy(precinct)

#calculate uniform random number to compare with ratio 
	u = uniform(0,1)

#acceptance acceptance ratio
	f = exp(alpha*currentCompac + beta*currentPopEng)
	fprime = exp(alpha*candCompac + beta*candEnergy)
	a = fprime/f

#accept or reject
if u <= a:
	#accept
	self.make_move(precinct, district)
else:
	#reject
	break

     









