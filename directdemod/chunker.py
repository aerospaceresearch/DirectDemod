'''
chunking helper
'''
import directdemod.constants as constants
import math

class chunker:
	def __init__(self, sigsrc, chunkSize = constants.PROC_CHUNKSIZE):
		self.__nChunks = math.ceil(sigsrc.length*1.0/chunkSize)
		self.chunks = []
		i = 0
		while(i + chunkSize < sigsrc.length):
			self.chunks.append([i,i + chunkSize])
			i += chunkSize 
		if len(self.chunks) == 0:
			self.chunks.append([0,sigsrc.length])
		else:
			if not self.chunks[-1][1] == sigsrc.length:
				self.chunks.append([self.chunks[-1][1],sigsrc.length])

	def getChunks(self):
		return self.chunks