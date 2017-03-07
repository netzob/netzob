# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Inference.Grammar.Angluin import MealyLSTAR
from netzob.Inference.Grammar.MQCache import MQCache
# Replace by previous import statement : from Angluin import Angluin
import threading
import time


#+----------------------------------------------
#| GrammarInferer:
#|    Given Angluin's L*a algorithm, it learns
#|    the grammar of a protocol
#+----------------------------------------------
class GrammarInferer(threading.Thread):

    def __init__(self, vocabulary, inputDictionary, oracle, equivalenceOracle, resetScript, cb_submitedQuery, cb_hypotheticalAutomaton):
        threading.Thread.__init__(self)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.GrammarInferer.py')
        self.vocabulary = vocabulary
        self.inputDictionary = inputDictionary
        self.oracle = oracle
        self.equivalenceOracle = equivalenceOracle
        self.resetScript = resetScript
        self.cb_submitedQuery = cb_submitedQuery
        self.cb_hypotheticalAutomaton = cb_hypotheticalAutomaton
        self.active = False
        self.inferedAutomaton = None
        self.hypotheticalAutomaton = None
        self.learner = None

    def run(self):
        self.log.info("Starting the Grammar inferring process")
        self.active = True
        self.infer()
        self.active = False
        self.log.info("Ending the Grammar inferring process")

    def hasFinish(self):
        return not self.active

    def getInferedAutomaton(self):
        return self.inferedAutomaton

    def getHypotheticalAutomaton(self):
        return self.hypotheticalAutomaton

    def getSubmitedQueries(self):
        if self.learner is not None:
            return self.learner.getSubmitedQueries()
        return []

    def stop(self):
        self.active = False

    def infer(self):
        self.active = True
        equivalent = False

        startTime = time.time()

        # Create a MQ cache
        cache = MQCache()


        # we first initialize the angluin's algo
        self.learner = Angluin(self.vocabulary, self.inputDictionary, self.oracle, self.resetScript, self.cb_submitedQuery, self.cb_hypotheticalAutomaton, cache)

        while not equivalent and self.active:
            self.log.info("=============================================================================")
            self.log.info("Execute one new round of the inferring process")
            self.log.info("=============================================================================")

            self.learner.learn()
            if not self.active:
                break

            self.hypotheticalAutomaton = self.learner.getInferedAutomata()
            self.log.info("An hypothetical automaton has been computed")

            # Execute the call back function for the hypothetial automaton
            # GObject.idle_add(self.cb_hypotheticalAutomaton, self.hypotheticalAutomaton)

            counterExample = self.equivalenceOracle.findCounterExample(self.hypotheticalAutomaton, self.inputDictionary, cache)

            if not self.active:
                break
            if counterExample is None:
                self.log.info("No counter-example were found !")
                equivalent = True
            else:
                self.log.info("A counter-example has been found")
                for s in counterExample.getSymbols():
                    self.log.info("symbol : " + str(s) + " => " + str(s.getID()))
                self.learner.addCounterExamples([counterExample])

        automaton = self.learner.getInferedAutomata()
        self.log.info("The following automaton has been computed : " + str(automaton.getDotCode()))

        # Now we apply indeterminism
        i_session = 0
        sessions = self.vocabulary.getSessions()
        for session in self.sessions:
            self.log.info("Re-inject session (" + str(i_session) + ") in the automata")
            new_automata = self.applyMessagesOnAutomata(automaton, messages)
            i_session = i_session + 1

        endTime = time.time()
        self.log.info("The inferring process is finished !")

        print("Elapsed time: {} msecs".format((endTime - startTime) * 1000))
        self.inferedAutomaton = automaton

    def applyMessagesOnAutomata(self, automaton, messages):
        self.log.info("Apply the messages ({0}) on automata".format(messages))
        currentState = automaton.getInitialState()
        return automaton
