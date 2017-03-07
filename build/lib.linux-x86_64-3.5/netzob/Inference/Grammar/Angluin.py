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

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Inference.Grammar.lstar.ObservationTable import ObservationTable

@NetzobLogger
class MealyLSTAR(object):
    """This class is an implementation of the Angluin L* Algorithm
    as detailled in "Learning regular sets from queries and counterexamples" [Ang87].

    This active grammatical inference algorithm infers state machine. It communicates with a target
    by sending membership queries which requires to have access to an implementation of the protocol.

    To illustrate its usage, we will infer the grammar of a fake simple protocol.

    >>> from netzob.all import *
    >>> import time

    We first create a fake server which requires a vocabulary of
    input (I) and output (O) symbols:

    >>> i0 = Symbol(name="a", fields=[Field("a\\n")])
    >>> i1 = Symbol(name="b", fields=[Field("b\\n")])
    >>> i2 = Symbol(name="c", fields=[Field("c\\n")])
    >>> i3 = Symbol(name="d", fields=[Field("d\\n")])
    >>> # List of Client > Server messages
    >>> I = [i0, i1, i2, i3]

    >>> o0 = Symbol(name="0", fields=[Field("0")])
    >>> o1 = Symbol(name="1", fields=[Field("1")])
    >>> o2 = Symbol(name="2", fields=[Field("2")])
    >>> o3 = Symbol(name="3", fields=[Field("3")])
    >>> # List of Server > Client messages
    >>> O = [o0, o1, o2, o3]

    >>> symbolList = I + O

    Now we can create the grammar which includes 5 states

    >>> s0 = State(name="S0")
    >>> s1 = State(name="S1")
    >>> s2 = State(name="S2")
    >>> s3 = State(name="S3")
    >>> s4 = State(name="S4")

    and their transitions

    >>> t0 = Transition(s0, s1, i0, [o0])
    >>> t1 = Transition(s1, s1, i1, [o1])
    >>> t2 = Transition(s1, s2, i2, [o2])
    >>> t3 = Transition(s2, s1, i1, [o1])
    >>> t4 = Transition(s2, s3, i0, [o0])
    >>> t5 = Transition(s3, s1, i1, [o1])
    >>> t6 = Transition(s3, s4, i2, [o2])
    >>> t7 = Transition(s1, s4, i0, [o1])

    we add an initial state and an ending state with open and close channel transitions

    >>> initialState = State(name="Initial")
    >>> endingState = State(name="End")
    >>> openTransition = OpenChannelTransition(initialState, s0)
    >>> closeTransition = CloseChannelTransition(s4, endingState)
    >>> automata = Automata(initialState, symbolList)

    >>> # Create an actor: Alice (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata = automata, initiator = False, abstractionLayer=abstractionLayer)
    >>> alice.start()

    We finaly create an angluin-based grammar learner

    >>> # Creates an inference channel
    >>> angluinChannel = UDPClient(remoteIP="127.0.0.1", remotePort=8887)
    # >>> angluin = MealyLSTAR(inputSymbols = I, outputSymbols = O, channel=angluinChannel)
    # >>> angluin.start()

    # We wait for the results

    >>> time.sleep(10)

    # >>> while (angluin.alive): time.sleep(5)
    >>> print("Inference finish")
    Inference finish

    >>> alice.stop()

    >>> print(angluin.initialStateOfInferedGrammar)
    State


    [Ang87]
    @article{Ang87, author = {Angluin, Dana}, title = {Learning regular sets from queries and counterexamples},
    journal = {Inf. Comput.}, year = {1987}, volume = {75}, pages = {87--106},  month = {November} }
    """

    def __init__(self, inputVocabulary, membershipOracle):
        self.inputVocabulary = inputVocabulary
        self.membershipOracle = membershipOracle
        self.__observationTable = ObservationTable(self.inputVocabulary)

    @property
    def hypothesisModel(self):
        self._logger.debug("Starting the computation of an hypothesis model")

    def refineHypothesis(self, counterExample):
        self._logger.debug("Refining the current hypothesis according to counter example : {}".format(counterExample))

    def startLearning(self):
        self._logger.debug("Starting the MealyLSTAR inference process.")

    @property
    def inputVocabulary(self):
        return self.__inputVocabulary

    @inputVocabulary.setter
    def inputVocabulary(self, inputVocabulary):
        self.__inputVocabulary = inputVocabulary

    @property
    def membershipOracle(self):
        return self.__membershipOracle

    @membershipOracle.setter
    def membershipOracle(self, mOracle):
        self.__membershipOracle = mOracle

    
        
