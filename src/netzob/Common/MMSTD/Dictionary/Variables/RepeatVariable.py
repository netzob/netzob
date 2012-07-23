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
import logging
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable import AbstractVariable


class RepeatVariable(AbstractVariable):
    """RepeatVariable:
            A variable with one child that repeats a certain time every treatment on this child.
    """

    MAX_ITERATIONS = 10

    def __init__(self, id, name, child, minIterations, maxIterations):
        """Constructor of RepeatVariable:
                Each treatment will be repeated at most maxIterations time.
                Each function will call once by iteration its equivalent in the class on the children.
                During an iteration, if the child treatment failed, we canceled the iteration loop.
                If we had done less than minIteration, the global processing is considered failed, else it is considered successful.

                @type child: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable
                @param child: the unique child which treatments will be repeated.
                @type minIterations: integer
                @param minIterations: the minimum number of iteration each treatment have to be repeated.
                @type maxIterations: integer
                @param maxIterations: the maximum number of iteration each treatment will be repeated.
        """
        AbstractVariable.__init__(self, id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.RepeatVariable.py')
        if child is not None:
            self.child = child
        else:
            log.debug(_("Construction of RepeatVariable: no child given."))
        if minIterations is not None and minChars >= 0:
            self.minIterations = minIterations
        else:
            log.debug(_("Construction of RepeatVariable: minIterations undefined or < 0. minIterations value is fixed to 0."))
            self.minIterations = 0
        if maxIterations is not None and maxIterations >= minIterations:
            self.maxIterations = maxIterations
        else:
            log.debug(_("Construction of RepeatVariable: maxIterations undefined or < minIterations. maxIterations value is fixed to minIterations."))
            self.maxIterations = self.minIterations

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def isDefined(self):
        return self.child.isDefined()

    def forget(self, processingToken):
        """forget:
                The child forgets its value.
        """
        self.log.debug(_("The value of the child of variable {0} is forgotten.").format(self.getName()))
        self.child.forget(processingToken)

    def memorize(self, processingToken):
        """memorize:
                The child memorizes its value.
        """
        self.log.debug(_("The value of the child of variable {0} is memorized.").format(self.getName()))
        self.child.memorize(processingToken)

    def learn(self, readingToken):
        """learn:
                The child tries to learn the read value at least minIterations time, at most maxIterations time.
        """
        self.log.debug(_("The child of variable {0} tries to learn the value {1} starting at {2} at least {3} times, at most {4} times.").format(self.getName(), str(readingToken.getValue()), str(readingToken.getIndex()), str(self.minIterations), str(self.maxIterations)))
        (minIterations, maxIterations) = selfgetNumberIterations()
        successfullIterations = 0
        for i in range(maxIterations):
            self.child.learn(readingToken)
            if readingToken.isOk():
                successfullIterations += 1
            else:
                break
        # We search if we have done the minimum number of iterations.
        if successfullIterations < minIterations:
            readingToken.setOk(False)
        else:
            readingToken.setOk(True)
            self.sefDefined(True)

    def compare(self, readingToken):
        """compare:
                The child compare its value to the read value at least minIterations time, at most maxIterations time.
        """
        self.log.debug(_("The child of variable {0} compares its current value to {1} starting at {2} at least {3} times, at most {4} times.").format(self.getName(), str(readingToken.getValue()), str(readingToken.getIndex()), str(self.minIterations), str(self.maxIterations)))
        (minIterations, maxIterations) = selfgetNumberIterations()
        successfullIterations = 0
        for i in range(maxIterations):
            self.child.compare(readingToken)
            if readingToken.isOk():
                successfullIterations += 1
            else:
                break
        # We search if we have done the minimum number of iterations.
        if successfullIterations < minIterations:
            readingToken.setOk(False)
        else:
            readingToken.setOk(True)

    def generate(self, writingToken):
        """generate:
                Calls the child generation method at least minIterations time, at most maxIterations time.
                It concatenates these values.
        """
        self.log.debug(_("The child of variable {0} generates a new value at least {3} times, at most {4} times.").format(self.getName(), str(self.minIterations), str(self.maxIterations)))
        (minIterations, maxIterations) = selfgetNumberIterations()
        successfullIterations = 0
        for i in range(maxIterations):
            self.child.generate(writingToken)
            if writingToken.isOk():
                successfullIterations += 1
            else:
                break
        # We search if we have done the minimum number of iterations.
        if successfullIterations < minIterations:
            writingToken.setOk(False)
        else:
            writingToken.setOk(True)
            self.sefDefined(True)

    def getValue(self, writingToken):
        """getValue:
                Calls the child generation method at least minIterations time, at most maxIterations time.
                It concatenates these values.
        """
        self.log.debug(_("The child of variable {0} gets its value at least {3} times, at most {4} times.").format(self.getName(), str(self.minIterations), str(self.maxIterations)))
        (minIterations, maxIterations) = selfgetNumberIterations()
        successfullIterations = 0
        for i in range(maxIterations):
            self.child.getValue(writingToken)
            if writingToken.isOk():
                successfullIterations += 1
            else:
                break
        # We search if we have done the minimum number of iterations.
        if successfullIterations < minIterations:
            writingToken.setOk(False)
        else:
            writingToken.setOk(True)

    def toXML(self, root, namespace):
        """toXML:
            Creates the xml tree associated to this variable.
            Adds every child's own xml definition as xml child to this tree.
        """
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:RepeatVariable")

        # Definition of child variable
        self.child.toXML(xmlVariable, namespace)

        # minIterations
        xmlMinIterations = etree.SubElement(xmlVariable, "{" + namespace + "}minIterations")
        xmlMinIterations.text = self.minIterations

        # maxIterations
        xmlMaxIterations = etree.SubElement(xmlVariable, "{" + namespace + "}maxIterations")
        xmlMaxIterations.text = self.maxIterations

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getNumberIterations(self):
        if self.isRandom():
            x = random.randint(0, MAX_ITERATIONS)
            y = random.randint(0, MAX_ITERATIONS)
            self.minIterations = min(x, y)
            self.maxIterations = max(x, y)
        return (self.minIterations, self.maxIterations)

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Loads a repeat variable from an XML definition.
                We do not trust the user and check every field (even mandatory).
        """
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlChild = xmlRoot.findall("{" + namespace + "}variable")
            child = AbstractVariable.loadFromXML(xmlChildren, namespace, version)

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
                maxIterations = MAX_ITERATIONS

            return RepeatVariable(id, name, child, minIterations, maxIterations)
        return None
