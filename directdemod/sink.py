'''
Object for different outputs e.g. file
'''
from scipy.io.wavfile import write
import PIL

class wavFile:
	def __init__(self, filename):
		self.__fname = filename

	def write(self, sig):
		write(self.__fname, sig.sampRate, sig.signal)

class image:
	def __init__(self, filename):
		self.__fname = filename

	def write(self, matrix):
		image = PIL.Image.fromarray(matrix)
		image.save(self.__fname)


	def show(self, matrix):
		image = PIL.Image.fromarray(matrix)
		image.show()