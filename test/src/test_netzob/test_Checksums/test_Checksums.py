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
#| Standard library imports
#+---------------------------------------------------------------------------+
import unittest
from netzob.all import *
import os


class test_Checksums(unittest.TestCase):

    def parse_file(self, file, checksum_class):
        file_path = os.path.join("test", "resources", "test_netzob", "test_Checksums", file)
        fd = open(file_path, 'r')
        msg = ""
        given_len = 0
        for line in fd:
            if 'Len =' in line:
                given_len = int(line[6:-1])
            elif 'Msg =' in line:
                msg = line[6:-1]
            elif 'CS =' in line:
                if len(msg) != given_len:
                    msg = msg[0 : given_len]
                self.check_res(msg, line[5:-1], checksum_class)
                msg = ""
                given_len = 0

    def check_res(self, msg, cs, checksum_class):
        b = msg.encode()
        f1 = Field(Raw(b))
        f2 = Field(checksum_class([f1]))
        s = Symbol(fields = [f1, f2])
        tmp = s.specialize()[len(b):]
        rep = tmp[::-1].hex()
        self.assertEqual(rep, cs)

    def test_CRC16_implementation(self):
        file = "CRC16_tests.txt"
        checksum_class = CRC16
        self.parse_file(file, checksum_class)

    def test_CRC16DNP_implementation(self):
        file = "CRC16DNP_tests.txt"
        checksum_class = CRC16DNP
        self.parse_file(file, checksum_class)

    def test_CRC16Kermit_implementation(self):
        file = "CRC16Kermit_tests.txt"
        checksum_class = CRC16Kermit
        self.parse_file(file, checksum_class)

    def test_CRC16SICK_implementation(self):
        file = "CRC16SICK_tests.txt"
        checksum_class = CRC16SICK
        self.parse_file(file, checksum_class)

    def test_CRC32_implementation(self):
        import binascii, zlib

        rand_str = ['42', 'azerty', 'f,efierjee', 'aqwzsxedc',
        'epgkrtgrtpg', '123456789', 'abcdefghijklmnopqrstuvwxyz', 'f54erf6er4ferfer54f4e56fe',
        'apc,tjdoped5r9654*ddjv,ror_çggrgt6845zeza2v84eg', 'gr4e56hrtj48ht4trjz84eaz48t48ui94loim45q31cf2qsd81a9fafekferef,9zfezgz4a98f']

        for msg in rand_str:
            msg = msg.encode()
            f1 = Field(Raw(msg))
            f2 = Field(CRC32([f1]))
            s = Symbol(fields = [f1, f2])
            tmp = s.specialize()[len(msg):]
            rep = tmp[::-1].hex()
            
            cs_ref = hex(binascii.crc32(msg))[2:]
            cs_ref2 = hex(zlib.crc32(msg))[2:]
            self.assertEqual(rep, cs_ref)
            self.assertEqual(rep, cs_ref2)

    def test_CRC_CCITT_implementation(self):
        file = "CRC_CCITT_tests.txt"
        checksum_class = CRCCCITT
        self.parse_file(file, checksum_class)
