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
# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Sumit Acharya <sumit.acharya@uni-ulm.de>                          |
# |       - Stephan Kleber <stephan.kleber@uni-ulm.de>                        |
# +---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import unittest
import os

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from common.NetzobTestCase import NetzobTestCase
from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Inference.Vocabulary.Format import Format
from netzob.Export.ScapyExporter.ScapyExporter import ScapyExporter

class test_ScapyExporter(NetzobTestCase):

    def test_exportToScapy(self):
	# Test if exportToScapy function in ScapyExporter is working correctly.
        # Test if created file runs without error
        # Verify the content of the exported file is as expected, including size info.
        # check for both iterable and non-iterable symbols
        m1=RawMessage("\x09\x70\x95\xcc\xef")
        m2=RawMessage("\x0a\x70\x03\x8f\x23\x5f")
        m3=RawMessage("\x09\x70\x31\xa0")
        m4=RawMessage("\x0a\xd6\xb5\x5b")
        messages = [m1, m2, m3, m4]
        symbols = Symbol(messages=messages)
        with self.assertRaises(TypeError):
            iter(symbols)
        self.assertEqual(ScapyExporter().exportToScapy(symbols,'test1.py','ProtocolName'),None)
        self.assertEqual(os.system("python test1.py"), 0)
        import test1
        self.assertEqual(test1.ProtocolName_Symbol().fields_desc[0].name,'Field')
        self.assertEqual(test1.ProtocolName_Symbol().fields_desc[0].default,None)
        self.assertEqual(test1.ProtocolName_Symbol().fields_desc[0].cls,(0,None))   # size
        with self.assertRaises(AttributeError): test1.ProtocolName_Symbol1().fields_desc[0].name
        os.remove('test1.py')

        symbl = Format.clusterByAlignment(messages, minEquivalence=50, internalSlick=True)
        self.assertEqual(type(symbl),list) 
        self.assertEqual(ScapyExporter().exportToScapy(symbl,'test2.py','ProtocolName'),None)
        self.assertEqual(os.system("python test2.py"), 0)
        import test2
        self.assertEqual(test2.ProtocolName_Symbol0().fields_desc[0].name,'Field00')
        self.assertEqual(test2.ProtocolName_Symbol0().fields_desc[0].cls,(0,32))     # size
        self.assertEqual(test2.ProtocolName_Symbol1().fields_desc[1].default,'p')
        self.assertEqual(test2.ProtocolName_Symbol1().Field01,'p')
        self.assertEqual(len(test2.ProtocolName_Symbol1().fields_desc),3)
        os.remove('test2.py')
