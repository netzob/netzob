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
from gettext import gettext as _
import logging
import time
from collections import deque
import os
#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Inference.Grammar.EquivalenceOracles.AbstractEquivalenceOracle import AbstractEquivalenceOracle
from netzob.Inference.Grammar.Queries.MembershipQuery import MembershipQuery
from netzob.Model.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Inference.Grammar.Oracles.NetworkOracle import NetworkOracle


#+----------------------------------------------
#| WMethodNetworkEquivalenceOracle:
#+----------------------------------------------
class WMethodNetworkEquivalenceOracle(AbstractEquivalenceOracle):

    def __init__(self, communicationChannel, maxSize, resetScript):
        AbstractEquivalenceOracle.__init__(self, "WMethodNetworkEquivalenceOracle")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.EquivalenceOracles.WMethodNetworkEquivalenceOracle')
        self.communicationChannel = communicationChannel
        self.m = maxSize
        self.resetScript = resetScript

    def canWeDistinguishStates(self, mmstd, mq, state1, state2):
        (traceState1, endStateTrace1) = mmstd.getOutputTrace(state1, mq.getSymbols())
        (traceState2, endStateTrace2) = mmstd.getOutputTrace(state2, mq.getSymbols())
        self.log.info("Trace 1 = {0}".format(str(traceState1)))
        self.log.info("Trace 2 = {0}".format(str(traceState2)))
        if traceState1 == traceState2:
            self.log.info("Impossible to distinguish the strings")
            return False
        else:
            self.log.info("YES, its distinguished strings")
            return True

    def findCounterExample(self, mmstd, inputSymbols, cache):
        self.log.info("=====================================================")
        self.log.info("Find a counterexample which invalids the given MMSTD")
        self.log.info("=====================================================")

        inputDictionary = []
        for entry in inputSymbols:
            letter = DictionarySymbol(entry)
            inputDictionary.append(letter)
            self.log.info("The vocabulary contains: {0}".format(str(letter)))

        # -----------------------------------------------------------------------
        # FIRST WE COMPUTE WHICH WILL WE MAKE !
        # -----------------------------------------------------------------------
        # This our plan to find same
        # STEP 1 : Estimate the maximum number of states (m) in the correct implementation
        #          of the FSM (DONE PREVISOULY AND TRANSMITED THROUGH PARAM self.maxsize
        # STEP 2 : Construct the characterization set W for [MMSTD]
        # STEP 3:
        #          (a) Construct the "testing tree" for MMSTD
        #          (b) Generate the transition cover set P from the testing tree
        # STEP 4 : Construct set Z from W and m
        # STEP 5 : We have the list of so desired test cases = P.Z

        # STEP 2:
        # - Construct a sequence of k-equivalence partitions of the states of MMSTD:

        # Find all the couples of states
        couples = []
        states = mmstd.getAllStates()
        W = []
        self.log.info("The MMSTD has " + str(len(states)) + " states")
        self.log.info("A number of " + str(self.m) + " states is estimated.")
        for state in states:
            for state2 in states:
                if state != state2:
                    found = False
                    for (s1, s2) in couples:
                        if not ((s1 == state) and (s2 == state2) or ((s1 == state2) and (s2 == state))):
                            found = True
                    if not found:
                        couples.append((state, state2))

        self.log.info("A number of " + str(len(couples)) + " couples was found")

        for (state1, state2) in couples:
            self.log.info("Search a distinguish string between " + state1.getName() + " and " + state2.getName())
            z = MembershipQuery([EmptySymbol()])

            mqToTest = deque([])
            for letter in inputDictionary:
                mqToTest.append(z.getMQSuffixedWithMQ(MembershipQuery([letter])))

            lastIndiguishableZ = z
            distinguishableZ = z
            done = False
            i = 0
            while not done:
                mq = mqToTest.popleft()
                if i > self.m * self.m:
                    break

                self.log.info("Can we distinguish with MQ = " + str(mq))
                if not self.canWeDistinguishStates(mmstd, mq, state1, state2):
                    done = False
                    lastIndiguishableZ = mq
                    for letter in inputDictionary:
                        z = mq.getMQSuffixedWithMQ(MembershipQuery([letter]))
                        mqToTest.append(z)
                else:
                    done = True
                    distinguishableZ = mq

                i = i + 1
            self.log.info("FOUND: the following distinguish them: {0} last which doesn't is {1}".format(str(distinguishableZ), str(lastIndiguishableZ)))
            W.append(distinguishableZ)
        self.log.info("=================================")
        self.log.info("W = " + str(W))
        self.log.info("=================================")

        # Execute STEP 3 : We compute P
        # init P = {E, ...}
        currentMQ = MembershipQuery([EmptySymbol()])
        P = [currentMQ]
        openMQ = deque([currentMQ])
        closeMQ = []
        statesSeen = [mmstd.getInitialState()]
        while len(openMQ) > 0:
            self.log.info("Compute P, ...")
            mq = openMQ.popleft()
            tmpstatesSeen = []
            for letter in inputDictionary:
                z = mq.getMQSuffixedWithMQ(MembershipQuery([letter]))
                self.log.debug("Get output trace if we execute the MMSTD with " + str(z.getSymbols()))
                (trace, outputState) = mmstd.getOutputTrace(mmstd.getInitialState(), z.getSymbols())
                if outputState in statesSeen:
                    # we close this one
                    self.log.info("Adding " + str(z) + " in closeMQ")
                    closeMQ.append(z)
                else:
                    tmpstatesSeen.append(outputState)
                    self.log.info("Adding " + str(z) + " in closeMQ")
                    closeMQ.append(z)
                    # still open
                    openMQ.append(z)
            statesSeen.extend(tmpstatesSeen)

        P.extend(closeMQ)

        # STEP 4 : We compute Z
        # it follows the formula Z= W U (X^1.W) U .... U (X^(m-1-n).W) U (W^(m-n).W)
        self.log.info("Computing Z:")
        Z = []
        # First we append W in Z
        for w in W:
            Z.append(w)

        v = self.m - len(states)
        if v < 0:
            v = 0

        mqInputs = []
        for input in inputDictionary:
            mqInputs.append(MembershipQuery([input]))

        X = dict()
        X[0] = W

        for i in range(1, v + 1):
            self.log.info("Computing X^{0}: ".format(str(i)))
            self.log.info("MQ INputs: {}".format(str(len(mqInputs))))
            self.log.info("W: {}".format(str(len(W))))
            X[i] = []
            previousX = X[i - 1]
            self.log.info(previousX)
            for x in previousX:
                X[i].extend(x.multiply(mqInputs))
            for w in W:
                for xi in X[i]:
                    if not xi in Z:
                        Z.append(xi)
                    else:
                        self.log.warn("Impossible to add X[{0}] = {1} in Z, it already exists".format(str(i), str(xi)))

        for z in Z:
            self.log.info("z = {0}".format(str(z)))

        # STEP 5 : We have the list of so desired test cases T = P.Z
        T = []
        for p in P:
            T.extend(p.multiply(Z))

        self.log.info("Tests cases are: ")
        for t in T:
            self.log.info("=> {0}".format(str(t)))

        testsResults = dict()
        self.log.info("----> Compute the responses to the the tests over our model and compare them with the real one")
        i_test = 0
        # We compute the response to the different tests over our learning model and compare them with the real one
        for test in T:
            i_test = i_test + 1
            # Compute our results
            (traceTest, stateTest) = mmstd.getOutputTrace(mmstd.getInitialState(), test.getSymbols())

            # Verify the request is not in the cache
            cachedValue = cache.getCachedResult(test)
            if cachedValue is None:
                # Compute real results
                if self.resetScript != "":
                    os.system("sh " + self.resetScript)

                self.log.debug("=====================")
                self.log.debug("Execute test {0}/{1}: {2}".format(str(i_test), str(len(T)), str(test)))
                self.log.debug("=====================")

                isMaster = not self.communicationChannel.isServer()

                testedMmstd = test.toMMSTD(mmstd.getVocabulary(), isMaster)  # TODO TODO
                oracle = NetworkOracle(self.communicationChannel, isMaster)  # TODO TODO is master ??
                oracle.setMMSTD(testedMmstd)
                oracle.start()
                while oracle.isAlive():
                    time.sleep(0.01)
                oracle.stop()

                if isMaster:
                    resultQuery = oracle.getGeneratedOutputSymbols()
                else:
                    resultQuery = oracle.getGeneratedInputSymbols()
                cache.cacheResult(test, resultQuery)

            else:
                resultQuery = cachedValue

            mqOur = MembershipQuery(traceTest)
            mqTheir = MembershipQuery(resultQuery)

            if not mqOur.isStrictlyEqual(mqTheir):
                self.log.info("========================")
                self.log.info("We found a counter example")
                self.log.info("========================")
                self.log.info("TEST: {0}".format(str(test)))
                self.log.info("OUR: {0}".format(str(mqOur)))
                self.log.info("THEIR: {0}".format(str(mqTheir)))
                return test
            else:
                self.log.info("========================")
                self.log.info("Not a counter example")
                self.log.info("========================")

        return None
