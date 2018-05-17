# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
# |             ANSSI,   https://www.ssi.gouv.fr                              |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# |       - Rémy Delion <remy.delion (a) amossys.fr>                          |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
import abc
from enum import Enum

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import public_api
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.conf import Conf

class MaxFuzzingException(Exception):
    pass


@public_api
class FuzzingMode(Enum):
    """Mutator Fuzzing modes"""
    FIXED = 0  #: Data is fixed (no fuzzing)
    MUTATE = 1  #: Fuzzing by mutation of a legitimate value
    GENERATE = 2  #: Fuzzing by generation
    __repr__ = Enum.__str__


@NetzobLogger
class Mutator(metaclass=abc.ABCMeta):
    """This class provides the interface that a mutator should implement.

    The Mutator constructor expects some parameters:

    :param seed: The initial seed value of the mutator. Default value is :attr:`SEED_DEFAULT` = Conf.seed.
    :type seed: :class:`int`

    The Mutator class provides the following public variables:

    :var generator: The underlying generator used to produce pseudo-random or deterministic values.
    :var seed: The seed value of the mutator used to initialize the generator.
    :vartype generator: :class:`iter`
    :vartype seed: :class:`int`

    """

    # Class constants
    SEED_DEFAULT = Conf.seed  #: the default seed value

    def __init__(self,
                 generator='xorshift',
                 seed=SEED_DEFAULT):
        # type: (...) -> None

        # Public variables linked with parameters
        self.generator = generator
        self.seed = seed

    # Properties

    @property
    def generator(self):
        return self._generator

    @generator.setter  # type: ignore
    def generator(self, generator):
        self._generator = generator

    @property
    def seed(self):
        return self._seed

    @seed.setter  # type: ignore
    def seed(self, seed):
        self._seed = seed
