
class TraceConfig:


	n_chunk = 1000
	
	simBoxTraffic = 18000 #minuti al giorno, 60 sim con 5 ore di funzionamento cadauna ala giorno
	average_call_duration = 6 #Average call duratio	


	international_tariff = 0.15
	local_tariff = 0.05

	transit_fee = 0.01
	min_fraudster_tariff = 0.03

	fraud_gain = 0.06
	fraud_gain_min = 0.03
	termin_loss = 0.15


class TrustConfig:

	fraudsters_camouflage = True
	pretrust_strategy = False
	simmetry_strategy = True
	l_cascade_agreements = 1 # minore di l_chain 1,2,3

class TNSLAsettings:
	trustee_score = 0.8
	cycle_deep_max = 10
	pos_forgetting_factor = 0.1
	neg_forgetting_factor = 1.0
	pretrust_agreements = 4
	use_pretrust = False



class Csv:
	ID = 0
	FRAUD = 1
	ORIGIN = 2
	TERMIN = 3
	TRANSIT = 4



class Tools:
	@staticmethod
	def printProgress(i,n):
		if i == n//100*10:
			print("10%")
		elif i == n//100*20:
			print("20%")
		elif i == n//100*30:
			print("30%")
		elif i == n//100*40:
			print("40%")
		elif i == n//100*50:
			print("50%")
		elif i == n//100*60:
			print("60%")
		elif i == n//100*70:
			print("70%")
		elif i == n//100*80:
			print("80%")
		elif i == n//100*90:
			print("90%")
		elif i == n-1:
			print("100%")
		return
		

		