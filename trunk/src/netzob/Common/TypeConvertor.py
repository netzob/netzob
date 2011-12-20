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

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
from bitarray import bitarray
import re
import datetime
import logging
import base64

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------

class TypeConvertor():
    
    #+---------------------------------------------- 
    #| Transform an ascii string to its binary representation
    #| @param the ascii string to transform
    #| @endian the endian selected (little or big) (normal = big)
    #| @return 
    #+----------------------------------------------
    @staticmethod
    def ascii2bin(ascii, endian):
        result = bitarray(endian=endian)
        result.fromstring(ascii)
        return result
    
    @staticmethod
    def bin2ascii(bin):
        return bin.tostring()
    
    @staticmethod
    def str2bool(val):
        return val.lower() in ("yes", "true", "t", "1")
    
    @staticmethod
    def bool2str(b):
        if b :
            return "True"
        else :
            return "False"


    
    #+---------------------------------------------- 
    #| Transform an hex to the bits : \xc9\xa1\x8d => bitarray
    #| @return 
    #+----------------------------------------------
    @staticmethod
    def hex2bin(hex):
        result = bitarray(endian='big')
        result.fromstring(hex)
        return result
    
    @staticmethod
    def bin2strhex(bin):
        return str(hex(int(bin.to01(), 2)))
    
    @staticmethod
    def int2bin(i, nbbits):
        l = nbbits - len(bin(i)[2:])
        b = bitarray(l, endian='big')
        b.setall(False)
        b.extend(bin(i)[2:])
        return b
    
    @staticmethod
    def bin2int(bin):
        return int(bin.to01(), 2)
    @staticmethod   
    def ascii2int(ascii):
        return int(ascii)
    @staticmethod
    def int2ascii(int):
        return str(int)
    
    @staticmethod
    def encodeNetzobRawToGivenType(raw, type):
        if type.lower() == "ascii" :
            return TypeConvertor.netzobRawToASCII(raw)
        elif type.lower() == "alphanum" :
            return TypeConvertor.netzobRawToAlphanum(raw)
        elif type.lower() == "num" :
            return TypeConvertor.netzobRawToNum(raw)
        elif type.lower() == "alpha" :
            return TypeConvertor.netzobRawToAlpha(raw)
        elif type.lower() == "base64dec" :
            return TypeConvertor.netzobRawToBase64Decoded(raw)
        elif type.lower() == "base64enc" :
            return TypeConvertor.netzobRawToBase64Encoded(raw)
        else :
            return raw
    
    
    @staticmethod
    def pythonDatetime2XSDDatetime(date):
        # XSD Format : [-]CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm]
#        if date == None :
#            return ""
        if not isinstance(date, datetime.datetime) and isinstance(date[0], datetime.datetime):
            date = date[0]
            
        return str(date.isoformat('T'))[:19]
        
        
    
    @staticmethod
    # Warning str must contain an XSD Datetime typed data
    def xsdDatetime2PythonDatetime(s):
        """Returns (datetime, tz offset in minutes) or (None, None)."""
        m = re.match(""" ^
        (?P<year>-?[0-9]{4}) - (?P<month>[0-9]{2}) - (?P<day>[0-9]{2})
        T (?P<hour>[0-9]{2}) : (?P<minute>[0-9]{2}) : (?P<second>[0-9]{2})
        (?P<microsecond>\.[0-9]{1,6})?
        (?P<tz>
          Z | (?P<tz_hr>[-+][0-9]{2}) : (?P<tz_min>[0-9]{2})
        )?
        $ """, s, re.X)
        if m is not None:
            values = m.groupdict()
            if values["tz"] in ("Z", None):
                tz = 0
            else:
                tz = int(values["tz_hr"]) * 60 + int(values["tz_min"])
            if values["microsecond"] is None:
                values["microsecond"] = 0
            else:
                values["microsecond"] = values["microsecond"][1:]
                values["microsecond"] += "0" * (6 - len(values["microsecond"]))
            values = dict((k, int(v)) for k, v in values.iteritems()
                              if not k.startswith("tz"))
            try:
                return datetime.datetime(**values), tz
            except ValueError:
                pass
            return None, None
    
    @staticmethod
    #+---------------------------------------------- 
    #| Return the string parameter in ASCII
    #+----------------------------------------------
    def netzobRawToASCII(raw):
        if len(raw) % 2 != 0:
