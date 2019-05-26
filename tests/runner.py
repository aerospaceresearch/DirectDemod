import unittest
import os

if __name__ == '__main__':
    loader = unittest.TestLoader()
    test_dir = os.path.abspath('tests')
    suite = loader.discover(test_dir)

    runner = unittest.TextTestRunner()
    runner.run(suite)
