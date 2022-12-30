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
#insert in the path the directory where _libNeedleman.pyd is
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


sys.path.insert(0, 'src/')


#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Model.RawMessage import RawMessage


class test_NeedlemanInC(unittest.TestCase):

    def generateRandomString(self, min_len, max_len):
        return ''.join((random.choice(string.letters + string.digits) for _ in range(random.randint(min_len, max_len))))

    def test_deserialisationMessages(self):
        nbTest = 10
        alignmentSolution = NeedlemanAndWunsch(8)

        for iTest in range(0, nbTest):
            messages = []
            # Generate a random number of message to serialize
            nbMessage = random.randint(2, 500)
            for iMessage in range(0, nbMessage):
                data = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 500))
                message = RawMessage(str(uuid.uuid4()), str(time.time()), data)
                messages.append(message)

            nbDeserializedTest = alignmentSolution.deserializeMessages(messages)
            self.assertEqual(nbMessage, nbDeserializedTest)

    def test_AlignementOfMessages(self):
        alignmentSolution = NeedlemanAndWunsch(4)
        nbTest = 100

        for iTest in range(0, nbTest):
            messages = []
            # Generate a random number of message to serialize
            nbMessage = random.randint(2, 50)
            for iMessage in range(0, nbMessage):
                data = TypeConvertor.stringToNetzobRaw("bonjour" + self.generateRandomString(5, 30) + ", tout va bien ?")
                message = RawMessage(str(uuid.uuid4()), str(time.time()), data)
                messages.append(message)

            (alignment, scores) = alignmentSolution.align(False, messages)
            (score1, score2, score3) = scores
            (alignmentBis, scoresBis) = alignmentSolution.align(True, messages)
            (scoreBis1, scoreBis2, scoreBis3) = scoresBis
            print(alignment)
            print(alignmentBis)

            self.assertGreaterEqual(scoreBis1, score1)
            self.assertGreaterEqual(scoreBis1, 90)

    def test_alignmentOfEquivalentMessages(self):
        alignmentSolution = NeedlemanAndWunsch(8)
        nbTest = 1000
        for i_test in range(0, nbTest):
            common_pattern = self.generateRandomString(30, 40)
            # Generate the content of two messages
            data1 = TypeConvertor.stringToNetzobRaw(common_pattern)
            data2 = TypeConvertor.stringToNetzobRaw(common_pattern)
            # Create the messages
            message1 = RawMessage(str(uuid.uuid4()), str(time.time()), data1)
            message2 = RawMessage(str(uuid.uuid4()), str(time.time()), data2)

            (scores, alignment) = alignmentSolution.alignTwoMessages(False, message1, message2)
            (score1, score2, score3) = scores
            self.assertEqual(score1, 100.0)
            self.assertEqual(score2, 100.0)
            self.assertEqual(score3, 100.0)

            (scores, alignment) = alignmentSolution.alignTwoMessages(True, message1, message2)
            (score1, score2, score3) = scores
            self.assertEqual(score1, 100.0)
            self.assertEqual(score2, 100.0)
            self.assertEqual(score3, 100.0)

    def test_alignmentOfAlmostEquivalentMessages(self):
        alignmentSolution = NeedlemanAndWunsch(8)
        nbTest = 1000
        for i_test in range(0, nbTest):
            common_pattern_before = self.generateRandomString(30, 40)
            common_pattern_after = self.generateRandomString(30, 40)
            # Generate the content of two messages
            data1 = TypeConvertor.stringToNetzobRaw(common_pattern_before + "hercule" + common_pattern_after)
            data2 = TypeConvertor.stringToNetzobRaw(common_pattern_before + "thomas" + common_pattern_after)
            # Create the messages
            message1 = RawMessage(str(uuid.uuid4()), str(time.time()), data1)
            message2 = RawMessage(str(uuid.uuid4()), str(time.time()), data2)

            (scores, alignment) = alignmentSolution.alignTwoMessages(False, message1, message2)
            (score1, score2, score3) = scores
            (scoresBis, alignment2) = alignmentSolution.alignTwoMessages(True, message1, message2)
            (scoreBis1, scoreBis2, scoreBis3) = scoresBis

            self.assertGreater(scoreBis1, score1)
            self.assertGreater(scoreBis1, 95)
