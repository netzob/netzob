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
from netzob.Model.Vocabulary.Types.ASCII import ASCII
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import Agg

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
def symbol_to_json(symbol):
    return {
        "id": str(symbol.id),
        "name": symbol.name,
        "description": symbol.description,
        "messages": [ str(message.id) for message in symbol.messages ],
        "fields": [ str(field.id) for field in symbol.fields ]
    }

def capture_to_json(capture):
    return {
        "id": str(capture.id),
        "name": capture.name,
        "date": capture.date,
        "messages": [ str(message.id) for message in capture.messages ]
    }


def message_to_json(message):
    return {
        "id": str(message.id),
        "messageType": str(message.messageType),
        "date": str(message.date),
        "source": str(message.source),
        "destination": str(message.destination),        
        "data": message.data.decode('unicode_escape')
    }

def field_to_json(field):
    return {
        "id": str(field.id),
        "name": str(field.name),
        "domain": str(field.domain.id)
    }

def domain_to_json(domain):
    if isinstance(domain, Data):
        return data_domain_to_json(domain)
    elif isinstance(domain, Agg):
        return aggregate_domain_to_json(domain)
    else:
        raise Exception("Unsupported domain type")

def data_domain_to_json(data_domain):
    return {
        "id": str(data_domain.id),
        "type": "DATA",
        "name": str(data_domain.name),
        "type_id": str(data_domain.dataType.id)
    }

def aggregate_domain_to_json(aggregate_domain):
    return {
        "id": str(aggregate_domain.id),
        "type": "AGGREGATE",
        "children": [str(child.id) for child in aggregate_domain.children]        
    }

def datatype_to_json(datatype):
    if isinstance(datatype, ASCII):
        return ascii_datatype_to_json(datatype)
    elif isinstance(datatype, Raw):
        return raw_datatype_to_json(datatype)
    else:
        raise Exception("Unsupported data type ({})".format(type(datatype)))

def ascii_datatype_to_json(ascii_type):
    return {
        "id": str(ascii_type.id),
        "type": "ASCII",
        "value": ascii_type.value,
        "nb_chars_min": ascii_type.nbChars[0],
        "nb_chars_max": ascii_type.nbChars[1]
    }

def raw_datatype_to_json(raw_type):
    return {
        "id": str(raw_type.id),
        "type": "RAW",
        "value": raw_type.value,
        "nb_bytes_min": raw_type.size[0],
        "nb_bytes_max": raw_type.size[1]
    }

def matrixlist_to_json(matrixlist):

    columns = [{"name": header} for header in matrixlist.headers]

    rows = []
    for cell in matrixlist:
        rows.append({"items": [{"data": str(data)[2:-1]} for data in cell]})

    result = {
        "columns": columns,
        "rows": rows,
    }
    return result
