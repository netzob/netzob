# -*- coding: utf-8 -*-

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
#+---------------------------------------------------------------------------+

from netzob.Common.Functions.Encoding.FormatFunction import FormatFunction
from netzob.Common.Type.Endianness import Endianness
from netzob.Common.Type.Format import Format
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.UnitSize import UnitSize
from common.NetzobTestCase import NetzobTestCase


class test_Encoding(NetzobTestCase):

    # UnitSize.NONE
    def test_HEX(self):
        ff = FormatFunction("Field Format Encoding", Format.HEX, UnitSize.NONE, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("30313233343536373839")
        self.assertEqual(res, "30313233343536373839")

    def test_STRING(self):
        ff = FormatFunction("Field Format Encoding", Format.STRING, UnitSize.NONE, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("30313233343536373839")
        self.assertEqual(res, "0123456789")

    def test_DECIMAL_4BITS(self):
        ff = FormatFunction("Field Format Encoding", Format.DECIMAL, UnitSize.BITS4, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "10 11 12 13 14 15")

    def test_DECIMAL_8BITS(self):
        ff = FormatFunction("Field Format Encoding", Format.DECIMAL, UnitSize.BITS8, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "171 205 239")

    def test_OCTAL_4BITS(self):
        ff = FormatFunction("Field Format Encoding", Format.OCTAL, UnitSize.BITS4, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "12 13 14 15 16 17")

    def test_OCTAL_8BITS(self):
        ff = FormatFunction("Field Format Encoding", Format.OCTAL, UnitSize.BITS8, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "253 315 357")

    def test_BINARY(self):
        ff = FormatFunction("Field Format Encoding", Format.BINARY, UnitSize.NONE, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "101010111100110111101111")

    # UnitSize.BITS4
    def test_HEX_BITS4(self):
        ff = FormatFunction("Field Format Encoding", Format.HEX, UnitSize.BITS4, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "a b c d e f")

    def test_STRING_BITS4(self):
        ff = FormatFunction("Field Format Encoding", Format.STRING, UnitSize.BITS4, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, ". . . . . .")

    def test_DECIMAL_BITS4(self):
        ff = FormatFunction("Field Format Encoding", Format.DECIMAL, UnitSize.BITS4, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "10 11 12 13 14 15")

    def test_OCTAL_BITS4(self):
        ff = FormatFunction("Field Format Encoding", Format.OCTAL, UnitSize.BITS4, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "12 13 14 15 16 17")

    def test_BINARY_BITS4(self):
        ff = FormatFunction("Field Format Encoding", Format.BINARY, UnitSize.BITS4, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "1010 1011 1100 1101 1110 1111")

    # UnitSize.BITS8
    def test_HEX_BITS8(self):
        ff = FormatFunction("Field Format Encoding", Format.HEX, UnitSize.BITS8, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "ab cd ef")

    def test_STRING_BITS8(self):
        ff = FormatFunction("Field Format Encoding", Format.STRING, UnitSize.BITS8, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("30313233343536373839")
        self.assertEqual(res, "0 1 2 3 4 5 6 7 8 9")

    def test_DECIMAL_BITS8(self):
        ff = FormatFunction("Field Format Encoding", Format.DECIMAL, UnitSize.BITS8, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "171 205 239")

    def test_OCTAL_BITS8(self):
        ff = FormatFunction("Field Format Encoding", Format.OCTAL, UnitSize.BITS8, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "253 315 357")

    def test_BINARY_BITS8(self):
        ff = FormatFunction("Field Format Encoding", Format.BINARY, UnitSize.BITS8, Endianness.BIG, Sign.UNSIGNED)
        res = ff.apply("abcdef")
        self.assertEqual(res, "10101011 11001101 11101111")
