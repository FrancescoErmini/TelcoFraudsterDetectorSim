import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config import TraceConfig,TNSLAsettings
import random

class Plot():

	def __init__(self, scenario):
		super(Plot, self).__init__()
		self.scenario = scenario
		
	def nodeColor(self, index):


		red_colors = ['red','orangered','crimson','firebrick','tomato','indianred','lightcoral']
		green_colors = ['green','forestgreen','limegreen','darkgreen','mediumseagreen','seagreen','springgreen','lime','limegreen']
		if self.scenario.isFraudster(index):
			return red_colors[random.randint(0,6)]
		else:
			return green_colors[random.randint(0,8)]

		

	def transitivity(self, targets, results):	


		x = [i for i in range(self.scenario.cycles)]

		df=pd.DataFrame({'x': x, 'n1': results[:,0], 'n2': results[:,1], 'n3': results[:,2], 'n4': results[:,3]})
		plt.style.use('seaborn')#-darkgrid
		palette = plt.get_cmap('Set1')
		num=0
		for column in df.drop('x', axis=1):
			
			plt.plot(df['x'], df[column], marker='', color=self.nodeColor(targets[num]), linewidth=1, alpha=0.9, label=column)
			num+=1
		plt.plot([0., self.scenario.cycles], [0.5, 0.5], "k--")
		plt.text(self.scenario.cycles-2, 0.37, 'fraudster', fontsize=12)
		plt.plot([0., self.scenario.cycles], [TNSLAsettings.trustee_score, TNSLAsettings.trustee_score], "k--")
		plt.text(self.scenario.cycles-2, TNSLAsettings.trustee_score+0.01, 'honests', fontsize=12)
		
		plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), shadow=True, fancybox=True,ncol=4, borderaxespad=0.)
		plt.xlabel("cycles")
		plt.ylabel("trust score")
		plt.show()	

	def statistics(self, result):

		plt.figure(1)
		plt.title("fraudsters detection statistics")
		plt.text(-1, -1.2, 'fraud behaviour: '+str(result.getFraudBehaviour()), fontsize=12)
		
		labels = 'detected', 'suspected', 'errors', 'missed'
		sizes = [result.fraudsters_detection, result.fraudsters_detection_suspect, result.fraudsters_detection_error, result.fraudsters_detection_missing]
		colors = ['yellowgreen', 'gold', 'lightcoral', 'lightskyblue']
		patches, texts = plt.pie(sizes, colors=colors, shadow=False, startangle=90)
		plt.legend(patches, labels, loc="best")
		plt.axis('equal')
		plt.tight_layout()

		plt.figure(2)
		plt.title("honests detection statistics")
		plt.text(-1, -1.2, 'fraud behaviour: '+str(result.getFraudBehaviour()), fontsize=12)

		sizes = [result.honests_detection, result.honests_detection_suspect, result.honests_detection_error, result.honests_detection_missing]
		colors = ['yellowgreen', 'gold', 'lightcoral', 'lightskyblue']
		patches, texts = plt.pie(sizes, colors=colors, shadow=False, startangle=90)
		plt.legend(patches, labels, loc="best")
		plt.axis('equal')
		plt.tight_layout()


		plt.show()

	def trustScore(self, honests_score_avg, fraudsters_score_avg,fraudBehaviour):
		N = len(honests_score_avg)
		ind = np.arange(N)
		width = 0.9
		fig, ax = plt.subplots()
		rects1 = ax.bar(ind-width/2, honests_score_avg, width, color='green')
		rects2 = ax.bar(ind+width/2, fraudsters_score_avg, width, color='red')
		
		ax.set_ylabel('reputation score')
		ax.set_xlabel('cycles')
		
		ax.legend((rects1[0], rects2[0]), ('honests', 'fraudsters'), bbox_to_anchor=(1.0,1.0))
		plt.plot([-width, N-1+width], [0.5, 0.5], "k--")
		plt.plot([-width, N-1+width], [TNSLAsettings.trustee_score, TNSLAsettings.trustee_score], "k--")
		plt.text(0, 1.1, 'fraud behaviour: '+str(fraudBehaviour), fontsize=12)
		plt.tight_layout()
		plt.show()

	def plotPie(self, result):

		detect = result.fraudsters * 100.0 / result.fraudsters_tot
		suspect = result.suspected_fraudsters * 100.0 / result.fraudsters_tot
		miss = result.unknown_fraudsters * 100.0 / result.fraudsters_tot
		fn = result.falsenegative * 100.0 / result.fraudsters_tot
		fp = result.falsepositive * 100.0 / result.honests_tot

		delay = self.scenario.n_calls/240000
		days = delay * self.scenario.cycles
		simbox_capacity = ((self.scenario.n_calls_fraud * TraceConfig.average_call_duration // self.scenario.n_fraudsters)//delay)*100/TraceConfig.simBoxTraffic 


		plt.figure(1)
		plt.title("Detection Stat at "+str(days)+"th day")
		
		plt.text(-0.7,-1.2,str(simbox_capacity)+"% simbox capacity "+str(result.scenario.frauds_percentage)+"% frauds",fontsize=11)

		labels = 'detect','suspect', 'fn','fp', 'miss'
		sizes = [detect, suspect, fn, fp, miss]
		colors = ['yellowgreen', 'gold', 'lightcoral','crimson','lightskyblue']

		labelspp = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(labels, sizes)]

		patches, texts = plt.pie(sizes, colors=colors, pctdistance=1.1, shadow=False, startangle=90,counterclock=False)
		plt.legend(patches, labelspp, loc="upper right", bbox_to_anchor=(1., 1.),fontsize=10)
		
		plt.axis('equal')
		plt.tight_layout()
		plt.show()

	def plotBars(self, revenues):

		N = self.scenario.cycles
		ind = np.arange(N)
		width = 0.3
		fig, ax = plt.subplots()
		rects1 = ax.bar(ind+width*0, revenues[0], width, color='yellowgreen', yerr=0)
		rects2 = ax.bar(ind+width*1, revenues[1], width, color='lightskyblue', yerr=1)
		rects3 = ax.bar(ind+2*width, revenues[2], width, color='lightcoral', yerr=2)
		
		ax.set_ylabel('profits')
		ax.set_xlabel('cycles')
		
		ax.legend((rects1[0], rects2[0], rects3[0]), ('termin', 'transit','fraudsters'), bbox_to_anchor=(1.0,1.0))
		
		plt.tight_layout()
		plt.show()

	def plotBars2(self, revenues, case):
		x = [i for i in range(self.scenario.cycles)]
		str_termin = 'Termin Loss'+'('+str(TraceConfig.termin_loss)+' c)'
		str_transit = 'Transit Loss'+'('+str(TraceConfig.transit_fee)+' c)'
		str_fraud = 'Fraud Gain'+'('+str(TraceConfig.fraud_gain)+' c)'


		termin_loss = revenues[0,:]
		transit_loss = revenues[1,:]
		fraud_gain = revenues[2,:]

		
		df=pd.DataFrame({'x': x, str_termin:termin_loss, str_transit:transit_loss, str_fraud:fraud_gain})
		
		num=0
		for column in df.drop('x', axis=1):
			plt.plot(df['x'], df[column], marker='', color=self.getColor(num), linestyle=self.getStyle(case), linewidth=2, alpha=0.9, label=column)
			num+=1

	def plotBars3(self, revenues, threshold, case):
		x = [i for i in range(self.scenario.cycles)]

		termin = 'termin'
		transit = 'transit'
		fraud  = 'fraud'

		str_termin = 'Termin Loss'+'('+str(TraceConfig.termin_loss)+' c)'
		str_transit = 'Transit Loss'+'('+str(TraceConfig.transit_fee)+' c)'
		str_fraud = 'Fraud Gain'+'('+str(TraceConfig.fraud_gain)+' c)'


		termin_loss = revenues[0,:]
		transit_loss = revenues[1,:]
		fraud_gain = revenues[2,:]

		df=pd.DataFrame({'x': x, 'termin':termin_loss, 'transit':transit_loss, 'fraud':fraud_gain})


		plt.subplot(1, 3, 1)
		plt.plot(df['x'], df['termin'], marker='', color=self.getColor2('termin',case), linewidth=2, alpha=0.9, label=str_termin)
		plt.subplot(1, 3, 2)
		plt.plot(df['x'], df['transit'], marker='', color=self.getColor2('transit',case), linewidth=2, alpha=0.9, label=str_transit)
		plt.subplot(1, 3, 3)
		plt.plot(df['x'], df['fraud'], marker='', color=self.getColor2('fraud',case), linewidth=2, alpha=0.9, label=str_fraud)
		plt.ylabel("Profits [Euros] ")



	def plotDetectResult(self, blacklists, fraudBehaviour):
		x = [i for i in range(self.scenario.cycles)]

		detects = []
		errors = []

		min_profit_curve = []
		max_profit_curve = []
		real_profit_curve = []

		days = self.scenario.n_calls // 240000

		up_tariff = TraceConfig.fraud_gain
		low_tariff = TraceConfig.fraud_gain_min
		
		fraudmins_per_fraudster = (self.scenario.n_calls_fraud * TraceConfig.average_call_duration) / self.scenario.n_fraudsters
		max_profit_per_cycle = fraudmins_per_fraudster * up_tariff


		low_limit = 18000*low_tariff*days #euros week compute as 18000min fraud per day times 7 days times 0.10 euros minute
		up_limit =  18000*up_tariff*days #euros week compute as 18000min fraud per day times 7 days times 0.03 euros minute
		
		min_profit = -5233
		max_profit = -5233
		real_profit = -5233



		for blacklist in blacklists:

			fraudsters = 0
			falsepositives = 0

			min_profit += low_limit
			max_profit += up_limit

			min_profit_curve.append(min_profit)
			max_profit_curve.append(max_profit)

			for node in blacklist:
				if self.scenario.isFraudster(node):
					print("found fraudster")
					fraudsters+=1
				else:
					print("fp fraudster")
					falsepositives+=1

			pDetect = fraudsters*100/self.scenario.n_fraudsters
			pError = falsepositives*100/self.scenario.n_honests

			detects.append(pDetect)
			errors.append(pError)

			real_profit += (max_profit_per_cycle-max_profit_per_cycle*pDetect/100)
			real_profit_curve.append(real_profit)

		print("min "+str(min_profit_curve[0])+" max "+str(max_profit_curve[0])+" real "+str(real_profit_curve[0]))




		N = len(blacklists)
		ind = np.arange(N)  
		width = 0.45  
		

		plt.style.use('seaborn')#-darkgrid
		palette = plt.get_cmap('Set1')

		fig, axes = plt.subplots(nrows=1, ncols=2)
		ax, ax2 = axes.flatten()

		rects1 = ax.bar(ind+width*0, detects, width, color='yellowgreen')
		rects2 = ax.bar(ind+width*1, errors, width, color='crimson')
		
		for rect in rects1:
			height = rect.get_height()
			ax.text(rect.get_x() + rect.get_width()/2., 0.99*height,'%d' % int(height) + "%", ha='center', va='bottom')
		for rect in rects2:
			height = rect.get_height()
			ax.text(rect.get_x() + rect.get_width()/2., 0.99*height,'%d' % int(height) + "%", ha='center', va='bottom')


		ax.set_ylabel('pDetect, pError')
		ax.set_xlabel('weeks')
		ax.set_title('Detection results from blacklist')
		ax.legend((rects1[0], rects2[0]), ('detects', 'errors'))

		str_min = "min ("+str(TraceConfig.fraud_gain_min)+" E)"
		str_max = "avg ("+str(TraceConfig.fraud_gain)+" E)"
		str_real = "fraud gain"

		ax2.plot(x,real_profit_curve,marker='o',  markersize=4, linewidth=3,linestyle='-',label=str_real, color='deepskyblue')
		ax2.plot(x,min_profit_curve,marker='',  linewidth=2,linestyle='--', label=str_min, color='black')
		ax2.plot(x,max_profit_curve,marker='',  linewidth=2,linestyle='--', label=str_max, color='orangered')
		ax2.legend(loc='best', ncol=3)
		ax2.set_ylabel('Euros')
		ax2.set_xlabel('weeks')
		ax2.set_title('Fraud profits analysis')

		plt.show()
		
	def plotEnd(self,days):
		plt.ylabel("Profits [Euros] ")
		plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), shadow=True, fancybox=True,ncol=3, borderaxespad=0.)
		plt.title("Cost-Benefit Analysis in "+str(days)+" days.")
		plt.show()

	def getColor2(self, role, case):

		red  = ['red','orangered','crimson','firebrick','tomato','indianred','lightcoral']
		green = ['green','forestgreen','limegreen','darkgreen','mediumseagreen','seagreen','springgreen','lime','limegreen']
		
		if role == 'termin':
			return green[case]
		
		if role == 'transit':
			return 'blue'

		if role == 'fraud':
			return red[case]

	def getStyle(self,case):
		if case == 0:
			return '--'
		else:
			return '-'


	def getColor(self, num):
		
		if num == 0:
			return 'green' #termin
		
		if num == 1:
			return 'blue' #transit

		if num == 2:
			return 'red' #fraudster




