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


class test_Hashes(unittest.TestCase):

    def parse_cavs_file(self, file, hash_class):
        file_path = os.path.join("test", "resources", "test_netzob", "test_Hashes", file)
        fd = open(file_path, 'r')
        msg = ""
        given_len = 0
        for line in fd:
            if 'Len =' in line:
                given_len = int(line[6:-1])
            elif 'Msg =' in line:
                msg = line[6:-1]
            elif 'MD =' in line:
                if len(msg) != given_len:
                    msg = msg[0 : given_len]
                if 'MD5' in file:
                    msg = msg.encode().hex()
                self.check_res(msg, line[5:-1], hash_class)
                msg = ""
                given_len = 0

    def check_res(self, msg, md, hash_class):
        b = bytes.fromhex(msg)
        f1 = Field(Raw(b))
        f2 = Field(hash_class([f1]))
        s = Symbol(fields = [f1, f2])
        rep = s.specialize().hex()
        self.assertEqual(rep, (msg + md))
    
    def test_MD5_implementation(self):
        file_1 = "MD5_test_suite.txt"
        hash_class = MD5
        self.parse_cavs_file(file_1, hash_class)

    def test_SHA1_implementation(self):
        file_1 = "SHA1ShortMsg.rsp"
        file_2 = "SHA1LongMsg.rsp"
        hash_class = SHA1
        self.parse_cavs_file(file_1, hash_class)
        self.parse_cavs_file(file_2, hash_class)

    def test_SHA2_224_implementation(self):
        file_1 = "SHA224ShortMsg.rsp"
        file_2 = "SHA224LongMsg.rsp"
        hash_class = SHA2_224
        self.parse_cavs_file(file_1, hash_class)
        self.parse_cavs_file(file_2, hash_class)

    def test_SHA2_256_implementation(self):
        file_1 = "SHA256ShortMsg.rsp"
        file_2 = "SHA256LongMsg.rsp"
        hash_class = SHA2_256
        self.parse_cavs_file(file_1, hash_class)
        self.parse_cavs_file(file_2, hash_class)

    def test_SHA2_384_implementation(self):
        file_1 = "SHA384ShortMsg.rsp"
        file_2 = "SHA384LongMsg.rsp"
        hash_class = SHA2_384
        self.parse_cavs_file(file_1, hash_class)
        self.parse_cavs_file(file_2, hash_class)

    def test_SHA2_512_implementation(self):
        file_1 = "SHA512ShortMsg.rsp"
        file_2 = "SHA512LongMsg.rsp"
        hash_class = SHA2_512
        self.parse_cavs_file(file_1, hash_class)
        self.parse_cavs_file(file_2, hash_class)
