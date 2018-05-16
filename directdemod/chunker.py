'''
chunking helper
'''
import directdemod.constants as constants
import math

'''
This object is just to help in chunking process
It is responsible for creating chunks of the signal and store the info to be used later
It can be helpful for avoiding border issues in filters and demods
'''
class chunker:
	'''
	# Description: initialize the object
	# Inputs: commSignal object to be chunked, chunkSize, Outputs: -
	'''
	def __init__(self, sigsrc, chunkSize = constants.PROC_CHUNKSIZE):
		self.__nChunks = math.ceil(sigsrc.length*1.0/chunkSize)
		self.__chunks = []
		i = 0

		# create normal sized chunks
		while(i + chunkSize < sigsrc.length):
			self.__chunks.append([i,i + chunkSize])
			i += chunkSize 

		# has it exhaused the whole signal?
		if len(self.__chunks) == 0:
			self.__chunks.append([0,sigsrc.length])
		else: # if not put the remaining as another smaller chunk
			if not self.__chunks[-1][1] == sigsrc.length:
				self.__chunks.append([self.__chunks[-1][1],sigsrc.length])

	'''
	# Description: get the created chunks
	# Inputs: -, Outputs: chunks list
	'''
	@property
	def getChunks(self):
		return self.__chunks