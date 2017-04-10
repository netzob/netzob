#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
#|             ANSSI,   https://www.ssi.gouv.fr                              |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import abc

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.AbstractField import AbstractField


class MutatorError(Exception):
    pass


class Mutator(object):
    """The model of any mutator.

    It provides the common properties and API to all inherited mutators.

    >>> mutator = Mutator()
    >>> mutator.seed = 10
    >>> mutator.field = astractField
    >>> rawMessage = mutator.mutate()

    """

    # Constants
    SEED_DEFAULT = 0

    def __init__(self):
        self._seed = Mutator.SEED_DEFAULT
        self._field = None

    @property
    def seed(self):
        """The seed used in pseudo-random generator

        :type: int
        """
        return self._seed

    @seed.setter
    @typeCheck(int)
    def seed(self, seedValue):
        self._seed = seedValue

    @property
    def field(self):
        """The field for which the mutation is applied

        :type: AbstractField
        """
        return self._field

    @field.setter
    @typeCheck(AbstractField)
    def field(self, abstractField):
        self._field = abstractField

    @abc.abstractmethod
    def mutate(self):
        raise MutatorError(
            "{}.mutate() not implemented yet".format(self._type()))
