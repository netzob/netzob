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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
import unittest
import random
import string
import uuid
import time

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.TypeIdentifier import TypeIdentifier
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Models.RawMessage import RawMessage
from netzob.Common.Symbol import Symbol
from common.NetzobTestCase import NetzobTestCase


class test_TypeConvertor(NetzobTestCase):
    
    def generateRandomString(self, min_len, max_len):
        return ''.join((random.choice(string.letters + string.digits) for _ in xrange(random.randint(min_len, max_len))))
    
    def test_serializeMessages(self):
        # Generate randoms messages and retrieve their 
        # serializations
        nb_test = 100
        for i_test in range(0, nb_test) :       
            messages = []
                 
            nb_messages = random.randint(5, 200)
            for i_message in range(0, nb_messages) :
                # Generate the content of two messages
                data = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 100))
                # Create the messages
                message = RawMessage(str(uuid.uuid4()), str(time.time()), data)
                messages.append(message)
            
            # start the serialization process
            (serializedMessages, format) = TypeConvertor.serializeMessages(messages, 8)
            
            # start the deserialisation process
            deserializedContents = TypeConvertor.deserializeContent(serializedMessages, format)
            
            for i_message in range(0, len(messages)) :
                message = messages[i_message]
                self.assertEqual(message.getData(), deserializedContents[i_message])
                
    def test_serializeSymbol(self):
        # Generate randoms symbols and retrieve their 
        # serializations

        workspace = self.getWorkspace()
        currentProject = workspace.getProjects()[0]
        nb_test = 100
        for i_test in range(0, nb_test) :                   
            symbol = Symbol(str(uuid.uuid4()), "TestSymbol", currentProject)
            nb_messages = random.randint(5, 50)
            size_messages = []
            for i_message in range(0, nb_messages) :
                # Generate the content of two messages
                size = self.generateRandomString(5, 100)
                size_messages.append(str(len(size)))
                data = TypeConvertor.stringToNetzobRaw(size)
                # Create the message
                message = RawMessage(str(uuid.uuid4()), str(time.time()), data)
                # Register the message
                symbol.addMessage(message)
            
            # start the serialization process
            (serializedSymbol, format) = TypeConvertor.serializeSymbol(symbol, 8)
            
            # We verify the format is good :
            test_format = str(nb_messages) + "G" + ("M".join(size_messages)) + "M"
            self.assertEqual(format, test_format)
            
            # We verify the content is good :
            # TODO