#         # create logger with the given configuration
#         self.log = logging.getLogger('netzob.Inference.Grammar.MealyLSTAR.py')

#         self.observationTable = dict()
#         self.initializeObservationTable()

#     def initializeObservationTable(self):

#         self.log.info("Initialization of the observation table")
#         self.suffixes = []
#         self.D = []
#         # Create the S and SA
#         self.S = []
#         self.SA = []
#         self.initialD = []
#         # fullfill D with the dictionary
#         for entry in self.getInputDictionary():
#             letter = DictionarySymbol(entry)
#             mq = MembershipQuery([letter])
#             self.addWordInD(mq)
#             self.initialD.append(mq)
# #            self.D.append(letter)
# #            self.suffixes.append(letter)

#         # Initialize the observation table
#         emptyMQ = MembershipQuery([EmptySymbol()])
#         self.addWordInS(emptyMQ)

#     def addWordInD(self, words):
#         if words in self.D:
#             self.log.info("The words " + str(words) + " already exists in D")
#             return
#         self.log.info("Adding word " + str(words) + " in D")
#         self.D.append(words)
#         self.observationTable[words] = None
#         # We compute the value of all existing S and SA
#         cel = dict()
#         for wordS in self.S:
#             mq = wordS.getMQSuffixedWithMQ(words)
#             cel[wordS] = self.submitQuery(mq)
#         for wordSA in self.SA:
#             mq = wordSA.getMQSuffixedWithMQ(words)
#             cel[wordSA] = self.submitQuery(mq)
#         self.observationTable[words] = cel

#     def addWordInS(self, word):
#         # first we verify the word is not already in S
#         if word in self.S:
#             self.log.info("The word " + str(word) + " already exists in S")
#             return

#         if word in self.SA:
#             self.log.info("The word " + str(word) + " already exists in SA")
#             self.SA.remove(word)

#         self.log.info("Adding word " + str(word) + " to S")
#         self.S.append(word)

#         # We create a MQ which looks like : MQ(word,letter)
#         for letter in self.D:
#             mq = word.getMQSuffixedWithMQ(letter)
#             # we add it in the observation table
#             if self.observationTable[letter] is not None:
#                 cel = self.observationTable[letter]
#             else:
#                 cel = dict()

#             cel[word] = self.submitQuery(mq)
#             self.observationTable[letter] = cel

#         # Now we add
#         for letter in self.D:
#             self.addWordInSA(word.getMQSuffixedWithMQ(letter))

#         self.displayObservationTable()

#     def addWordInSA(self, word):
#         # first we verify the word is not already in SA
#         if word in self.SA:
#             self.log.info("The word " + str(word) + " already exists in SA")
#             return

#         if word in self.S:
#             self.log.info("The word " + str(word) + " already exists in S (addWordInSA)")
#             return

#         self.log.info("Adding word " + str(word) + " to SA")
#         self.SA.append(word)

#         for letter in self.D:
#             mq = word.getMQSuffixedWithMQ(letter)
#             if self.observationTable[letter] is not None:
#                 cel = self.observationTable[letter]
#             else:
#                 cel = dict()
#             cel[word] = self.submitQuery(mq)
#             self.observationTable[letter] = cel

#         self.displayObservationTable()

#     def learn(self):
#         self.log.info("Learn...")
#         self.displayObservationTable()

