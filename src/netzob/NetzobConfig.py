# -*- coding: utf-8 -*-

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
#|       - Sergej Schmidt <sergej.schmidt (a) uni-ulm.de>                    |
#+---------------------------------------------------------------------------+)


#+---------------------------------------------------------------------------+
#| Class containing global configurations of Netzob.
#+---------------------------------------------------------------------------+
class NetzobConfig(object):
    """
    Contains global configuration and tuning options of Netzob.
    """
    # This value will be used if generate() method is called
    # without any upper size limit
    # 8192 is completly arbitrary and equals 1k of data (1024 bytes)
    max_gen_size = 8192

    @staticmethod
    def setMaxDataSize(size):
        """
        Set the maximal data size of a packet in bytes. The value is limited
        so the during generation of packets the memory usage doesn't explode.
        You can increase the maximal value by calling setMaxDataSize() gloabally.

        >> from netzob.all import *
        >> NetzobConfig.setMaxDataSize(4048)
        """
        if not isinstance(size, int):
            raise ValueError("Size must be an integer value!")
        if size <= 0 or (size & (size - 1) != 0):
            raise ValueError("Value of size must be power of two. E.g. 2048.")
        NetzobConfig.max_gen_size = size * 8

    @staticmethod
    def getMaxDataSize():
        """
        Returns the current configuration of the maximal value of a packet size
        in bytes.
        """
        return NetzobConfig.max_gen_size / 8
