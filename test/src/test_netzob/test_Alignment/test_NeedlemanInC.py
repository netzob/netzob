# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
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


#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Models.RawMessage import RawMessage


class test_NeedlemanInC(unittest.TestCase):
    
    def generateRandomString(self, min_len, max_len):
        return ''.join((random.choice(string.letters + string.digits) for _ in xrange(random.randint(min_len, max_len))))

    def test_deserialisationMessages(self):
        nbTest = 10
        alignmentSolution = NeedlemanAndWunsch()
        
        for iTest in range(0, nbTest) :
            messages = []
            # Generate a random number of message to serialize
            nbMessage = random.randint(2, 500)
            for iMessage in range(0, nbMessage) :
                data = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 500))
                message = RawMessage(uuid.uuid4(), str(time.time()), data)
                messages.append(message)
            
            nbDeserializedTest = alignmentSolution.deserializeMessages(messages)
            self.assertEqual(nbMessage, nbDeserializedTest)
        
    def test_AlignementOfMessages(self):     
        alignmentSolution = NeedlemanAndWunsch()
        nbTest = 100
        
        for iTest in range(0, nbTest) :
            messages = []
            # Generate a random number of message to serialize
            nbMessage = random.randint(2, 50)
            for iMessage in range(0, nbMessage) :
                data = TypeConvertor.stringToNetzobRaw("bonjour" + self.generateRandomString(5, 30) + ", tout va bien ?")
                message = RawMessage(uuid.uuid4(), str(time.time()), data)
                messages.append(message)
            
            (score, alignment) = alignmentSolution.align(False, messages)
            (score2, alignmen2t) = alignmentSolution.align(True, messages)
            
            self.assertGreaterEqual(score2, score)
            self.assertGreaterEqual(score2, 90)            
        
    def test_alignmentOfEquivalentMessages(self):     
        alignmentSolution = NeedlemanAndWunsch()
        nbTest = 1000
        for i_test in range(0, nbTest) :
            common_pattern = self.generateRandomString(30, 40)
            # Generate the content of two messages
            data1 = TypeConvertor.stringToNetzobRaw(common_pattern)
            data2 = TypeConvertor.stringToNetzobRaw(common_pattern)
            # Create the messages
            message1 = RawMessage(uuid.uuid4(), str(time.time()), data1)
            message2 = RawMessage(uuid.uuid4(), str(time.time()), data2)
            
            (score, alignment) = alignmentSolution.alignTwoMessages(False, message1, message2)
            self.assertEqual(score, 100.0)
            
            (score, alignment) = alignmentSolution.alignTwoMessages(True, message1, message2)
            self.assertEqual(score, 100.0)
            
    def test_alignmentOfAlmostEquivalentMessages(self):     
        alignmentSolution = NeedlemanAndWunsch()
        nbTest = 1000
        for i_test in range(0, nbTest) :
            common_pattern_before = self.generateRandomString(30, 40)
            common_pattern_after = self.generateRandomString(30, 40)
            # Generate the content of two messages
            data1 = TypeConvertor.stringToNetzobRaw(common_pattern_before + "hercule" + common_pattern_after)
            data2 = TypeConvertor.stringToNetzobRaw(common_pattern_before + "thomas" + common_pattern_after)
            # Create the messages
            message1 = RawMessage(uuid.uuid4(), str(time.time()), data1)
            message2 = RawMessage(uuid.uuid4(), str(time.time()), data2)
            
            (score, alignment) = alignmentSolution.alignTwoMessages(False, message1, message2)
            (score2, alignment2) = alignmentSolution.alignTwoMessages(True, message1, message2)
                        
            self.assertGreater(score2, score)
            self.assertGreater(score2, 95)
