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
#| Standard library imports
#+----------------------------------------------
import os

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------
from lxml.etree import ElementTree

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.MMSTD.States.impl import NormalState
from netzob.Common.MMSTD.Transitions.impl import SemiStochasticTransition
from netzob.Common.MMSTD.Transitions.impl import OpenChannelTransition
from netzob.Common.MMSTD.Transitions.impl import CloseChannelTransition
from netzob.Common.MMSTD.Tools.Parsers.DictionaryParser import DictionaryXmlParser
from netzob.Common.MMSTD import MMSTD

#+----------------------------------------------
#| MMSTDXmlParser :
#|    Parser for an MMSTD
#+----------------------------------------------
class MMSTDXmlParser(object):

    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML :
    #|     Function which parses an XML and extract from it
    #[     the definition of an MMSTD
    #| @param rootElement: XML root of the MMSTD definition
    #| @return an instance of an MMSTD
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement):
        if rootElement.tag != "automata" :
            raise NameError("The parsed XML doesn't represent an automata.")

        if rootElement.get("type", "none") != "mmstd" :
            raise NameError("The parsed XML doesn't represent an MMSTD")

        if rootElement.get("dictionary", "none") == "none" :
            raise NameError("The MMSTD doesn't have any dictionary declared")


        automatonDir = ConfigurationParser().get("automata", "path")
        dictionaryFile = os.path.join(automatonDir, rootElement.get("dictionary", "none"))
        # Parsing dictionary file
        dicoTree = ElementTree()
        dicoTree.parse(dictionaryFile)
        dictionary = DictionaryXmlParser.DictionaryXmlParser.loadFromXML(dicoTree.getroot(), dictionaryFile)

        # parse for all the states
        states = []
        initialState = None
        for xmlState in rootElement.findall("state") :
            idState = int(xmlState.get("id", "-1"))
            classState = xmlState.get("class", "NormalState")
            nameState = xmlState.get("name", "none")
            state = NormalState.NormalState(idState, nameState)
            states.append(state)
            if idState == 0 :
                initialState = state

        # parse for all the transitions
        for xmlTransition in rootElement.findall("transition") :

            classTransition = xmlTransition.get("class", "none")

            transition = None
            if classTransition == "SemiStochasticTransition" :
                transition = SemiStochasticTransition.SemiStochasticTransition.parse(xmlTransition, dictionary, states)
            elif classTransition == "OpenChannelTransition" :
                transition = OpenChannelTransition.OpenChannelTransition.parse(xmlTransition, states)
            elif classTransition == "CloseChannelTransition" :
                transition = CloseChannelTransition.CloseChannelTransition.parse(xmlTransition, states)


        # create an MMSTD
        automata = MMSTD.MMSTD(initialState, dictionary)
        return automata

