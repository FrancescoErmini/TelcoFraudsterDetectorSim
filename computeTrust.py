import argparse
import os
import csv
import random

from TrustMan import *
from TraceGenerator import *
from config import *
from Scenario import Scenario
from TNSLA import *
from Result import *
from Dataset import Dataset
from Plot import *

def main():

	parser = argparse.ArgumentParser(prog='TRACES GENERATOR')
	#abs params
	parser.add_argument('--providers',  type=int, help="Number of local telco providers" )
	parser.add_argument('--intermidiaries', type=int, help="Number of intermidiary providers" )
	parser.add_argument('--calls', type=int, help="Number of calls" )
	parser.add_argument('--hops', type=int, help="Numer of hops per call" )

	#percentage params
	parser.add_argument('--fraudsters', type=float, help="Percentage of fraudolent intemidiaraies" )
	parser.add_argument('--frauds', type=float, help="Percentage of fraud calls. " )
	parser.add_argument('--pcoop', type=float, help="Percentage of cooperation provider " )
	parser.add_argument('--icoop', type=float, help="Percentage of cooperation intermidiaries. " )
	parser.add_argument('--cycles', type=int, help="Number of traces to simulate" )

	parser.add_argument('--scenario', help="Name of the simulation directory" )
	parser.add_argument('--useblacklist', dest='blacklist', action='store_true')
	parser.add_argument('--no-useblacklist', dest='blacklist', action='store_false')
	parser.set_defaults(blacklist=True)
	
	args = parser.parse_args()

	#create an istance of TraceGenerator with the params from cli
	scenario =  Scenario(n_providers=int(args.providers), 
					n_intermidiaries=int(args.intermidiaries), 
					n_calls=int(args.calls), 
					l_chain = int(args.hops),
					fraudsters_percentage=float(args.fraudsters), 
					frauds_percentage=float(args.frauds),
					provider_participation = int(args.pcoop),
					intermidiaries_participation = int(args.icoop),
					cycles = int(args.cycles),
					blacklist=args.blacklist)

	print('\n\nstart simulation: ' + args.scenario +'\n')	

	N = scenario.n_providers + scenario.n_intermidiaries
	cycles = int(args.cycles)
	sources = [x for x in range(0,scenario.n_providers,10)]
	
	step = 1
	targets = [(x+scenario.n_providers) for x in range(0,scenario.n_intermidiaries,step)]
	for f in range(scenario.n_fraudsters):
		targets[scenario.n_intermidiaries//step-f-1] = N-f-1
	
	results = np.zeros((cycles,len(targets)))
	revenues = np.zeros((3,cycles))
	days=0

	blacklist_history = []


	for c in range(cycles):

		scenario_directory = 'simulation/' + args.scenario

		trace_file  =  scenario_directory + '/' + str(c) + '/traces.csv'
		result_file = scenario_directory  + '/results/result.txt'

		dataset = Dataset(N, scenario_directory, c)
		dataset.destroy()
		dataset.create()


		if (c)%4 == 0 and scenario.use_blacklist:
			scenario.reset_blacklist()

		traceGenerator = TraceGenerator(scenario=scenario)
		traceGenerator.createCsv(file=trace_file)

		manager = TrustMan(scenario=scenario, dataset=dataset)
		manager.createFeedbackMatrix(infile=trace_file)
		manager.updateFeedbackMatrix(scenario_directory=scenario_directory, cycle=c)

		result = Result(scenario=scenario,dataset=dataset, manager=manager)
		days+=result.calcDelay()
		print("\n\nPERIOD: "+str(days))
		print("Blacklisted operators are:")
		blacklist_history.append(scenario.blacklist[:])
		print(scenario.blacklist)

		trust = TNSLA(scenario=scenario, dataset=dataset)
		
		for i in range(len(targets)):
			Tools.printProgress( i, len(targets))

			for j in range(len(sources)):
				if scenario.isCoopProvider(sources[j]):
					results[c][i] = trust.computeTrust2(sources[j], targets[i])

					#print("\nTrust from "+str(sources[j])+" to "+str(targets[i])+" at period "+str(c)+"th is "+str(results[c][i]))
					res = result.fraudsterClassifier2(targets[i], results[c][i])
					if res and scenario.use_blacklist: #is Fraudster
						scenario.push_in_blacklist(targets[i])		
			
		result.printRes()
		scenario.revenue_termin += manager.revenue_termin
		scenario.revenue_transit += manager.revenue_transit
		scenario.revenue_fraudster += manager.revenue_fraudster

		revenues[0][c]=scenario.revenue_termin
		revenues[1][c]=scenario.revenue_transit
		revenues[2][c]=scenario.revenue_fraudster

	plot = Plot(scenario=scenario)
	#plot.plotDetectResult(blacklist_history, result.getFraudBehaviour())
	plot.plotPie(result)

	'''
	if os.path.isfile(sim_root+'/info/sim_params.csv'):
		os.remove(sim_root+'/info/sim_params.csv')

	with open(sim_root+'/info/sim_params.csv', mode='w') as info:
		writer = csv.writer(info, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(["providers", "intermidiaries","fraudsterspercentage", "l_chain","calls","fraudspercentage", "n_coop_providers", "n_coop_intermidiaries", "fraudster_camuflage", "simmetry_strategy", "pretrust_strategy"])
		writer.writerow([scenario.n_providers, scenario.n_intermidiaries, scenario.fraudsters_percentage, scenario.l_chain, scenario.n_calls, scenario.frauds_percentage, scenario.provider_participation, scenario.intermidiaries_participation, TrustConfig.fraudsters_camouflage, TrustConfig.simmetry_strategy, TrustConfig.pretrust_strategy])
	'''
if __name__ == '__main__':
   main()