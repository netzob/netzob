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
from gettext import gettext as _
import logging
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.States.AbstractState import AbstractState
from netzob.Common.MMSTD.Transitions.AbstractTransition import AbstractTransition
from netzob.Common.Automata import Automata
from netzob.Common.Sequence import Sequence


#+---------------------------------------------------------------------------+
#| Grammar:
#|     Class definition of a grammar
#+---------------------------------------------------------------------------+
class Grammar(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self):
        self.automata = None
        self.sequences = []

    def addsequence(self, sequence):
        if not sequence in self.sequences:
            self.sequences.append(sequence)
        else:
            logging.debug("Can't add the provided sequence, since its already registered")

    def update(self, vocabulary):
        """update:
        verifies the grammar and its automata is still valid
        and that none of its symbols has been deprecated"""
        if self.automata is not None:
            self.automata.update(vocabulary)

    #+-----------------------------------------------------------------------+
    #| Save & Load
    #+-----------------------------------------------------------------------+
    def save(self, root, namespace):
        xmlGrammar = etree.SubElement(root, "{" + namespace + "}grammar")
        if self.automata is not None:
            self.automata.save(xmlGrammar, namespace)

        if len(self.sequences) > 0:
            xmlSequences = etree.SubElement(xmlGrammar, "{" + namespace + "}sequences")
            for sequence in self.getSequences():
                sequence.save(xmlSequences, namespace)

    @staticmethod
    def loadGrammar(xmlRoot, vocabulary, namespace, version):
        if version == "0.1":
            automata = None
            sequences = []

            if xmlRoot.find("{" + namespace + "}automata") is not None:
                xmlAutomata = xmlRoot.find("{" + namespace + "}automata")
                automata = Automata.loadFromXML(xmlAutomata, vocabulary, namespace, version)

            if xmlRoot.find("{" + namespace + "}sequences") is not None:
                xmlSequences = xmlRoot.find("{" + namespace + "}sequences")
                for xmlSequence in xmlSequences.findall("{" + namespace + "}sequence"):
                    sequence = Sequence.loadFromXML(xmlSequence, vocabulary, namespace, version)
                    sequences.append(sequence)

            grammar = None
            if automata is not None or len(sequences) > 0:
                grammar = Grammar()
                if automata is not None:
                    grammar.setAutomata(automata)
                if len(sequences) > 0:
                    grammar.setSequences(sequences)

            return grammar

        return None

    #+-----------------------------------------------------------------------+
    #| Getters & Setters
    #+-----------------------------------------------------------------------+
    def getAutomata(self):
        return self.automata

    def getSequences(self):
        return self.sequences

    def setAutomata(self, automata):
        self.automata = automata

    def setSequences(self, sequences):
        self.sequences = sequences
