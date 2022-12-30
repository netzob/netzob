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
import uuid
import time
import random
import string
import unittest
import os
import sys

# insert in the path the directory where _libNeedleman.pyd is
if os.name == 'nt':
    sys.path.insert(0, 'lib/libNeedleman/')

try:
    # Verify that libNeedleman is in the path
    from netzob import _libNeedleman
except:
    # Else, assume the path is gotten from the 'python setup.py build' command
    arch = os.uname()[-1]
    python_version = sys.version[:3]
    build_lib_path = "../../../../build/lib.linux-" + arch + "-" + python_version
    sys.path.append(build_lib_path)

from netzob.Common.ExecutionContext import ExecutionContext
from netzob.Model.RawMessage import RawMessage
from netzob.Common.Symbol import Symbol
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Inference.Vocabulary.Alignment.UPGMA import UPGMA

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


class test_UPGMAInC(unittest.TestCase):

    def generateRandomString(self, min_len, max_len):
        return ''.join((random.choice(string.letters + string.digits) for _ in range(random.randint(min_len, max_len))))

    def test_deserialisationGroups(self):
        print("start")

        symbols = []
        nbSymbol = random.randint(2, 50)

        for iSymbol in range(0, nbSymbol):
            # We create 6 messages of 2 group
            originalSymbol = Symbol(str(uuid.uuid4()), "TestSymbol", None)
            # group1
            message1 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("bonjour " + self.generateRandomString(20, 30) + " comment vas-tu ?"))
            message2 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("bonjour " + self.generateRandomString(20, 30) + " comment vas-tu ?"))
            message3 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("bonjour " + self.generateRandomString(20, 30) + " comment vas-tu ?"))
            # group2
            message4 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("salut à toi " + self.generateRandomString(10, 15) + " what's up ?"))
            message5 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("salut à toi " + self.generateRandomString(10, 15) + " what's up ?"))
            message6 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("salut à toi " + self.generateRandomString(10, 15) + " what's up ?"))

            originalSymbol.addMessage(message1)
            originalSymbol.addMessage(message2)
            originalSymbol.addMessage(message3)
            originalSymbol.addMessage(message4)
            originalSymbol.addMessage(message5)
            originalSymbol.addMessage(message6)
            symbols.append(originalSymbol)

        # Start the clustering
        clusteringSolution = UPGMA(None, [originalSymbol], True, 100, 90, True)
        result = clusteringSolution.deserializeGroups(symbols)
        self.assertEqual(result, len(symbols))
