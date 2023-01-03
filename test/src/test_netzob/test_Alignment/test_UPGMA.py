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

from netzob.Common.ExecutionContext import ExecutionContext
from netzob.Model.RawMessage import RawMessage
from netzob.Common.Symbol import Symbol
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Inference.Vocabulary.Alignment.UPGMA import UPGMA
from netzob.Common.Type.Format import Format

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


class test_UPGMA(unittest.TestCase):

    def generateRandomString(self, min_len, max_len):
        return ''.join((random.choice(string.letters + string.digits) for _ in range(random.randint(min_len, max_len))))

    def test_executingClustering(self):

        # We create 6 messages of 2 group

        # group1
        originalSymbol1 = Symbol(str(uuid.uuid4()), "TestSymbol", None)
        message1 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("bonjour " + self.generateRandomString(20, 30) + " comment vas-tu ?"))
        originalSymbol1.addMessage(message1)

        originalSymbol2 = Symbol(str(uuid.uuid4()), "TestSymbol2", None)
        message2 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("bonjour " + self.generateRandomString(20, 30) + " comment vas-tu ?"))
        originalSymbol2.addMessage(message2)

        originalSymbol3 = Symbol(str(uuid.uuid4()), "TestSymbol3", None)
        message3 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("bonjour " + self.generateRandomString(20, 30) + " comment vas-tu ?"))
        originalSymbol3.addMessage(message3)

        # group2
        originalSymbol4 = Symbol(str(uuid.uuid4()), "TestSymbol4", None)
        message4 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("salut à toi " + self.generateRandomString(10, 15) + " what's up ?"))
        originalSymbol4.addMessage(message4)

        originalSymbol5 = Symbol(str(uuid.uuid4()), "TestSymbol5", None)
        message5 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("salut à toi " + self.generateRandomString(10, 15) + " what's up ?"))
        originalSymbol5.addMessage(message5)

        originalSymbol6 = Symbol(str(uuid.uuid4()), "TestSymbol6", None)
        message6 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("salut à toi " + self.generateRandomString(10, 15) + " what's up ?"))
        originalSymbol6.addMessage(message6)

        symbols = [originalSymbol1, originalSymbol2, originalSymbol3, originalSymbol4, originalSymbol5, originalSymbol6]

        # Start the clustering
        clusteringSolution = UPGMA(None, symbols, True, 100, 90, True, Format.ASCII)
        result = clusteringSolution.executeClustering()

        for symbol in result:
            print("Symbol: " + str(symbol.getName()))
            for m in symbol.getMessages():
                print(" + " + str(m.getStringData()))

    def test_executingClusteringWithOrphanReduction(self):

        # We create 6 messages of 2 group

        # group1
        originalSymbol1 = Symbol(str(uuid.uuid4()), "TestSymbol", None)
        message1 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("bonjour " + self.generateRandomString(200, 1000)))
        originalSymbol1.addMessage(message1)

        originalSymbol2 = Symbol(str(uuid.uuid4()), "TestSymbol2", None)
        message2 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("bonjour " + self.generateRandomString(200, 1000)))
        originalSymbol2.addMessage(message2)

        originalSymbol3 = Symbol(str(uuid.uuid4()), "TestSymbol3", None)
        message3 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("bonjour " + self.generateRandomString(200, 1000)))
        originalSymbol3.addMessage(message3)

        # group2
        originalSymbol4 = Symbol(str(uuid.uuid4()), "TestSymbol4", None)
        message4 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("salut " + self.generateRandomString(200, 1000)))
        originalSymbol4.addMessage(message4)

        originalSymbol5 = Symbol(str(uuid.uuid4()), "TestSymbol5", None)
        message5 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("salut " + self.generateRandomString(200, 1000)))
        originalSymbol5.addMessage(message5)

        originalSymbol6 = Symbol(str(uuid.uuid4()), "TestSymbol6", None)
        message6 = RawMessage(str(uuid.uuid4()), str(time.time()), TypeConvertor.stringToNetzobRaw("salut " + self.generateRandomString(200, 1000)))
        originalSymbol6.addMessage(message6)

        symbols = [originalSymbol1, originalSymbol2, originalSymbol3, originalSymbol4, originalSymbol5, originalSymbol6]

        # Start the clustering
        clusteringSolution = UPGMA(None, symbols, True, 100, 80, True, Format.ASCII)
        resultBeforeOrphan = clusteringSolution.executeClustering()
        resultAfterOrphan = clusteringSolution.executeOrphanReduction()

        if (len(resultAfterOrphan) < len(resultBeforeOrphan)):
            print("Before Orphan Reduction: ")
            for symbol in resultBeforeOrphan:
                print("Symbol: " + str(symbol.getName()))
                for m in symbol.getMessages():
                    print(" + " + str(m.getStringData()))

            print("After Orphan Reduction: ")
            for symbol in resultAfterOrphan:
                print("Symbol: " + str(symbol.getName()))
                for m in symbol.getMessages():
                    print(" + " + str(m.getStringData()))

        self.assertGreaterEqual(len(resultBeforeOrphan), len(resultAfterOrphan))
