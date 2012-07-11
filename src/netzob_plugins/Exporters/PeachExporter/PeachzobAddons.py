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
#| Global Imports                                                            |
#+---------------------------------------------------------------------------+
import random
import string

#+---------------------------------------------------------------------------+
#| Local Imports                                                             |
#+---------------------------------------------------------------------------+
from Peach.fixup import Fixup
from Peach.Engine.common import *
# Peach needs to be in the Python path.


class Or(Fixup):
    """
        Or:
            Replace field's value with a logical OR of values in Param "values" (separated by ';' characters).

    """

    def __init__(self, values):
        """
            Constructor of Or:

            @type values: string
            @param values: a list of values (separated by ';' characters) allowed by the user to be set in the father field.

        """
        Fixup.__init__(self)
        self.values = values

    def fixup(self):
        """
            fixup:
                Called by the Peach engine. Replace the father field value by one of the value given (randomly chosen).

                @return type: string
                @return: the new value of the father field.

        """
        values = string.split(self.values, ";")
        values.append("")  # We append an empty value for having empty fields sometimes.
        if values == None:
            raise Exception("Error: Or was unable to locate its values.")
        ran = random.randint(0, len(values) - 1)
        return values[ran]


class RandomString(Fixup):
    """
        RandomString:
            Replace field's value with a random string which size is in a given range.

    """

    def __init__(self, minlen, maxlen):
        """
            Constructor of RandomString:

                @type minlen: string
                @param minlen: the minimum length of the random string we will create.
                @type maxlen: string
                @param maxlen: the maximum length of the random string we will create.

        """
        Fixup.__init__(self)
        self.minlen = minlen
        self.maxlen = maxlen

    def fixup(self):
        """
            fixup:
                Called by the Peach engine. Replace the father field value by a random value which size is between minlen and maxlen.

                @return type: string
                @return: the new value of the father field.

        """
        minlen = self.minlen
        maxlen = self.maxlen
        if minlen == None:
            raise Exception("Error: RandomString was unable to locate minlen.")
        if maxlen == None:
            raise Exception("Error: RandomString was unable to locate maxlen.")
        if minlen > maxlen:
            raise Exception("Error: minlen > maxlen.")
        value = ""
        length = random.randint(int(minlen), int(maxlen))
        # We potentially add all printable characters
        for i in range(length):
            value = value + random.choice(string.printable)
        return value
