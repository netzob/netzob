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
import logging
from datetime import datetime

from common.NetzobTestCase import NetzobTestCase
from netzob.Common.ExecutionContext import ExecutionContext
from netzob.Model.RawMessage import RawMessage
from netzob.Common.Symbol import Symbol
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Project import Project
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch

from netzob.all import *
#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


class test_Needleman(NetzobTestCase):

    def generateRandomString(self, min_len, max_len):
        return ''.join((random.choice(string.letters + string.digits) for _ in range(random.randint(min_len, max_len))))

    def generateRandomBytes(self, min_len, max_len):
        result = ""
        nb = random.randint(min_len, max_len)

        for i in range(0, nb):
            val = str(hex(random.randint(0, 255)))[2:]
            result += "0" * (len(val) % 2) + val
        return result

    def emptyAlignmentCB(self, stage, percent, message):
        pass

    def test_semanticAlignment_bug1(self):
        """test_semanticAlignment_bug1:
        A bug on the semantic alignment has been identified which prevent
        the computation of a valid regex. This test verifies the bug is not comming back.
        @date 18/04/2013
        """

        firstname1 = "antoine"
        email1 = "thomas@hotmail.com"

        firstname2 = "luc"
        email2 = "thomas@kotmail.com"

        msg1 = RawMessage(uuid.uuid4(), None, TypeConvertor.stringToNetzobRaw("6" + firstname1 + "GAHFSHQS" + email1))
        msg2 = RawMessage(uuid.uuid4(), None, TypeConvertor.stringToNetzobRaw("3" + firstname2 + "CVSDHISD" + email2))

        project = Project(uuid.uuid4(), "Experiment", datetime.now(), "")
        nwEngine = NeedlemanAndWunsch(8, project, False, None)
        symbol = Symbol(uuid.uuid4(), "Test", project)

        symbol.addMessages([msg1, msg2])
        msg1.addSemanticTag("firstname", 2, 2 + len(firstname1) * 2)
        msg1.addSemanticTag("email", 2 + len(firstname1) * 2 + 16, 2 + len(firstname1) * 2 + 16 + len(email1) * 2)

        msg2.addSemanticTag("firstname", 2, 2 + len(firstname2) * 2)
        msg2.addSemanticTag("email", 2 + len(firstname2) * 2 + 16, 2 + len(firstname2) * 2 + 16 + len(email2) * 2)

        nwEngine.alignField(symbol.getField())
        symbol.getField().setFormat(Format.STRING)

        print("Computed Regex : {0}".format(symbol.getRegex()))
        print("=======")
        print(symbol.getCells(True))

        computedFields = symbol.getExtendedFields()
        self.assertTrue(len(computedFields) > 1, "Only one field has been computed which tells us something went wrong.")

    def test_semanticAlignment_simple(self):
        """test_semanticAlignment_simple:
        Test that messages with embedded semantic are efficiently aligned.
        Format : <random 10 bytes><random username><random 5 ASCII><random email>

        Optimal Needleman & Wunsch Parameters :
        // Cost definitions for the alignment
        static const short int MATCH = 5;
        static const short int SEMANTIC_MATCH = 30;
        static const short int MISMATCH = -5;
        static const short int GAP = 0;
        static const short int BLEN = 10;
        // Consts for the definition of a mask
        static const unsigned char END = 2;
        static const unsigned char DIFFERENT = 1;
        static const unsigned char EQUAL = 0;
        """
        project = Project(uuid.uuid4(), "Experiment", datetime.now(), "")
        symbol = Symbol(uuid.uuid4(), "Test", project)

        nbMessage = 500
        usernames = []
        emails = []
        for iMessage in range(0, nbMessage):
            str_username = self.generateRandomString(4, 10)
            username = TypeConvertor.stringToNetzobRaw(str_username)
            usernames.append(str_username)

            email_prefix = self.generateRandomString(4, 10)
            email_domain = self.generateRandomString(4, 10)
            email_extension = self.generateRandomString(2, 3)
            str_email = "{0}@{1}.{2}".format(email_prefix, email_domain, email_extension)
            emails.append(str_email)
            email = TypeConvertor.stringToNetzobRaw(str_email)
            random10Bytes = self.generateRandomBytes(10, 10)
            random5ASCII = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 5))
            data = "{0}{1}{2}{3}".format(random10Bytes, username, random5ASCII, email)

            message = RawMessage(uuid.uuid4(), None, data)
            message.addSemanticTag("username", len(random10Bytes), len(random10Bytes) + len(username))
            message.addSemanticTag("email", len(random10Bytes) + len(username) + len(random5ASCII), len(random10Bytes) + len(username) + len(random5ASCII) + len(email))

            symbol.addMessage(message)

        nwEngine = NeedlemanAndWunsch(8, project, False, None)
        nwEngine.alignField(symbol.getField())

        symbol.getField().setFormat(Format.STRING)

        print("Number of computed fields : {0}".format(len(symbol.getExtendedFields())))
        self.assertEqual(4, len(symbol.getExtendedFields()))
        nbValidMessages = 0

        for message in symbol.getMessages():
            isValid = symbol.getField().isRegexValidForMessage(message)
            if isValid:
                nbValidMessages += 1
            self.assertTrue(isValid)

        print(symbol.getCells())

        print("Computed regex is valid for {0}/{1} messages.".format(nbValidMessages, len(symbol.getMessages())))


    # def test_randomAlignmentsWithTwoCenteredMessages(self):

    #     currentProject = Project(uuid.uuid4(), "test_randomAlignmentsWithTwoCenteredMessages", datetime.now(), "")

    #     doInternalSlick = currentProject.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)
    #     defaultFormat = currentProject.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
    #     defaultUnitSize = 8

    #     # We generate 1000 random couples of data and try to align them
    #     # Objectives: just test if it executes
    #     nb_data = 2
    #     nb_failed = 0
    #     nb_success = 0
    #     for i_test in range(0, nb_data):

    #         common_pattern = self.generateRandomString(30, 40)
    #         # Generate the content of two messages
    #         data1 = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 10) + common_pattern + self.generateRandomString(5, 10))
    #         data2 = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 10) + common_pattern + self.generateRandomString(5, 10))
    #         # Create the messages
    #         message1 = RawMessage(str(uuid.uuid4()), str(time.time()), data1)
    #         message2 = RawMessage(str(uuid.uuid4()), str(time.time()), data2)
    #         # Create the symbol
    #         symbol = Symbol(str(uuid.uuid4()), "test_randomAlignments#" + str(i_test), currentProject)
    #         symbol.addMessage(message1)
    #         symbol.addMessage(message2)
    #         field = symbol.getField()

    #         # Starts the alignment process
    #         alignmentProcess = NeedlemanAndWunsch(defaultUnitSize, currentProject, False, self.emptyAlignmentCB)
    #         alignmentProcess.alignField(field)
    #         print "-----------"+str(TypeConvertor.stringToNetzobRaw(common_pattern))
    #         for message in symbol.getMessages():

    #             print message.applyAlignment()

    #         if not TypeConvertor.stringToNetzobRaw(common_pattern[:]) in field.getAlignment():
    #             if self.debug is True:
    #                 print "Message 1: " + str(data1)
    #                 print "Message 2: " + str(data2)
    #                 print "Common pattern: " + TypeConvertor.stringToNetzobRaw(common_pattern)
    #                 print "Alignment: " + field.getAlignment()
    #                 print message1.applyAlignment()
    #                 print message2.applyAlignment()
    #             nb_failed += 1
    #             quit()
    #         else:
    #             nb_success += 1
    #     if nb_failed > 0:
    #         print "A number of " + str(nb_failed) + "/" + str(nb_data) + " alignment failed !"
    #     self.assertEqual(0, nb_failed)
    #     self.assertEqual(nb_success, nb_data)


    # def test_randomAlignmentsWithTwoPrefixedMessages(self):
    #     workspace = self.getWorkspace()
    #     currentProject = workspace.getProjects()[0]

    #     doInternalSlick = currentProject.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)
    #     defaultFormat = currentProject.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
    #     defaultUnitSize = 8

    #     # We generate 1000 random couples of data and try to align them
    #     # Objectives: just test if it executes
    #     nb_data = 1000
    #     nb_failed = 0
    #     nb_success = 0
    #     for i_test in range(0, nb_data):
    #         common_pattern = self.generateRandomString(30, 40)
    #         # Generate the content of two messages
    #         data1 = TypeConvertor.stringToNetzobRaw(common_pattern + self.generateRandomString(5, 100))
    #         data2 = TypeConvertor.stringToNetzobRaw(common_pattern + self.generateRandomString(5, 100))
    #         # Create the messages
    #         message1 = RawMessage(str(uuid.uuid4()), str(time.time()), data1)
    #         message2 = RawMessage(str(uuid.uuid4()), str(time.time()), data2)
    #         # Create the symbol
    #         symbol = Symbol(str(uuid.uuid4()), "test_randomAlignments#" + str(i_test), currentProject)
    #         symbol.addMessage(message1)
    #         symbol.addMessage(message2)
    #         field = symbol.getField()

    #         # Starts the alignment process
    #         alignmentProcess = NeedlemanAndWunsch(defaultUnitSize, currentProject, False, self.emptyAlignmentCB)
    #         alignmentProcess.alignField(field)

    #         if not TypeConvertor.stringToNetzobRaw(common_pattern[:]) in field.getAlignment():
    #             if self.debug is True:
    #                 print "Message 1: " + str(data1)
    #                 print "Message 2: " + str(data2)
    #                 print "Common pattern: " + TypeConvertor.stringToNetzobRaw(common_pattern)
    #                 print "Alignment: " + field.getAlignment()
    #             nb_failed += 1
    #         else:
    #             nb_success += 1
    #     if nb_failed > 0:
    #         print "A number of " + str(nb_failed) + "/" + str(nb_data) + " alignment failed !"
    #     self.assertEqual(0, nb_failed)
    #     self.assertEqual(nb_success, nb_data)

    # def test_randomAlignmentsWithTwoSuffixedMessages(self):
    #     workspace = self.getWorkspace()
    #     currentProject = workspace.getProjects()[0]

    #     doInternalSlick = currentProject.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)
    #     defaultFormat = currentProject.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
    #     defaultUnitSize = 8

    #     # We generate 1000 random couples of data and try to align them
    #     # Objectives: just test if it executes
    #     nb_data = 1000
    #     nb_failed = 0
    #     nb_success = 0
    #     for i_test in range(0, nb_data):
    #         common_pattern = self.generateRandomString(30, 40)
    #         # Generate the content of two messages
    #         data1 = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 100) + common_pattern)
    #         data2 = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 100) + common_pattern)
    #         # Create the messages
    #         message1 = RawMessage(str(uuid.uuid4()), str(time.time()), data1)
    #         message2 = RawMessage(str(uuid.uuid4()), str(time.time()), data2)
    #         # Create the symbol
    #         symbol = Symbol(str(uuid.uuid4()), "test_randomAlignments#" + str(i_test), currentProject)
    #         symbol.addMessage(message1)
    #         symbol.addMessage(message2)
    #         field = symbol.getField()

    #         # Starts the alignment process
    #         alignmentProcess = NeedlemanAndWunsch(defaultUnitSize, currentProject, False, self.emptyAlignmentCB)
    #         alignmentProcess.alignField(field)

    #         if not TypeConvertor.stringToNetzobRaw(common_pattern[:]) in field.getAlignment():
    #             if self.debug is True:
    #                 print "Message 1: " + str(data1)
    #                 print "Message 2: " + str(data2)
    #                 print "Common pattern: " + TypeConvertor.stringToNetzobRaw(common_pattern)
    #                 print "Alignment: " + field.getAlignment()
    #             nb_failed += 1
    #         else:
    #             nb_success += 1
    #     if nb_failed > 0:
    #         print "A number of " + str(nb_failed) + "/" + str(nb_data) + " alignment failed !"
    #     self.assertEqual(0, nb_failed)
    #     self.assertEqual(nb_success, nb_data)
