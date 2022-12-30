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

# About the test vector file (HMAC.rsp):
# the choice of the algorithm is defined by the starting length of the Mac (described as '[L=XX]' in the test file)
#   [L=20] stand for SHA1
#   [L=28] stand for SHA2-224
#   [L=32] stand for SHA2-256
#   [L=48] stand for SHA2-384
#   [L=64] stand for SHA2-512

class test_Hmacs(unittest.TestCase):

    file = "HMAC.rsp"
    
    def parse_file(self, mac_len_start, hmac_class):
        file_path = os.path.join("test", "resources", "test_netzob", "test_Hmacs", self.file)
        fd = open(file_path, 'r')
        msg = ""
        key = ""
        mac_len = 0
        for line in fd:
            if line.find('[L='+str(mac_len_start)+']') != -1:      # mean start of the algorithm section
                break
        for line in fd:
            if line.find('[L=') != -1:      # mean end of the algorithm section
                break
            elif 'Tlen =' in line:
                mac_len = int(line[7:-1]) * 2
            elif 'Key =' in line:
                key = line[6:-1]
            elif 'Msg =' in line:
                msg = line[6:-1]
            elif 'Mac =' in line:
                self.check_res(key, msg, line[6:-1], hmac_class, mac_len)
                msg = ""
                key = ""

    def check_res(self, key, msg, mac, hmac_class, mac_len):
        b = bytes.fromhex(msg)
        k = bytes.fromhex(key)
        f1 = Field(Raw(b))
        f2 = Field(hmac_class([f1], key=k))
        s = Symbol(fields = [f1, f2])
        tmp = s.specialize()[len(b):]
        rep = tmp.hex()[:mac_len]
        self.assertEqual(rep, mac)

    def test_SHA1_implementation(self):
        mac_len_start = 20
        hmac_class = HMAC_SHA1
        self.parse_file(mac_len_start, hmac_class)
    
    def test_SHA2_224_implementation(self):
        mac_len_start = 28
        hmac_class = HMAC_SHA2_224
        self.parse_file(mac_len_start, hmac_class)
    
    def test_SHA2_256_implementation(self):
        mac_len_start = 32
        hmac_class = HMAC_SHA2_256
        self.parse_file(mac_len_start, hmac_class)

    def test_SHA2_384_implementation(self):
        mac_len_start = 48
        hmac_class = HMAC_SHA2_384
        self.parse_file(mac_len_start, hmac_class)

    def test_SHA2_512_implementation(self):
        mac_len_start = 64
        hmac_class = HMAC_SHA2_512
        self.parse_file(mac_len_start, hmac_class)
