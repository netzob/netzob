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
# | File contributors :                                                       |
# |       - Georges Bossert <gbossert (a) miskin.fr>                          |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
import collections
import shutil
from tempfile import mkdtemp
import os
import time

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import Agg
from netzob.Model.Vocabulary.Types.ASCII import ASCII
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Inference.Vocabulary.Format import Format
from netzob.Inference.Vocabulary.FormatOperations.FieldSplitAligned.FieldSplitAligned import FieldSplitAligned
from netzob.Import.PCAPImporter.PCAPImporter import PCAPImporter
from netzob.Import.FileImporter.FileImporter import FileImporter


# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob_web.utils.Capture import Capture

@NetzobLogger
class Project(object):

    PROJECTS = {    }
    
    def __init__(self, name):
        self.name = name

        self.__symbols = collections.OrderedDict()
        self.__messages = collections.OrderedDict()
        self.__fields = collections.OrderedDict()
        self.__domains = collections.OrderedDict()
        self.__datatypes = collections.OrderedDict()
        self.__captures = collections.OrderedDict()        
        
    @staticmethod
    def get_project_by_name(project_name):
        if project_name not in Project.PROJECTS.keys():
            Project.PROJECTS[project_name] = Project(name = "Project {}".format(project_name))
        return Project.PROJECTS[project_name]

    #
    # Symbols
    #
    def get_symbols(self, limit, offset):
        return list(self.__symbols.values())[offset: offset + limit]

    def create_symbol(self, name):
        symbol = Symbol(name = name)
        self.__symbols[str(symbol.id)] = symbol

        for field in symbol.fields:
            self.__fields[str(field.id)] = field

            self.__domains[str(field.domain.id)] = field.domain

            self.__datatypes[str(field.domain.dataType.id)] = field.domain.dataType

        
        return symbol
    
    def get_symbol(self, sid):
        return self.__symbols[str(sid)]

    def update_symbol(self, sid, name, description):
        symbol = self.get_symbol(sid)
        if name is not None:
            symbol.name = name
        if description is not None:
            symbol.description = description
        return symbol
    
    def delete_symbol(self, sid):
        del self.__symbols[str(sid)]

    def specialize_symbol(self, sid):
        return self.get_symbol(sid).specialize()

    def get_symbol_cells(self, sid):
        return self.get_symbol(sid).getCells()

    def get_symbol_messages(self, sid, limit, offset):
        symbol = self.get_symbol(sid)
        return symbol.messages[offset: offset + limit]

    def remove_message_from_symbol(self, sid, mid):
        symbol = self.get_symbol(sid)
        new_message = []
        for message in symbol.messages:
            if str(message.id) != mid:
                new_message.append(message)

        symbol.messages = new_message

    def add_message_in_symbol(self, sid, mid):
        symbol = self.get_symbol(sid)
        message = self.get_message(mid)

        if message in symbol.messages:
            raise Exception("Message is already attached to the symbol")
        
        symbol.messages.append(message)

    def get_symbol_fields(self, sid, limit, offset):
        symbol = self.get_symbol(sid)
        return symbol.fields[offset: offset + limit]

    def remove_field_from_symbol(self, sid, fid):
        symbol = self.get_symbol(sid)
        new_fields = []
        for field in symbol.fields:
            if str(field.id) != fid:
                new_fields.append(field)

        symbol.fields = new_fields

    def add_field_in_symbol(self, sid, fid, fid_before_new = None):
        symbol = self.get_symbol(sid)
        field = self.get_field(fid)
        if field in symbol.fields:
            raise Exception("Field is already attached to the symbol")
        
        position_to_insert = 0
        if fid_before_new is not None:
            previous_field = self.get_field(fid_before_new)
            if previous_field not in symbol.fields:
                raise Exception("Previous field cannot be found")
            position_to_insert = symbol.fields.index(previous_field) + 1

        symbol.fields.insert(position_to_insert, field)

    def symbol_split_align(self, sid):
        symbol = self.get_symbol(sid)
        FieldSplitAligned(doInternalSlick=True).execute(symbol, True)
        
    #
    # Messages
    #
    def get_messages(self, limit, offset):
        return list(self.__messages.values())[offset: offset + limit]

    def get_message(self, mid):
        return self.__messages[str(mid)]

    def create_message(self, cid, messageType, data, date = None, source = None, destination = None):

        capture = self.__captures[str(cid)]
        message = RawMessage(data = data.encode('utf-8'), date = date, source = source, destination = destination)
        capture.messages.append(message)
        
        self.__messages[str(message.id)] = message
        return message

    def delete_message(self, mid):
        del self.__messages[str(mid)]

    #
    # Fields
    #
    def get_fields(self, limit, offset):
        return list(self.__fields.values())[offset: offset + limit]

    def get_field(self, fid):
        return self.__fields[str(fid)]

    def create_field(self, name, did):
        domain = self.get_domain(did)
        field = Field(name = name, domain = domain)
        self.__fields[str(field.id)] = field
        return field

    def delete_field(self, fid):
        del self.__fields[str(fid)]

    #
    # Domains
    #
    def get_domains(self, limit, offset):
        return list(self.__domains.values())[offset: offset + limit]

    def get_domain(self, did):
        return self.__domains[str(did)]

    def create_domain_data(self, name, tid):
        data_type = self.get_datatype(tid)
        data = Data(dataType = data_type, name = name)        
        self.__domains[str(data.id)] = data
        return data

    def create_domain_aggregate(self):
        aggregate = Agg()
        self.__domains[str(aggregate.id)] = aggregate
        return aggregate

    def get_domains_in_aggregate(self, aid, limit, offset):
        return self.__domains[str(aid)].children[offset: offset + limit]

    def add_domain_in_aggregate(self, aid, did):
        aggregate = self.__domains[str(aid)]
        domain = self.__domains[str(did)]
        aggregate.children.append(domain)

        return aggregate

    def remove_domain_in_aggregate(self, aid, did):
        aggregate = self.__domains[str(aid)]
        new_children = []
        for child in aggregate.children:
            if str(child.id) != str(did):
                new_children.append(child)

        aggregate.children = new_children
        return aggregate

    def delete_domain(self, did):
        del self.__domains[str(did)]

    #
    # DataTypes
    #
    def get_datatypes(self, limit, offset):
        return list(self.__datatypes.values())[offset: offset + limit]

    def get_datatype(self, tid):
        return self.__datatypes[str(tid)]

    def delete_datatype(self, tid):
        del self.__datatypes[str(tid)]

    def create_type_ascii(self, value = None, nb_char_min = None, nb_char_max = None):
        data_type = ASCII(value = value, nbChars=(nb_char_min, nb_char_max))
        self.__datatypes[str(data_type.id)] = data_type
        return data_type
    
    def create_type_raw(self, value = None, nb_byte_min = None, nb_byte_max = None):
        data_type = Raw(value = value, nbBytes=(nb_byte_min, nb_byte_max))
        self.__datatypes[str(data_type.id)] = data_type
        return data_type    
        
    #
    # Captures
    #
    def get_captures(self, limit, offset):
        return list(self.__captures.values())[offset: offset + limit]

    def get_capture(self, cid):
        return self.__captures[str(cid)]

    def create_capture(self, name, date = None):
        capture = Capture(name = name, date = date)
        self.__captures[str(capture.id)] = capture
        return capture

    def delete_capture(self, cid):
        del self.__captures[str(cid)]
    
    #
    # Project
    #


    #
    # Importers
    #
    def parse_pcap(self, filename, layer, pcap_content, bpf_filter = None):

        try:
            tmp_dir = mkdtemp()
            pcap_file = os.path.join(tmp_dir, "{}.{}".format(time.time(), filename))
            with open(pcap_file, "wb") as fd:
                fd.write(pcap_content)
            return PCAPImporter.readFile(pcap_file, bpfFilter = bpf_filter, importLayer = layer).values()

        finally:
            shutil.rmtree(tmp_dir)

    def parse_raw(self, filename, raw_content, delimiter = b"\n"):

        try:
            tmp_dir = mkdtemp()
            raw_file = os.path.join(tmp_dir, "{}.{}".format(time.time(), filename))
            with open(raw_file, "wb") as fd:
                fd.write(raw_content)
            return FileImporter.readFile(raw_file, delimitor = delimiter).values()

        finally:
            shutil.rmtree(tmp_dir)

            
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if name is None:
            raise TypeError("Name cannot be None")
        self.__name = name



