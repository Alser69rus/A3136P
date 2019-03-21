import unittest
import os

tests=unittest.defaultTestLoader.discover(os.path.dirname(__file__))
runner=unittest.TextTestRunner(verbosity=2)
runner.run(tests)
input()