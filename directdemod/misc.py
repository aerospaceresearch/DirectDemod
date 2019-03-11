'''
library checker
'''
import os.path

'''
The class provides functionality to determine whether all needed
libraries are installed and functional.
'''

class Checker:

    '''
    Class for checking libraries installation
    '''

    @staticmethod
    def is_file(filename):

        '''Check if give path is file

        Args:
            filename (:obj:`string`): path

        Returns:
            :obj:`bool`: is file
        '''

        return os.path.isfile(filename)

    @staticmethod
    def is_dir(dirname):

        '''Check if give path is directory

        Args:
            dirname (:obj:`string`): path

        Returns:
            :obj:`bool`: is directory
        '''

        return os.path.isdir(filename)

    @staticmethod
    def check_libs():
        '''Check if pyorbital and (cartopy or basemap) are installed.'''

        if not Checker.check_pyorbital():
            raise ModuleNotFoundError("Pyorbital must be installed.")

        if not Checker.check_cartopy() and not Checker.check_basemap():
            raise ModuleNotFoundError("Cartopy or Basemap must be installed.")

    @staticmethod
    def check_pyorbital():
        '''Check if pyorbital is installed.'''

        try:
            import pyorbital
            from pyorbital import tlefile
            from pyorbital.orbital import Orbital
            return True
        except ModuleNotFoundError:
            return False

    @staticmethod
    def check_cartopy():
        '''Check if cartopy is installed.'''

        try:
            import cartopy
            import cartopy.crs
            import cartopy.feature
            return True
        except ModuleNotFoundError:
            return False

    @staticmethod
    def check_basemap():
        '''Check if basemap is installed.'''

        try:
            import mpl_toolkits.basemap
            from mpl_toolkits.basemap import Basemap
            return True
        except ModuleNotFoundError:
            return False
