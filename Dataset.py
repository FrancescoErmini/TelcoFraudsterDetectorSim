import h5py
import os, sys

class Dataset:


	def __init__(self, dimension, directory, cycle):
		super(Dataset, self).__init__()
		self.directory = directory
		self.cycle = cycle
		self.dimension = dimension
		self.dataset = self.directory + '/' + str(self.cycle) + '/dataset.hdf5'

	def create(self):

		N = self.dimension
		if not os.path.exists(self.directory+'/'+str(self.cycle)):
			print ("create dir: "+self.directory+'/'+str(self.cycle))
			os.makedirs(self.directory+'/'+str(self.cycle))

		with h5py.File(self.dataset, "a") as f:
			f.create_dataset("fback_matrix", shape=(N,N,2), dtype='uint16')
			f.create_dataset("normal_matrix", shape=(N,N), dtype='uint16')
			f.create_dataset("opinion_matrix", shape=(N,N,4), dtype='uint16')
			f.create_dataset("trust_score", shape=(N,0))
			f.create_dataset("fback_matrix_updated", shape=(N,N,2), dtype='float16')
	
	def destroy(self):
		if os.path.isfile(self.dataset):
			os.remove(self.dataset)