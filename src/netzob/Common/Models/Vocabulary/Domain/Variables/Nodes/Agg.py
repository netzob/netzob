#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
from netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Common.Models.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Common.Models.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath


@NetzobLogger
class Agg(AbstractVariableNode):
    """Represents an Aggregate (AND) in the domain definition

    To create an aggregate:

    # >>> from netzob.all import *
    # >>> domain = Agg([Raw(), ASCII()])
    # >>> print domain.varType
    # Agg
    # >>> print domain.children[0].dataType
    # Raw=None ((0, None))
    # >>> print domain.children[1].dataType
    # ASCII=None ((0, None))
    # >>> domain.children.append(Agg([10, 20, 30]))
    # >>> print len(domain.children)
    # 3
    # >>> domain.children.remove(domain.children[0])
    # >>> print len(domain.children)
    # 2


    Let's see the abstraction process of an AGGREGATE

    # >>> from netzob.all import *
    # >>> v1 = ASCII(nbChars=(1, 10))
    # >>> v2 = ASCII(".txt")
    # >>> f0 = Field(Agg([v1, v2]), name="f0")
    # >>> f1 = Field(ASCII("!"))
    # >>> s = Symbol([f0, f1])
    # >>> msg1 = RawMessage("netzob.txt!")
    # >>> mp = MessageParser()
    # >>> print mp.parseMessage(msg1, s)
    # [bitarray('01101110011001010111010001111010011011110110001000101110011101000111100001110100'), bitarray('00100001')]

    # >>> msg2 = RawMessage("netzobtxt!")
    # >>> mp = MessageParser()
    # >>> print mp.parseMessage(msg2, s)
    # Traceback (most recent call last):
    #   ...
    # Exception: No parsing path returned while parsing message netzobtxt!
    

    Let's see the specializing process of an AGGREGATE

    >>> from netzob.all import *
    >>> d1 = ASCII("hello")
    >>> d2 = ASCII(" netzob")
    >>> f = Field(Agg([d1, d2]))
    >>> s = Symbol(fields=[f])
    >>> print s.specialize()
    hello netzob

    """

    def __init__(self, children=None, svas=None):
        super(Agg, self).__init__(self.__class__.__name__, children, svas=svas)

    @typeCheck(ParsingPath)
    def parse(self, parsingPath, carnivorous=False):
        """Parse the content with the definition domain of the aggregate.
        """
        dataToParse = parsingPath.getDataAssignedToVariable(self).copy()
        self._logger.debug("Parse '{0}' as {1} with parser path '{2}'".format(dataToParse, self, parsingPath))

        # initialy, there is a unique path to test (the provided one)
        parsingPath.assignDataToVariable(dataToParse.copy(), self.children[0])
        parsingPaths = [parsingPath]
        
        # we parse all the children with the parserPaths produced by previous children
        for i_child in xrange(len(self.children)):
            self._logger.warn("CHILD: {0}/{1}".format(i_child, len(self.children)))
            current_child = self.children[i_child]
            if i_child < len(self.children)-1:
                next_child = self.children[i_child+1]
            else:
                next_child = None
                
            newParsingPaths = []
            
            for parsingPath in parsingPaths:
                self._logger.warn("Parse {0} with {1}".format(current_child.id, parsingPath))
                value_before_parsing = parsingPath.getDataAssignedToVariable(current_child).copy()
                childParsingPaths = current_child.parse(parsingPath)

                if len(childParsingPaths) == 0:
                    # current child did not produce any valid parser path
                    self._logger.debug("Children {0} failed to parse with the parsingPath {1}.".format(current_child, parsingPath))
                else:

                    for childParsingPath in childParsingPaths:
                        if childParsingPath.ok():
                            value_after_parsing =  childParsingPath.getDataAssignedToVariable(current_child).copy()
                            remainingValue = value_before_parsing[len(value_after_parsing):].copy()
                            self._logger.warn("RM={0}".format(remainingValue))
                            if next_child is not None:
                                childParsingPath.assignDataToVariable(remainingValue, next_child)
                        
                            # at least one child path managed to parse, we save the valid paths it produced
                            self._logger.debug("Children {0} succesfuly applied with the parsingPath {1} ({2} procuded paths)".format(current_child, parsingPath, len(childParsingPaths)))
                            newParsingPaths.append(childParsingPath)

            parsingPaths = newParsingPaths

            if len(parsingPaths) == 0:
                self._logger.debug("Children {0} didn't apply to any of the parser path we have, we stop Agg parser".format(current_child))
                return [] # return no valid paths

        # ok we managed to parse all the children, and it produced some valid parser paths. We return them
        for parsingPath in parsingPaths:
            parsedData = None
            for child in self.children:
                if parsedData is None:
                    parsedData = parsingPath.getDataAssignedToVariable(child).copy()
                else:
                    parsedData+= parsingPath.getDataAssignedToVariable(child).copy()
                    
            parsingPath.addResult(self, parsedData)
        return parsingPaths

    @typeCheck(SpecializingPath)
    def specialize(self, originalSpecializingPath):
        """Specializes an Agg"""

        # initialy, there is a unique path to specialize (the provided one)
        specializingPaths = [originalSpecializingPath]

        # we parse all the children with the specializerPaths produced by previous children
        for child in self.children:
            newSpecializingPaths = []

            self._logger.debug("Specializing AGG child with {0} paths".format(len(specializingPaths)))
            
            for specializingPath in specializingPaths:
                self._logger.debug("Spcialize {0} with {1}".format(child, specializingPath))
            
                childSpecializingPaths = child.specialize(specializingPath)
                
                
                if len(childSpecializingPaths) > 0:
                    # at least one child path managed to specialize, we save the valid paths it produced
                    for childSpecializingPath in childSpecializingPaths:
                        newSpecializingPaths.append(childSpecializingPath)

            specializingPaths = newSpecializingPaths

        self._logger.debug("Specializing AGG child has produced {0} paths".format(len(specializingPaths)))

        if len(specializingPaths) == 0:
            self._logger.debug("Children {0} didn't apply to any of the specializer path we have, we stop Agg specializer".format(child))
            return [] # return no valid paths

        for specializingPath in specializingPaths:
            value = None
            for child in self.children:
                if value is None:
                    value = specializingPath.getDataAssignedToVariable(child)
                else:
                    value += specializingPath.getDataAssignedToVariable(child)
        
            specializingPath.addResult(self, value)
        
            
        # ok we managed to parse all the children, and it produced some valid specializer paths. We return them
        return specializingPaths


    # OLD
        
    # @typeCheck(VariableReadingToken)
    # def read(self, readingToken):
    #     """Grants a reading access to the variable.
    #     Each child tries sequentially to read a part of the read value.
    #     If one of them fails, the whole operation is cancelled.

    #     :param readingToken: a token which contains all critical information on this reading access.
    #     :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.VariableReadingToken.VariableReadingToken`
    #     :raise: TypeError if parameter is not Valid
    #     """
    #     if readingToken is None:
    #         raise TypeError("readingToken cannot be None")

    #     self._logger.debug("[ {0} (Aggregate): read access:".format(self))
    #     if len(self.children) > 0:
    #         if self.mutable:
    #             # mutable.
    #             self.sortChildrenToRead(readingToken)
    #             self.readChildren(readingToken)
    #         else:
    #             # not mutable.
    #             self.readChildren(readingToken)
    #     else:
    #         # no child.
    #         self._logger.debug("Write abort: the variable has no child.")
    #         readingToken.Ok = False

    #     # Variable notification
    #     if readingToken.Ok:
    #         self.notifyBoundedVariables("read", readingToken, self.currentValue)

    #     self._logger.debug("\t {0}. ]".format(readingToken))

    # @typeCheck(VariableWritingToken)
    # def write(self, writingToken):
    #     """Each child tries sequentially to write its value.
    #     one of them fails, the whole operation is cancelled.

    #     >>> from netzob.all import *
    #     >>> fHello = Field(Agg(["hello", "+"]))
    #     >>> fName = Field(Agg(["zoby"]))
    #     >>> s = Symbol([fHello, fName])
    #     >>> print "\\n".join([s.specialize() for x in range(5)])
    #     hello+zoby
    #     hello+zoby
    #     hello+zoby
    #     hello+zoby
    #     hello+zoby

    #     :param readingToken: a token which contains all critical information on this reading access.
    #     :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.VariableReadingToken.VariableReadingToken`
    #     :raise: TypeError if parameter is not Valid
    #     """

    #     if writingToken is None:
    #         raise TypeError("writingToken cannot be None")

    #     self._logger.debug("[ {0} (Aggregate): write access:".format(self))
    #     #self.resetTokenChoppedIndexes()  # New write access => new final value and new reference to it.
    #     if len(self.children) > 0:
    #         if self.mutable:
    #             # mutable.
    #             self.shuffleChildren()
    #             self.writeChildren(writingToken)

    #         else:
    #             # not mutable.
    #             self.writeChildren(writingToken)
    #     else:
    #         # no child.
    #         self._logger.debug("Write abort: the variable has no child.")
    #         writingToken.Ok = False

    #     # Variable notification
    #     # if writingToken.Ok:
    #     #    self.notifyBoundedVariables("write", writingToken)

    #     self._logger.debug("\t :{0}. ]".format(writingToken))

    # def writeChildren(self, writingToken):
    #     """Executes a write access sequentially on each child of the variable.
    #     If all child successes, then it returns OK, else it returns NOK and restores the former value for each child.

    #     :type writingToken: :class:`netzob.Common.Models.Vocabulary.Domain.VariableProcessingTokens.VariableWritingToken.VariableWritingToken`
    #     :param writingToken: a token which contains all critical information on this access.
    #     """
    #     self._logger.debug("- [ {0}: writeChildren.".format(self))

    #     result = None
    #     errorFlag = False
    #     for child in self.children:
    #         child.write(writingToken)
    #         if writingToken.Ok and writingToken.isValueForVariableAvailable(child):
    #             if result is None:
    #                 result = writingToken.getValueForVariable(child)
    #             else:
    #                 result += writingToken.getValueForVariable(child)
    #         else:
    #             errorFlag = True
    #             break

    #     if not errorFlag:
    #         writingToken.setValueForVariable(self, result)
    #     else:
    #         # Remove any computed value from the writing token
    #         writingToken.removeValueForVariable(self)
    #         for child in self.children:
    #             writingToken.removeValueForVariable(child)

    # def readChildren(self, readingToken):
    #     """Each child tries to read its value..
    #     If one fails its all the aggregate that fails.

    #     >>> from netzob.all import *
    #     >>> data = TypeConverter.convert("Our world is earth", ASCII, BitArray)
    #     >>> agg = Agg([ASCII("Our world is "), ASCII("earth")])
    #     >>> rToken = VariableReadingToken(value=data)
    #     >>> rToken.setValueForVariable(agg, data)
    #     >>> agg.readChildren(rToken)
    #     >>> print rToken.Ok
    #     True

    #     >>> data = TypeConverter.convert("Our world is earth", ASCII, BitArray)
    #     >>> agg = Agg([ASCII("Our world is "), ASCII("not "), ASCII("earth")])
    #     >>> rToken = VariableReadingToken(value=data)
    #     >>> rToken.setValueForVariable(agg, data)
    #     >>> agg.readChildren(rToken)
    #     >>> print rToken.Ok
    #     False

    #     """
    #     self._logger.debug("- [ {0}: readChildren.".format(str(self)))

    #     # Computing memory, contains all values before the start of the computation. So, if an error occured, we can restore the former and correct values.
    #     dictOfValues = dict()
    #     savedIndex = readingToken.index
    #     self.currentValue = ''

    #     if not readingToken.isValueForVariableAvailable(self):
    #         raise Exception("Nothing to read because no data is assigned to the current Agg.")

    #     valueToParse = readingToken.getValueForVariable(self)
    #     sizeValueParsed = 0

    #     for child in self.children:
    #         # Memorize each child susceptible to be restored. One by one.
    #         dictOfValue = child.getDictOfValues(readingToken)
    #         for key, val in dictOfValue.iteritems():
    #             dictOfValues[key] = val

    #         # Child execution.
    #         self._logger.debug("AGG-child will parse: {0}".format(valueToParse))
    #         readingToken.setValueForVariable(child, valueToParse)
    #         child.read(readingToken)
    #         if not readingToken.Ok:
    #             break
    #         else:
    #             childValue = readingToken.getValueForVariable(child)
    #             valueToParse = valueToParse[len(childValue):]
    #             sizeValueParsed += len(childValue)
    #             self._logger.debug("child has parsed {0} bit".format(len(childValue)))

    #     self._logger.debug("Agg parsed : {0}".format(valueToParse[:sizeValueParsed]))
    #     #readingToken.setValueForVariable(self, valueToParse[:sizeValueParsed])

    #     # If it has failed we restore every executed children and the index.
    #     if not readingToken.Ok:
    #         # If something went wrong and we can adapt, we learn to adapt.
    #         if self.learnable:
    #             self.learn(child, readingToken)
    #         # If it is still not OK.
    #         if not readingToken.Ok:
    #             readingToken.index = savedIndex
    #             vocabulary = readingToken.vocabulary
    #             # for key, val in dictOfValues.iteritems():
    #             #     child = vocabulary.getVariableByID(key)
    #             #     # We restore the current values.
    #             #     child.currentValue = val
    #             #     # We restore the cached values.
    #             #     child.restore(readingToken)
    #     else:
    #         pass
    #         # The value of the variable is simply the value we 'ate'.
    #         #self.currentValue = readingToken.value[savedIndex:readingToken.index]

    #     self._logger.debug("Variable {0} ] -".format(readingToken))

    # @typeCheck(AbstractVariableProcessingToken)
    # def isDefined(self, processingToken):
    #     """If one child is not defined the node is not defined.

    #     :param processingToken: a variable processing token fro mwhich we can have access to the memory
    #     :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken`
    #     :raise: TypeError if parameter is not Valid
    #     """

    #     if processingToken is None:
    #         raise TypeError("processingToken cannot be None")

    #     if len(self.children) > 0:
    #         for child in self.children:
    #             if not child.isDefined(processingToken):
    #                 return False
    #         return True
    #     else:
    #         return False

    # def maxSize(self):
    #     """Returns the max size of a data this variable can represent

    #     :return: the max size
    #     :rtype: :class:`int`
    #     """
    #     maxSize = 0
    #     self._logger.debug("maxsize of agg")
    #     for child in self.children:
    #         if maxSize is None or child.maxSize() is None:
    #             maxSize = None
    #         else:
    #             maxSize += child.maxSize()
    #     return maxSize

    # def buildRegex(self):
    #     """This method creates a regex based on the children of the Aggregate.

    #     >>> from netzob.all import *
    #     >>> import regex as re
    #     >>> import random

    #     >>> d1 = ASCII("Hello ")
    #     >>> d2 = ASCII(nbChars=4)
    #     >>> d3 = ASCII(nbChars=12)
    #     >>> d = Agg([d1, d2, d3])
    #     >>> nRegex = d.buildRegex()

    #     >>> data = "Hello Zoby, are U ok ?"
    #     >>> hexData = TypeConverter.convert(data, ASCII, HexaString)

    #     >>> compiledRegex = re.compile(str(nRegex))
    #     >>> dynamicDatas = compiledRegex.match(hexData)
    #     >>> print TypeConverter.convert(hexData[dynamicDatas.start(nRegex.id):dynamicDatas.end(nRegex.id)], HexaString, ASCII)
    #     Hello Zoby, are U ok ?

    #     :return: a regex which can be used to identify the section in which the domain can be found
    #     :rtype: :class:`netzob.Common.Utils.NetzobRegex.NetzobRegex`
    #     """
    #     regexes = [child.buildRegex() for child in self.children]
    #     regex = NetzobRegex.buildRegexForAggregateRegexes(regexes)
    #     return regex

    # def _addEOL(self):
    #     """Adds in the definition domain of this element the implicit EOL in the last child of the AGG"""
    #     self.children[len(self.children) - 1]._addEOL()

    # def _removeEOL(self):
    #     """Removes any EOL element in this definition domain"""
    #     self.children[len(self.children) - 1]._removeEOL()
