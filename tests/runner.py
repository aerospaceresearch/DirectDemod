import unittest
import contextlib
import sys
import os

# python tests/runner.py 2>/dev/null
if __name__ == '__main__':
    with contextlib.redirect_stderr(sys.stdout):
        loader = unittest.TestLoader()
        test_dir = os.path.abspath('tests')
        suite = loader.discover(test_dir)

        runner = unittest.TextTestRunner()
        runner.run(suite)
