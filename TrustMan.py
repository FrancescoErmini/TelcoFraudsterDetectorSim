#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import math
import numpy as np
import h5py
import csv
import logging
import pandas as pd
from pandas import DataFrame
from config import *



class TrustMan(object):

	def __init__(self, scenario, dataset):
		super(TrustMan, self).__init__()

		self.scenario = scenario
		self.dataset = dataset

		self.disguised_behaviour = 0
		self.malicious_behaviour = 0
		self.frauds_detector_counter = 0 #conta quante chiamate con frode sono effettivamente valutate a casusa della non risposta del terminator
		self.frauds_detector_counter_ref = 0
		self.accusations_counter_ref = 0 #conta quante accuse dovrebbero essere fatte nel sottoinsieme delle chiamate con frode rilevate
		self.accusations_counter = 0 #conta quante accuse vengono effettivamente fatte a casua della non risposta degli intermediari
		self.transactions_counter = 0

		self.fraudBehaviour = 0
		self.accusationsAnalyzed = 0
		self.fraudsAnalyzed = 0


		self.revenue_termin = 0
		self.revenue_fraudster = 0
		self.revenue_transit = 0

		
	def createFeedbackMatrix(self, infile):

		
		

		N = self.scenario.n_providers + self.scenario.n_intermidiaries
		POS = 0 #const
		NEG = 1 #const
		
		fx = h5py.File(self.dataset.dataset, 'a')
		matrix = fx['fback_matrix']


		count=0


		with open(infile, 'r') as src:
			reader = csv.reader(src)
			traces = list(reader)

		print("\nParse call traces and create the feedback matrix.")

		for trace in traces:

				Tools.printProgress( count, self.scenario.n_calls)
				count+=1

				self.calcRevenue2(trace)

				#self.measure_fraudsters_behaviour(trace)

				if self.scenario.isFraud(trace[Csv.FRAUD]):
						self.frauds_detector_counter_ref += 1


				for i in range(self.scenario.l_chain):
					ind=int(trace[Csv.TRANSIT+i])					
					if self.scenario.isFraudster(ind):
						if not self.scenario.isFraud(trace[Csv.FRAUD]):

							self.disguised_behaviour += 1 #le transazioni buone fatte da un frodatre nel campione
						
						else:

							self.malicious_behaviour += 1 #le transazioni maligne fatte da un frodatre nel campione

				if self.scenario.isCoopProvider(trace[Csv.TERMIN]) and not self.scenario.isFraud(trace[Csv.FRAUD]):
					
					origin = int(trace[Csv.ORIGIN])
					nextop = int(trace[Csv.TRANSIT])
					self.transactions_counter += 1
					matrix[origin,nextop,POS]=matrix[origin,nextop,POS] + 1
					for i in range(self.scenario.l_chain-1):
						source = int(trace[Csv.TRANSIT+i])
						target = int(trace[Csv.TRANSIT+i+1])
						if self.scenario.isCoopIntermidiary(source):
							self.transactions_counter += 1
							matrix[source,target,POS] = matrix[source,target,POS] + 1

				if self.scenario.isCoopProvider(trace[Csv.TERMIN]) and self.scenario.isFraud(trace[Csv.FRAUD]):
					
					self.frauds_detector_counter += 1
					self.accusations_counter_ref += 1 #self.scenario.l_chain
					self.accusations_counter += 1 #la prima accusa da origin al primo transit esiste indipendentemente dalla risposta dei tranists
					'''Origin accuses the first transit op'''
					origin = int(trace[Csv.ORIGIN])
					nextop = int(trace[Csv.TRANSIT])
					#M[origin][nextop][1] = M[origin][nextop][1] + 1
					self.transactions_counter += 1
					matrix[origin,nextop,NEG]=matrix[origin,nextop,NEG] + 1
					if TrustConfig.pretrust_strategy and TrustConfig.l_cascade_agreements > 0 and matrix[origin,nextop,NEG]>0: #condizione sul valore positivo serve a evitare di avere valori negativi
						matrix[origin,nextop,NEG]=matrix[origin,nextop,NEG] - 1

					'''Transit-i accuses transit-i+1'''
					for i in range(self.scenario.l_chain-1):
						source = int(trace[(Csv.TRANSIT+i)])
						target = int(trace[(Csv.TRANSIT+i+1)])
						self.accusations_counter_ref += 1
						if self.scenario.isCoopIntermidiary(source):
							self.accusations_counter += 1
							self.transactions_counter += 1
							matrix[source,target,NEG] = matrix[source,target,NEG] + 1
							if TrustConfig.simmetry_strategy:			

								if matrix[target,source,NEG]>=1 and matrix[source,target,NEG]>=1:
									matrix[source,target,NEG] = matrix[source,target,NEG] -  1
									matrix[target,source,NEG] = matrix[target,source,NEG] -  1
							
							if TrustConfig.pretrust_strategy and i < TrustConfig.l_cascade_agreements and not self.scenario.isFraudster(target) and matrix[source,target,NEG]>=1:  
								matrix[source,target,NEG] = matrix[source,target,NEG] -  1.0 / (i+2)
						
		

		try:
			self.fraudBehaviour = 100.0*self.malicious_behaviour/(self.malicious_behaviour+self.disguised_behaviour)
		except ZeroDivisionError:
			self.fraudBehaviour = 0
		try:
			self.accusationsAnalyzed = int(100.0*self.accusations_counter/self.accusations_counter_ref) #tasso di risposta per nodi transizione nel campione
		except ZeroDivisionError:
			self.accusationsAnalyzed = 0
		try:
			self.fraudsAnalyzed =int(100.0*self.frauds_detector_counter/self.frauds_detector_counter_ref) #tasso di frodi conosciute (rilevate) nel campione
		except ZeroDivisionError:
			self.fraudsAnalyzed = 0

	

	def updateFeedbackMatrix(self, scenario_directory, cycle):
		
		cycle_deep_max = TNSLAsettings.cycle_deep_max

		if cycle > cycle_deep_max:
			cycle_deep = cycle_deep_max
		else:
			cycle_deep = cycle

		if cycle_deep_max == 0:
			cycle_deep = 0
		
		try:

			curr_dataset_path = scenario_directory+'/'+str(cycle)+'/dataset.hdf5'
			curr_dataset = h5py.File(curr_dataset_path, 'a')
			#inizializzo fback_matrix_updated con i valori della simulazione corrente
			curr_dataset['fback_matrix_updated'][:] = curr_dataset['fback_matrix'][:]

			for i in range(0,cycle_deep):
				print(".")
				prev_dataset_path = scenario_directory+'/'+str(cycle-1-i)+'/dataset.hdf5'
				prev_dataset = h5py.File(prev_dataset_path, 'a')

				for j in range(self.scenario.N):

					pos_forgetting_factor = ((cycle_deep_max-i-1)/cycle_deep_max)*TNSLAsettings.pos_forgetting_factor
					neg_forgetting_factor = ((cycle_deep_max-i-1)/cycle_deep_max)*TNSLAsettings.neg_forgetting_factor

					curr_dataset['fback_matrix_updated'][:,j,0] += np.array(prev_dataset['fback_matrix'][:,j,0]) * pos_forgetting_factor   #(1.0-(i/(cycle_deep+1)))
					curr_dataset['fback_matrix_updated'][:,j,1] += np.array(prev_dataset['fback_matrix'][:,j,1]) * neg_forgetting_factor #(1.0-(i/(cycle_deep+2)))

		except IOError:
			print("error read prev dataset")
			pass	
		

	'''
	def calcRevenue(self, trace):


		if self.scenario.isFraud(trace[Csv.FRAUD]):

			self.revenue_termin += TraceConfig.termin_loss*TraceConfig.average_call_duration
			self.revenue_fraudster += TraceConfig.fraud_gain*TraceConfig.average_call_duration
			self.revenue_transit += TraceConfig.transit_fee*TraceConfig.average_call_duration
	'''

	def calcRevenue2(self, trace):


		if self.scenario.isFraud(trace[Csv.FRAUD]):

			self.revenue_termin += TraceConfig.local_tariff*TraceConfig.average_call_duration
			self.revenue_fraudster += (TraceConfig.international_tariff-TraceConfig.local_tariff)*TraceConfig.average_call_duration
			self.revenue_transit += TraceConfig.transit_fee*(self.scenario.l_chain-1)*TraceConfig.average_call_duration

		else:
			self.revenue_termin += TraceConfig.international_tariff*TraceConfig.average_call_duration
			self.revenue_transit += TraceConfig.transit_fee*(self.scenario.l_chain)*TraceConfig.average_call_duration