#         while (not self.isClosed() or not self.isConsistent()):
#             if not self.isClosed():
#                 self.log.info("#================================================")
#                 self.log.info("The table is not closed")
#                 self.log.info("#================================================")
#                 self.closeTable()
#                 self.displayObservationTable()
#             else:
#                 self.log.info("Table is closed !")

#             if not self.isConsistent():
#                 self.log.info("#================================================")
#                 self.log.info("The table is not consistent")
#                 self.log.info("#================================================")
#                 self.makesTableConsistent()
#                 self.displayObservationTable()
#             else:
#                 self.log.info("Table is consistent !")

#             self.log.info("Another turn")
#             self.displayObservationTable()

#         self.log.info("Table is closed and consistent")
#         # We compute an automata
#         self.computeAutomata()

#     def add_column(self):
#         pass

#     def move_row(self):
#         pass

#     def isEquivalent(self):
#         return True

#     def isClosed(self):
#         self.log.debug("Compute if the table is closed")
#         rowSA = []
#         rowS = []
#         for wordSA in self.SA:
#             rowSA = self.getRowOfObservationTable(wordSA)
#             found = False
#             self.log.info("isClosed()? We verify with SA member: {0}".format(str(rowSA)))
#             for wordS in self.S:
#                 rowS = self.getRowOfObservationTable(wordS)
#                 if self.rowsEquals(rowS, rowSA):
#                     self.log.debug("     isClosed(): YES ({0}) is equal!".format(str(rowS)))
#                     found = True

#             if not found:
#                 self.log.info("The low-row associated with {0} was not found in S".format(str(wordSA)))
#                 return False

#         return True

#     def closeTable(self):
#         self.log.debug("We close the table")

#         rowSA = []
#         rowS = []

#         for wordSA in self.SA:
#             rowSA = self.getRowOfObservationTable(wordSA)
#             found = False
#             for wordS in self.S:
#                 rowS = self.getRowOfObservationTable(wordS)

#                 if self.rowsEquals(rowS, rowSA):
#                     found = True

#             if not found:
#                 self.log.info("The low-row associated with " + str(wordSA) + " was not found in S")
#                 self.moveWordFromSAtoS(wordSA)
#                 return False
#         return True

#     def isConsistent(self):
#         self.log.info("Is consistent ... ?")
#         # search for all the rows of S which are equals
#         rowS = []
#         equalsRows = []
#         for wordS in self.S:
#             rowS.append((wordS, self.getRowOfObservationTable(wordS)))
#         for (word, row) in rowS:
#             for (word2, row2) in rowS:
#                 if word != word2 and self.rowsEquals(row, row2):
#                     equalsRows.append((word, word2))

#         self.log.info("isConsistent ? Equals Rows in S are from words: ")
#         for (w1, w2) in equalsRows:
#             self.log.info("w1=" + str(w1) + ";w2=" + str(w2))

#             # We verify all the equals rows are still equals one letter more
#             for a in self.initialD:
#                 w1a = w1.getMQSuffixedWithMQ(a)
#                 w2a = w2.getMQSuffixedWithMQ(a)
#                 self.log.info("Searching for word " + str(w1a))
#                 self.log.info("Searching for word " + str(w2a))

#                 row_w1a = self.getRowOfObservationTable(w1a)
#                 row_w2a = self.getRowOfObservationTable(w2a)
#                 if not self.rowsEquals(row_w1a, row_w2a):
#                     self.log.info("The table is not consistent because the rows from w1=" + str(w1a) + ";w2=" + str(w2a) + " are NOT equals")
#                     return False
#         return True

#     def makesTableConsistent(self):

#         # search for all the rows of S which are equals
#         rowS = []
#         equalsRows = []
#         for wordS in self.S:
#             rowS.append((wordS, self.getRowOfObservationTable(wordS)))
#         for (word, row) in rowS:
#             for (word2, row2) in rowS:
#                 if word != word2 and self.rowsEquals(row, row2):
#                     equalsRows.append((word, word2))

#         self.log.info("Equals Rows in S are from words: ")
#         for (w1, w2) in equalsRows:
#             self.log.info("w1=" + str(w1) + ";w2=" + str(w2))

