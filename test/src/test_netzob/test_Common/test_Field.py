
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

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import unittest

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.all import *


class test_Field(unittest.TestCase):

    def test_createField(self):
        f = Field()
        self.assertNotEqual(f, None)
        self.assertEqual(f.name, None)

        f = Field(name="Test")
        self.assertNotEqual(f, None)

        f = Field(Raw(size=(5, 150)), name="Default")
        self.assertNotEqual(f, None)
        self.assertEqual(f.name, "Default")


    ## Encoding (format, unitsize, sign and endianness)
    def test_format(self):
        f = Field()
        f.encodingFunctions.add(TypeEncodingFunction(ASCII))
        self.assertEqual(len(f.encodingFunctions), 1)

    def test_unitSize(self):
        f = Field()
        f.setUnitSize(UnitSize.BIT)
        self.assertEqual(f.getUnitSize(), UnitSize.BIT)

    def test_sign(self):
        f = Field()
        f.setSign(Sign.SIGNED)
        self.assertEqual(f.getSign(), Sign.SIGNED)

    def test_endianness(self):
        f = Field()
        f.setEndianness(Endianness.LITTLE)
        self.assertEqual(f.getEndianness(), Endianness.LITTLE)

    ## Functions (visualization, encoding and transformation)
    def test_visualizationFunction(self):
        f = Field()
        func = TextColorFunction("My function", "red")
        f.addVisualizationFunction(func)
        self.assertEqual(getVisualizationFunctions(), [func])

        f.removeVisualizationFunction(func)
        self.assertEqual(getVisualizationFunctions(), [])

        func2 = TextColorFunction("My other function", "red")
        f.addVisualizationFunction(func2)
        f.cleanVisualizationFunctions()
        self.assertEqual(getVisualizationFunctions(), [])

    def test_encodingFunction(self):
        f = Field()
        func = FormatFunction("My function", Format.STRING, UnitSize.BIT, Endianness.LITTLE, Sign.SIGNED)
        f.addEncodingFunction(func)
        self.assertEqual(getEncodingFunctions(), [func])

        f.removeEncodingFunction(func)
        self.assertEqual(getEncodingFunctions(), [])

        func2 = FormatFunction("My other function", Format.STRING, UnitSize.BIT, Endianness.LITTLE, Sign.SIGNED)
        f.addEncodingFunction(func2)
        f.cleanEncodingFunctions()
        self.assertEqual(getEncodingFunctions(), [])

    def test_transformationFunction(self):
        f = Field()
        func = Base64Function("My function")
        f.addTransformationFunction(func)
        self.assertEqual(getTransformationFunctions(), [func])

        f.removeTransformationFunction(func)
        self.assertEqual(getTransformationFunctions(), [])

        func2 = Base64Function("My other function")
        f.addTransformationFunction(func2)
        f.cleanTransformationFunctions()
        self.assertEqual(getTransformationFunctions(), [])
