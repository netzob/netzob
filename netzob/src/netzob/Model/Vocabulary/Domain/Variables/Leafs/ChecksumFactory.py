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
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from typing import Callable  # noqa: F401

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractChecksum import AbstractChecksum
from netzob.Model.Vocabulary.Types.AbstractType import UnitSize  # noqa: F401


class ChecksumFactory(object):
    """
    Factory that create :class:`AbstractChecksum <netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractChecksum.AbstractChecksum>`
    classes by providing concrete methods as argument.
    """

    @classmethod
    def create(cls,
               name,       # type: str
               calculate,  # type: Callable[[AbstractChecksum, bytes], int]
               bitSize     # type: int
               ):
        r"""
        Given a :attr:`name`, corresponding to the name of the class to create,
        this method will produce a specific :class:`AbstractChecksum <netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractChecksum.AbstractChecksum>`
        class.

        The following attributes are expected:

        - :attr:`calculate`: a function whose prototype respects abstract method \
          :meth:`AbstractChecksum.calculate <netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractChecksum.AbstractChecksum.calculate>`
        - :attr:`bitSize`: an int value, respecting the :meth:`getBitSize <netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractChecksum.AbstractChecksum.getBitSize>` \
          returned value prototype

        :param name: the class name to produce
        :type name: :class:`str`
        :param calculate: the calculate method
        :type calculate: ``Callable[[AbstractChecksum, bytes], bytes]``
        :param bitSize: the bit-size of the checksum value
        :type bitSize: :class:`int`


        >>> from netzob.all import *
        >>> import binascii
        >>> def calculate(checksum, msg):
        ...     return 0x0123456789abcdef
        >>> MyCRC = ChecksumFactory.create('MyCRC',
        ...                                calculate=calculate,
        ...                                bitSize=64)
        >>> f1 = Field(Raw(b'\xaa\xbb'))
        >>> f2 = Field(MyCRC([f1]))
        >>> s = Symbol(fields = [f1, f2])
        >>> binascii.hexlify(s.specialize())
        b'aabbefcdab8967452301'
        """
        return type(name, (AbstractChecksum,), {
            'calculate': calculate,
            'getBitSize': lambda self: bitSize
        })
