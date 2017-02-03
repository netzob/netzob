# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
import abc

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Domain.Variables.SVAS import SVAS


@NetzobLogger
class AbstractVariableLeaf(AbstractVariable):
    """Represents a leaf in the variable definition of a field.

    A leaf is a variable with no children. Most of of leaf variables
    are :class:`netzob.Model.Vocabulary.Domain.Variables.Leafs.Data.Data` variables and
    :class:`netzob.Model.Vocabulary.Domain.Variables.Leafs.Relations.AbstractRelation.AbstractRelation`.

    """

    def __init__(self, varType, name=None, svas=None):
        super(AbstractVariableLeaf, self).__init__(varType, name=name, svas=svas)
        
    def parse(self, parsingPath, acceptCallBack=True, carnivorous=False):
        """@toto TO BE DOCUMENTED"""

        if self.svas is None:
            raise Exception("Cannot parse if the variable has no assigned SVAS.")

        if self.isDefined(parsingPath):
            if self.svas == SVAS.CONSTANT or self.svas == SVAS.PERSISTENT:
                return self.valueCMP(parsingPath, acceptCallBack, carnivorous=carnivorous)
            elif self.svas == SVAS.EPHEMERAL:
                return self.learn(parsingPath, acceptCallBack, carnivorous=carnivorous)
            elif self.svas == SVAS.VOLATILE:
                return self.domainCMP(parsingPath, acceptCallBack, carnivorous=carnivorous)
        else:
            if self.svas == SVAS.CONSTANT:
                self._logger.debug("Cannot parse '{0}' as svas is CONSTANT and no value is available.".format(self))
                return []
            elif self.svas == SVAS.EPHEMERAL or self.svas == SVAS.PERSISTENT:
                return self.learn(parsingPath, acceptCallBack, carnivorous=carnivorous)
            elif self.svas == SVAS.VOLATILE:
                return self.domainCMP(parsingPath, acceptCallBack, carnivorous=carnivorous)

        raise Exception("Not yet implemented: {0}.".format(self.svas))

    #
    # methods that must be defined to support the abstraction process
    #
    @abc.abstractmethod
    def isDefined(self, parsingPath):
        raise NotImplementedError("method isDefined is not implemented")

    @abc.abstractmethod
    def domainCMP(self, parsingPath, acceptCallBack, carnivorous):
        raise NotImplementedError("method domainCMP is not implemented")

    @abc.abstractmethod
    def valueCMP(self, parsingPath, acceptCallBack, carnivorous):
        raise NotImplementedError("method valueCMP is not implemented")

    @abc.abstractmethod
    def learn(self, parsingPath, acceptCallBack, carnivorous):
        raise NotImplementedError("method learn is not implemented")

    def specialize(self, parsingPath, acceptCallBack=True):
        """@toto TO BE DOCUMENTED"""

        if self.svas is None:
            raise Exception("Cannot specialize if the variable has no assigned SVAS.")
        if self.isDefined(parsingPath):
            if self.svas == SVAS.CONSTANT or self.svas == SVAS.PERSISTENT:
                return self.use(parsingPath, acceptCallBack)
            elif self.svas == SVAS.EPHEMERAL:
                return self.regenerateAndMemorize(parsingPath, acceptCallBack)
            elif self.svas == SVAS.VOLATILE:
                return self.regenerate(parsingPath, acceptCallBack)
        else:
            if self.svas == SVAS.CONSTANT:
                self._logger.debug("Cannot specialize '{0}' as svas is CONSTANT and no value is available.".format(self))
                return []
            elif self.svas == SVAS.EPHEMERAL or self.svas == SVAS.PERSISTENT:
                return self.regenerateAndMemorize(parsingPath, acceptCallBack)
            elif self.svas == SVAS.VOLATILE:
                return self.regenerate(parsingPath, acceptCallBack)

        raise Exception("Not yet implemented.")

    def _str_debug(self, deepness=0):
        """Returns a string which denotes
        the current field definition using a tree display"""

        tab = ["     " for x in range(deepness - 1)]
        tab.append("|--   ")
        tab.append("{0}".format(self))
        return ''.join(tab)
