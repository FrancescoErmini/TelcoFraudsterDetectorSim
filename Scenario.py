
class Scenario:


   def __init__(self, n_providers, n_intermidiaries, n_calls,  l_chain, fraudsters_percentage,  frauds_percentage, provider_participation, intermidiaries_participation, cycles, blacklist):
      super(Scenario, self).__init__()
      self.n_providers = n_providers
      self.n_intermidiaries = n_intermidiaries 
      self.fraudsters_percentage= fraudsters_percentage
      self.n_calls = n_calls
      self.frauds_percentage = frauds_percentage
      self.l_chain=l_chain
      self.provider_participation = provider_participation
      self.intermidiaries_participation = intermidiaries_participation

      self.n_fraudsters = int(n_intermidiaries * fraudsters_percentage / 100.0)
      self.n_calls_fraud = int(n_calls * frauds_percentage / 100.0)
      self.n_coop_providers = int(provider_participation*n_providers/100.0)
      self.n_coop_intermidiaries = int(intermidiaries_participation*(n_intermidiaries-self.n_fraudsters)/100.0)
      self.n_honests = self.n_intermidiaries - self.n_fraudsters
      self.N = n_providers + n_intermidiaries
      self.cycles = cycles
      self.blacklist = []
      self.revenue_termin = 0
      self.revenue_transit = 0
      self.revenue_fraudster = 0 
      self.use_blacklist = blacklist
      


   def printDetails(self):

      #print('trust alg: ' + args.trustalg)
      print('scenario: ' + str(self.n_providers) + ' providers,  ' + str(self.n_intermidiaries) + ' intermidiaries,  ' + str(self.fraudsters_percentage) + '[%] fradusters')
      print('transactions: ' + str(self.n_calls) + ' calls,  ' + str(self.frauds_percentage) + '[%]  call frauds,  ' + str(self.l_chain) + ' chain length')
      print('cooperation: ' + str(self.provider_participation) + '[%] providers,  ' + str(self.intermidiaries_participation) + '[%] intermidiaries')


   def isIntermidiary(self, index):

      ind = int(index)
      low = self.n_providers
      up =  self.N

      if ind in range(low,up):
         return True 
      else:
         return False

   def isProvider(self, index):

      ind = int(index)
      low = 0
      up =  self.n_providers
      
      if ind in range(low,up):
         return True
      else:
         return False

   def isFraudster(self, index):

      ind = int(index)
      low = self.n_providers+self.n_intermidiaries-self.n_fraudsters
      up =  self.n_providers+self.n_intermidiaries

      if ind in range(low,up):
         return True 
      else:
         return False

   def isFraud(self, value):

      val = int(value)

      if val == 1:
         return True
      else:
         return False

   def isCoopProvider(self, index):

      ind = int(index)
      low = int(self.n_providers/2) - int(self.n_coop_providers/2)
      up =  int(self.n_providers/2) + int(self.n_coop_providers/2)
      
      if ind in range(low,up+1):
         return True
      else:
         return False

   def isCoopIntermidiary(self, index):

      ind = int(index)
      low = self.n_providers+int((self.n_intermidiaries-self.n_fraudsters)/2)-int(self.n_coop_intermidiaries/2)
      up =  self.n_providers+int((self.n_intermidiaries-self.n_fraudsters)/2)+int(self.n_coop_intermidiaries/2)

      if ind in range(low,up+1):
         return True
      else:
         return False

   def is_blacklisted(self, index):
      if index in self.blacklist:
         return True
      else:
         return False
   def pull_from_blacklist(self, index):
      self.blacklist.remove(index)

   def push_in_blacklist(self, index):
      #avoid put index twice
      if index not in self.blacklist:

         self.blacklist.append(index)

   def dump_blacklist(self):
      return self.blacklist

   def fullfill_blacklist(self):
      low = self.n_providers+self.n_intermidiaries-self.n_fraudsters
      up =  self.n_providers+self.n_intermidiaries

      for i in range(low, up):
         self.blacklist.append(i)

   def reset_blacklist(self):

      self.blacklist = []




