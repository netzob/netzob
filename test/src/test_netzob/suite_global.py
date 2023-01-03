#!/usr/bin/python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import unittest
import sys

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from test_netzob import suite_Common
from test_netzob import suite_Tutorials
from test_netzob import suite_DocTests
import test_netzob.test_public_api as test_public_api

#from test_netzob import suite_Import
from common.xmlrunner import XMLTestRunner


def getSuite():
    globalSuite = unittest.TestSuite()

    modulesOfTests = []
    modulesOfSuites = [
        suite_DocTests,  # tests extracted from docstrings (doctests)
        # suite_Common,
        # suite_Tutorials
    ]
    modulesOfTests = []  #test_public_api]

    # Add individual tests
    for module in modulesOfTests:
        globalSuite.addTests(unittest.TestLoader().loadTestsFromModule(module))

    # Add suites
    for module in modulesOfSuites:
        globalSuite.addTests(module.getSuite())

    return globalSuite

if __name__ == "__main__":
    # Output is given through argument.
    # If no argument: output to stdout
    outputStdout = True

    if (len(sys.argv) == 2):
        outputStdout = False
        reportFile = sys.argv[1]

    # We retrieve the current test suite
    currentTestSuite = getSuite()

    # We execute the test suite
    if outputStdout:
        runner = unittest.TextTestRunner()
        testResult = runner.run(currentTestSuite)
    else:
        File = open(reportFile, "w")
        reporter = XMLTestRunner(File)
        reporter.run(currentTestSuite)
        File.close()
