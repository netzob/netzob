#-*- coding: utf-8 -*-

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

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import uuid
import os
import json
import logging
import bitarray

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
import jsonpickle

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck


class UUIDJsonPickleHandler(jsonpickle.handlers.BaseHandler):
    """Handler used to process serialization of 'uuid' objects, as
    they are, by default, un-deserializable with jsonpickle.
    """

    def flatten(self, obj, data):
        data['hex'] = obj.get_hex()
        return data 

    def restore(self, data):
        return uuid.UUID(hex=data['hex'])

class BitarrayJsonPickleHandler(jsonpickle.handlers.BaseHandler):
    """Handler used to process serialization of 'uuid' objects, as
    they are, by default, un-deserializable with jsonpickle.
    """

    def flatten(self, obj, data):
        data['value01'] = obj.to01()
        return data 

    def restore(self, data):
        return bitarray.bitarray(data['value01'])

jsonpickle.handlers.registry.register(uuid.UUID, UUIDJsonPickleHandler)
jsonpickle.handlers.registry.register(bitarray.bitarray, BitarrayJsonPickleHandler)

class Serializer(object):
    """Class providing static methods for object serialization and
    deserialization. The current implementation relies on
    jsonpickle. As such, and for security reasons, important care
    should be taken when deserializing data from untrusted source.
    """

    @staticmethod
    def dump(obj):
        if obj is not None:
            return jsonpickle.encode(obj)
        else:
            logging.warn("Cannot serialize None.")
            return None

    @staticmethod
    @typeCheck(str)
    def restore(jsonString):
        # Check if the string has a valid JSON format
        try:
            json_object = json.loads(jsonString)
        except ValueError, e:
            logging.warn("The string has not a valid JSON format.")
            return None
        logging.warn("This is just a reminder that, for security reasons, important care should be taken when deserializing data from untrusted source !")
        return jsonpickle.decode(jsonString)

    @staticmethod
    @typeCheck(object, str)
    def dumpToFile(obj, aFile):
        if aFile is not None:
            jsonString = jsonpickle.encode(obj)
            try:
                fd = open(aFile, 'w')
                fd.write(jsonString)
                fd.close()
            except:
                logging.warn("Cannot write to file: {0}".format(str(aFile)))
                return None                
        else:
            logging.warn("This file is not reachable: {0}".format(str(aFile)))
            return None

    @staticmethod
    @typeCheck(str)
    def restoreFromFile(aFile):
        if aFile is not None and os.path.exists(aFile):
            fd = open(aFile, 'r')
            jsonString = fd.read()
            fd.close()

            # Check if this string has a valid JSON format
            try:
                json_object = json.loads(jsonString)
            except ValueError, e:
                logging.warn("The string has not a valid JSON format.")
                return None
            logging.warn("This is just a reminder that, for security reasons, important care should be taken when deserializing data from untrusted source !")
            return jsonpickle.decode(jsonString)
        else:
            logging.warn("This file is not reachable: {0}".format(str(aFile)))
            return None
