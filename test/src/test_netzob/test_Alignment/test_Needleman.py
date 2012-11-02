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

from common.NetzobTestCase import NetzobTestCase
from netzob.Common.ExecutionContext import ExecutionContext
from netzob.Common.Models.RawMessage import RawMessage
from netzob.Common.Symbol import Symbol
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


class test_Needleman(NetzobTestCase):
    
    def generateRandomString(self, min_len, max_len):
        return ''.join((random.choice(string.letters + string.digits) for _ in xrange(random.randint(min_len, max_len))))
    
    def emptyAlignmentCB(self, stage, percent, message):
        pass
  
    def test_randomAlignmentsWithTwoCenteredMessages(self):        
        workspace = self.getWorkspace()
        currentProject = workspace.getProjects()[0]
        
        doInternalSlick = currentProject.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)
        defaultFormat = currentProject.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
        defaultUnitSize = 8
        
        # We generate 1000 random couples of data and try to align them
        # Objectives : just test if it executes
        nb_data = 1000
        nb_failed = 0
        nb_success = 0
        for i_test in range(0, nb_data) :
            
            common_pattern = self.generateRandomString(30, 40)
            # Generate the content of two messages
            data1 = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 100) + common_pattern + self.generateRandomString(5, 100))
            data2 = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 100) + common_pattern + self.generateRandomString(5, 100))
            # Create the messages
            message1 = RawMessage(str(uuid.uuid4()), str(time.time()), data1)
            message2 = RawMessage(str(uuid.uuid4()), str(time.time()), data2)
            # Create the symbol
            symbol = Symbol(str(uuid.uuid4()), "test_randomAlignments#" + str(i_test), currentProject)
            symbol.addMessage(message1)
            symbol.addMessage(message2)
            
            # Starts the alignment process
            alignmentProcess = NeedlemanAndWunsch(defaultUnitSize, self.emptyAlignmentCB)
            alignmentProcess.alignSymbol(symbol, doInternalSlick, defaultFormat)
            
            if not TypeConvertor.stringToNetzobRaw(common_pattern[:]) in symbol.getAlignment() :
                if self.debug is True:
                    print "Message 1 : " + str(data1)
                    print "Message 2 : " + str(data2)
                    print "Common pattern : " + TypeConvertor.stringToNetzobRaw(common_pattern)
                    print "Alignment : " + symbol.getAlignment()
                nb_failed += 1
            else :
                nb_success += 1
        if nb_failed > 0 :
            print "A number of " + str(nb_failed) + "/" + str(nb_data) + " alignment failed !"
        self.assertEqual(0, nb_failed)
        self.assertEqual(nb_success, nb_data)
        
    def test_randomAlignmentsWithTwoPrefixedMessages(self):        
        workspace = self.getWorkspace()
        currentProject = workspace.getProjects()[0]
        
        doInternalSlick = currentProject.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)
        defaultFormat = currentProject.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
        defaultUnitSize = 8
        
        # We generate 1000 random couples of data and try to align them
        # Objectives : just test if it executes
        nb_data = 1000
        nb_failed = 0
        nb_success = 0
        for i_test in range(0, nb_data) :            
            common_pattern = self.generateRandomString(30, 40)
            # Generate the content of two messages
            data1 = TypeConvertor.stringToNetzobRaw(common_pattern + self.generateRandomString(5, 100))
            data2 = TypeConvertor.stringToNetzobRaw(common_pattern + self.generateRandomString(5, 100))
            # Create the messages
            message1 = RawMessage(str(uuid.uuid4()), str(time.time()), data1)
            message2 = RawMessage(str(uuid.uuid4()), str(time.time()), data2)
            # Create the symbol
            symbol = Symbol(str(uuid.uuid4()), "test_randomAlignments#" + str(i_test), currentProject)
            symbol.addMessage(message1)
            symbol.addMessage(message2)
            
            # Starts the alignment process
            alignmentProcess = NeedlemanAndWunsch(defaultUnitSize, self.emptyAlignmentCB)
            alignmentProcess.alignSymbol(symbol, doInternalSlick, defaultFormat)
            
            if not TypeConvertor.stringToNetzobRaw(common_pattern[:]) in symbol.getAlignment() :
                if self.debug is True:
                    print "Message 1 : " + str(data1)
                    print "Message 2 : " + str(data2)
                    print "Common pattern : " + TypeConvertor.stringToNetzobRaw(common_pattern)
                    print "Alignment : " + symbol.getAlignment()
                nb_failed += 1
            else :
                nb_success += 1
        if nb_failed > 0 :
            print "A number of " + str(nb_failed) + "/" + str(nb_data) + " alignment failed !"
        self.assertEqual(0, nb_failed)
        self.assertEqual(nb_success, nb_data)
        
    
    
        
    def test_randomAlignmentsWithTwoSuffixedMessages(self):        
        workspace = self.getWorkspace()
        currentProject = workspace.getProjects()[0]
        
        doInternalSlick = currentProject.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)
        defaultFormat = currentProject.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
        defaultUnitSize = 8
        
        # We generate 1000 random couples of data and try to align them
        # Objectives : just test if it executes
        nb_data = 1000
        nb_failed = 0
        nb_success = 0
        for i_test in range(0, nb_data) :            
            common_pattern = self.generateRandomString(30, 40)
            # Generate the content of two messages
            data1 = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 100) + common_pattern)
            data2 = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 100) + common_pattern)
            # Create the messages
            message1 = RawMessage(str(uuid.uuid4()), str(time.time()), data1)
            message2 = RawMessage(str(uuid.uuid4()), str(time.time()), data2)
            # Create the symbol
            symbol = Symbol(str(uuid.uuid4()), "test_randomAlignments#" + str(i_test), currentProject)
            symbol.addMessage(message1)
            symbol.addMessage(message2)
            
            # Starts the alignment process
            alignmentProcess = NeedlemanAndWunsch(defaultUnitSize, self.emptyAlignmentCB)
            alignmentProcess.alignSymbol(symbol, doInternalSlick, defaultFormat)
            
            if not TypeConvertor.stringToNetzobRaw(common_pattern[:]) in symbol.getAlignment() :
                if self.debug is True:
                    print "Message 1 : " + str(data1)
                    print "Message 2 : " + str(data2)
                    print "Common pattern : " + TypeConvertor.stringToNetzobRaw(common_pattern)
                    print "Alignment : " + symbol.getAlignment()
                nb_failed += 1
            else :
                nb_success += 1
        if nb_failed > 0 :
            print "A number of " + str(nb_failed) + "/" + str(nb_data) + " alignment failed !"
        self.assertEqual(0, nb_failed)
        self.assertEqual(nb_success, nb_data)
          
  
    
