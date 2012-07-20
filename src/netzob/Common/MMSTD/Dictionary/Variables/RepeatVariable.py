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
from bitarray import bitarray
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable.AggregateVariable import AggregateVariable


class RepeatVariable(AggregateVariable):
    """RepeatVariable:
            A variable that is an aggregate variable for which each treatment is repeated.
    """

    MAX_ITERATIONS = 10

    def __init__(self, id, name, children=None, minIterations, maxIterations):
        """Constructor of RepeatVariable:
                Each treatment will be repeated at most maxIterations time.
                Each function will call once by iteration its equivalent in the AggregateVariable class on the children.
                During an iteration, if one child's treatment failed, we canceled the iteration loop.
                If we had done less than minIteration, the global processing is considered failed, else it is considered successful.

                @type minIterations: integer
                @param minIterations: the minimum number of iteration each treatment have to be repeated.
                @type maxIterations: integer
                @param maxIterations: the maximum number of iteration each treatment will be repeated.
        """
        AggregateVariable.__init__(self, id, name, children)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.RepeatVariable.py')
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
    def learn(self, readingToken):
        """learn:
        """
        successfullIterations = 0
        for i in range(self.maxIterations):
            AggregateVariable.learn(self, readingToken)
            if readingToken.isOk():
                successfullIterations += 1
            else:
                break
        # We search if we have done the minimum number of iterations.
        if successfullIterations < selfminIterations:
            readingToken.setOk(False)
        else:
            readingToken.setOk(True)

    def compare(self, readingToken):
        """compare:
        """
        successfullIterations = 0
        for i in range(self.maxIterations):
            AggregateVariable.compare(self, readingToken)
            if readingToken.isOk():
                successfullIterations += 1
            else:
                break
        # We search if we have done the minimum number of iterations.
        if successfullIterations < selfminIterations:
            readingToken.setOk(False)
        else:
            readingToken.setOk(True)

    def getValue(self, writingToken):
        """getValue:
        """
        AggregateValue.getValue(self, writingToken)

    def toXML(self, root, namespace):
        """toXML:
            Creates the xml tree associated to this variable.
            Adds every child's own xml definition as xml child to this tree.
        """
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:RepeatVariable")

        # Definition of children variables
        for child in self.children:
            child.toXML(xmlVariable, namespace)

        # minIterations
        xmlMinIterations = etree.SubElement(xmlVariable, "{" + namespace + "}minIterations")
        xmlMinIterations.text = self.minIterations

        # maxIterations
        xmlMaxIterations = etree.SubElement(xmlVariable, "{" + namespace + "}maxIterations")
        xmlMaxIterations.text = self.maxIterations

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Loads an aggregate variable from an XML definition.
                We do not trust the user and check every field (even mandatory).
        """
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            children = []
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable"):
                child = AbstractVariable.loadFromXML(xmlChildren, namespace, version)
                children.append(child)

            # minIterations
            xmlMinIterations = xmlRoot.find("{" + namespace + "}minIterations")
            if xmlMinIterations != None:
                minIterations = int(xmlMinIterations.text)
            else:
                minIterations = 0

            # maxIterations
            xmlMaxIterations = xmlRoot.find("{" + namespace + "}maxIterations")
            if xmlMaxIterations != None:
                maxIterations = int(xmlMaxIterations.text)
            else:
                maxIterations = MAX_ITERATIONS

            return RepeatVariable(id, name, children, minIterations, maxIterations)
        return None
