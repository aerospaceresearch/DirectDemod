'''
Object for json manipulation
'''
import json
import urllib
import numpy as np

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
