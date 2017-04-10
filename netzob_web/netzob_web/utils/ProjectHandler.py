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

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob_web.utils.Project import Project
from netzob_web.utils import Serializer

class ProjectHandler(object):

    def __init__(self, project_id):
        self.project_id = project_id

        self.__load_project()

    def __load_project(self):
        self.__project = Project("Project {}".format(self.project_id))

    def __save_project(self):
        pass
    #
    # Symbols
    #
        
    def get_symbols(self, limit, offset):
        return [Serializer.symbol_to_json(symbol) for symbol in self.__project.get_symbols(limit, offset)]

    def add_symbol(self, name):

        if name is None:
            raise ValueError("A name must be specified")

        name = str(name).strip()
        if len(name) == 0:
            raise ValueError("A name must be specified")
        
        x = Serializer.symbol_to_json(self.__project.create_symbol(name = name))
        return x

    def get_symbol(self, sid):
        if sid is None:
            raise ValueError("A SID must be specified")

        sid = str(sid).strip()
        if len(sid) == 0:
            raise ValueError("A SID must be specified")
            
        return Serializer.symbol_to_json(self.__project.get_symbol(sid = sid))
    
    def update_symbol(self, sid, name, description):
        if sid is None:
            raise ValueError("A SID must be specified")

        sid = str(sid).strip()
        if len(sid) == 0:
            raise ValueError("A SID must be specified")

        if name is not None:
            name = str(name).strip()
            if len(name) == 0:
                raise ValueError("A non-empty name must be specified")
        if description is not None:
            description = str(description).strip()
            
        return Serializer.symbol_to_json(self.__project.update_symbol(sid = sid, name = name, description = description))
        
    def delete_symbol(self, sid):
        if sid is None:
            raise ValueError("A SID must be specified")

        sid = str(sid).strip()
        if len(sid) == 0:
            raise ValueError("A SID must be specified")
            
        return self.__project.delete_symbol(sid = sid)

    def specialize_symbol(self, sid):
        if sid is None:
            raise ValueError("A SID must be specified")

        sid = str(sid).strip()
        if len(sid) == 0:
            raise ValueError("A SID must be specified")

        return str(self.__project.specialize_symbol(sid = sid))
        
    def get_symbol_cells(self, sid):
        if sid is None:
            raise ValueError("A SID must be specified")

        sid = str(sid).strip()
        if len(sid) == 0:
            raise ValueError("A SID must be specified")

        return Serializer.matrixlist_to_json(self.__project.get_symbol_cells(sid = sid))

    def get_symbol_messages(self, sid, limit, offset):
        if sid is None:
            raise ValueError("A SID must be specified")

        sid = str(sid).strip()
        if len(sid) == 0:
            raise ValueError("A SID must be specified")

        return [Serializer.message_to_json(message) for message in self.__project.get_symbol_messages(sid = sid, limit = limit, offset = offset)]

    def remove_message_from_symbol(self, sid, mid):
        if sid is None:
            raise ValueError("A SID must be specified")

        sid = str(sid).strip()
        if len(sid) == 0:
            raise ValueError("A SID must be specified")

        if mid is None:
            raise ValueError("A MID must be specified")

        mid = str(mid).strip()
        if len(mid) == 0:
            raise ValueError("A MID must be specified")

        return self.__project.remove_message_from_symbol(sid = sid, mid = mid)

    def add_message_in_symbol(self, sid, mid):
        if sid is None:
            raise ValueError("A SID must be specified")

        sid = str(sid).strip()
        if len(sid) == 0:
            raise ValueError("A SID must be specified")

        if mid is None:
            raise ValueError("A MID must be specified")

        mid = str(mid).strip()
        if len(mid) == 0:
            raise ValueError("A MID must be specified")

        return self.__project.add_message_in_symbol(sid = sid, mid = mid)
        
    def get_symbol_fields(self, sid, limit, offset):
        if sid is None:
            raise ValueError("A SID must be specified")

        sid = str(sid).strip()
        if len(sid) == 0:
            raise ValueError("A SID must be specified")

        return [Serializer.field_to_json(field) for field in self.__project.get_symbol_fields(sid = sid, limit = limit, offset = offset)]

    def remove_field_from_symbol(self, sid, fid):
        if sid is None:
            raise ValueError("A SID must be specified")

        sid = str(sid).strip()
        if len(sid) == 0:
            raise ValueError("A SID must be specified")

        if fid is None:
            raise ValueError("A FID must be specified")

        fid = str(fid).strip()
        if len(fid) == 0:
            raise ValueError("A FID must be specified")

        return self.__project.remove_field_from_symbol(sid = sid, fid = fid)

    def add_field_in_symbol(self, sid, fid, fid_before_new = None):
        if sid is None:
            raise ValueError("A SID must be specified")

        sid = str(sid).strip()
        if len(sid) == 0:
            raise ValueError("A SID must be specified")

        if fid is None:
            raise ValueError("A FID must be specified")

        fid = str(fid).strip()
        if len(fid) == 0:
            raise ValueError("A FID must be specified")

        return self.__project.add_field_in_symbol(sid = sid, fid = fid, fid_before_new = fid_before_new)

    def symbol_split_align(self, sid):
        if sid is None:
            raise ValueError("A SID must be specified")

        sid = str(sid).strip()
        
        if len(sid) == 0:
            raise ValueError("A SID must be specified")

        self.__project.symbol_split_align(sid = sid)
    #
    # Messages
    #
        
    def get_messages(self, limit, offset):
        return [Serializer.message_to_json(message) for message in self.__project.get_messages(limit, offset)]

    def get_message(self, mid):
        if mid is None:
            raise ValueError("A MID must be specified")

        mid = str(mid).strip()
        if len(mid) == 0:
            raise ValueError("A MID must be specified")
                
        return Serializer.message_to_json(self.__project.get_message(mid = mid))

    def add_message(self, cid, messageType, data, date = None, source = None, destination = None):

        if cid is None:
            raise ValueError("A CID must be specified")

        if messageType is None:
            raise ValueError("A messageType must be specified")
        
        if data is None:
            raise ValueError("A data must be specified")

        data = str(data).strip()
        if len(data) == 0:
            raise ValueError("A data must be specified")
        
        return Serializer.message_to_json(self.__project.create_message(cid = cid,
                                                                        messageType = messageType,
                                                                        data = data,
                                                                        date = date,
                                                                        source = source,
                                                                        destination = destination))
    def delete_message(self, mid):
        if mid is None:
            raise ValueError("A MID must be specified")

        mid = str(mid).strip()
        if len(mid) == 0:
            raise ValueError("A MID must be specified")

        return self.__project.delete_message(mid)
    
    #
    # Fields
    #
    def get_fields(self, limit, offset):
        return [Serializer.field_to_json(field) for field in self.__project.get_fields(limit, offset)]

    def get_field(self, fid):

        if fid is None:
            raise ValueError("A FID must be specified")

        fid = str(fid).strip()
        if len(fid) == 0:
            raise ValueError("A FID must be specified")
        
        return Serializer.field_to_json(self.__project.get_field(fid))
    
    def add_field(self, name, did):
        if name is None:
            raise ValueError("A name must be specified")

        name = str(name).strip()
        if len(name) == 0:
            raise ValueError("A name must be specified")
        
        if did is None:
            raise ValueError("A DID must be specified")

        did = str(did).strip()
        if len(did) == 0:
            raise ValueError("A DID must be specified")
                
        x = Serializer.field_to_json(self.__project.create_field(name = name, did = did))
        return x

    def delete_field(self, fid):
        if fid is None:
            raise ValueError("A FID must be specified")

        fid = str(fid).strip()
        if len(fid) == 0:
            raise ValueError("A FID must be specified")

        return self.__project.delete_field(fid)

    #
    # Domains
    #
    
    def get_domains(self, limit, offset):
        return [Serializer.domain_to_json(domain) for domain in self.__project.get_domains(limit, offset)]

    def get_domain(self, did):
        if did is None:
            raise ValueError("A DID must be specified")

        did = str(did).strip()
        if len(did) == 0:
            raise ValueError("A DID must be specified")
                
        return Serializer.domain_to_json(self.__project.get_domain(did = did))

    def create_domain_data(self, name, tid):
        if name is None:
            raise ValueError("A name must be specified")

        name = str(name).strip()
        if len(name) == 0:
            raise ValueError("A name must be specified")
        
        if tid is None:
            raise ValueError("A TID must be specified")

        tid = str(tid).strip()
        if len(tid) == 0:
            raise ValueError("A TID must be specified")

        return Serializer.domain_to_json(self.__project.create_domain_data(name = name, tid = tid))

    def create_domain_aggregate(self):
        return Serializer.domain_to_json(self.__project.create_domain_aggregate())
    
    def get_domains_in_aggregate(self, aid, limit, offset):
        if aid is None:
            raise ValueError("A AID must be specified")

        aid = str(aid).strip()
        if len(aid) == 0:
            raise ValueError("A AID must be specified")

        return [Serializer.domain_to_json(domain) for domain in self.__project.get_domains_in_aggregate(aid = aid, limit = limit, offset = offset)]

    def add_domain_in_aggregate(self, aid, did):
        if aid is None:
            raise ValueError("A AID must be specified")

        aid = str(aid).strip()
        if len(aid) == 0:
            raise ValueError("A AID must be specified")

        if did is None:
            raise ValueError("A AID must be specified")

        did = str(did).strip()
        if len(did) == 0:
            raise ValueError("A DID must be specified")

        return Serializer.domain_to_json(self.__project.add_domain_in_aggregate(aid = aid, did = did))

    def remove_domain_in_aggregate(self, aid, did):
        if aid is None:
            raise ValueError("A AID must be specified")

        aid = str(aid).strip()
        if len(aid) == 0:
            raise ValueError("A AID must be specified")

        if did is None:
            raise ValueError("A AID must be specified")

        did = str(did).strip()
        if len(did) == 0:
            raise ValueError("A DID must be specified")

        return Serializer.domain_to_json(self.__project.remove_domain_in_aggregate(aid = aid, did = did))    
   
    def delete_domain(self, did):
        if did is None:
            raise ValueError("A DID must be specified")

        did = str(did).strip()
        if len(did) == 0:
            raise ValueError("A DID must be specified")
        
        return self.__project.delete_domain(did = did)
        
    #
    # DataTypes
    #

    def get_datatypes(self, limit, offset):
        return [Serializer.datatype_to_json(domain) for domain in self.__project.get_datatypes(limit, offset)]

    def get_datatype(self, tid):
        if tid is None:
            raise ValueError("A TID must be specified")

        tid = str(tid).strip()
        if len(tid) == 0:
            raise ValueError("A TID must be specified")
                
        return Serializer.datatype_to_json(self.__project.get_datatype(tid = tid))

    def delete_datatype(self, tid):
        if tid is None:
            raise ValueError("A TID must be specified")

        tid = str(tid).strip()
        if len(tid) == 0:
            raise ValueError("A TID must be specified")
        
        return self.__project.delete_datatype(tid = tid)
    
    def create_type_ascii(self, value = None, nb_char_min = None, nb_char_max = None):
        return Serializer.datatype_to_json(self.__project.create_type_ascii(value = value,
                                                                            nb_char_min = nb_char_min,
                                                                            nb_char_max = nb_char_max))

    def create_type_raw(self, value = None, nb_byte_min = None, nb_byte_max = None):
        return Serializer.datatype_to_json(self.__project.create_type_raw(value = value,
                                                                          nb_byte_min = nb_byte_min,
                                                                          nb_byte_max = nb_byte_max))
    
                                                                                
    #
    # Captures
    #
        
    def get_captures(self, limit, offset):
        return [Serializer.capture_to_json(capture) for capture in self.__project.get_captures(limit, offset)]

    def get_capture(self, cid):
        if cid is None:
            raise ValueError("A CID must be specified")

        cid = str(cid).strip()
        if len(cid) == 0:
            raise ValueError("A CID must be specified")
                
        return Serializer.capture_to_json(self.__project.get_capture(cid = cid))

    def add_capture(self, name, date = None):

        if name is None:
            raise ValueError("A name must be specified")

        name = str(name).strip()
        if len(name) == 0:
            raise ValueError("A name must be specified")
        
        return Serializer.capture_to_json(self.__project.create_capture(name = name,
                                                                        date = date))
    def delete_capture(self, cid):
        if cid is None:
            raise ValueError("A CID must be specified")

        cid = str(cid).strip()
        if len(cid) == 0:
            raise ValueError("A CID must be specified")

        return self.__project.delete_capture(cid)
    
    def get_messages_in_capture(self, cid, limit, offset):

        if cid is None:
            raise ValueError("A CID must be specified")

        cid = str(cid).strip()
        if len(cid) == 0:
            raise ValueError("A CID must be specified")
        
        return [Serializer.message_to_json(message) for message in self.__project.get_capture(cid).messages[offset:offset+limit]] 

    #
    # Importers
    #
    def parse_pcap(self, filename, layer, pcap_content, bpf_filter = None):

        if filename is None or len(filename.strip()) == 0:
            raise ValueError("Filename cannot be None nor empty")

        if layer not in range(1,6):
            raise ValueError("Invalid import layer ({})".format(layer))

        if pcap_content is None or len(pcap_content) == 0:
            raise ValueError("PCAP file cannot be None nor empty")

        x = [Serializer.message_to_json(message) for message in self.__project.parse_pcap(filename = filename, layer = layer, pcap_content = pcap_content, bpf_filter = bpf_filter)]
        return x
                                           
    
    def parse_raw(self, filename, raw_content, delimiter = b"\n"):

        if filename is None or len(filename.strip()) == 0:
            raise ValueError("Filename cannot be None nor empty")

        if raw_content is None or len(raw_content) == 0:
            raise ValueError("RAW file cannot be None nor empty")

        x = [Serializer.message_to_json(message) for message in self.__project.parse_raw(filename = filename, delimiter = delimiter, raw_content = raw_content)]
        return x
                                           
    
