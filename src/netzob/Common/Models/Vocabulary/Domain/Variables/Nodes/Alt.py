#-*- coding: utf-8 -*-

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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Utils.NetzobRegex import NetzobRegex
from netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken import AbstractVariableProcessingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken import VariableReadingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableWritingToken import VariableWritingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.Agg import Agg
from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.Eol import Eol


@NetzobLogger
class Alt(AbstractVariableNode):
    """Represents an Alternative (OR) in the domain definition

    To create an alternative:

    >>> from netzob.all import *
    >>> domain = Alt([Raw(), ASCII()])
    >>> print domain.varType
    Alt
    >>> print domain.children[0].dataType
    Raw=None ((0, None))
    >>> print domain.children[1].dataType
    ASCII=None ((0, None))

    That's another simple example that also illustrates rollback mechanisms

    >>> from netzob.all import *
    >>> m1 = RawMessage("220044")
    >>> f1 = Field("22")
    >>> f2 = Field(Alt(["00", "0044", "0", "004"]))
    >>> s = Symbol([f1, f2], messages=[m1])
    >>> print s
    22 | 000044

    """

    def __init__(self, children=None, learnable=False, mutable=True):
        super(Alt, self).__init__(self.__class__.__name__, children, learnable=learnable, mutable=mutable)

    @typeCheck(AbstractVariableProcessingToken)
    def isDefined(self, processingToken):
        """If one child is defined the node is defined.

        :param processingToken: a variable processing token fro mwhich we can have access to the memory
        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken`
        :raise: TypeError if parameter is not Valid
        """

        if processingToken is None:
            raise TypeError("processingToken cannot be None")

        if len(self.children) > 0:
            for child in self.children:
                if child.isDefined(processingToken):
                    return True
        return False

    @typeCheck(VariableReadingToken)
    def read(self, readingToken):
        """Grants a reading access to the variable.
        Each child tries sequentially to read a part of the read value.
        If none of them is read, the whole operation fails

        :param readingToken: a token which contains all critical information on this reading access.
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.VariableReadingToken.VariableReadingToken`
        :raise: TypeError if parameter is not Valid
        """
        if readingToken is None:
            raise TypeError("readingToken cannot be None")

        self._logger.debug("[ {0} (Alternate): read access:".format(self))
        if len(self.children) > 0:
            self.readChildren(readingToken, self.mutable)
        else:
            # no child.
            self._logger.debug("read abort: the variable has no child.")
            readingToken.Ok(False)

        # Variable notification
        #if readingToken.Ok:
        #    self.notifyBoundedVariables("read", readingToken, self.currentValue)

        self._logger.debug("{0}. ]".format(readingToken))

    @typeCheck(VariableWritingToken)
    def write(self, writingToken):
        """Each child tries sequentially to write its value.
        one of them fails, the whole operation is cancelled.

        >>> from netzob.all import *
        >>> fHello = Field(Agg(["hello", " "]))
        >>> fName = Field(Alt(["zoby", "netzob"]))
        >>> fName.domain.mutable = True
        >>> s = Symbol([fHello, fName])
        >>> result = [s.specialize() for x in range(300)]
        >>> print "hello netzob" in result
        True
        >>> print "hello zoby" in result
        True

        :param readingToken: a token which contains all critical information on this reading access.
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.VariableReadingToken.VariableReadingToken`
        :raise: TypeError if parameter is not Valid
        """

        if writingToken is None:
            raise TypeError("writingToken cannot be None")

        self._logger.debug("[ {0} (Alternate): write access:".format(self))
        self.tokenChoppedIndex = []  # New write access => new final value and new reference to it.
        if len(self.children) > 0:
            self.writeChildren(writingToken, self.mutable)
            # if self.mutable:
            #     # mutable.
            #     self.shuffleChildren()
            #     self.writeChildren(writingToken)
            # else:
            #     # not mutable.
            #     self.writeChildren(writingToken)
        else:
            # no child.
            self._logger.debug("Write abort: the variable has no child.")
            writingToken.Ok = False

        # Variable notification
        if writingToken.Ok:
            self.notifyBoundedVariables("write", writingToken)

        self._logger.debug("{0}. ]".format(writingToken))

    def readChildren(self, readingToken, shuffleChildren=False):
        """Each child tries to read its value..
        If it fails, it restore it value and the next child try.
        It stops if one child successes.

        >>> from netzob.all import *
        >>> data = TypeConverter.convert("earth", ASCII, BitArray)
        >>> alt = Alt([ASCII("world"), ASCII("earth")])
        >>> rToken = VariableReadingToken()
        >>> rToken.setValueForVariable(alt, data)
        >>> alt.readChildren(rToken)
        >>> print rToken.Ok
        True

        >>> data = TypeConverter.convert("no-earth", ASCII, BitArray)
        >>> alt = Alt([ASCII("world"), ASCII("earth")])
        >>> rToken = VariableReadingToken(value=data)
        >>> rToken.setValueForVariable(alt, data)
        >>> alt.readChildren(rToken)
        >>> print rToken.Ok
        False


        """

        # Check we have something to read
        if not readingToken.isValueForVariableAvailable(self):
            raise Exception("No value to read/parse assigned in the provided reading token to the current Alt.")

        valueToParse = readingToken.getValueForVariable(self)

        listOfChildren = self.children
        if shuffleChildren:
            listOfChildren = sorted(listOfChildren, key=lambda *args: random.random())

        self._logger.debug("[ {0} (Alternate): readChildren:".format(self))

        result = None
        errorFlag = True
        for child in self.children:
            readingToken.setValueForVariable(child, valueToParse)
            child.read(readingToken)

            if readingToken.Ok and readingToken.isValueForVariableAvailable(child):
                errorFlag = False
                result = readingToken.getValueForVariable(child)
                break

        if not errorFlag:
            readingToken.setValueForVariable(self, result)
        else:
            readingToken.removeValueForVariable(self)

        #     # Memorized values for the child and its successors.
        #     dictOfValues = dict()
        #     dictOfValue = child.getDictOfValues(readingToken)
        #     for key, val in dictOfValue.iteritems():
        #         dictOfValues[key] = val

        #     child.read(readingToken)
        #     if readingToken.Ok:
        #         break
        #     else:
        #         readingToken.index = savedIndex

        #         # We restore values for the child and its successors.
        #         child.restore(readingToken)
        #         if readingToken.vocabulary is not None:
        #             vocabulary = readingToken.vocabulary
        #             for key, val in dictOfValues.iteritems():
        #                 vocabulary.getVariableByID(key).setCurrentValue(val)

        # if readingToken.Ok:
        #     # The value of the variable is simply the value we 'ate'.
        #     self.currentValue = readingToken.value[savedIndex:readingToken.index]

        if self.learnable and not readingToken.Ok and not self.learnable:
            # If we dont not found a proper child but the node can learn, we learn the value.
            self.learn(child, readingToken)

        self._logger.debug("Variable {0}: {1}. ]".format(self.name, readingToken))

    def writeChildren(self, writingToken, shuffleChildren=False):
        """Each child tries to write its value..
        If it fails, it restore it value and the next child try.
        It stops if one child successes.

        >>> from netzob.all import *
        >>> data = Alt([ASCII("netzob"), ASCII("!")])
        >>> wToken = VariableWritingToken()
        >>> data.writeChildren(wToken)
        >>> print TypeConverter.convert(wToken.getValueForVariable(data), BitArray, ASCII)
        netzob

        """
        self._logger.debug("[ {0} (Alternate): writeChildren:".format(self))

        errorFlag = True
        result = None

        listOfChildren = self.children
        if shuffleChildren:
            listOfChildren = sorted(listOfChildren, key=lambda *args: random.random())

        for child in listOfChildren:
            child.write(writingToken)
            if writingToken.Ok and writingToken.isValueForVariableAvailable(child):
                errorFlag = False
                result = writingToken.getValueForVariable(child)
                break

        if not errorFlag:
            writingToken.setValueForVariable(self, result)

        # savedValue = writingToken.value
        # savedIndex = writingToken.index
        # for child in self.children:
        #     # Memorized values for the child and its successor.
        #     dictOfValues = dict()
        #     dictOfValue = child.getDictOfValues(writingToken)
        #     for key, val in dictOfValue.iteritems():
        #         dictOfValues[key] = val

        #     child.write(writingToken)
        #     if writingToken.Ok and writingToken.value is not None:
        #         break
        #     else:
        #         writingToken.value = savedValue

        #         # We restore values for the child and its successor.
        #         child.restore(writingToken)
        #         vocabulary = writingToken.getVocabulary()
        #         for key, val in dictOfValues.iteritems():
        #             vocabulary.getVariableByID(key).setCurrentValue(val)

        # if writingToken.Ok:
        #     # The value of the variable is simply the value we made.
        #     self.currentValue = writingToken.value[savedIndex:writingToken.index]

        # self._logger.debug("Variable {0}: {1}. ]".format(self.name, writingToken))

    def maxSize(self):
        """Returns the max size of a data this variable can represent

        :return: the max size
        :rtype: :class:`int`
        """
        maxSize = 0
        self._logger.debug("max size of alt")
        for child in self.children:
            if maxSize is None or child.maxSize() is None:
                maxSize = None
            elif maxSize < child.maxSize():
                maxSize = child.maxSize()
        return maxSize

    def buildRegex(self):
        """This method creates a regex based on the children of the Alternate.

        >>> from netzob.all import *
        >>> import regex as re
        >>> import random

        >>> d1 = ASCII("Hello!")
        >>> d2 = ASCII(nbChars=10)
        >>> d = Alt([d1, d2])
        >>> nRegex = d.buildRegex()

        >>> possibleChoice = ["Hello!", "Vive Zoby!"]
        >>> data = random.choice(possibleChoice)
        >>> hexData = TypeConverter.convert(data, ASCII, HexaString)

        >>> compiledRegex = re.compile(str(nRegex))
        >>> dynamicDatas = compiledRegex.match(hexData)
        >>> result = TypeConverter.convert(hexData[dynamicDatas.start(nRegex.id):dynamicDatas.end(nRegex.id)], HexaString, ASCII)
        >>> result in possibleChoice
        True

        :return: a regex which can be used to identify the section in which the domain can be found
        :rtype: :class:`netzob.Common.Utils.NetzobRegex.NetzobRegex`
        """
        regexes = [child.buildRegex() for child in self.children]
        regex = NetzobRegex.buildRegexForAlternativeRegexes(regexes)
        return regex

    def _addEOL(self):
        """Adds in the definition domain of this element the implicit EOL in every child of the ALT"""
        newChilds = []
        for child in self.children:
            if isinstance(child, AbstractVariableLeaf):
                # replace the child which is a node by an aggregation that denotes the child + EOL
                agg = Agg(children=[child, Eol()])
                newChilds.append(agg)
            else:
                child._addEOL()
                newChilds.append(child)

        self.children = newChilds

    def _removeEOL(self):
        """Removes any EOL element in this definition domain"""
        for child in self.children:
            child._removeEOL()
