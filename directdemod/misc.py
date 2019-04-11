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

'''
Object for json manipulation
'''
import json
import urllib
import numpy as np

from datetime import datetime

'''
These classes provide API for the input/output operations
with json files.
'''

class Encoder(json.JSONEncoder):

    '''
    JSON encoder
    '''

    def default(self, obj):

        '''Encode the object

        Args:
            obj (:obj:`object`): oject to encode
        '''

        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super.default(self, obj)

class JsonParser:

    '''
    Wrapper class over json module to add numpy serialization.
    '''

    @staticmethod
    def to_string(json_dict):

        '''Convert dict to json string

        Args:
            json_dict (:obj:`dict`): object to convert

        Returns:
            :obj:`string`: json string
        '''

        return json.dumps(json_dict, cls=Encoder)

    @staticmethod
    def from_string(str):

        '''Convert json string to dict

        Args:
            str (:obj:`string`): string to convert

        Returns:
            :obj:`dict`: json dictionary
        '''

        return json.loads(str)

    @staticmethod
    def from_file(filename):

        '''Convert text from file into json dict

        Args:
            filename (:obj:`string`): path to file

        Returns:
            :obj:`dict`: json dictionary
        '''

        with open(filename, 'r') as f:
            return json.load(f)

    @staticmethod
    def from_url(url):

        '''Convert text from url into json dict

        Args:
            filename (:obj:`string`): path to url

        Returns:
            :obj:`dict`: json dictionary
        '''

        return json.load(urllib.urlopen(url))

    @staticmethod
    def save(json_dict, output_file):

        '''Serialize json dict into file

        Args:
            json_dict (:obj:`dict`): dictionary
            output_file (:obj:`string`): path to file
        '''

        with open(output_file, 'w') as out:
            json.dump(json_dict, out, cls=Encoder)

if __name__ == "__main__":
    import os

    filename = "../samples/image_desc.json"

    jstr1 = JsonParser.from_file(filename)
    jstr2 = JsonParser.from_string(open(filename, 'r').read())

    print(jstr1)
    print(jstr2)
    print(jstr1 == jstr2)
    print(type(jstr1) == dict)

    test_file = 'sample_desc.json'
    JsonParser.save_json(jstr1, test_file)
    os.remove(test_file)
