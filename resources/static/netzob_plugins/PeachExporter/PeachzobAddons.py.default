# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 AMOSSYS                                                |
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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import random
import string
import re

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from Peach.fixup import Fixup
from Peach.Engine.common import *
# Peach needs to be in the Python path.

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class Or(Fixup):
    """Or:
            Replace field's value with a logical OR of values in Param "values" (separated by ';' characters).
    """

    def __init__(self, values, mainSep='; ', sndSep=","):
        """Constructor of Or:

            @type values: string
            @param values: a list of type and values (default : type1, values1; type2, values2 ...) allowed by the user to be set in the father field. Type are String, Number and what remains.
            @type mainSep: string
            @param mainSep: a separator for the type-value couple given in entry.
            @type sndSep: string
            @param sndSep: a word that separates each value from its type.
        """
        Fixup.__init__(self)
        self.values = values
        self.mainSep = mainSep
        self.sndSep = sndSep

    def fixup(self):
        """fixup:
                Called by the Peach engine. Replace the father field value by one of the value given (randomly chosen).

                @return type: string
                @return: the new value of the father field.
        """
        values = string.split(self.values, self.mainSep)
        if values is None:
            raise Exception("Error: Or was unable to locate its values.")
        rvalue = ""
        ran = random.randint(0, len(values) - 1)
        value = string.split(values[ran], self.sndSep)
        if value[0] == "String":
            rvalue = PeachTranslate(value[1])
        elif value[0] == "Number":
            rvalue = int(value[1], 16)
        else:
            rvalue = PeachTranslate(value[1])
        return rvalue


class RandomField(Fixup):
    """RandomString:
            Replace field's value with a random string which size is in a given range.
    """

    def __init__(self, minlen, maxlen, type="Blob"):
        """Constructor of RandomField:

                @type minlen: string
                @param minlen: the minimum length of the random string we will create.
                @type maxlen: string
                @param maxlen: the maximum length of the random string we will create.
                @type type: string
                @param type: the type of the eventual randomly created string, chosen between "Blob", "String", "Number", IPv4.
        """
        Fixup.__init__(self)
        self.minlen = minlen
        self.maxlen = maxlen
        self.type = type

    def fixup(self):
        """fixup:
                Called by the Peach engine. Replace the father field value by a random value which size is between minlen and maxlen.

                @return type: string
                @return: the new value of the father field.
        """
        minlen = self.minlen
        maxlen = self.maxlen
        if minlen is None:
            raise Exception("Error: RandomField was unable to locate minlen.")
        if maxlen is None:
            raise Exception("Error: RandomField was unable to locate maxlen.")
        if int(minlen) > int(maxlen):
            raise Exception("Error: minlen ({0}) > maxlen ({1}).".format(minlen, maxlen))
        value = ""
        length = random.randint(int(minlen), int(maxlen))
        # We potentially add all printable characters.
        if self.type == "String":
            for i in range(length):
                value = value + random.choice(string.printable)
        elif self.type == "Number":
            for i in range(length):
                value = value + random.choice(string.digits)
        elif self.type == "IPv4":
            for i in range(4):
                value = value + "." + random.randint(0, 255)
            value = value[1:]  # Remove the first '.'
        else:  # We assume it is "Blob"/hexa type.
            for i in range(length):
                value = value + random.choice(string.hexdigits)
            value = PeachTranslate(value)
        return value


def PeachTranslate(value):
    """PeachTranslate:
        This function is taken from the Peach project. It transforms an hexadecimal string in a binary string understandable by the peach data sender.

        @type value: string
        @param value: the value in hex string which is translated in binary string following the Peach way to do so.
        @rtype: string
        @return: a binary string understandable by peach that will be sent to the targetes program.
    """
#
# Copyright (c) Michael Eddington
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
    regsHex = (
        re.compile(r"^([,\s]*\\x([a-zA-Z0-9]{2})[,\s]*)"),
        re.compile(r"^([,\s]*%([a-zA-Z0-9]{2})[,\s]*)"),
        re.compile(r"^([,\s]*0x([a-zA-Z0-9]{2})[,\s]*)"),
        re.compile(r"^([,\s]*x([a-zA-Z0-9]{2})[,\s]*)"),
        re.compile(r"^([,\s]*([a-zA-Z0-9]{2})[,\s]*)")
    )
    ret = ""
    valueLen = len(value) + 1
    while valueLen > len(value):
        valueLen = len(value)
        for i in range(len(regsHex)):
            match = regsHex[i].search(value)
            if match is not None:
                while match is not None:
                    ret += chr(int(match.group(2), 16))
                    value = regsHex[i].sub('', value)
                    match = regsHex[i].search(value)
                break
    return ret
