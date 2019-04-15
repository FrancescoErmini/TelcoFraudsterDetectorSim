import numpy as np
import h5py
from config import Tools, TNSLAsettings
import csv
import pandas as pd
import random

   
class TNSLA():

	b = 0
	d = 1
	u = 2
	a = 3

	POS = 0
	NEG = 1



	def __init__(self, scenario, dataset):
		super(TNSLA, self).__init__()
		self.scenario = scenario
		self.dataset = dataset
		self.pretrust = [0.5 for i in range(self.scenario.N)]
		

	"""
	A esprime le proprie opinoni sulla riga A
	B riceve le opinioni altrui sulla colonna B
	"""
		
	def computeTrust2(self, A, B):

		N = self.scenario.n_providers + self.scenario.n_intermidiaries


		dataset = h5py.File(self.dataset.dataset, 'a')
		
		#carica pos e neg da A verso tutti, per evitare successivi acessi alla memoria
		fback_from_A =  dataset['fback_matrix_updated'][:]
		pos = fback_from_A[A][B][TNSLA.POS]
		neg = fback_from_A[A][B][TNSLA.NEG]


		if pos > 10 or neg > 10:
			#A has direct feedback over B, then compute directly A opion over B
			opinion_A_B = self.edit(pos, neg, self.hasPreTrust(A,B))
			#store A opinion over B in the opinion matrix
			self.storeOpinion(A,B,opinion_A_B)
			print(str(A)+" has direct opinion over "+str(B))
			return self.eval(opinion_A_B)
		
		
		else:

			opinion_A_i = [0.0, 0.0, 1.0, 0.5]
			opinion_i_B = [0.0, 0.0, 1.0, 0.5]
			trustee_score = TNSLAsettings.trustee_score
			trustee_count = 0

			for i in range(self.scenario.N):
				pos_A_i = fback_from_A[A][i][TNSLA.POS]
				neg_A_i = fback_from_A[A][i][TNSLA.NEG]
				pos_i_B = fback_from_A[i][B][TNSLA.POS]
				neg_i_B = fback_from_A[i][B][TNSLA.NEG]

				
				if self.eval(self.edit(pos_A_i,neg_A_i, self.hasPreTrust(A,i))) > trustee_score and self.eval(self.edit(pos_i_B,neg_i_B,self.hasPreTrust(i,B)))!= 0.5:			

					if trustee_count == 0:
						#update new trustee values
						opinion_A_i = self.edit(pos_A_i,neg_A_i,self.hasPreTrust(A,i))
						opinion_i_B = self.edit(pos_i_B,neg_i_B,self.hasPreTrust(i,B))
					else:
						opinion_A_i = self.consensus(opinion_A_i, self.edit(pos_A_i,neg_A_i, self.hasPreTrust(A,i)))
						opinion_i_B = self.consensus(opinion_i_B, self.edit(pos_i_B,neg_i_B, self.hasPreTrust(i,B)))
					trustee_count += 1

			if trustee_count == 0:
				return 0.5
			else:					
				opinion_A_B = self.discount(opinion_A_i, opinion_i_B)
				self.storeOpinion(A,B,opinion_A_B)
				res = self.eval(opinion_A_B)
				if res > 1.0 or res < 0.0:
					print("error occur")
					TNSLA.printOpinion(opinion_A_B)
				return res

	




	def computeTrust(self,target):
		
		#N = self.scenario.n_providers + self.scenario.n_intermidiaries
		
		if not self.scenario.isIntermidiary(target):
			#print("error: you can not compute. trust of an originating/terminating provider")
			return -1

		dataset = h5py.File(self.dataset.dataset, 'a')
		
		fback_to_target =  dataset['fback_matrix_updated'][:,target,:]

		opinion_all_target   = [0.0, 0.0, 1.0, 0.5]

		neg_counter = 0
		pos_counter = 0

		for j in range(self.scenario.N):
			
				pos_j_target = fback_to_target[j][TNSLA.POS]
				neg_j_target = fback_to_target[j][TNSLA.NEG]


				neg_counter += neg_j_target
				pos_counter += pos_j_target

				if pos_j_target > 0 or neg_j_target > 0:

					
						opinion_j_target = self.edit(pos_j_target, neg_j_target, 0.5)
						opinion_all_target = self.consensus(opinion_all_target, opinion_j_target)
		
		if neg_counter > 100 or pos_counter > 100:
			return self.eval(opinion_all_target)		
		else:
			return 0.5


	def storeOpinion(self, _from, _to, opinion):
		
		dataset = h5py.File(self.dataset.dataset, 'a')
		dataset['opinion_matrix'][_to,_from,:] = opinion
		

	def getOpinion(self, _from, _to):
		dataset = h5py.File(self.dataset.dataset, 'r')
		return dataset['opinion_matrix'][_to,_from,:]


	def eval(self, opinion):
		return opinion[TNSLA.b]+(opinion[TNSLA.a]*opinion[TNSLA.u])

	def edit(self, pos, neg, pretrust):

		opinion_res = np.zeros(4)
		opinion_res[TNSLA.b] = pos / (pos + neg + 2.0)
		opinion_res[TNSLA.d] = neg / (pos + neg + 2.0)
		opinion_res[TNSLA.u] = 2.0 / (pos + neg + 2.0)
		opinion_res[TNSLA.a] = pretrust
		return opinion_res

	def consensus(self, opinion1, opinion2):
		opinion_res = np.zeros(4)

		b1 = opinion1[TNSLA.b]
		d1 = opinion1[TNSLA.d]
		u1 = opinion1[TNSLA.u]
		a1 = opinion1[TNSLA.a]

		b2 = opinion2[TNSLA.b]
		d2 = opinion2[TNSLA.d]
		u2 = opinion2[TNSLA.u]
		a2 = opinion2[TNSLA.a]		

		denom = u1 + u2 - u1 * u2
		if denom == 0.0 or denom < 0.1:

			opinion_res[TNSLA.b] = (b1 + b2) / 2.0
			opinion_res[TNSLA.d] = 1.0 - opinion_res[TNSLA.b]
			opinion_res[TNSLA.u] = 0.0
		else:
			
			opinion_res[TNSLA.b] = 	(b1*u2 + b2*u1) / denom
			opinion_res[TNSLA.d] =  (d1*u2 + d2*u1) / denom
			opinion_res[TNSLA.u] =  (u1 * u2) / denom
			

		opinion_res[TNSLA.a] = a1

		return opinion_res

	def discount(self, opinion1, opinion2):
		opinion_res = np.zeros(4)

		b1 = opinion1[TNSLA.b]
		d1 = opinion1[TNSLA.d]
		u1 = opinion1[TNSLA.u]
		a1 = opinion1[TNSLA.a]

		b2 = opinion2[TNSLA.b]
		d2 = opinion2[TNSLA.d]
		u2 = opinion2[TNSLA.u]
		a2 = opinion2[TNSLA.a]	

		opinion_res[TNSLA.b] = b1 * b2
		opinion_res[TNSLA.d] = b1 * d2
		opinion_res[TNSLA.u] = d1 + u1 + b1*u2
		
		opinion_res[TNSLA.a] = a2
		return opinion_res

	def hasPreTrust(self, source, target):
		if TNSLAsettings.use_pretrust == False:
			return 0.5
		if self.scenario.isFraudster(target):
			return 0.5
		if not self.scenario.isCoopIntermidiary(target):
			return 0.5
		if not self.scenario.isCoopProvider(target):
			return 0.5

		if self.scenario.isProvider(source):
			#source ha accordi con 4 intermediari che hanno id 
			if target in range(self.scenario.n_providers+source, self.scenario.n_providers+source+4):
				
				return 1.0
			#se target è un operatore con id vicino, vuol dire che operano nello stesso paese si conoscono e si fidano
			if target in range(source,source+2):
				
				return 1.0

		return 0.5



	def printOpinion(opinion):
		print("belief: "+str(opinion[TNSLA.b]))
		print("disbelief: "+str(opinion[TNSLA.d]))
		print("uncertainty: "+str(opinion[TNSLA.u]))
		print("baserate: "+str(opinion[TNSLA.a]))
		