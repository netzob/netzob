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
#| Global Imports
#+---------------------------------------------------------------------------+
from locale import gettext as _
import logging
import uuid

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Inference.Vocabulary.Searcher import Searcher
from netzob.Inference.Vocabulary.Clustering.AbstractClusteringAlgorithm import AbstractClusteringAlgorithm
from netzob.Common.Symbol import Symbol


#+---------------------------------------------------------------------------+
#| ASAPClustering
#+---------------------------------------------------------------------------+
class ApplicativeDataClustering(AbstractClusteringAlgorithm):

    __algorithm_name__ = "ApplicativeDataClustering"
    __algorithm_description = """no description yet"""

    def __init__(self):
        super(ApplicativeDataClustering, self).__init__("appDataClustering")

    def execute(self, symbols):
        """Execute the clustering"""
        self.log = logging.getLogger(__name__)

        if symbols is None or len(symbols) < 1:
            self.log.debug("No symbol provided")
            return []

        messages = []
        for symbol in symbols:
            messages.extend(symbol.getMessages())

        project = symbols[0].getProject()

        searcher = Searcher(project)
        groups = dict()
        for message in messages:
            founds = searcher.searchContextInMessage(message)
            tokens = []
            for f in founds:
                token = None
                for appData in message.getSession().getApplicativeData():
                    if appData.getValue() == f.getDescription():
                        token = str(appData.getName())
                        break
                if token is None:
                    token = f.getDescription()

                tokens.append(token)

            strToken = ";".join(tokens)
            if strToken in groups.keys():
                groups[strToken].append(message)
            else:
                groups[strToken] = [message]

        newSymbols = []
        for groupSignature, groupMessages in groups.items():
            if len(groupSignature) == 0:
                groupSignature = "None"
            sym = Symbol(uuid.uuid4(), groupSignature, project)
            sym.addMessages(groupMessages)
            newSymbols.append(sym)
        return newSymbols

    def getConfigurationParameters(self):
        parameters = dict()
        return parameters

    def setConfigurationParameters(self, parameters):
        pass

    def getConfigurationController(self):
        return None