#             # We verify all the equals rows are still equals one letter more
#             for a in self.initialD:
#                 w1a = w1.getMQSuffixedWithMQ(a)
#                 w2a = w2.getMQSuffixedWithMQ(a)
#                 row_w1a = self.getRowOfObservationTable(w1a)
#                 row_w2a = self.getRowOfObservationTable(w2a)
#                 if not self.rowsEquals(row_w1a, row_w2a):
#                     # We find the E (col) which makes the unconsistency
#                     e = None
#                     for i in range(0, len(row_w1a)):
#                         if row_w1a[i].getID() != row_w2a[i].getID():
#                             e = self.D[i]
#                     self.log.info("E found is " + str(e))
#                     newCol = a.getMQSuffixedWithMQ(e)
#                     self.log.info("So we add (a.e) to E (=D) a.e=[" + str(newCol) + "]")
#                     self.addWordInD(newCol)

#                     self.log.info("The table is not consistent because the rows from w1=" + str(w1a) + ";w2=" + str(w2a) + " are NOT equals")
#                     return False
#         return True

#     def rowsEquals(self, r1, r2):
#         if (len(r1) != len(r2)):
#             return False

#         for i in range(0, len(r1)):
#             if r1[i].getID() != r2[i].getID():
#                 return False
#         self.log.debug(str(r1) + " == " + str(r2))
#         return True

#     def moveWordFromSAtoS(self, wordSA):
#         if not wordSA in self.SA:
#             self.log.warn("Impossible to move the word from SA since it doesn't exist")
#             return
#         self.SA.remove(wordSA)
#         self.addWordInS(wordSA)

#     def getRowOfObservationTable(self, rowName):
#         cols = []
#         for letter in self.D:
#             val = self.observationTable[letter]
#             mem = None
#             for rN in val.keys():
#                 if rN == rowName:
#                     mem = rN
#                     break
#             if mem is not None:
#                 cols.append(self.observationTable[letter][mem])
#         return cols

#     def getUniqueRowsInS(self):
#         # Unique rows in S => new states (name = value of the row)
#         uniqueRowsInS = []
#         for wordS in self.S:
#             rowS = self.getRowOfObservationTable(wordS)
#             found = False
#             for (w, r) in uniqueRowsInS:
#                 if self.rowsEquals(r, rowS):
#                     found = True
#             if not found:
#                 uniqueRowsInS.append((wordS, rowS))
#         return uniqueRowsInS

#     def getSandSAWords(self):
#         result = []
#         for wordS in self.S:
#             result.append(wordS)
#         for wordSA in self.SA:
#             result.append(wordSA)
#         return result

#     def computeAutomata(self):
#         wordAndStates = []
#         startState = None
#         idState = 0
#         idTransition = 0
#         states = []

#         self.log.info("Compute the automata...")

#         # Create the states of the automata
#         uniqueRowsInS = self.getUniqueRowsInS()
#         for (w, r) in uniqueRowsInS:
#             self.log.info("The row with word {0} is unique !".format(str(w)))
#             # We create a State for each unique row
#             nameState = self.appendValuesInRow(r)
#             self.log.info("Create state: {0}".format(nameState))
#             currentState = NormalState(idState, nameState)
#             states.append(currentState)
#             wordAndStates.append((w, currentState))
#             # Is it the starting state (wordS = [EmptySymbol])
#             if startState is None and w == MembershipQuery([EmptySymbol()]):
#                 startState = currentState
#                 self.log.info("Its the starting state")

#             idState = idState + 1

#         self.log.debug("Create the transition of the automata")
#         # Create the transitions of the automata
#         for (word, state) in wordAndStates:
#             self.log.debug("Working on state: {0}".format(str(state.getName())))

#             for symbol in self.initialD:
#                 # retrieve the value:
#                 dicValue = self.observationTable[symbol]
#                 value = dicValue[word]
#                 # search for the output state
#                 mq = word.getMQSuffixedWithMQ(symbol)
#                 self.log.debug("> What happen when we send " + str(symbol) + " after " + str(word))
#                 self.log.debug(">> " + str(mq))

