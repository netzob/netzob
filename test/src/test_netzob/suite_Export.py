#!/usr/bin/python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Sumit Acharya <sumit.acharya@uni-ulm.de>                          |
# |       - Stephan Kleber <stephan.kleber@uni-ulm.de>                        |
# +---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import unittest
from test_netzob.test_Export import test_ScapyExporter

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


def getSuite():
    exportSuite = unittest.TestSuite()

    modulesOfTests = [test_ScapyExporter]
    modulesOfSuites = []

    # Add individual tests
    for module in modulesOfTests:
        exportSuite.addTests(unittest.TestLoader().loadTestsFromModule(module))

    # Add suites
    for module in modulesOfSuites:
        exportSuite.addTests(module.getSuite())

    return exportSuite
