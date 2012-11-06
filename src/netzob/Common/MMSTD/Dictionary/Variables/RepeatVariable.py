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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
from lxml import etree
import logging
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variables.AbstractNodeVariable import \
    AbstractNodeVariable
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable


class RepeatVariable(AbstractNodeVariable):
    """RepeatVariable:
            A variable with one child that repeats a certain time every treatment on this child.
    """

    MAX_ITERATIONS = 10  # TODO: Choose a better value.
    TYPE = "Repeat Variable"

    def __init__(self, _id, name, mutable, learnable, child, minIterations, maxIterations):
        """Constructor of RepeatVariable:
                Each treatment will be repeated at most maxIterations time.
                Each function will call once by iteration its equivalent in the class on the child.
                During an iteration, if the child treatment failed, we canceled the iteration loop.
                If we had done less than minIteration, the global processing is considered failed, else it is considered successful.

                @type child: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable
                @param child: the unique child which treatments will be repeated.
                @type minIterations: integer
                @param minIterations: the minimum number of iteration each treatment have to be repeated.
                @type maxIterations: integer
                @param maxIterations: the maximum number of iteration each treatment will be repeated.
        """
        AbstractNodeVariable.__init__(self, _id, name, mutable, learnable, [child])
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.RepeatVariable.py')
        if minIterations is not None and minIterations >= 0:
            self.minIterations = minIterations
        else:
            self.log.info("Variable {0} (Repeat): Construction of RepeatVariable: minIterations undefined or < 0. minIterations value is fixed to 0.".format(self.getName()))
            self.minIterations = 0
        if maxIterations is not None and maxIterations >= minIterations:
            self.maxIterations = maxIterations
        else:
            self.log.info("Variable {0} (Repeat): Construction of RepeatVariable: maxIterations undefined or < minIterations. maxIterations value is fixed to minIterations.".format(self.getName()))
            self.maxIterations = self.minIterations
        self.currentIteration = 0  # Tells on which iteration we currently are.

    def readChild(self, readingToken):
        """read:
                The pointed variable reads the value.
        """
        self.log.debug("[ {0}: read access:".format(self.toString()))
        (minIterations, maxIterations) = self.getNumberIterations()
        self.currentIteration = 0

        # Memorized initial values for the child and its successors.
        dictOfValues = dict()
        dictOfValue = self.getChild().getDictOfValues(readingToken)
        savedIndex = readingToken.getIndex()

        for key, val in dictOfValue.iteritems():
            dictOfValues[key] = val

        if self.isLearnable():
            # We assume to be unlimited.
            while True:
                self.getChild().read(readingToken)
                if readingToken.isOk():
                    self.currentIteration += 1
                else:
                    break
            self.maxIterations = max(self.currentIteration, self.maxIterations)
        else:
            for i in range(maxIterations):
                self.getChild().read(readingToken)
                if readingToken.isOk():
                    self.currentIteration += 1
                else:
                    break
        # We search if we have done the minimum number of iterations.
        if self.currentIteration < minIterations:
            if self.isLearnable():
                # We adapt the minimum number of iterations to comply to the read value.
                minIterations = self.currentIteration
                readingToken.setOk(True)
            else:
                readingToken.setOk(False)
                # If not, we clean our traces.
                readingToken.setIndex(savedIndex)
                vocabulary = readingToken.getVocabulary()
                for key, val in dictOfValues.iteritems():
                    child = vocabulary.getVariableByID(key)
                    # We restore the current values.
                    child.setCurrentValue(val)
                    # We restore the cached values.
                    child.restore(readingToken)
        else:
            readingToken.setOk(True)
            # The value of the variable is simply the value we 'ate'.
            self.currentValue = readingToken.getValue()[savedIndex:readingToken.getIndex()]

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), readingToken.toString()))

    def writeChild(self, writingToken):
        """write:
                The pointed variable writes its value.
        """
        self.log.debug("[ {0}: write access:".format(self.toString()))
        (minIterations, maxIterations) = self.getNumberIterations()
        self.currentIteration = 0
        savedIndex = writingToken.getIndex()
        savedValue = writingToken.getValue()

        # Memorized initial values for the child and its successors.
        dictOfValues = dict()
        dictOfValue = self.getChild().getDictOfValues(writingToken)
        for key, val in dictOfValue.iteritems():
            dictOfValues[key] = val

        for i in range(maxIterations):
            self.getChild().write(writingToken)
            if writingToken.isOk():
                self.currentIteration += 1
            else:
                break
        # We search if we have done the minimum number of iterations.
        if self.currentIteration < minIterations:
            writingToken.setOk(False)
            # If not, we clean our traces.
            writingToken.setValue(savedValue)
            vocabulary = writingToken.getVocabulary()
            for key, val in dictOfValues.iteritems():
                child = vocabulary.getVariableByID(key)
                # We restore the current values.
                child.setCurrentValue(val)
                # We restore the cached values.
                child.restore(writingToken)
        else:
            writingToken.setOk(True)
            # The value of the variable is simply the value we made.
            self.currentValue = writingToken.getValue()[savedIndex:writingToken.getIndex()]

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), writingToken.toString()))

    def randomizeIterations(self):
        """randomizeIterations:
                Generate randomly a couple of max and min number iterations.
                TODO: implement a better random finding way (for example a Poisson law center around 10, so we would mostly have short values, and sometimes we would have high values.
        """
        x = random.randint(0, RepeatVariable.MAX_ITERATIONS)
        y = random.randint(0, RepeatVariable.MAX_ITERATIONS)
        self.minIterations = min(x, y)
        self.maxIterations = max(x, y)
        return self.getNumberIterations()

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def getVariableType(self):
        """getVariableType:
        """
        return RepeatVariable.TYPE

    def toString(self):
        """toString:
        """
        return "[Repeat] {0}, iterations: ({1}, {2})".format(AbstractVariable.toString(self), str(self.minIterations), str(self.maxIterations))

    def getDescription(self, processingToken):
        """getDescription:
        """
        return "[{0}, child:\n - {1}]".format(self.toString(), self.getChild().getDescription(processingToken))

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
        """
        return "[{0}, child:\n - {1}]".format(self.toString(), self.getChild().getUncontextualizedDescription())

    def isDefined(self, processingToken):
        """isDefined:
        """
        return self.getChild().isDefined(processingToken)

    def read(self, readingToken):
        """read:
                Each child tries sequentially to read a part of the read value.
                If one of them fails, the whole operation is cancelled.
        """
        self.log.debug("[ {0} (Aggregate): read access:".format(AbstractVariable.toString(self)))
        if self.getChildren() is not None:
            self.readChild(readingToken)

        else:
            # no child.
            self.log.debug("Write abort: the variable has no child.")
            readingToken.setOk(False)

        # Variable notification
        if readingToken.isOk():
            self.notifyBoundedVariables("read", readingToken, self.currentValue)

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), readingToken.toString()))

    def write(self, writingToken):
        """write:
                Each child tries sequentially to write its value.
                If one of them fails, the whole operation is cancelled.
        """
        self.log.debug("[ {0} (Aggregate): write access:".format(AbstractVariable.toString(self)))
        if self.getChildren() is not None:
            if self.isMutable():
                # mutable.
                self.randomizeIterations()
                self.writeChild(writingToken)

            else:
                # not mutable.
                self.writeChild(writingToken)

        else:
            # no child.
            self.log.debug("Write abort: the variable has no child.")
            writingToken.setOk(False)

        # Variable notification
        if writingToken.isOk():
            self.notifyBoundedVariables("write", writingToken)

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), writingToken.toString()))

    def toXML(self, root, namespace):
        """toXML:
            Creates the xml tree associated to this variable.
            Adds every child's own xml definition as xml child to this tree.
        """
        self.log.debug("[ {0}: toXML:".format(self.toString()))
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:RepeatVariable")
        xmlVariable.set("mutable", str(self.isMutable()))
        xmlVariable.set("learnable", str(self.isLearnable()))

        # Definition of child variable
        self.getChild().toXML(xmlVariable, namespace)

        # minIterations
        xmlMinIterations = etree.SubElement(xmlVariable, "{" + namespace + "}minIterations")
        xmlMinIterations.text = str(self.minIterations)

        # maxIterations
        xmlMaxIterations = etree.SubElement(xmlVariable, "{" + namespace + "}maxIterations")
        xmlMaxIterations.text = str(self.maxIterations)
        self.log.debug("Variable {0}. ]".format(self.getName()))

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getNumberIterations(self):
        return (self.minIterations, self.maxIterations)

    def getCurrentIteration(self):
        return self.currentIteration

    def getChild(self):
        return self.children[0]

    def addChild(self, child):
        self.children[0] = child
        child.addFather(self)

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version, symbol):
        """loadFromXML:
                Loads a repeat variable from an XML definition.
                We do not trust the user and check every field (even mandatory).
        """
        logging.debug("[ RepeatVariable: loadFromXML:")
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable") == "True"
            xmlLearnable = xmlRoot.get("learnable") == "True"

            xmlChild = xmlRoot.find("{" + namespace + "}variable")
            child = AbstractVariable.loadFromXML(xmlChild, namespace, version, symbol)

            # minIterations
            xmlMinIterations = xmlRoot.find("{" + namespace + "}minIterations")
            if xmlMinIterations is not None:
                minIterations = int(xmlMinIterations.text)
            else:
                minIterations = 0

            # maxIterations
            xmlMaxIterations = xmlRoot.find("{" + namespace + "}maxIterations")
            if xmlMaxIterations is not None:
                maxIterations = int(xmlMaxIterations.text)
            else:
                maxIterations = RepeatVariable.MAX_ITERATIONS

            result = RepeatVariable(xmlID, xmlName, xmlMutable, xmlLearnable, child, minIterations, maxIterations)
            logging.debug("RepeatVariable: loadFromXML successes: {0} ]".format(result.toString()))
            return result
        logging.debug("RepeatVariable: loadFromXML fails")
        return None
