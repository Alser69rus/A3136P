import unittest

import opc.test_ai
import opc.test_ao
import opc.test_di
import opc.test_do
import opc.test_multimeter
import opc.test_M7084
import opc.test_gen
import opc.test_port
import opc.test_pchv
import menu.tstMenu
import tests.test_icpdas


tst = unittest.TestSuite()
loader = unittest.TestLoader()
runner = unittest.TextTestRunner(verbosity=2)

# tests.addTests(loader.loadTestsFromModule(opc.test_multimeter))
#tests.addTests(loader.loadTestsFromModule(opc.test_do))
#tests.addTests(loader.loadTestsFromModule(opc.test_di))
#tests.addTests(loader.loadTestsFromModule(opc.test_ao))
#tests.addTests(loader.loadTestsFromModule(opc.test_ai))
tst.addTest(loader.loadTestsFromModule(tests.test_icpdas))

#tests.addTests(loader.loadTestsFromModule(opc.test_M7084))
#tests.addTests(loader.loadTestsFromModule(opc.test_port))
#tests.addTests(loader.loadTestsFromModule(opc.test_gen))
# tests.addTests(loader.loadTestsFromModule(opc.test_pchv))
# tests.addTest((loader.loadTestsFromModule(menu.tstMenu)))

runner.run(tst)
input()
