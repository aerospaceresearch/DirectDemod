'''
Object for logging
'''
import numpy as np
import scipy.signal as signal
from directdemod import filters, constants
import logging

'''
Object for logging into a file/function call back
'''

class log():

    '''
    Object for logging
    '''

    def __init__(self, file = None, console = False):

        '''Initialize the object
        
        Args:
            file (:obj:`str`, optional): Filename, if log is to be stored into a file
            console (:obj:`bool`, optional): Enables console logging

        '''

        self.__file = file
        self.__console = console


        logging.getLogger('').setLevel(logging.DEBUG)

        if not self.__file is None:
            logging.basicConfig(filename=self.__file, level=logging.DEBUG, format='%(asctime)-13s.%(msecs)-4d %(levelname)-8s %(message)s [%(filename)s:%(lineno)d]', datefmt='%d-%m-%Y %H:%M:%S')

        if self.__console:
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter('%(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)