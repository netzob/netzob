#!/usr/bin/env python
# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Sumit Acharya <sumit.acharya@uni-ulm.de>                          |
# |       - Stephan Kleber <stephan.kleber@uni-ulm.de>                        |
# +---------------------------------------------------------------------------+

# Import necessary scripts from netzob codes
from netzob.Common.all import *
from netzob.Inference.all import *
from netzob.Import.all import *
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Sign, UnitSize, Endianness

# Related third party packages
import rlcompleter
import readline
import code
import re
import keyword

#Main class
@NetzobLogger
class ScapyExporter(object):
        """ Scapy Exporter to export the output 
                of the Inference to a python file which can later be executed in Scapy
        """

        _symbols = None
        __reFieldLengths = dict()

        def __init__(self, symbols, protocolName="ProtocolName_from_netzob"):
            """
            Initializes the exporter with the list of symbols to be processed and the protocol name for the output.
            :param symbols: one or list of Symbol
            :param protocolName: name of the protocol for the output
            :type protocolName str
            """
            if not re.match("[A-Z_][a-zA-Z0-9_]*$",protocolName) or keyword.iskeyword(protocolName):
                raise NameError ("INVALID ProtocolName. It should be a valid Class Name.")
            self._protocolName = protocolName

            try:
                iter(symbols) # checks if the symbols are iterable
                self._symbols = symbols
            except TypeError:  # if its only one symbol
                self._symbols = [ symbols ]
            self.__recalculateFieldLengths()


        def exportToScapy(self, filename):
            """ The function walks through all the fields in each of the symbols, checks their dataType (Raw, Integer, ASCII, BitArray, HexaString, TimeStamp, IPv4), field type (constant or variable) and size. Based on this information creates a scapy executable python script.
            Netzob datatype fields has been matched to Scapy fields in the following way:
                Integer    ---> ByteField, ShortField, SignedShortField, LEShortField, IntField, SignedIntField, LEIntField, LESignedIntField, LongField or LELongField, depending on the unitSize(8,16,32,64), SignedType(Signed or Unsigned) and/or endianness (Big or Little) 
                IPv4       ---> IPField
                Timestamp  ---> TimeStampField
                Others     ---> BitField
            If a field is 'constant' then constant field value is added to the export file, if field is 'variable', then field value is set to 'None'
            In BitField, size information are present as third argument, while for other field types, they have their own specific size example - ByteField(unsigned 1byte), ShortField (unsigned 2byte), etc
            Field size (field.domain.dataType.size) are also represented in comments.

            ProtocolName is the class name in generated scapy script.
        
            Usage: ScapyExporter(symbols,'ProtocolName').exportToScapy('OutputFilename')

            >>> m1 = RawMessage("someexamplemessage")
            >>> fields = [Field("some", name="f0"), Field("example", name="f1"), Field("message", name="f2")]
            >>> symbol = Symbol(fields, messages=[m1])

            Export one symbol...
            >>> ScapyExporter(symbol).exportToScapy("scapy_test_protocol.py")
            >>> import scapy_test_protocol
            >>> sem = scapy_test_protocol.ProtocolName_from_netzob_Symbol0()
            >>> sem.show()
            ###[ ProtocolName_from_netzob ]###
              f0        = 0x736f6d65
              f1        = 0x6578616d706c65
              f2        = 0x6d657373616765

            ... or a list of symbols.
            >>> ScapyExporter([symbol]).exportToScapy("scapy_test_protocol.py")
            >>> sem = scapy_test_protocol.ProtocolName_from_netzob_Symbol0(f1=0xcaffee)
            >>> sem.show()
            ###[ ProtocolName_from_netzob ]###
              f0        = 0x736f6d65
              f1        = 0xcaffee
              f2        = 0x6d657373616765

            >>> bytes(sem)
            b'some\\x00\\x00\\x00\\x00\\xca\\xff\\xeemessage'
            """

            protocolName = self._protocolName
            symbols = self._symbols

            sfilecontents = '' # contents for export file are initally written to this variable 
            sfilecontents += "#! /usr/bin/python" + '\n'
            sfilecontents += "from scapy.all import *" + '\n'
            sfilecontents += "from netaddr import IPAddress" + '\n'
            sfilecontents += "from bitarray import bitarray" + '\n\n'

            for i in range(0,len(symbols)):
                syml = symbols[i]
                sfilecontents += "# === Start of new PROTOCOL from Symbol{}\n".format(syml.name)
                sfilecontents += "class {}_{}{:d} (Packet):\n".format(protocolName, syml.name, i)
                sfilecontents += "\tname = \"{}\"\n".format(protocolName)
                sfilecontents += "\tfields_desc = [ \n"
                for field in syml.fields:
                    try:
                       sfilecontents += self._check_dataType(field) + '\n'
                    except AttributeError:
                       sfilecontents += "\t\t\t BitField(" + "\"" + field.name + "\","+repr(None)+ "," \
                                        + repr(self._aggDomain(field.domain)[1]) + ")," \
                                        + "\t#size:" + str(self._aggDomain(field.domain)) + '\n'

                sfilecontents += "\t\t ]" + '\n'

            with open(filename,'w') as f:
                    f.write(sfilecontents)
                    f.close()

        def __recalculateFieldLengths(self):
            """
            Workaround for inconsistent max field length in field.domain.size
            
            Field lengths in
            [a.domain.dataType.size[1] for a in symbols[i].fields]
            is not consistent with
            [len(o.getValues()[0]) * 8 for o in eachSymbol.fields]
            thus results in "some"^TM eratic values for
            fl_s = [a.size for a in dissymbol[i].fields_desc]
            and failure of dissectors
            so lets set the size max values anew from the real value max lengths
            (this has "some" performance impact!)
            
            Output gets written to self.__reFieldLengths[field]

            :return: None
            """
            try:
                symIter = iter(self._symbols)
            except TypeError:
                symIter = [ self._symbols ]

            self._logger.debug("Recalculate maximum field lengths.")
            for eachSymbol in symIter:
                fl_n_value = [len(o.getValues()[0]) * 8 for o in eachSymbol.fields]
                for field, value in zip(eachSymbol.fields, fl_n_value):
                    self.__reFieldLengths[field] = value


        def _aggDomain(self, domain):
            """
            To find the size of the Merged Field.

            Parameters have the following meanings
            :param domain: value of field.domain
            :return The size of the merged field including the size of all of its children

            >>> m1 = RawMessage("someexamplemessage")
            >>> fields = [ \
                    Field("some", name="f0"), \
                    Field( Agg([ Agg ([ Raw("ex"), Raw("ample") ]), Raw("message") ]), name="f1") \
                ]
            >>> symbol = Symbol(fields, messages=[m1])
            >>> se = ScapyExporter(symbol)
            >>> se.exportToScapy("scapy_test_agg.py")
            >>> se._aggDomain(fields[1].domain)
            (0, 112)

            >>> ofields = [ \
                    Field( Agg([ Raw("some"), Agg ([ Raw("ex"), Raw("ample") ]),  ]), name="f0"), \
                    Field("message", name="f1"), \
                ]
            >>> se._aggDomain(ofields[0].domain)
            (0, 88)


            """

            if not isinstance(domain, Agg):
                return domain.dataType.size

            lsize = self._aggDomain(domain.children[0])
            rsize = self._aggDomain(domain.children[1])

            return ( lsize[0] + rsize[0], lsize[1] + rsize[1])

        @staticmethod
        def _integer_unitSize_8(field):
            """
            :param field: The field
            :type field Field
            :return: Scapy field definition for Integer unitSize_8 signed and unsigned type
            :returns str

            >>> fields = [ \
                   Field( Integer(180, unitSize=UnitSize.SIZE_8, sign=Sign.UNSIGNED), name="int8_unsigned"), \
                   Field( Integer(-3, unitSize=UnitSize.SIZE_8, sign=Sign.SIGNED), name="int8_signed") \
                ]
            >>> ScapyExporter._integer_unitSize_8(fields[0])
            '\\t\\t\\t ByteField("int8_unsigned",180),\\t#size:(16, 16)'
            >>> ScapyExporter._integer_unitSize_8(fields[1])
            '\\t\\t\\t BitField("int8_signed",-3,8),\\t#size:(8, 8)'

            """
            if field.domain.dataType.sign == 'unsigned':
                return "\t\t\t ByteField(" + "\"" + field.name + "\"," \
                        + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                               if (field.domain.currentValue) else None)\
                       + "),"+ "\t#size:" +str(field.domain.dataType.size)
            else:
                return "\t\t\t BitField(" + "\"" + field.name + "\"," \
                       +  repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer,dst_unitSize=AbstractType.defaultUnitSize(), dst_sign=Sign.SIGNED)
                               if (field.domain.currentValue) else None) \
                       + "," + repr(field.domain.dataType.size[1]) + ")," + "\t#size:" \
                       + str(field.domain.dataType.size)

        @staticmethod
        def _integer_unitSize_16(field):
                """
                :param field: The field
                :type field Field
                :return: Scapy field definition for Integer unitSize_16 signed, unsigned and both endianness'
                :returns str

                >>> fields = [ \
                       Field( Integer(1800, unitSize=UnitSize.SIZE_16, sign=Sign.UNSIGNED), name="int16_u_be"), \
                       Field( Integer(-300, unitSize=UnitSize.SIZE_16, sign=Sign.SIGNED), name="int16_s_be"), \
                       Field( Integer(1800, unitSize=UnitSize.SIZE_16, sign=Sign.UNSIGNED, endianness=Endianness.LITTLE), name="int16_u_le"), \
                       Field( Integer(-300, unitSize=UnitSize.SIZE_16, sign=Sign.SIGNED, endianness=Endianness.LITTLE), name="int16_s_le") \
                    ]
                >>> ScapyExporter._integer_unitSize_16(fields[0])
                '\\t\\t\\t ShortField("int16_u_be",1800),\\t#size:(16, 16)'
                >>> ScapyExporter._integer_unitSize_16(fields[1])
                '\\t\\t\\t SignedShortField("int16_s_be",-300),\\t#size:(16, 16)'
                >>> ScapyExporter._integer_unitSize_16(fields[2])
                '\\t\\t\\t LEShortField("int16_u_le",1800),\\t#size:(16, 16)'
                >>> ScapyExporter._integer_unitSize_16(fields[3])
                '\\t\\t\\t BitField("int16_s_le",-300,16),\\t#size:(16, 16)'

                """
                if field.domain.dataType.sign == 'signed' and field.domain.dataType.endianness == 'big':
                    return "\t\t\t SignedShortField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer, dst_sign=Sign.SIGNED)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 
                elif field.domain.dataType.sign == 'unsigned' and field.domain.dataType.endianness == 'little':
                    return "\t\t\t LEShortField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer, dst_endianness=Endianness.LITTLE)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 
                elif field.domain.dataType.sign == 'unsigned' and field.domain.dataType.endianness == 'big':
                    return "\t\t\t ShortField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size)
                else:
                    return "\t\t\t BitField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer, dst_sign=Sign.SIGNED, dst_endianness=Endianness.LITTLE)
                                   if (field.domain.currentValue) else None) \
                           + "," + repr(field.domain.dataType.size[1]) + ")," + "\t#size:" \
                           + str(field.domain.dataType.size)    


        @staticmethod
        def _integer_unitSize_32(field):
                """
                :param field: The field
                :type field Field
                :return: Scapy field definition for Integer unitSize_32 signed unsigned and endianness
                :returns str

                >>> fields = [ \
                       Field( Integer(180000, unitSize=UnitSize.SIZE_32, sign=Sign.UNSIGNED), name="int32_u_be"), \
                       Field( Integer(-30000, unitSize=UnitSize.SIZE_32, sign=Sign.SIGNED), name="int32_s_be"), \
                       Field( Integer(180000, unitSize=UnitSize.SIZE_32, sign=Sign.UNSIGNED, endianness=Endianness.LITTLE), name="int32_u_le"), \
                       Field( Integer(-30000, unitSize=UnitSize.SIZE_32, sign=Sign.SIGNED, endianness=Endianness.LITTLE), name="int32_s_le") \
                    ]
                >>> ScapyExporter._integer_unitSize_32(fields[0])
                '\\t\\t\\t IntField("int32_u_be",180000),\\t#size:(32, 32)'
                >>> ScapyExporter._integer_unitSize_32(fields[1])
                '\\t\\t\\t SignedIntField("int32_s_be",-30000),\\t#size:(32, 32)'
                >>> ScapyExporter._integer_unitSize_32(fields[2])
                '\\t\\t\\t LEIntField("int32_u_le",180000),\\t#size:(32, 32)'
                >>> ScapyExporter._integer_unitSize_32(fields[3])
                '\\t\\t\\t LESignedIntField("int32_s_le",-30000),\\t#size:(32, 32)'

                """
                if field.domain.dataType.sign == 'unsigned' and field.domain.dataType.endianness == 'little':
                    return "\t\t\t LEIntField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer, dst_endianness=Endianness.LITTLE)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 
                elif field.domain.dataType.sign == 'signed' and field.domain.dataType.endianness == 'little':
                    return "\t\t\t LESignedIntField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer, dst_sign=Sign.SIGNED, dst_endianness=Endianness.LITTLE)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 
                elif field.domain.dataType.sign == 'signed' and field.domain.dataType.endianness == 'big':
                    return "\t\t\t SignedIntField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer, dst_sign=Sign.SIGNED)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 
                elif field.domain.dataType.sign == 'unsigned' and field.domain.dataType.endianness == 'big':
                    return "\t\t\t IntField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 

        @staticmethod
        def _integer_unitSize_64(field):
                """
                :param field: The field
                :type field Field
                :return: Scapy field definition for Integer unitSize_64 signed unsigned and endianness
                :returns str

                >>> fields = [ \
                       Field( Integer(180000000000, unitSize=UnitSize.SIZE_64, sign=Sign.UNSIGNED), name="int64_u_be"), \
                       Field( Integer(-30000000000, unitSize=UnitSize.SIZE_64, sign=Sign.SIGNED), name="int64_s_be"), \
                       Field( Integer(180000000000, unitSize=UnitSize.SIZE_64, sign=Sign.UNSIGNED, endianness=Endianness.LITTLE), name="int64_u_le"), \
                       Field( Integer(-30000000000, unitSize=UnitSize.SIZE_64, sign=Sign.SIGNED, endianness=Endianness.LITTLE), name="int64_s_le") \
                    ]
                >>> ScapyExporter._integer_unitSize_64(fields[0])
                '\\t\\t\\t LongField("int64_u_be",180000000000),\\t#size:(64, 64)'
                >>> ScapyExporter._integer_unitSize_64(fields[1])
                '\\t\\t\\t BitField("int64_s_be",-30000000000,64),\\t#size:(64, 64)'
                >>> ScapyExporter._integer_unitSize_64(fields[2])
                '\\t\\t\\t LELongField("int64_u_le",180000000000),\\t#size:(64, 64)'
                >>> ScapyExporter._integer_unitSize_64(fields[3])
                '\\t\\t\\t BitField("int64_s_le",-30000000000,64),\\t#size:(64, 64)'

                """
                if field.domain.dataType.sign == 'unsigned' and field.domain.dataType.endianness == 'little':
                    return "\t\t\t LELongField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer, dst_endianness=Endianness.LITTLE)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 
                elif field.domain.dataType.sign == 'unsigned' and field.domain.dataType.endianness == 'big':
                    return "\t\t\t LongField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size)
                else:
                    return "\t\t\t BitField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer, dst_sign=Sign.SIGNED, dst_endianness=field.domain.dataType.endianness)
                                   if (field.domain.currentValue) else None) \
                           + "," + repr(field.domain.dataType.size[1]) + ")," + "\t#size:" \
                           + str(field.domain.dataType.size)  
     

        @staticmethod
        def _dataType_integer(field):
                """
                Select the correct integer dataType for field
                :param field: The Field
                :type field Field
                :return: The method for handling the integer type of field
                """
                switcher = {
                        '8'   : ScapyExporter._integer_unitSize_8,
                        '16'  : ScapyExporter._integer_unitSize_16,
                        '32'  : ScapyExporter._integer_unitSize_32,
                        '64'  : ScapyExporter._integer_unitSize_64
                }
                return switcher.get(field.domain.dataType.unitSize, ScapyExporter._integer_unitSize_8)(field)


        @staticmethod
        def _dataType_timestamp(field):
                """
                :param field: The field
                :return: Scapy field definition for TimeStamp dataType

                >>> field = Field(Timestamp(1444737333), name="Timestamp")
                >>> ScapyExporter._dataType_timestamp(field)
                '\\t\\t\\t TimeStampField("Timestamp",\\'Tue Oct 13 11:55:33 2015\\'),\\t#size:(32, 32)'

                """
                return "\t\t\t TimeStampField(" + "\"" + field.name + "\"," \
                       + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Timestamp) if
                               (field.domain.currentValue) else None)\
                       + "),"+ "\t#size:" +str(field.domain.dataType.size) 


        @staticmethod
        def _dataType_ipv4(field):
                """
                :param field: The field
                :return: Scapy field definition for IPv4 dataType

                >>> field = Field(IPv4("192.168.23.42"), name="IP-Address")
                >>> ScapyExporter._dataType_ipv4(field)
                '\\t\\t\\t IPField("IP-Address",IPAddress(\\'192.168.23.42\\')),\\t#size:(32, 32)'

                """
                return "\t\t\t IPField(" + "\"" + field.name + "\"," \
                       + repr(TypeConverter.convert(field.domain.currentValue,BitArray,IPv4) if
                               (field.domain.currentValue) else None)\
                       + "),"+ "\t#size:" +str(field.domain.dataType.size)           


        def _dataType_raw(self, field):
                """
                :param field: The field
                :return: Scapy field definition for Raw, BitArray, HexaString, and ASCII dataTypes

                >>> m = b"\\x42\\x43\\x44\\x45"
                >>> field = Field(Raw(m), name="Some Field")
                >>> se = ScapyExporter( Symbol([field], messages=[RawMessage(m)]) )
                >>> se._dataType_raw(field)
                '\\t\\t\\t XBitField("Some Field",1111704645,32),\\t#size:(0, 32)'
                """
                return "\t\t\t XBitField(\"{}\",{},{:d}),\t#size:{}".format(
                        field.name,
                        repr(TypeConverter.convert(field.domain.currentValue, BitArray, Integer,
                                                   dst_unitSize=AbstractType.defaultUnitSize(),
                                                   dst_endianness=Endianness.BIG)
                             if (field.domain.currentValue) else None),
                        self.__reFieldLengths[field],
                        str(field.domain.dataType.size)
                    )
                    # replace line -3 by the following one when domain.dataType.size-"bug" is fixed
                    # repr(field.domain.dataType.size[1])


        def _check_dataType(self, field):
                """
                Check dataType of the field
                :param field: The field
                :return: function to handle data type of field
                """

                # Workaround for empty Netzob fields which erroneously receive a maximum size of 8 bits
                if max([len(f6v) for f6v in field.getValues()]) == 0:
                    return '' # return an empty string to effectively skip this field

                switcher = {
                        'Integer'   : ScapyExporter._dataType_integer,
                        'Timestamp' : ScapyExporter._dataType_timestamp,
                        'IPv4'      : ScapyExporter._dataType_ipv4
                }
                return switcher.get(field.domain.dataType.typeName, self._dataType_raw)(field)
