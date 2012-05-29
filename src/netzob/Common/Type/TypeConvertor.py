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
import struct

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.Format import Format
from netzob.Common.Type.UnitSize import UnitSize
import StringIO
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.Endianess import Endianess


class TypeConvertor():

    #+----------------------------------------------
    #| Transform a string to its binary representation
    #| @param the string to transform
    #| @endian the endian selected (little or big) (normal = big)
    #| @return
    #+----------------------------------------------
    @staticmethod
    def string2bin(aStr, endian='big'):
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
        if b:
            return "true"
        else:
            return "false"

    #+----------------------------------------------
    #| Transforms : bitarray('011101010') -> 011101010
    #+----------------------------------------------
    @staticmethod
    def bitarray2StrBitarray(bin):
        return str(bin)[10:len(str(bin)) - 2]

    #+----------------------------------------------
    #| Transforms : 011101010 -> bitarray('011101010')
    #+----------------------------------------------
    @staticmethod
    def strBitarray2Bitarray(strBin):
        result = bitarray(strBin)
        return result

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
    def encodePythonRawToGivenType(raw, aType):
        netzobRaw = TypeConvertor.pythonRawToNetzobRaw(raw)
        return TypeConvertor.encodeNetzobRawToGivenType(netzobRaw, aType)

    @staticmethod
    def encodeNetzobRawToGivenType(raw, aType):
        if aType == Format.STRING:
            return TypeConvertor.netzobRawToString(raw)
        elif aType == Format.HEX:
            return raw
        elif aType == Format.OCTAL:
            return TypeConvertor.netzobRawToOctal(raw)
        elif aType == Format.BINARY:
            return TypeConvertor.netzobRawToBinary(raw)
        elif aType == Format.DECIMAL:
            return TypeConvertor.netzobRawToDecimal(raw)
        elif aType == Format.IP:
            return TypeConvertor.netzobRawToIP(raw)
        else:
            return raw

    @staticmethod
    def encodeNetzobRawToGivenField(raw, field):
        res = TypeConvertor.applyFieldEncoding(raw, field)
        return res

    @staticmethod
    def string2hex(msg):
        return [hex(ord(x)) for x in msg]

    @staticmethod
    def encodeGivenTypeToNetzobRaw(raw, aType):
        if aType == Format.STRING:
            return TypeConvertor.stringToNetzobRaw(raw)
        elif aType == Format.HEX:
            return raw
        elif aType == Format.OCTAL:
            return TypeConvertor.octalToNetzobRaw(raw)
        elif aType == Format.BINARY:
            return TypeConvertor.binaryToNetzobRaw(raw)
        elif aType == Format.DECIMAL:
            return TypeConvertor.decimalToNetzobRaw(raw)
        elif aType == Format.IP:
            return TypeConvertor.ipToNetzobRaw(raw)
        else:
            return raw

    @staticmethod
    def pythonDatetime2XSDDatetime(date):
        # XSD Format : [-]CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm]
