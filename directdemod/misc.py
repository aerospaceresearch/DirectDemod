'''
library checker
'''
import os.path
import json
import urllib
import numpy as np

from datetime import datetime

'''
The class provides functionality to determine whether all needed
libraries are installed and functional.
'''

class Checker:

    '''
    The class provides functionality to determine whether all needed
    libraries are installed and functional.
    '''

    @staticmethod
    def is_file(filename):

        '''check if given path is a file

        Args:
            filename (:obj:`string`): path

        Returns:
            :obj:`bool`: true if file, else otherwise
        '''

        return os.path.isfile(filename)

    @staticmethod
    def is_dir(dirname):

        '''check if given path is directory

        Args:
            dirname (:obj:`string`): path

        Returns:
            :obj:`bool`: true directory, else otherwise
        '''

        return os.path.isdir(filename)

    @staticmethod
    def check_libs():
        '''check if pyorbital and (cartopy or basemap) are installed

        Throws:
            :obj:`ModuleNotFoundError`: if module is not installed
        '''

        if not Checker.check_pyorbital():
            raise ModuleNotFoundError("Pyorbital must be installed.")

        if not Checker.check_cartopy() and not Checker.check_basemap():
            raise ModuleNotFoundError("Cartopy or Basemap must be installed.")

    @staticmethod
    def check_pyorbital():
        '''check if pyorbital is installed

        Returns:
            :obj:`bool`: true if installed, false otherwise
        '''

        try:
            import pyorbital
            from pyorbital import tlefile
            from pyorbital.orbital import Orbital
            return True
        except ModuleNotFoundError:
            return False

    @staticmethod
    def check_cartopy():
        '''check if cartopy is installed

        Returns:
            :obj:`bool`: true if installed, false otherwise
        '''

        try:
            import cartopy
            import cartopy.crs
            import cartopy.feature
            return True
        except ModuleNotFoundError:
            return False

    @staticmethod
    def check_basemap():
        '''check if basemap is installed

        Returns:
            :obj:`bool`: true if installed, false otherwise
        '''

        try:
            import mpl_toolkits.basemap
            from mpl_toolkits.basemap import Basemap
            return True
        except ModuleNotFoundError:
            return False

'''
Object for json manipulation
'''

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

        Returns:
            :obj:`object`: encoded object
        '''

        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super.default(self, obj)

class JsonParser:

    '''
    Wrapper class over json module to add numpy and datetime json serialization
    '''

    @staticmethod
    def to_string(json_dict):

        '''convert dict to json string

        Args:
            json_dict (:obj:`dict`): object to convert

        Returns:
            :obj:`string`: json string
        '''

        return json.dumps(json_dict, cls=Encoder)

    @staticmethod
    def from_string(str):

        '''convert json string to dict

        Args:
            str (:obj:`string`): string to convert

        Returns:
            :obj:`dict`: json dictionary
        '''

        return json.loads(str)

    @staticmethod
    def from_file(filename):

        '''convert text from file into json dict

        Args:
            filename (:obj:`string`): path to file

        Returns:
            :obj:`dict`: json dictionary
        '''

        with open(filename, 'r') as f:
            return json.load(f)

    @staticmethod
    def from_url(url):

        '''convert text from url into json dict

        Args:
            filename (:obj:`string`): path to url

        Returns:
            :obj:`dict`: json dictionary
        '''

        return json.load(urllib.urlopen(url))

    @staticmethod
    def save(json_dict, output_file):

        '''serialize json dict into file

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
