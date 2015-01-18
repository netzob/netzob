#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob.Orgob : Inferring communication protocols                  |
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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Vocabulary.Domain.Specializer.FieldSpecializer import FieldSpecializer
from netzob.Common.Models.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.ASCII import ASCII


@NetzobLogger
class MessageSpecializer(object):
    """
    >>> from netzob.all import *

    >>> f11 = Field(domain=ASCII("hello"), name="F11")
    >>> f12 = Field(domain=ASCII(";"), name="F12")
    >>> f13 = Field(domain=ASCII(nbChars=(5,10)), name="F13")
    >>> s1 = Symbol(fields=[f11, f12, f13], name="S1")

    >>> f21 = Field(domain=ASCII("master"), name="F21")
    >>> f22 = Field(domain=ASCII(">"), name="F22")
    >>> f23 = Field(domain=Value(f13), name="F23")
    >>> s2 = Symbol(fields=[f21, f22, f23])

    >>> ms = MessageSpecializer()
    >>> m1 = TypeConverter.convert(ms.specializeSymbol(s1).generatedContent, BitArray, Raw)
    >>> m1.startswith("hello;")
    True
    
    >>> m2 = TypeConverter.convert(ms.specializeSymbol(s2).generatedContent, BitArray, Raw)
    >>> m2.startswith("master>")
    True
    
    >>> m1[6:] == m2[7:]
    True

    """

    def __init__(self, memory = None):
        if memory is None:
            memory = Memory()
        self.memory = memory


    @typeCheck(Symbol)    
    def specializeSymbol(self, symbol):
        """This method generates a message based on the provided symbol definition."""
        if symbol is None:
            raise Exception("Specified symbol is None")

        self._logger.debug("Specifies symbol '{0}'.".format(symbol.name))

        # this variable host all the specialization path
        specializingPaths = [SpecializingPath(memory=self.memory)]

        for field in symbol.children:
            self._logger.debug("Specializing field {0}".format(field.name))

            fieldDomain = field.domain
            if fieldDomain is None:
                raise Exception("Cannot specialize field '{0}' since it defines no domain".format(fieldDomain))

            fs = FieldSpecializer(field)    

            newSpecializingPaths = []
            for specializingPath in specializingPaths:
                newSpecializingPaths.extend(fs.specialize(specializingPath))
                                
            specializingPaths = newSpecializingPaths

        if len(specializingPaths) > 1:
           self._logger.info("TODO: multiple valid paths found when specializing this message.")

        if len(specializingPaths) == 0:
            raise Exception("Cannot specialize this symbol.")

        retainedPath = specializingPaths[0]

        generatedContent = None
        # let's configure the generated content
        for field in symbol.children:
            d = retainedPath.getDataAssignedToVariable(field.domain)
            if generatedContent is None:
                generatedContent = d.copy()
            else:
                generatedContent += d.copy()

        retainedPath.generatedContent = generatedContent
        
        self._logger.debug("Specialized message: {0}".format(TypeConverter.convert(retainedPath.generatedContent, BitArray, ASCII)))
        self.memory = retainedPath.memory

        return retainedPath
             
        
            
        
        
    
