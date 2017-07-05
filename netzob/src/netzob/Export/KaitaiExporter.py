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
class KaitaiExporter(object):

    def __init__(self):
        pass

    @typeCheck(list,str)
    def export_to_kaitai(self,meta,application,symbols):
        """
        Exports a List of netzob symbols to a kaitai parsing script.
        For more info on kaitai, please visit http://kaitai.io/
        The messages of the symbols must have the file to be parsed as session name

        Args:
            symbols: A list of symbols
            dest_file: A string which is a path to the destination file the file must be .ksy
            port: An int destination port(server port, not client)
            TCP: A boolean set True for TCP protocol False for UDP (True by default)

        """
        #file = open(dest_file, 'w')

        #We are creating one parser per file => One parser per session
        #Hence we need to create a set of all sessions available
        sessions_list = []
        for symbol in symbols:
            for message in symbol.messages:
                sessions_list.append(message.session.name)
        sessions_set = set(sessions_list)
        for session in sessions_set:
            header_buffer = 'meta:\n id: ' + meta + '\n'
            header_buffer += ' application: ' + application + '\n'
            header_buffer += ' endian: ' + "le" + '\n'
            instances_buffer = 'instances:\n'
            types_buffer = "types:\n"
            #buffer3 = "enums:\n"
            in_file = open(session,"rb")
            out_file = open(session+".ksy","w")
            file_buffer = b""
            for line in in_file:
                file_buffer += line
            in_file.close()
            for symbol in symbols:
                for key,value in symbol.getMessageValues().items():
                    if key.session.name == session:
                        #We have the value of a message, let's get it's position in the file:
                        found = file_buffer.find(value)
                        #We add the types part for the kaitai script as each type corresponds to a symbol's message
                        types_buffer += ' ' + symbol.name.lower() + '_message_' + str(key.id).replace('-','').lower() + ':\n'
                        types_buffer += '  seq: \n'
                        #We set the instances in the instance buffer
                        instances_buffer += ' body_' + symbol.name.lower() + '_message_' + str(key.id).replace('-','').lower() + ':\n'
                        instances_buffer += '  type: ' + symbol.name.lower() + '_message_' + str(key.id).replace('-','').lower() + '\n'
                        instances_buffer += '  pos: ' + hex(found) + '\n'
                        for index,cell in enumerate(symbol.getMessageCells()[key]):
                            diff = len(symbol.getMessageCells()[key]) - len(symbol.fields)
                            if type(cell) == str:
                                continue
                            types_buffer += '   - id: ' + symbol.fields[index - diff].name.replace('-','').lower() + '\n'
                            contents_buffer = ""
                            for i in range(0, len(cell.hex()), 2):
                                contents_buffer += "0x" + cell.hex()[i:i+2] + ","
                            types_buffer += '     contents: [' + contents_buffer[:-1] + ']\n'
                    else:
                        continue
            buffer = header_buffer + instances_buffer + types_buffer
            out_file.write(buffer)
            out_file.close()


