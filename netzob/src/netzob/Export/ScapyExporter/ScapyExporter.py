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

# Related third party packages
import rlcompleter
import readline
import code
import re
import keyword

#Main class
class ScapyExporter(object):
        """ Scapy Exporter to export the output 
                of the Inference to a python file which can later be executed in Scapy
        """

        __reFieldLengths = dict()

        def __init__(self):
            pass

        def exportToScapy(self, symbols, filename, protocolName="ProtocolName_from_netzob"):
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
        
            Usage: >>> ScapyExporter().exportToScapy(symbols,'OutputFilename','ProtocolName')
            """
            if not re.match("[A-Z_][a-zA-Z0-9_]*$",protocolName) or keyword.iskeyword(protocolName):
                raise NameError ("INVALID ProtocolName. It should be a valid Class Name.")

            self.__recalculateFieldLengths(symbols)

            sfilecontents = '' # contents for export file are initally written to this variable 
            sfilecontents += "#! /usr/bin/python" + '\n'
            sfilecontents += "from scapy.all import *" + '\n'
            sfilecontents += "from netaddr import IPAddress" + '\n'
            sfilecontents += "from bitarray import bitarray" + '\n\n'
            try:
                """ checks if the symbols are iterable
        """
                iter(symbols)
                i=0 # counts number of symbols
                for syml in symbols:
                        sfilecontents += "# === Start of new PROTOCOL from Symbol" + str(i) + '\n'
                        sfilecontents += "class " + protocolName + "_" + syml.name + str(i) + "(Packet):" + '\n'
                        sfilecontents += "\tname = \"" + protocolName  + "\"" +'\n'
                        sfilecontents += "\tfields_desc = [ " + '\n'
                        for field in syml.fields:
                                try:
                                        sfilecontents += self.check_dataType(field) + '\n'
                                except AttributeError:
                                        sfilecontents += "\t\t\t BitField(" + "\"" + field.name + "\","+repr(None)+ "," + repr(self.aggDomain(field.domain,[],1000,0)[1])+")," + "\t#size:" + str(self.aggDomain(field.domain,[],1000,0)) + '\n'
                        sfilecontents += "\n\t\t ]" + '\n'
                        i=i+1
                with open(filename,'w') as f:
                        f.write(sfilecontents)
                        f.close()

            except TypeError:
                syml = symbols
                sfilecontents += "# === Start of new PROTOCOL from " + syml.name + '\n'
                sfilecontents += "class " + protocolName + "_" + syml.name + "(Packet):" + '\n'
                sfilecontents += "\tname = \"" + protocolName + "\""  + '\n'
                sfilecontents += "\tfields_desc = [ " + '\n'
                for field in syml.fields:
                        try:
                                sfilecontents += self.check_dataType(field) + '\n'
                        except AttributeError:
                                sfilecontents += "\t\t\t BitField(" + "\"" + field.name + "\","+repr(None)+ "," + repr(self.aggDomain(field.domain,[],1000,0))+")," + "\t#size:" + str(self.aggDomain(field.domain,[],1000,0))
                        sfilecontents += '\n'
                sfilecontents += "\n\t\t ]" + '\n'
                with open(filename,'w') as f:
                        f.write(sfilecontents)
                        f.close()

        def __recalculateFieldLengths(self, symbols):
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
            
            Output gets written to self.reFieldLengths[field]
            
            :param symbols: The symbol(s) to calculate the length of fields for
            :return: None
            """
            try:
                symIter = iter(symbols)
            except TypeError:
                symIter = [ symbols ]

            print("Recalculate maximum field lengths:", end=' ')
            for eachSymbol in symIter:
                print('.', end=' ')
                fl_n_value = [len(o.getValues()[0]) * 8 for o in eachSymbol.fields]
                for field, value in zip(eachSymbol.fields, fl_n_value):
                    self.__reFieldLengths[field] = value
            print()


        # To find the size of the Merged Field
        def aggDomain(self, domain,remaining_domain, size0, size1):
                """ Parameters have the following meanings
                        domain          --> field.domain
                        remaining_domain    --> specially used in Nested children in Aggregate domain
                        size0           --> minimum size of the field, initially set to 1000
                        size1           --> maximum size of the field, initially set to 0
                    Function returns the size of the merged field, considering all possible combinations. Possible combinations in aggregate field can be
                        i)   Field contains only two children(children0 and children1), no grand-children present
                        ii)  Field contains Grand-children but only through Children0 or Children1, not both 
                        iii) Field contains grand-children from both children (children0 and children1)     
                """
                if str(domain.children[1]) == 'Agg' and str(domain.children[0]) != 'Agg':
                        sizefield1 = list(domain.children[0].dataType.size)
                        size0 = min(sizefield1[0],size0)
                        size1 = size1 + sizefield1[1]
                        return self.aggDomain(domain.children[1], remaining_domain,size0, size1)
                elif str(domain.children[0]) == 'Agg' and str(domain.children[1]) != 'Agg':
                        sizefield = list(domain.children[1].dataType.size)
                        size0 = min(sizefield[0],size0)
                        size1 = size1 + sizefield[1]
                        return self.aggDomain(domain.children[0],remaining_domain,size0,size1)
                elif str(domain.children[0]) == 'Agg' and str(domain.children[1]) == 'Agg':
                        remaining_domain.append(domain.children[1])
                        return self.aggDomain(domain.children[0],remaining_domain,size0,size1)
                else:
                        sizefield0 = list(domain.children[0].dataType.size)
                        sizefield1 = list(domain.children[1].dataType.size)
                        size0 = min(size0,sizefield0[0],sizefield1[0])
                        size1 = size1 + sizefield0[1] + sizefield1[1]
                if(remaining_domain):
                        return self.aggDomain(remaining_domain.pop(),remaining_domain,size0,size1)  
                else:
                        return (size0,size1)


        # Integer unitSize_8 signed and unsigned type
        def integer_unitSize_8(self,field):
                if field.domain.dataType.sign == 'unsigned':
                    return "\t\t\t ByteField(" + "\"" + field.name + "\"," \
                            + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size)
                else:
                    return "\t\t\t BitField(" + "\"" + field.name + "\"," \
                           +  repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer,dst_unitSize=AbstractType.defaultUnitSize())
                                   if (field.domain.currentValue) else None) \
                           + "," + repr(field.domain.dataType.size[1]) + ")," + "\t#size:" \
                           + str(field.domain.dataType.size)
 
        # Integer unitSize_16 signed unsigned and endianness
        def integer_unitSize_16(self,field):
                if field.domain.dataType.sign == 'signed':
                    return "\t\t\t SignedShortField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 
                elif field.domain.dataType.sign == 'unsigned' and field.domain.dataType.endianness == 'little':
                    return "\t\t\t LEShortField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 
                elif field.domain.dataType.sign == 'unsigned' and field.domain.dataType.endianness == 'big':
                    return "\t\t\t ShortField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size)
                else:
                    return "\t\t\t BitField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer,dst_unitSize=AbstractType.defaultUnitSize())
                                   if (field.domain.currentValue) else None) \
                           + "," + repr(field.domain.dataType.size[1]) + ")," + "\t#size:" \
                           + str(field.domain.dataType.size)    

        # Integer unitSize_32 signed unsigned and endianness
        def integer_unitSize_32(self,field):
                if field.domain.dataType.sign == 'unsigned' and field.domain.dataType.endianness == 'little':
                    return "\t\t\t LEIntField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 
                elif field.domain.dataType.sign == 'signed' and field.domain.dataType.endianness == 'little':
                    return "\t\t\t LESignedIntField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 
                elif field.domain.dataType.sign == 'signed' and field.domain.dataType.endianness == 'big':
                    return "\t\t\t SignedIntField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 
                elif field.domain.dataType.sign == 'unsigned' and field.domain.dataType.endianness == 'big':
                    return "\t\t\t IntField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 

        # Integer unitSize_64 signed unsigned and endianness
        def integer_unitSize_64(self,field):
                if field.domain.dataType.sign == 'unsigned' and field.domain.dataType.endianness == 'little':
                    return "\t\t\t LELongField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size) 
                elif field.domain.dataType.sign == 'unsigned' and field.domain.dataType.endianness == 'big':
                    return "\t\t\t LongField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer)
                                   if (field.domain.currentValue) else None)\
                           + "),"+ "\t#size:" +str(field.domain.dataType.size)
                else:
                    return "\t\t\t BitField(" + "\"" + field.name + "\"," \
                           + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer,dst_unitSize=AbstractType.defaultUnitSize())
                                   if (field.domain.currentValue) else None) \
                           + "," + repr(field.domain.dataType.size[1]) + ")," + "\t#size:" \
                           + str(field.domain.dataType.size)  
     

        # Integer dataType
        def dataType_integer(self, field):
                switcher = {
                        '8'   : self.integer_unitSize_8,
                        '16'  : self.integer_unitSize_16,                
                        '32'  : self.integer_unitSize_32,
                        '64'  : self.integer_unitSize_64
                }
                return switcher.get(field.domain.dataType.unitSize, self.integer_unitSize_8)(field)

        # TimeStamp dataType
        def dataType_timestamp(self, field):
                return "\t\t\t TimeStampField(" + "\"" + field.name + "\"," \
                       + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Timestamp) if
                               (field.domain.currentValue) else None)\
                       + "),"+ "\t#size:" +str(field.domain.dataType.size) 

        # IPv4 dataType
        def dataType_ipv4(self, field):
                return "\t\t\t IPField(" + "\"" + field.name + "\"," \
                       + repr(TypeConverter.convert(field.domain.currentValue,BitArray,IPv4) if
                               (field.domain.currentValue) else None)\
                       + "),"+ "\t#size:" +str(field.domain.dataType.size)           

        # Raw, BitArray, HexaString and ASCII dataTypes
        def dataType_raw(self, field):
                return "\t\t\t BitField(" + "\"" + field.name + "\"," \
                       + repr(TypeConverter.convert(field.domain.currentValue,BitArray,Integer,dst_unitSize=AbstractType.defaultUnitSize())
                               if (field.domain.currentValue) else None) \
                       + "," + str(self.__reFieldLengths[field]) + ")," + "\t#size:" \
                       + str(field.domain.dataType.size)
                    # replace line -2 by the following one when domain.dataType.size-"bug" is fixed
                    # + "," + repr(field.domain.dataType.size[1]) + ")," + "\t#size:" \

        # check dataType of the field
        def check_dataType(self,field):
                # Workaround for empty Netzob fields which erroneously receive a maximum size of 8 bits
                if max([len(f6v) for f6v in field.getValues()]) == 0:
                    return '' # return an empty string to effectively skip this field
                switcher = {
                        'Integer'   : self.dataType_integer,
                        'Timestamp' : self.dataType_timestamp,
                        'IPv4'      : self.dataType_ipv4
                }
                return switcher.get(field.domain.dataType.typeName, self.dataType_raw)(field)