#                 for wordSandSA in self.getSandSAWords():
#                     self.log.info("IS " + str(wordSandSA) + " eq " + str(mq))
#                     if wordSandSA == mq:
#                         self.log.info("YES its equal")
#                         rowOutputState = self.getRowOfObservationTable(wordSandSA)
#                         outputStateName = self.appendValuesInRow(rowOutputState)
#                         self.log.debug("rowOutputState = " + str(rowOutputState))
#                         self.log.debug("outputStateName = " + str(outputStateName))

#                         # search for the state having this name:
#                         outputState = None
#                         self.log.info("Search for the output state: {0}".format(outputStateName))
#                         for (w2, s2) in wordAndStates:
#                             if s2.getName() == outputStateName:
#                                 outputState = s2
#                                 self.log.info("  == " + str(s2.getName()))
#                             else:
#                                 self.log.info("   != " + str(s2.getName()))

#                         if outputState is not None:
#                             inputSymbol = symbol.getSymbolsWhichAreNotEmpty()[0]

#                             self.log.info("We create a transition from " + str(state.getName()) + "=>" + str(outputState.getName()))
#                             self.log.info(" input: {0}".format(str(inputSymbol)))
#                             self.log.info(" output: {0}".format(str(value)))

#                             transition = SemiStochasticTransition(idTransition, "Transition " + str(idTransition), state, outputState, inputSymbol)
#                             transition.addOutputSymbol(value, 100, 1000)
#                             state.registerTransition(transition)

#                             idTransition = idTransition + 1

#                         else:
#                             self.log.error("<!!> Impossible to retrieve the output state named " + str(s2.getName()))

#         if startState is not None:
#             self.log.info("An infered automata has been computed.")

#             self.inferedAutomata = MMSTD(startState, self.dictionary)
#             for state in states:
#                 self.inferedAutomata.addState(state)
#             self.log.info("----------------------------------------------")
#             self.log.info("Constructed Hypothetised Automata:")
#             self.log.info("----------------------------------------------")
#             self.log.info(self.inferedAutomata.getDotCode())

#     def addCounterExamples(self, counterExamples):
#         self.log.info("Modify the automata in order to consider the " + str(len(counterExamples)) + " counterexamples")
#         for counterExample in counterExamples:
#             # we add all the prefix of the counterexample to S
#             prefixes = counterExample.getNotEmptyPrefixes()
#             self.log.info("A number of " + str(len(prefixes)) + " will be added !")
#             for p in prefixes:
#                 self.log.info("=> " + str(p))
#             for prefix in prefixes:
#                 self.displayObservationTable()
#                 self.addWordInS(prefix)
#                 self.displayObservationTable()

#     def appendValuesInRow(self, row):
#         result = []
#         for i in range(0, len(row)):
#             result.append(str(row[i]))
#         return '-'.join(result)

#     def displayObservationTable(self):
#         self.log.info(self.observationTable)

#         horizontal = "---------------------------------------------------------------------------------"
#         horizontal2 = "================================================================================="
#         self.log.info(horizontal)
#         line = []
#         for letter in self.D:
#             line.append(str(letter))
#         self.log.info("\t|\t|" + "\t|".join(line))
#         self.log.info(horizontal2)

#         for mqS in self.S:
#             line = []
#             line.append(str(mqS))
#             for letter in self.D:
#                 tmp = self.observationTable[letter]
#                 line.append(str(tmp[mqS]))
#             self.log.info("\t|".join(line))
#             self.log.info(horizontal)
#         self.log.info(horizontal2)
#         for mqSA in self.SA:
#             line = []
#             line.append(str(mqSA))
#             for letter in self.D:
#                 tmp = self.observationTable[letter]
#                 line.append(str(tmp[mqSA]))
#             self.log.info("\t|".join(line))
#             self.log.info(horizontal)

# #        self.addWordInS(MembershipQuery([]))

