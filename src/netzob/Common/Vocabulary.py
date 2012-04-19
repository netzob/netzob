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
import logging
import time
from lxml.etree import ElementTree
from lxml import etree
import uuid

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Symbol import Symbol
from netzob.Common.Session import Session
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Field import Field
from netzob.Common.MMSTD.Symbols.impl.EmptySymbol import EmptySymbol
from netzob.Inference.Vocabulary.Alignment.UPGMA import UPGMA
from netzob.Common.Models.Factories.AbstractMessageFactory import AbstractMessageFactory
from netzob.Common.MMSTD.Symbols.impl.UnknownSymbol import UnknownSymbol


#+---------------------------------------------------------------------------+
#| Vocabulary:
#|     Class definition of the vocabulary
#+---------------------------------------------------------------------------+
class Vocabulary(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self):
        self.messages = []
        self.symbols = []
        self.sessions = []

    def getMessages(self):
        return self.messages

    def getMessageByID(self, id):
        for message in self.messages:
            if message.getID() == id:
                return message
        return None

    def getSymbolWhichContainsMessage(self, message):
        for symbol in self.symbols:
            for msg in symbol.getMessages():
                if msg.getID() == message.getID():
                    return symbol
        return None

    def getSymbols(self):
        return self.symbols

    def getSessions(self):
        return self.sessions

    def getSymbol(self, symbolID):
        for symbol in self.symbols:
            if symbol.getID() == symbolID:
                return symbol
        # Exceptions : if ID = "EmptySymbol", we return an EmptySymbol
        if symbolID == str("EmptySymbol"):
            return EmptySymbol()
        # Exceptions : if ID = "UnknownSymbol", we return an UnknownSymbol
        if symbolID == str("UnknownSymbol"):
            return UnknownSymbol()
        return None

    def getSymbolByName(self, symbolName):
        for symbol in self.symbols:
            if symbol.getName() == symbolName:
                return symbol
            # Exceptions : if name = "EmptySymbol", we return an EmptySymbol
            if symbolName == EmptySymbol.TYPE:
                return EmptySymbol()
            # Exceptions : if name = "UnkownSymbol", we return an UnknownSymbol
            if symbolName == UnknownSymbol.TYPE:
                return UnknownSymbol()
        return None

    def getSymbolByID(self, symbolID):
        for symbol in self.symbols:
            if str(symbol.getID()) == str(symbolID):
                return symbol
        return None

    def getSession(self, sessionID):
        for session in self.sessions:
            if session.getID() == sessionID:
                return session
        return None

    def setMessages(self, messages):
        self.messages = messages

    def setSymbols(self, symbols):
        self.symbols = symbols

    def setSessions(self, sessions):
        self.sessions = sessions

    def addMessage(self, message):
        if not message in self.messages:
            self.messages.append(message)
        else:
            logging.warn("The message cannot be added in the vocabulary since it's already declared in.")

    def addSymbol(self, symbol):
        if not symbol in self.symbols:
            self.symbols.append(symbol)
        else:
            logging.warn("The symbol cannot be added in the vocabulary since it's already declared in.")

    def addSession(self, session):
        if not session in self.sessions:
            self.sessions.append(session)
        else:
            logging.warn("The session cannot be added in the vocabulary since it's already declared in.")

    def removeSymbol(self, symbol):
        self.symbols.remove(symbol)

    def removeSession(self, session):
        self.sessions.remove(session)

    def removeMessage(self, message):
        self.messages.remove(message)

    def getVariables(self):
        variables = []
        for symbol in self.symbols:
            for variable in symbol.getVariables():
                if not variable in variables:
                    variables.append(variable)
        return variables

    def getVariableByID(self, idVar):
        for symbol in self.symbols:
            for variable in symbol.getVariables():
                    if str(variable.getID()) == idVar:
                        return variable
        return None

    def estimateNeedlemanWunschNumberOfExecutionStep(self, project):
        # The alignment is proceeded as follows:
        # align and cluster each individual group
        # align and cluster the groups together
        # orphan reduction

        if project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION):
            reductionStep = 1
        else:
            reductionStep = 0

        nbSteps = len(self.symbols) + 1 + reductionStep
        logging.debug("The number of estimated steps for Needleman is " + str(nbSteps))
        return nbSteps

    #+----------------------------------------------
    #| alignWithDelimiter:
    #|  Align each message of each symbol with a specific delimiter
    #+----------------------------------------------
    def forcePartitioning(self, configuration, aFormat, delimiter):
        for symbol in self.symbols:
            symbol.forcePartitioning(configuration, aFormat, delimiter)

    #+----------------------------------------------
    #| simplePartitioning:
    #|  Do message partitioning according to column variation
    #+----------------------------------------------
    def simplePartitioning(self, configuration, unitSize):
        for symbol in self.symbols:
            symbol.simplePartitioning(configuration, unitSize)

    def save(self, root, namespace_project, namespace_common):
        xmlVocabulary = etree.SubElement(root, "{" + namespace_project + "}vocabulary")
        # Messages
        xmlMessages = etree.SubElement(xmlVocabulary, "{" + namespace_project + "}messages")
        for message in self.messages:
            AbstractMessageFactory.save(message, xmlMessages, namespace_project, namespace_common)
        # Symbols
        xmlSymbols = etree.SubElement(xmlVocabulary, "{" + namespace_project + "}symbols")
        for symbol in self.symbols:
            symbol.save(xmlSymbols, namespace_project, namespace_common)
        # Sessions
        xmlSessions = etree.SubElement(xmlVocabulary, "{" + namespace_project + "}sessions")
        for session in self.sessions:
            session.save(xmlSessions, namespace_project, namespace_common)

    @staticmethod
    def loadVocabulary(xmlRoot, namespace_project, namespace_common, version, project):
        vocabulary = Vocabulary()

        if version == "0.1":
            # Messages
            for xmlMessage in xmlRoot.findall("{" + namespace_project + "}messages/{" + namespace_common + "}message"):
                message = AbstractMessageFactory.loadFromXML(xmlMessage, namespace_common, version)
                if message != None:
                    vocabulary.addMessage(message)
            # Symbols
            for xmlSymbol in xmlRoot.findall("{" + namespace_project + "}symbols/{" + namespace_project + "}symbol"):
                symbol = Symbol.loadSymbol(xmlSymbol, namespace_project, namespace_common, version, project, vocabulary)
                if symbol != None:
                    vocabulary.addSymbol(symbol)
            # Sessions
            for xmlSession in xmlRoot.findall("{" + namespace_project + "}sessions/{" + namespace_common + "}session"):
                session = Session.loadFromXML(xmlSession, namespace_project, namespace_common, version, vocabulary)
                if session != None:
                    vocabulary.addSession(session)
        return vocabulary
