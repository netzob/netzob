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
import logging
import time


#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Inference.Grammar.Queries.MembershipQuery import MembershipQuery
from netzob.Common.MMSTD.Symbols.impl.DictionarySymbol import DictionarySymbol
from netzob.Inference.Grammar.Oracles.NetworkOracle import NetworkOracle
from netzob.Common.MMSTD.Dictionary.Memory import Memory
import gobject

#+----------------------------------------------
#| LearningAlgorithm:
#|    Abstract class which provides to his children
#| the necessary functions to learn
#+----------------------------------------------
class LearningAlgorithm(object):

    def __init__(self, dictionary, communicationChannel, callbackFunction):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.LearningAlgorithm.py')
        self.dictionary = dictionary
        self.communicationChannel = communicationChannel
        self.inferedAutomata = None
        self.submitedQueries = []

        self.callbackFunction = callbackFunction


    def attachStatusCallBack(self, callbackFunction):
        self.callbackFunction = callbackFunction

    def learn(self):
        self.log.error("The LearningAlgorithm class doesn't support 'learn'.")
        raise NotImplementedError("The LearningAlgorithm class doesn't support 'learn'.")

    def getSubmitedQueries(self):
        return self.submitedQueries


    def submitQuery(self, query):
        self.log.info("Submit the following query : " + str(query))


        # transform the query into a MMSTD
        mmstd = query.toMMSTD(self.dictionary)

        # create an oracle for this MMSTD
        oracle = NetworkOracle(self.communicationChannel)

        # start the oracle with the MMSTD
        oracle.setMMSTD(mmstd)
        oracle.start()

        # wait it has finished
        self.log.info("Waiting for the oracle to finish")
        while oracle.isAlive():
            time.sleep(0.01)
        self.log.info("The oracle has finished !")

        # stop the oracle and retrieve the query
        oracle.stop()

        resultQuery = oracle.getResults()
        tmpResultQuery = oracle.getGeneratedOutputSymbols()

        self.log.info("The following query has been computed : " + str(resultQuery))

        # Register this query and the associated response
        self.submitedQueries.append([query, resultQuery])

        # return only the last result
        if len(resultQuery) > 0:
            # Execute the call back function
            gobject.idle_add(self.callbackFunction, query, tmpResultQuery)
            return resultQuery[len(resultQuery) - 1]
        else:
            # Execute the call back function
            gobject.idle_add(self.callbackFunction, query, "OUPS")
            return resultQuery

    def getInferedAutomata(self):
        return self.inferedAutomata
