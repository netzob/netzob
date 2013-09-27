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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Utils.NetzobRegex import NetzobRegex
from netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken import AbstractVariableProcessingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken import VariableReadingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableWritingToken import VariableWritingToken


@NetzobLogger
class Agg(AbstractVariableNode):
    """Represents an Aggregate (AND) in the domain definition

    To create an aggregate:

    >>> from netzob.all import *
    >>> domain = Agg([Raw(), ASCII()])
    >>> print domain.varType
    Agg
    >>> print domain.children[0].dataType
    Raw=None ((0, None))
    >>> print domain.children[1].dataType
    ASCII=None ((0, None))
    >>> domain.children.append(Agg([10, 20, 30]))
    >>> print len(domain.children)
    3
    >>> domain.children.remove(domain.children[0])
    >>> print len(domain.children)
    2

    """

    def __init__(self, children=None):
        super(Agg, self).__init__(self.__class__.__name__, children)

    @typeCheck(AbstractVariableProcessingToken)
    def isDefined(self, processingToken):
        """If one child is not defined the node is not defined.

        :param processingToken: a variable processing token fro mwhich we can have access to the memory
        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken`
        :raise: TypeError if parameter is not Valid
        """

        if processingToken is None:
            raise TypeError("processingToken cannot be None")

        if len(self.children) > 0:
            for child in self.children:
                if not child.isDefined(processingToken):
                    return False
            return True
        else:
            return False

    @typeCheck(VariableReadingToken)
    def read(self, readingToken):
        """Grants a reading access to the variable.
        Each child tries sequentially to read a part of the read value.
        If one of them fails, the whole operation is cancelled.

        :param readingToken: a token which contains all critical information on this reading access.
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.VariableReadingToken.VariableReadingToken`
        :raise: TypeError if parameter is not Valid
        """
        if readingToken is None:
            raise TypeError("readingToken cannot be None")

        self._logger.debug("[ {0} (Aggregate): read access:".format(self))
        if len(self.children) > 0:
            if self.mutable:
                # mutable.
                self.sortChildrenToRead(readingToken)
                self.readChildren(readingToken)
            else:
                # not mutable.
                self.readChildren(readingToken)
        else:
            # no child.
            self._logger.debug("Write abort: the variable has no child.")
            readingToken.Ok = False

        # Variable notification
        if readingToken.Ok:
            self.notifyBoundedVariables("read", readingToken, self.currentValue)

        self._logger.debug("\t {0}. ]".format(readingToken))

    @typeCheck(VariableWritingToken)
    def write(self, writingToken):
        """Each child tries sequentially to write its value.
        one of them fails, the whole operation is cancelled.

        :param readingToken: a token which contains all critical information on this reading access.
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.VariableReadingToken.VariableReadingToken`
        :raise: TypeError if parameter is not Valid
        """

        if writingToken is None:
            raise TypeError("writingToken cannot be None")

        self._logger.debug("[ {0} (Aggregate): write access:".format(self))
        self.resetTokenChoppedIndexes()  # New write access => new final value and new reference to it.
        if len(self.children) > 0:
            if self.isMutable():
                # mutable.
                self.shuffleChildren()
                self.writeChildren(writingToken)

            else:
                # not mutable.
                self.writeChildren(writingToken)

        else:
            # no child.
            self._logger.debug("Write abort: the variable has no child.")
            writingToken.Ok = False

        # Variable notification
        if writingToken.Ok:
            self.notifyBoundedVariables("write", writingToken)

        self.log.debug("\t :{0}. ]".format(writingToken))

    def readChildren(self, readingToken):
        """Each child tries to read its value..
        If one fails its all the aggregate that fails.

        >>> from netzob.all import *
        >>> data = TypeConverter.convert("Our world is earth", ASCII, BitArray)
        >>> agg = Agg([ASCII("Our world is "), ASCII("earth")])
        >>> rToken = VariableReadingToken(value=data)
        >>> agg.readChildren(rToken)
        >>> print rToken.Ok
        True
        >>> print rToken.index > 0
        True

        >>> data = TypeConverter.convert("Our world is earth", ASCII, BitArray)
        >>> agg = Agg([ASCII("Our world is "), ASCII("not "), ASCII("earth")])
        >>> rToken = VariableReadingToken(value=data)
        >>> agg.readChildren(rToken)
        >>> print rToken.Ok
        False
        >>> print rToken.index > 0
        False

        """
        self._logger.debug("- [ {0}: readChildren.".format(str(self)))

        # Computing memory, contains all values before the start of the computation. So, if an error occured, we can restore the former and correct values.
        dictOfValues = dict()
        savedIndex = readingToken.index
        self.currentValue = ''

        for child in self.children:
            # Memorize each child susceptible to be restored. One by one.
            dictOfValue = child.getDictOfValues(readingToken)
            for key, val in dictOfValue.iteritems():
                dictOfValues[key] = val

            # Child execution.
            child.read(readingToken)
            if not readingToken.Ok:
                break

        # If it has failed we restore every executed children and the index.
        if not readingToken.Ok:
            # If something went wrong and we can adapt, we learn to adapt.
            if self.learnable:
                self.learn(child, readingToken)
            # If it is still not OK.
            if not readingToken.Ok:
                readingToken.index = savedIndex
                vocabulary = readingToken.vocabulary
                # for key, val in dictOfValues.iteritems():
                #     child = vocabulary.getVariableByID(key)
                #     # We restore the current values.
                #     child.currentValue = val
                #     # We restore the cached values.
                #     child.restore(readingToken)
        else:
            # The value of the variable is simply the value we 'ate'.
            self.currentValue = readingToken.value[savedIndex:readingToken.index]

        self._logger.debug("Variable {0} ] -".format(readingToken))

    def buildRegex(self):
        """This method creates a regex based on the children of the Aggregate.

        >>> from netzob.all import *
        >>> import regex as re
        >>> import random

        >>> d1 = ASCII("Hello ")
        >>> d2 = ASCII(nbChars=4)
        >>> d3 = ASCII(nbChars=12)
        >>> d = Agg([d1, d2, d3])
        >>> nRegex = d.buildRegex()

        >>> data = "Hello Zoby, are U ok ?"
        >>> hexData = TypeConverter.convert(data, ASCII, HexaString)

        >>> compiledRegex = re.compile(str(nRegex))
        >>> dynamicDatas = compiledRegex.match(hexData)
        >>> print TypeConverter.convert(hexData[dynamicDatas.start(nRegex.id):dynamicDatas.end(nRegex.id)], HexaString, ASCII)
        Hello Zoby, are U ok ?

        :return: a regex which can be used to identify the section in which the domain can be found
        :rtype: :class:`netzob.Common.Utils.NetzobRegex.NetzobRegex`
        """
        regexes = [child.buildRegex() for child in self.children]
        regex = NetzobRegex.buildRegexForAggregateRegexes(regexes)
        return regex