#            self.log.error("Hex string len not even !")
            return raw

        res = ""
        for i in range(0, len(raw), 2):
            v = int(raw[i: i + 2], 16)
            if v >= 0x20 and v <= 0x7e: # means between ' ' and '~'
                res += chr(v)
            else:
                res += "."
        return res

    @staticmethod
    #+---------------------------------------------- 
    #| Return the string parameter in numerical value
    #+----------------------------------------------
    def netzobRawToNum(raw):
        if len(raw) % 2 != 0:
            logging.error("(toNum) Hex string len not even : " + raw)
            return raw

        s = ""
        for i in range(0, len(raw), 2):
            s += chr(int(raw[i:i + 2], 16))

        if not s.isdigit():
            logging.error("Not a digit")
            return raw

        return s

    @staticmethod
    #+---------------------------------------------- 
    #| Return the string parameter in alpha
    #+----------------------------------------------
    def netzobRawToAlpha(raw):
        if len(raw) % 2 != 0:
            logging.error("(toAlpha) Hex string len not even : " + raw)
            return raw

        s = ""
        for i in range(0, len(raw), 2):
            s += chr(int(raw[i:i + 2], 16))

        if not s.isalpha():
            logging.error("Not an alpha string")
            return raw

        return s

    @staticmethod
    #+---------------------------------------------- 
    #| Return the string parameter in alphanum
    #+----------------------------------------------
    def netzobRawToAlphanum(raw):
        if len(raw) % 2 != 0:
            logging.error("(toAlphanum) Hex string len not even : " + raw)
            return raw

        s = ""
        for i in range(0, len(raw), 2):
            s += chr(int(raw[i:i + 2], 16))

        if not s.isalnum():
            logging.error("Not an alphanumerical string")
            return raw

        return s

    @staticmethod
    #+---------------------------------------------- 
    #| Return the string parameter base64 encoded
    #+----------------------------------------------
    def netzobRawToBase64Encoded(raw):
        if len(raw) % 2 != 0:
            logging.error("(toBase64Encoded) Hex string len not even : " + raw)
            return raw

        s = ""
        for i in range(0, len(raw), 2):
            s += chr(int(raw[i:i + 2], 16))

        res = ""
        try:
            res = base64.b64decode(s)
            if res == "":
                res = raw
        except TypeError:
            res = raw

        return s

    @staticmethod
    #+---------------------------------------------- 
    #| Return the string parameter base64 decoded
    #+----------------------------------------------
    def netzobRawToBase64Decoded(raw):
        if len(raw) % 2 != 0:
            logging.error("(toBase64Decoded) Hex string len not even : " + raw)
            return raw

        s = ""
        for i in range(0, len(raw), 2):
            s += chr(int(raw[i:i + 2], 16))

        res = ""
        try:
            res = base64.b64decode(s)
            if res == "":
                res = raw
        except TypeError:
            res = raw

        return res

    @staticmethod
    #+---------------------------------------------- 
    #| Transform the current hex message ( '1fdf' ) in binary ( '\x1f\xdf' )
    #+----------------------------------------------          
    def netzobRawToBinary(msg):
        res = ""
        msg = msg.strip()
        
        if len(msg) % 2 == 0: # Even length
            for i in range(0, len(msg), 2):
                res = res + chr(int(msg[i: i + 2], 16))
        else: # Odd length
            for i in range(0, len(msg) - 1, 2):
                print msg[i: i + 2]
                res = res + chr(int(msg[i: i + 2], 16))
            res = res + chr(int(msg[-1], 16))
        return res    
        
    
