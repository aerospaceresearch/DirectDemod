'''
Object for different outputs e.g. image, audio.wav etc.
'''
from scipy.io.wavfile import write
import PIL

'''
This object is used to write wav files
'''
class wavFile:
	'''
	# Description: initialize the object
	# Inputs: filename of the wav file, commSignal object, Outputs: -
	'''
	def __init__(self, filename, sig):
		self.__fname = filename
		self.__sig = sig

	'''
	# Description: write the signal to wav file
	# Inputs: -, Outputs: self
	'''
	@property
	def write(self):
		write(self.__fname, self.__sig.sampRate, self.__sig.signal)
		return self

'''
This object is used to display and write images
'''
class image:
	'''
	# Description: initialize the object
	# Inputs: filename of the wav file, a matrix of pixel values, Outputs: -
	'''
	def __init__(self, filename, mat):
		self.__fname = filename
		self.__mat = mat
		self.__image = PIL.Image.fromarray(self.__mat)

	'''
	# Description: write the image to file
	# Inputs: -, Outputs: self
	'''
	@property
	def write(self):
		self.__image.save(self.__fname)
		return self

	'''
	# Description: show the image
	# Inputs: -, Outputs: self
	'''
	@property
	def show(self):
		self.__image.show()
		return self