#        if date == None:
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
                return datetime.datetime(**values)
            except ValueError:
                pass
            return None, None

    @staticmethod
    def stringToNetzobRaw(aStr):
        raw = []
        for c in aStr:
            strhexc = str(hex(ord(c)))[2:]
            if len(strhexc) < 2:
                strhexc = "0" + strhexc
            raw.append(strhexc)
        return ''.join(raw)

    @staticmethod
    #+----------------------------------------------
    #| Return the string parameter in string
    #+----------------------------------------------
    def netzobRawToString(raw):
        res = ""
        for i in range(0, len(raw), 2):
            if len(raw[i: i + 2]) % 2 == 0:
                v = int(raw[i: i + 2], 16)
            else:  # Unaligned octet
                v = int(raw[i: i + 1], 16)
            if v >= 0x20 and v <= 0x7e:  # means between ' ' and '~'
                res += chr(v)
            else:
                res += "."
        return res

    @staticmethod
    #+----------------------------------------------
    #| Return the string parameter in octal
    #+----------------------------------------------
    def netzobRawToOctal(raw):
        res = ""
        raw = raw.strip()

        if len(raw) % 2 == 0:  # Even length
            for i in range(0, len(raw), 2):
                res = res + oct(int(raw[i: i + 2], 16))
        else:  # Odd length
            for i in range(0, len(raw) - 1, 2):
                res = res + oct(int(raw[i: i + 2], 16))
            res = res + oct(int(raw[-1], 16))
        return res

    @staticmethod
    #+----------------------------------------------
    #| Return the octal parameter in string
    #+----------------------------------------------
    def octalToNetzobRaw(raw):
        logging.error("Not yet implemented")
        # TODO
        return raw

    @staticmethod
    #+----------------------------------------------
    #| Return the string parameter in decimal
    #+----------------------------------------------
    def netzobRawToDecimal(raw):
        res = ""
        raw = raw.strip()

        if len(raw) % 2 == 0:  # Even length
            for i in range(0, len(raw), 2):
                res = res + str(int(raw[i: i + 2], 16))
        else:  # Odd length
            for i in range(0, len(raw) - 1, 2):
                res = res + str(int(raw[i: i + 2], 16))
            res = res + str(int(raw[-1], 16))
        return res

    @staticmethod
    #+----------------------------------------------
    #| Return the decimal parameter in string
    #+----------------------------------------------
    def decimalToNetzobRaw(raw):
        result = str(int(raw, 16))
        if len(result) % 2 == 1:
            result = "0" + result
        return result

    @staticmethod
    #+----------------------------------------------
    #| Return the hex string parameter in IP
    #+----------------------------------------------
    def netzobRawToIP(raw):
        logging.error("Not yet implemented")
        # TODO
        return raw

    @staticmethod
    #+----------------------------------------------
    #| Return the IP parameter provide in string in hex string
    #| "192.168.0.10" -> "ab3e10ea"
    #+----------------------------------------------
    def ipToNetzobRaw(raw):
        dec_octets = str.split(raw, '.')
        hex_octets = []
        for dec_octet in dec_octets:
            if int(dec_octet) > 255:
                logging.error("The provided IP is not valid ! " + str(raw))
                return None
            if int(dec_octet) < 16:
                hex_octets.append('0' + hex(int(dec_octet))[2:])
            else:
                hex_octets.append(hex(int(dec_octet))[2:])

        hex_ip = ''.join(hex_octets)
        return hex_ip

    @staticmethod
    #+----------------------------------------------
    #| Return the string parameter in bit
    #+----------------------------------------------
    def netzobRawToBinary(raw):
        res = bitarray()
        for c in raw:
            tmp = bitarray()
            tmp.fromstring(chr(int(c, 16)))
            tmp = str(tmp)[10:len(str(tmp)) - 2][4:]
            res.extend(tmp)
        return res.to01()

    @staticmethod
    #+----------------------------------------------
    #| Return the string parameter in a bitarray
    #+----------------------------------------------
    def netzobRawToBitArray(raw):
        res = bitarray()
        for c in raw:
            tmp = bitarray()
            tmp.fromstring(chr(int(c, 16)))
            tmp = str(tmp)[10:len(str(tmp)) - 2][4:]
            res.extend(tmp)
        return res

    @staticmethod
    #+----------------------------------------------
    #| Return the bits parameter in raw
    #+----------------------------------------------
    def binaryToNetzobRaw(raw):
        logging.error("Not yet implemented")
        # TODO
        return raw

    @staticmethod
    #+----------------------------------------------
    #| Transform the current hex message ('1fdf') in binary python raw ('\x1f\xdf')
    #+----------------------------------------------
    def netzobRawToPythonRaw(msg):
        res = ""
        msg = msg.strip()

        if len(msg) % 2 == 0:  # Even length
            for i in range(0, len(msg), 2):
                res = res + chr(int(msg[i: i + 2], 16))
        else:  # Odd length
            for i in range(0, len(msg) - 1, 2):
                res = res + chr(int(msg[i: i + 2], 16))
            res = res + chr(int(msg[-1], 16))
        return res

    @staticmethod
    #+----------------------------------------------
    #| Transform the current binary python raw message ('\x1f\xdf') in hex ('1fdf')
    #+----------------------------------------------
    def pythonRawToNetzobRaw(msg):
        res = ""
        for i in range(0, len(msg), 1):
            res = res + msg[i:i + 1].encode("hex")
        return res

    @staticmethod
    #+----------------------------------------------
    #| serializeScores :
    #|     create a serialization view of the scores
    #| @returns (format)
    #+---------------------------------------------
    def serializeScores(symbol, scores, symbols):
        format = ""
        iuid = symbol.getID()
        canAppend = False
        if iuid in scores.keys():
            for j in symbols:
                juid = j.getID()
                if juid in scores[iuid].keys() and canAppend:
                    format += str(scores[iuid][juid]) + "S"
                canAppend = (j == symbol)
        format += "E"
        return format

    @staticmethod
    #+----------------------------------------------
    #| serializeScores :
    #|     create a serialization view of the scores
    #| @returns (format)
    #+---------------------------------------------
    def deserializeScores(symbols, scores):
        listScores = [[symbols[i].getID(), symbols[j].getID(), score] for (i, j, score) in scores]
        return listScores

    @staticmethod
    #+----------------------------------------------
    #| serializeMessages :
    #|     create a serialization view of the messages
    #| @returns (serialized, format)
    #+----------------------------------------------
    def serializeMessages(messages, unitSize):
        serialMessages = ""
        format = ""
        for m in messages:
            data = m.getReducedStringData()

            if unitSize == 8:
                data = data
            elif unitSize == 4:
                data = "".join(["0" + i for i in data])
            else:
                logging.warn("Serializing at " + str(unitSize) + " unit size not yet implemented")
                return

            format += str(len(data) / 2) + "M"
            serialMessages += TypeConvertor.netzobRawToPythonRaw(data)
        return (serialMessages, format)

    @staticmethod
    #+----------------------------------------------
    #| serializeSymbol :
    #|     create a serialization view of a symbol
    #| @returns (serialized, format)
    #+----------------------------------------------
    def serializeSymbol(symbol, unitSize):
        serialSymbol = ""
        format = ""
        if symbol.getAlignment() != None and symbol.getAlignment() != "":
            format += "1" + "G"
            messageTmp = ""
            alignmentTmp = ""

            if unitSize == 8:
                for i in range(0, len(symbol.getAlignment()), 2):
                    format += str(len(symbol.getAlignment()) / 2) + "M"
                    if symbol.getAlignment()[i:i + 2] == "--":
                        messageTmp += "\xff"
                        alignmentTmp += "\x01"
                    else:
                        messageTmp += TypeConvertor.netzobRawToPythonRaw(symbol.getAlignment()[i:i + 2])
                        alignmentTmp += "\x00"
            elif unitSize == 4:
                format += str(len(symbol.getAlignment())) + "M"
                for i in range(0, len(symbol.getAlignment())):
                    if symbol.getAlignment()[i:i + 1] == "-":
                        messageTmp += "\xff"
                        alignmentTmp += "\x01"
                    else:
                        messageTmp += TypeConvertor.netzobRawToPythonRaw("0" + symbol.getAlignment()[i:i + 1])
                        alignmentTmp += "\x00"
            else:
                logging.warn("Serializing at " + str(unitSize) + " unit size not yet implemented")
                return
            serialSymbol += messageTmp
            serialSymbol += alignmentTmp
        else:
            format += str(len(symbol.getMessages())) + "G"
            for m in symbol.getMessages():
                data = m.getReducedStringData()
                if unitSize == 8:
                    format += str(len(data) / 2) + "M"
                    data = data
                elif unitSize == 4:
                    format += str(len(data)) + "M"
                    data = "".join(["0" + i for i in data])
                else:
                    logging.warn("Serializing at " + str(unitSize) + " unit size not yet implemented")
                    return
                serialSymbol += TypeConvertor.netzobRawToPythonRaw(data)  # The message
                serialSymbol += "".join(['\x00' for x in range(len(data) / 2)])  # The alignement == "\x00" * len(the message), the first time
        return (serialSymbol, format)

    @staticmethod
    #+----------------------------------------------
    #| serializeSymbols :
    #|     create a serialization view of symbols
    #| @returns (serialized, format)
    #+----------------------------------------------
    def serializeSymbols(symbols, unitSize, scores):
        serialSymbols = ""
        formatSymbols = ""
        for symbol in symbols:
            (serialSymbol, formatSymbol) = TypeConvertor.serializeSymbol(symbol, unitSize)
            formatScores = TypeConvertor.serializeScores(symbol, scores, symbols)
            formatSymbols += formatScores
            serialSymbols += serialSymbol
            formatSymbols += formatSymbol
        return (serialSymbols, formatSymbols)

    @staticmethod
    #+----------------------------------------------
    #| deserializeContent :
    #|     python deserialization process
    #| @returns (serialized, format)
    #+----------------------------------------------
    def deserializeContent(serializedContents, format):
        result = []
        # first we retrieve the size of all the messages
        size_messages = format.split("M")
        total = 0
        for str_size_message in size_messages[:-1]:
            size_message = int(str_size_message)
            result.append(TypeConvertor.pythonRawToNetzobRaw(serializedContents[total:total + size_message]))
            total += size_message

        return result

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
            elif str == '\n':
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
    #| Transform each chunk according to the endianess
    #+----------------------------------------------
    def applyFieldEncoding(raw, field):
        unitSize = field.getUnitSize()
        endianess = field.getEndianess()
        sign = field.getSign()
        aFormat = field.getFormat()

        # Handle unitSize
        # TODO: support 4BITS
        if unitSize == UnitSize.NONE:
            tmp = TypeConvertor.encodeNetzobRawToGivenType(raw, aFormat)
            return tmp
        elif unitSize == UnitSize.BIT:
            size = 1
            return TypeConvertor.encodeNetzobRawToGivenType(raw, aFormat)
        elif unitSize == UnitSize.BITS8:
            size = 8
        elif unitSize == UnitSize.BITS16:
            size = 16
        elif unitSize == UnitSize.BITS32:
            size = 32
        elif unitSize == UnitSize.BITS64:
            size = 64
        else:  # Render with no splitting
            tmp = TypeConvertor.encodeNetzobRawToGivenType(raw, aFormat)
            return tmp

        # Handle endianess
        if endianess == Endianess.BIG:
            transform = ">"
        else:
            transform = "<"

        res = ""
        for i in range(0, len(raw), size / 4):
            tmp = raw[i:i + (size / 4)]
            initTmp = tmp

            if len(tmp) == 2:  # In half-bytes
                sizeStr = "B"
            elif len(tmp) == 4:
                sizeStr = "H"
            elif len(tmp) == 8:
                sizeStr = "I"
            elif len(tmp) == 16:
                sizeStr = "Q"
            else:
                sizeStr = "Q"
                if endianess == Endianess.BIG:
                    tmp = (16 - len(tmp)) * "0" + tmp  # Put padding on the left
                else:
                    tmp = tmp + (16 - len(tmp)) * "0"  # Put padding on the right

            tmp = TypeConvertor.netzobRawToPythonRaw(tmp)

            # Handle sign
            if sign == Sign.SIGNED:
                sizeStr = sizeStr.lower()

            (tmp,) = struct.unpack(transform + sizeStr, tmp)

            # Handle format
            if aFormat == Format.BINARY:
                tmp = TypeConvertor.netzobRawToBinary(initTmp)
            elif aFormat == Format.OCTAL:
                tmp = "%o" % tmp
            elif aFormat == Format.DECIMAL:
                tmp = "%d" % tmp
            elif aFormat == Format.HEX:
                fmt = "%" + str(size / 4) + "x"
                tmp = fmt % tmp
            elif aFormat == Format.STRING:
                tmp = TypeConvertor.netzobRawToString(initTmp)
            elif aFormat == Format.FLOAT:
                tmp = "%f" % tmp

            res += str(tmp)

        return res  # s[:-1]  # We delete the last space character
