from rakan import PyRakan as BaseRakan
import random
import math

class MarcovChainMonteCarlo(BaseRakan):
    """
    A MCMC method for the state of Iowa
    We hope to generalize code for any state

    """
  def __init__(self, int rid, int district, int alpha, int beta, int num_steps)
    	self.initial_precinct = rid 
   	self.alpha = alpha
    	self.beta = beta
    	self.num_steps = num_steps
    	self.district = district


  def get_acceptance_ratio(curr_compact_score, proposed_compact_score, curr_pop_score, proposed_pop_score)
  
    	f_of_x = exp(self.alpha*curr_compact_score+self.beta*curr_pop_score)
   	f_of_x_prime = exp(self.alpha*proposed_compact_score+self.beta*proposed_pop_score)

   	return (f_of_x_prime/f_of_x)



  def step(self):
    	#propose a move
    	precinct, proposed_district = self.propose_random_move()
        
        #calculate curren compact/pop scores
        curr_compact_score = self.compactness_score()
        curr_pop_score = self.population_score()

        #calculate proposed compact/pop scores
        proposed_compact_score = self.compactness_score(precinct, proposed_district)
        proposed_pop_score = self.get_proposed_population_score(precinct, proposed_district)

        #calculate acceptance ratio
        acceptance_ratio = self.get_acceptance_ratio(curr_compact_score, curr_pop_score,proposed_pop_score,proposed_compact_score)
        acceptance_ratio = min(1, acceptance_ratio)
        uni_rand = random.random(0, 1)

        #accept and move
        if acceptance_ratio < uni_rand:
        	self.move_precinct(precinct, proposed_district)
        #reject and do nothing
        else:
        	break


   def walk(self, num_steps):
        # walk for determined number of steps 
        for i in range(self.num_steps):
            self.step(self)
     









