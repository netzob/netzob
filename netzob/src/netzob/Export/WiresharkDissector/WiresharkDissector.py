# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
# | Standard library imports
# +---------------------------------------------------------------------------+
import errno
from gettext import gettext as _
from operator import methodcaller
import re
import binascii
import random
# +---------------------------------------------------------------------------+
# | Related third party imports
# +---------------------------------------------------------------------------+


# +---------------------------------------------------------------------------+
# | Local application imports
# +---------------------------------------------------------------------------+
from netzob.Export.WiresharkDissector.CodeBuffer import LUACodeBuffer
from netzob.Model.Vocabulary.Messages.L2NetworkMessage import L2NetworkMessage
from netzob.Model.Vocabulary.Messages.L3NetworkMessage import L3NetworkMessage
from netzob.Model.Vocabulary.Messages.L4NetworkMessage import L4NetworkMessage
from netzob.Export.WiresharkDissector.WiresharkFilter import WiresharkFilterFactory
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Domain.Variables.Leafs import AbstractVariableLeaf
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Types.HexaString import HexaString
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger



@NetzobLogger
class WiresharkDissector(object):
    """ Usage: >>> WiresharkDissector.dissectSymbols(symbols,'outputFilename')
        or for single symbols
        Usage: >>> WiresharkDissector.dissectSymbol(symbol,'outputFilename')

        >>> from netzob.all import *
        >>> messages = PCAPImporter.readFile("./test/resources/pcaps/target_src_v1_session1.pcap").values()
        >>> symbols = Format.clusterByAlignment(messages)
        # Symbols need different Names in Wireshark
        >>> symbols[0].name = "Symbol_A"
        >>> symbols[1].name = "Symbol_B"
        >>> symbols[2].name = "Symbol_C"
        >>> WiresharkDissector.dissectSymbols(symbols,'./test/resources/test.lua')
        >>> f = open("./test/resources/test.lua",'r')
        >>> print(len(f.readlines()))
        204
    """

    def __init__(self):
        pass

    @typeCheck(AbstractField)
    def __getMessageContext(self, sym):
        '''
        This function prepares some important values in the format supported by LUA / Wireshark
        :param sym: Symbol
        :return Symbol specific values like name or id are extracted and prepared for the use in the LUA Code
        :rtype local variablels
        '''
        def clean(s):
            # Respect wireshark syntax.
            # Allowed are lower characters, digits, '-', '_' and '.'
            return re.sub("[^a-z\-_\.]", "_", str(s).lower())
        # sym = msg.getSymbol()
        msg = sym.messages[0]
        proto_name = clean(sym.name)
        proto_keyname = proto_name.upper()
        proto_desc = "{} Protocol".format(proto_name.capitalize())
        class_var = "proto_{}".format(str(msg.id).replace('-', '_'))
        if isinstance(msg, L4NetworkMessage):
            filter_name = msg.l4Protocol
        elif isinstance(msg, L3NetworkMessage):
            filter_name = msg.l3Protocol
        elif isinstance(msg, L2NetworkMessage):
            filter_name = msg.l2Protocol
        else:
             self._logger.error("Cannot find a compatible protocol for {}.".format(msg))

        del msg
        # Returns all local values as dict
        return locals()

    @typeCheck(list)
    def __findShortestUniqueIdentifier(self, symbols):
        '''
        Finds the shortest substrings of a Symbol to identify it from other symbols.
        It basically searches for the first n bytes of a symbols messages to be diffrent from every other first n-bythes in other
        symbols
        :param symbols:
        :return: shortestUniqueIndetifer : List of Lists with the shortest unique identifiers per symbol
        :rtype List
        '''
        found = False
        i = 1
        while not found:
            # Generate List of Lists with the first i-th bytes of the messages
            list = []
            for s in symbols:
                msg_list = []
                for m in s.messages:
                    msg_list.append(m.data[:i])
                list.append(msg_list)

            # search for ever identifier in every list for every symbol if its unique or not
            for msg_list in list:
                list.remove(msg_list)
                for m in msg_list:
                    for other_msg_list in list:
                        # if an identifier is found in an others symbol identifier list besides its own:
                        # break and search with a longer identifier
                        if m in other_msg_list:
                            i = i + 1
                            break  # Break through all for loop layers to the while-loop
                        else:
                            continue
                    else:
                        continue
                    break
                else:
                    continue
                break
            else:
                found = True
        shortestUniqueIndetifer = []
        for s in symbols:
            msg_list = []
            for m in s.messages:
                msg_list.append(m.data[:i])
            shortestUniqueIndetifer.append(msg_list)
        return shortestUniqueIndetifer

    @typeCheck(AbstractVariableLeaf, str)
    def __getDataRepresentation(self, domain, dataType=None):
        '''
        Concatenates a string containing a valid LUA function call for a casting / data-representation function
        :param domain: Data or a Size Object:
        :type  netzob.Model.Vocabulary.Domain.Variables.Leafs.Data.Data
        :param dataType: a string containing the LUA function for casting. This is used in case its a size Field and
        one wants to force the data-representation to be int and not raw
        :return: Sting: representing the Data-representation for the buffer in LUA
        :rtype string
        '''
        # Dictionaries for the translation from the Netzob type model to the LUA types
        sign_switcher = {
            'signed': '',
            'unsigned': 'u',
        }
        endianness_switcher = {
            'big': '',
            'little': 'le_',
        }
        dataType_switcher = {
            'Raw': '',
            'BitArray': 'bytes()',
            'String': 'string()',
            'Integer': 'int()',
            'HexaString': 'bytes()',
            'IPv4': 'ipv4()',
            'Timestamp': 'nstime()'
        }

        # In case the data type is determined by the caller
        if dataType is None:
            dataType = dataType_switcher.get(domain.dataType.typeName, '')

        # Different special cases to distinguish between.
        if domain.dataType.typeName in ['Integer', 'String']:
            sign = sign_switcher.get(domain.dataType.sign, '')
        else:
            sign = ''

        if domain.dataType.typeName in ['Integer', 'IPv4', 'Timestamp']:
            endian = endianness_switcher.get(domain.dataType.endianness, '')
        else:
            endian = ''

        if domain.dataType.typeName == 'Integer' and int(domain.dataType.unitSize) >= 32:
            dataRep = ':'+endian + sign + dataType[:-2] + '64()'
        elif endian + sign + dataType == '':
            dataRep = ''
        else:
            dataRep = ':'+endian + sign + dataType
        return dataRep

    @typeCheck(LUACodeBuffer, AbstractField, list, dict)
    def __writeDynSizeBlock(self, buf, field, sorted_ivalues, size_field_data=None):
        '''
        Writes a block of LUA Code for Fields with dynamic field length
        :param buf: The LUA Code Buffer
        :param field: The current field, to write the LUA code for
        :param sorted_ivalues: a List of values of this field, to later search for while dissecting the protocol and
        determining the length
        :param size_field_data: a dictionary with information for Size fields. If present it is a Size field,
        if not it is no size Field
        :return: Output is writen to the passed buffer object. No return value
        '''
        # decision if this is a size field
        if size_field_data is not None:
            data_representation = self.__getDataRepresentation(field.domain, dataType='uint()')
        else:
            data_representation = self.__getDataRepresentation(field.domain)
        with buf.new_block("do"):
            # List with values from Netzob
            buf << "local values = {{{}}}"\
                .format(", ".join('"{}"'.format(val) for val in sorted_ivalues))
            with buf.new_block("for k,v in next,values,nil do"):
                buf << "local vlen = v:len() / 2"
                # Search for every list element in the protocol and determine the length in the process
                with buf.new_block("if buffer(idx):len() >= vlen and tostring(ByteArray.new(v)) == tostring(buffer(idx,vlen):bytes()) then"):
                    # Handling if its a Size field
                    if size_field_data is not None:
                        buf << 'size_{target_nr} = (buffer(idx,vlen){data_rep} - {offset})*{factor}' \
                            .format(data_rep=data_representation, **size_field_data)
                        buf << 'subtree:add(buffer(idx,vlen), "Size of {prefix}: " .. size_{target_nr})' \
                            .format(prefix=size_field_data['target_name'],
                                    target_nr=size_field_data['target_nr'])
                    # Handling if its no Size Field
                    else:
                        buf << 'subtree:add(buffer(idx,vlen), "{prefix}: " .. tostring(buffer(idx,vlen){data_rep}))'\
                            .format(prefix=field.name, data_rep=data_representation)
                    buf << "idx = idx + vlen"
                    buf << "break"

    @typeCheck(LUACodeBuffer, AbstractField, list, dict)
    def __writeUniqueSizeBlock(self, buf, field, values, size_field_data=None):
        '''
        Writes a block of LUA Code for Fields with static field length
        :param buf: The LUA Code Buffer
        :param field: The current field, to write the LUA code for
        :param values: Values of the field. Only for determining the length of the field
        :param size_field_data: a dictionary with information for Size fields. If present it is a Size field,
        if not it is no size Field
        :return: Output is writen to the passed buffer object. No return value
        '''
        j = min(map(len, values))
        if size_field_data is not None:
            data_representation = self.__getDataRepresentation(field.domain, dataType='uint()')
        else:
            data_representation = self.__getDataRepresentation(field.domain)
        with buf.new_block("if buffer(idx):len() >= {} then".format(j)):
            # Handling if its a Size field
            if size_field_data is not None:
                buf << 'size_{target_nr} = (buffer(idx,{length}){data_rep} - {offset})*{factor}' \
                    .format(length=j, data_rep=data_representation, **size_field_data)
                buf << 'subtree:add(buffer(idx,{length}), "Size of {prefix}: " .. size_{target_nr})' \
                    .format(length=j, prefix=size_field_data['target_name'], target_nr=size_field_data['target_nr'])
            # Handling if its no Size Field
            else:
                buf << 'subtree:add(buffer(idx,{length}), "{prefix}: " .. tostring(buffer(idx,{length}){data_rep}))'\
                    .format(length=j, prefix=field.name, data_rep=data_representation)
            buf << "idx = idx + {}".format(j)

    @typeCheck(LUACodeBuffer, AbstractField, list, int)
    def __writeSizeFieldDependentBlock(self, buf, field, target_nr):
        '''
        Writes a block of LUA Code for Fields which depend on a size field
        :param buf: The LUA Code Buffer
        :param field: The current field, to write the LUA code f
        :param target_nr: Number of this field. It is imported because a size variable in Lua is named with this number
        :return: Output is writen to the passed buffer object. No return value
        '''
        data_representation = self.__getDataRepresentation(field.domain)
        with buf.new_block("if buffer(idx):len() >= size_{} then".format(target_nr)):
                buf << 'subtree:add(buffer(idx,size_{target_nr}), "{prefix}: " .. tostring(buffer(idx,size_{target_nr}){data_rep}))' \
                    .format(target_nr=target_nr, prefix=field.name, data_rep=data_representation)
                buf << "idx = idx + size_{}".format(target_nr)

    @typeCheck(list)
    def __writeHeuristicDissector(self,symbols):
        """
        Writes a heuristic dissector to determin from the first n Bytes of a message which Symbol / message type it is.
        :param symbols: List of Symbols
        :return: A Tuple with the string containing the Code for the heuristic dissector and the name of the dissector
        :rtype Tuple of two Strings
        """
        uniqueIdentifier = self.__findShortestUniqueIdentifier(symbols)
        buf = LUACodeBuffer()
        buf << "--\n-- Symbol Heuristic Dissector\n--\n"

        # Every protcol is revered by name in Netzob. If more than one heuristic Dissector from Netzob is used in
        # Wireshark a name collision occurres. This is why the name of the heuristic dissector is randomised.
        random.seed()
        r = random.randint(1, 1000000)
        heur_dissector_name = 'heuristic_dissector_{randomness}'.format(randomness=r)
        buf << '''{dissector_name} = Proto("{dissector_name}", "{dissector_name} Protocol")'''.format(dissector_name=heur_dissector_name)
        with buf.new_block('function {dissector_name}.dissector(buffer, pinfo, tree)'.format(dissector_name=heur_dissector_name)):
            for i,uid_list in enumerate(uniqueIdentifier):
                # Get Hex-Values from the UIDs
                hex_values = []
                for v in uid_list:
                    hex_values.append(HexaString.encode(v, AbstractType.defaultUnitSize,
                                                        AbstractType.defaultEndianness,
                                                        AbstractType.defaultSign))
                sorted_UIDs = sorted(set(str(v)[2:-1] for v in hex_values if v), key=len, reverse=True)
                del hex_values

                ctx = self.__getMessageContext(symbols[i])

                # List with the first n bytes which happen to be unique for this symbol
                buf << "local values = {{{}}}" \
                    .format(", ".join('"{}"'.format(val) for val in sorted_UIDs))
                buf << 'local match = false'
                with buf.new_block("for k,v in next,values,nil do"):
                    buf << "local vlen = v:len() / 2"
                    # if one of the values from the list matches => dissect the packet with the corresponding dissector.
                    with buf.new_block(
                "if buffer(0):len() >= vlen and tostring(ByteArray.new(v)) == tostring(buffer(0,vlen):bytes()) then"):
                            buf << '{class_var}.dissector(buffer, pinfo, tree)'.format(**ctx)
                            buf << 'match = false'
            # if nothing matches dissect the packet with the last added dissector
            with buf.new_block('if match == true then'):
                buf << "{class_var}.dissector(buffer, pinfo, tree)".format(**ctx)

        return (heur_dissector_name, buf.getvalue())

    @typeCheck(list, str)
    def __writeDissectorRegistration(self, symbols, dissector_name):
        """
        Writes the LUA Code for registering the passed dissector_name in Wireshark. Binds the dissector to a specified
        port / network address
        :param symbols: List of Symbols
        :param dissector_name: Name of the dissector to be registered
        :return: String conating the LUA code
        :rtype: String
        """
        # Register dissector function to specific filter criterion
        filter_set = set()
        buf = LUACodeBuffer()
        #  For the case that the same address / port is used by multiple messages, the duplicates get filtered out
        for sym in symbols:
            filter_ = WiresharkFilterFactory.getFilter(sym)
            luatype = self.__getLuaTableType(filter_.pytype)
            for expr in filter_.getExpressions():
                filter_set.add((str(expr[0]),str(expr[1]),str(luatype)))
        for exp_0,exp_1,type in filter_set:
            buf << """if not pcall(DissectorTable.get, "{exp_0}") then
                      DissectorTable.new("{exp_0}", "Netzob-generated table", {type})
                    end
                    DissectorTable.get("{exp_0}"):add({exp_1}, {class_var})
        """.format(exp_0=exp_0,exp_1=exp_1, type=type, class_var=dissector_name)
        return buf.getvalue()

    @typeCheck(AbstractField)
    def __dessect_raw(self, sym):
        """
        Writes a dissector for a RAW / binary-based Protocol
        :param sym: Symbol
        :return: String containing the LUA Code
        """
        # msgs = sym.messages
        ctx = self.__getMessageContext(sym)
        buf = LUACodeBuffer()
        # Head of the dissector
        buf << "--\n-- Symbol {proto_keyname}\n--\n".format(**ctx)
        buf << """{class_var} = Proto("{proto_name}", "{proto_name} Protocol")
        function {class_var}.dissector(buffer, pinfo, tree)
          pinfo.cols.protocol = "{proto_keyname}"
          local subtree = tree:add({class_var}, buffer(), "{proto_desc}")
          local idx = 0
        """.format(**ctx)

        fields = sym.getLeafFields()

        # Find Size-Relation in the Fields
        size_relation = dict()
        for i, field in enumerate(fields):
            if field.domain.varType == 'Size':
                if len(field.domain.fieldDependencies) == 1:
                    target_field = field.domain.fieldDependencies[0]
                    size_data = dict()
                    size_data['target_nr'] = fields.index(target_field)
                    size_data['target_name'] = target_field.name
                    size_data['factor'] = float(1)/field.domain.factor/8.0
                    size_data['offset'] = field.domain.offset
                    size_relation[i] = size_data
                    #size_relation[fields.index(target_field)] = size_data
                else:
                    self._logger.error("Can't handle Size-Field which revere to more than one Field: {}"
                                       .format(field.name))
        # write the LUA Code for every field
        with buf.new_block():
            for i,field in enumerate(fields):
                ivalues = field.getValues(encoded=False, styled=False)
                hex_values = []
                for v in ivalues:
                    hex_values.append(HexaString.encode(v, field.domain.dataType.unitSize, field.domain.dataType.endianness, field.domain.dataType.sign))

                sorted_ivalues = sorted(set(str(v)[2:-1] for v in hex_values if v), key=len, reverse=True)
                del hex_values

                # Get the relevant size relation data for this field if existing
                if i in size_relation.keys():
                    size_field_data = size_relation[i]
                else:
                    size_field_data = None

                # Write size-dependent field
                relation_found = False
                for size_data in size_relation.values():
                    if size_data['target_nr'] == i:
                        self.__writeSizeFieldDependentBlock(buf, field, size_data['target_nr'])
                        relation_found = True

                # Write fields without size field
                if relation_found == False:
                    if len(set(map(len, ivalues))) > 1:
                        self.__writeDynSizeBlock(buf, field, sorted_ivalues,size_field_data)
                    else:
                        self.__writeUniqueSizeBlock(buf, field, ivalues,size_field_data)
        return buf.getvalue()


    @typeCheck(AbstractField)
    def __dessect_text(self, sym):
        """
        Writes a dissector for a text-based Protocol
        :param sym: Symbol
        :return: Sting containing the LUA Code
        """
        ctx = self.__getMessageContext(sym)
        buf = LUACodeBuffer()

        # Head of the dissector
        buf << "--\n-- Symbol {proto_keyname}\n--\n".format(**ctx)
        buf << """{class_var} = Proto("{proto_name}", "{proto_name} Protocol")
        function {class_var}.dissector(buffer, pinfo, tree)
          pinfo.cols.protocol = "{proto_keyname}"
          local subtree = tree:add({class_var}, buffer(), "{proto_desc}")
          local idx = 0
          local len = buffer(idx):len()
        """.format(**ctx)

        # Some special handling for the data type of the Text in the protocol
        sign_switcher = {
            'signed': '',
            'unsigned': 'u',
        }
        endianness_switcher = {
            'big': '',
            'little': 'le_',
        }
        sym.fields[0].domain.dataType.sign
        sign = sign_switcher.get( sym.fields[0].domain.dataType.sign, '')
        if sign == 'u':
            endian = endianness_switcher.get( sym.fields[0].domain.dataType.endianness, '')
        else:
            endian = ''
        data_rep = ':'+endian+sign+'string()'

        # Due to a limitation in Wireshark the Text is splitted in blocks of 239 Bytes. (240 bytes are truncated)
        with buf.new_block():
            with buf.new_block("while buffer(idx):len() >0 do"):
                buf << "local remaining_len = buffer(idx):len()"
                with buf.new_block("if remaining_len >= 239 then"):
                    buf << 'subtree:add(buffer(idx, 239), tostring(buffer(idx,239){data_rep}))' \
                        .format(data_rep=data_rep)
                    buf << "idx = idx + 239"
                    buf << "else"
                    buf << 'subtree:add(buffer(idx, remaining_len), tostring(buffer(idx,remaining_len){data_rep}))' \
                        .format(data_rep=data_rep)
                    buf << "idx = idx + remaining_len"

        return buf.getvalue()


    @staticmethod
    def __getLuaTableType(pytype):
        if issubclass(pytype, (int)):
            return 'ftypes.UINT32'
        if issubclass(pytype, str):
            return 'ftypes.STRING'
        raise ValueError("Cannot match LUA type for {!s}".format(pytype))

    @staticmethod
    @typeCheck(list, str)
    def dissectSymbols(symbols, fname):
        """
        The user method for generating the LUA code representing the wireshark dissector for the passed symbols.
        The output is in file, named like the passed fname parameter, relative to the current working directory.
        :param symbols: List of Symbols
        :param fname: Sting with the name of the File
        :return: No return value
        """
        dissector = WiresharkDissector()
        text_based = True
        symbol_dissector = ''

        for sym in symbols:
            for leaf in sym.getLeafFields():
                if not isinstance(leaf.domain.dataType, String):
                    text_based = False
                    break
            if text_based:
                #print('Text Dissector')
                symbol_dissector = symbol_dissector + dissector.__dessect_text(sym) + '\n\n\n'
            else:
                #print('Binary Dissector')
                symbol_dissector = symbol_dissector + dissector.__dessect_raw(sym) + '\n\n\n'

        # If there is more than one symbol a heuristic is needed to determ which symbol is used for the dissection

        if len(symbols) > 1:
            heur_dissector_name, heur_dissector = dissector.__writeHeuristicDissector(symbols)
            symbol_dissector = symbol_dissector + heur_dissector + '\n\n\n'
        else:
            ctx = dissector.__getMessageContext(symbols[0])
            heur_dissector_name = '{class_var}'.format(**ctx)
        # Register the heuristic dissector or if not existened the dissector for the only symbol
        symbol_dissector = symbol_dissector + dissector.__writeDissectorRegistration(symbols, heur_dissector_name) + '\n\n\n'

        with open(fname, 'w') as f:
            f.write(symbol_dissector)

    @staticmethod
    @typeCheck(AbstractField, str)
    def dissectSymbol(sym, fname):
        """
        The user method for generating the LUA code representing the wireshark dissector for the passed symbol.
        The output is in file, named like the passed fname parameter, relative to the current working directory.
        :param sym: Symbol
        :param fname: Sting with the name of the File
        :return: No return value
        """
        dissector = WiresharkDissector()
        return dissector.dissectSymbols([sym], fname)

