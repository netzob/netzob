#!/usr/bin/env python
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
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger

@NetzobLogger
class WiresharkExporter(object):

    def __init__(self):
        pass

    @typeCheck(list,str)
    def export_to_wireshark(self,symbols,dest_file,port,TCP=True):
        """
        Exports a List of netzob symbols to a wireshark lua dissector.
        Run wireshark likeso: wireshark -X lua_script:<my_script.lua>

        Args:
            symbols: A list of symbols
            dest_file: A string which is a path to the destination file the file must be .lua
            port: An int destination port(server port, not client)
            TCP: A boolean set True for TCP protocol False for UDP (True by default)

        """
        file = open(dest_file, 'w')
        buffer0 = 'local protocol = Proto("' + 'myprotocol' + '","' + 'MyProtocol' + '")' + '\n'
        buffer1 = ''
        for i, sym in enumerate(symbols):
            for j, field in enumerate(sym.fields):
                buffer1 += 'protocol.fields.field_' + str(i) + '_' + str(
                    j) + ' = ' 'ProtoField.bytes("myprotocol.' + field.name + '","' + field.name.upper() + '" ) \n'  # , ftypes.BYTES )' + '\n'

        buffer2 = 'function protocol.dissector(buf, pinfo, tree)' + '\n'
        buffer3 = 'local subtree = tree:add( protocol, buf() )' + '\n'
        buffer = buffer0 + buffer1 + buffer2 + buffer3
        for i, sym in enumerate(symbols):

            # Create tree for a symbol of size N (fixed size, variable size=not supported yet)
            buffer4 = 'if buf:len() == ' + str(len(sym.getValues()[0])) + ' then' + '\n'
            buffer += buffer4
            base_len = 0
            for j, field in enumerate(sym.fields):
                try:
                    buffer5 = 'subtree:add( protocol.fields.field_' + str(i) + '_' + str(j) + ',buf(' + str(
                        int(field.domain.dataType.size[0] / 8) + base_len) + ',' + str(
                        int(field.domain.dataType.size[1] / 8)) + '))' + "\n"
                    base_len += int(field.domain.dataType.size[1] / 8)
                except:
                    buffer5 = 'subtree:add(protocol.fields.field_' + str(i) + '_' + str(j) + ',buf(' + str(
                        int(field.domain.children[0].dataType.size[0] / 8) + base_len) + ',' + str(
                        int(field.domain.children[0].dataType.size[1] / 8)) + '))' + "\n"
                    base_len += int(field.domain.children[0].dataType.size[1] / 8)
                buffer += buffer5
            buffer += 'end\n'
        buffer += 'end\n'
        if TCP:
            buffer += 'tcp_table = DissectorTable.get("tcp.port")' + '\n'
            buffer += 'tcp_table: add('+str(port)+', protocol)' + '\n'
        else:
            buffer += 'udp_table = DissectorTable.get("udp.port")' + '\n'
            buffer += 'udp_table: add('+str(port)+', protocol)' + '\n'
        file.write(buffer)
        file.close()