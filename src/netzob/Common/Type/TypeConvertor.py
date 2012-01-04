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
from netzob.Common.Type.Format import Format
from netzob.Common.Type.UnitSize import UnitSize

class TypeConvertor():

    #+---------------------------------------------- 
    #| Transform a string to its binary representation
    #| @param the string to transform
    #| @endian the endian selected (little or big) (normal = big)
    #| @return 
    #+----------------------------------------------
    @staticmethod
    def string2bin(aStr, endian):
        result = bitarray(endian=endian)
        result.fromstring(aStr)
        return result
    
    @staticmethod
    def bin2string(bin):
        return bin.tostring()
    
    @staticmethod
    def str2bool(val):
        return val.lower() in ("yes", "true", "t", "1")
    
    @staticmethod
    def bool2str(b):
        if b :
            return "true"
        else :
            return "false"
    
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
    def string2int(aStr):
        return int(aStr)
    @staticmethod
    def int2string(int):
        return str(int)
    
    @staticmethod
    def encodeNetzobRawToGivenType(raw, aType):
        if aType == Format.STRING :
            return TypeConvertor.netzobRawToString(raw)
        elif aType == Format.HEX :
            return raw
        elif aType == Format.OCTAL :
            return TypeConvertor.netzobRawToOctal(raw)
        elif aType == Format.BINARY :
            return TypeConvertor.netzobRawToBinary(raw)
        elif aType == Format.DECIMAL :
            return TypeConvertor.netzobRawToDecimal(raw)
        else :
            return raw

    @staticmethod
    def encodeNetzobRawToGivenField(raw, field):
        res = TypeConvertor.applyUnitSize(raw, field.getUnitSize())
        print res
        return
        res = TypeConvertor.applyEndianess(res, field.getEndianess())
        res = TypeConvertor.applySign(res, field.getSign())
        res = TypeConvertor.encodeNetzobRawToGivenType(res, field.getFormat())
        return res

    @staticmethod
    def string2hex(msg):
        return [hex(ord(x)) for x in msg]

    @staticmethod
    def encodeGivenTypeToNetzobRaw(raw, aType):
        if aType == Format.STRING :
            return TypeConvertor.stringToNetzobRaw(raw)
        elif aType == Format.HEX :
            return raw
        elif aType == Format.OCTAL :
            return TypeConvertor.octalToNetzobRaw(raw)
        elif aType == Format.BINARY :
            return TypeConvertor.binaryToNetzobRaw(raw)
        elif aType == Format.DECIMAL :
            return TypeConvertor.decimalToNetzobRaw(raw)
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
    def stringToNetzobRaw(aStr):
        raw = []
        for c in aStr :
            strhexc = str(hex(ord(c)))[2:]
            if len(strhexc) < 2 :
                strhexc = "0" + strhexc
            raw.append(strhexc)
        return ''.join(raw)
    
    @staticmethod
    #+---------------------------------------------- 
    #| Return the string parameter in string
    #+----------------------------------------------
    def netzobRawToString(raw):
        if len(raw) % 2 != 0:
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
    #| Return the string parameter in octal
    #+----------------------------------------------
    def netzobRawToOctal(raw):
        if len(raw) % 2 != 0:
            logging.error("(toOctal) Hex string len not even : " + raw)
            return raw

        # TODO
        return raw

    @staticmethod
    #+---------------------------------------------- 
    #| Return the octal parameter in string
    #+----------------------------------------------
    def octalToNetzobRaw(raw):
        if len(raw) % 2 != 0:
            logging.error("(toOctal) Hex string len not even : " + raw)
            return raw

        # TODO
        return raw

    @staticmethod
    #+---------------------------------------------- 
    #| Return the string parameter in decimal
    #+----------------------------------------------
    def netzobRawToDecimal(raw):
        if len(raw) % 2 != 0:
            logging.error("(toOctal) Hex string len not even : " + raw)
            return raw

        # TODO
        return raw

    @staticmethod
    #+---------------------------------------------- 
    #| Return the decimal parameter in string
    #+----------------------------------------------
    def decimalToNetzobRaw(raw):
        if len(raw) % 2 != 0:
            logging.error("(toOctal) Hex string len not even : " + raw)
            return raw

        # TODO
        return raw

    @staticmethod
    #+---------------------------------------------- 
    #| Return the string parameter in bit
    #+----------------------------------------------
    def netzobRawToBinary(raw):
        if len(raw) % 2 != 0:
            logging.error("(toBit) Hex string len not even : " + raw)
            return raw
        binary = TypeConvertor.netzobRawToPythonRaw(raw)
        return TypeConvertor.hex2bin(binary).to01()

    @staticmethod
    #+---------------------------------------------- 
    #| Return the bits parameter in raw
    #+----------------------------------------------
    def binaryToNetzobRaw(raw):
        if len(raw) % 2 != 0:
            logging.error("(toBit) Hex string len not even : " + raw)
            return raw
        # TODO
        return raw

    @staticmethod
    #+---------------------------------------------- 
    #| Transform the current hex message ( '1fdf' ) in binary python raw ( '\x1f\xdf' )
    #+----------------------------------------------          
    def netzobRawToPythonRaw(msg):
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

    @staticmethod
    #+---------------------------------------------- 
    #| Transform the current binary python raw message ( '\x1f\xdf' ) in hex ( '1fdf' )
    #+----------------------------------------------          
    def pythonRawToNetzobRaw(msg):
        res = ""
        for i in range(0, len(msg), 1):
            res = res + msg[i:i + 1].encode("hex")
        return res

    @staticmethod
    #+---------------------------------------------- 
    #| Return a hexdump of a hex message
    #+----------------------------------------------          
    def hexdump(buf, start=0):
        length = len(buf)
        res = StringIO.StringIO()
        def GetPrintableChar(str):
            if str.isalnum():
                return str
            elif str == '\n' :
                return "<CR>"
            else:
                return '.'

        i = 0
        while i < length:
            if length - i > 16:
                l = 16
            else:
                l = length - i
            
            res.write('0x%08x  ' % (i + start))
            s = ' '.join(["%02x" % ord(c) for c in buf[i:i + l]])
            res.write(s)
            sp = 49 - len(s)
            res.write(' ' * sp)
            s = ''.join(["%s" % GetPrintableChar(c) for c in buf[i:i + l]])
            res.write(s)
            res.write('\n')
            i = i + 16

        return res.getvalue()

    @staticmethod
    #+---------------------------------------------- 
    #| Split a raw message by chunk of specific size
    #+----------------------------------------------          
    def applyUnitSize(raw, unitSize):
        size = None
        # TODO: handle BIT level
#        if unitSize == UnitSize.BIT:
#            size = 1
#        elif unitSize == UnitSize.HALFBYTE:
        if unitSize == UnitSize.HALFBYTE:
            size = 4
        elif unitSize == UnitSize.BYTE:
            size = 8
        elif unitSize == UnitSize.HALFWORD:
            size = 16
        elif unitSize == UnitSize.WORD:
            size = 32
        elif unitSize == UnitSize.DOUBLEWORD:
            size = 64
        elif unitSize == UnitSize.QUADWORD:
            size = 128

        size = size / 4
        res = ""
        for i in range(len(raw)):
            res += raw[i:i+size] + " "
        return res[:-1] # We delete the last space character
