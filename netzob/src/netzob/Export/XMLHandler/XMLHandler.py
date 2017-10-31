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
#| Standard library imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree, DocumentInvalid
from lxml import etree
import uuid
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Symbol import Symbol



SYMBOLS_NAMESPACE = "http://www.netzob.org/symbols"
COMMON_NAMESPACE = "http://www.netzob.org/common"

@NetzobLogger
class XMLHandler(object):
    """ The XML Handler provides methods for persisting a symbol and all included data structures.

        Usage for saving a List of Symbols in a XML-File:
            XMLHandler.saveToXML(symbols, filepath)

        Usage for loading it back and creating all the Python Objects based on the  provided XML File
            [symbols[0:-1], sessions[:]] = XMLHandler.loadFromXML(filePath)
            Returned are a list of all symbols, plus the sessions, which were linked to the messages of the symbols.

        >>> from netzob.all import *
        >>> messages = PCAPImporter.readFile("./test/resources/pcaps/target_src_v1_session1.pcap").values()
        >>> symbols = Format.clusterByAlignment(messages)
        >>> XMLHandler.saveToXML(symbols,'./test/resources/test.xml')
        >>> f = open("./test/resources/test.xml",'r')
        >>> print(len(f.readlines()))
        197

        # Testing if the loaded is the same as before.
        >>> from netzob.all import *
        >>> messages = PCAPImporter.readFile("./test/resources/pcaps/target_src_v1_session1.pcap").values()
        >>> symbols = Format.clusterByAlignment(messages)
        >>> XMLHandler.saveToXML(symbols,'./test/resources/test.xml')
        >>> restored = XMLHandler.loadFromXML('./test/resources/test.xml')
        >>> equal = False
        >>> if len(restored) == len(symbols):
        >>>     equal = True
        >>>     for i in range(len(restored)):
        >>>         if restored[i] != symbols[i]:
        >>>             equal = False
        >>> print(equal)
        True
    """
    unresolved_dict = dict()

    def __init__(self):
        pass

    @staticmethod
    @typeCheck(str, dict)
    def add_to_unresolved_dict(name, unresolved):
        if unresolved is not None and isinstance(unresolved, dict):
            if name not in XMLHandler.unresolved_dict.keys():
                XMLHandler.unresolved_dict[name] = dict()
            for key, value in unresolved.items():
                XMLHandler.unresolved_dict[name][key] = value

    @staticmethod
    @typeCheck(list, str)
    def saveToXML(symbols, filepath):
        '''
        Saves the List of Symbols to XML
        :return:
        '''
        # Register the namespace
        etree.register_namespace('netzob', SYMBOLS_NAMESPACE)
        etree.register_namespace('netzob-common', COMMON_NAMESPACE)


        # We generate the XML Config file

        root = etree.Element("{" + SYMBOLS_NAMESPACE + "}symbols")
        root.set('file-path', str(filepath))

        # Symbols
        for symbol in symbols:
            symbol.saveToXML(root, SYMBOLS_NAMESPACE, COMMON_NAMESPACE)
        # Sessions
        sessions = set()
        for symbol in symbols:
            for msg in symbol.messages:
                from netzob.Model.Vocabulary.Session import Session
                if msg.session is not None and isinstance(msg.session, Session):
                    sessions.add(msg.session)
        for session in sessions:
            session.saveToXML(root, SYMBOLS_NAMESPACE, COMMON_NAMESPACE)


        tree = ElementTree(root)

        tree.write(filepath, pretty_print=True)

    @staticmethod
    @typeCheck(str)
    def loadFromXML(filePath):
        xmlHandler = XMLHandler()
        tree = ElementTree()

        tree.parse(filePath)

        xmlroot = tree.getroot()

        etree.register_namespace('netzob', SYMBOLS_NAMESPACE)
        etree.register_namespace('netzob-common', COMMON_NAMESPACE)


        # Restore Symbols
        symbols = []
        for xmlSymbol in xmlroot.findall("{" + SYMBOLS_NAMESPACE + "}symbol"):
                symbol = Symbol.loadFromXML(xmlSymbol, SYMBOLS_NAMESPACE, COMMON_NAMESPACE)
                if symbol is not None:
                    symbols.append(symbol)
        # Restore Sessions
        sessions = []
        from netzob.Model.Vocabulary.Session import Session
        for xmlSymbol in xmlroot.findall("{" + SYMBOLS_NAMESPACE + "}session"):
            session = Session.loadFromXML(xmlSymbol, SYMBOLS_NAMESPACE, COMMON_NAMESPACE)
            if session is not None:
                sessions.append(session)

        # Handling of the delayed creation of some references
        if len(sessions) > 0:
            session_resolve_dict = dict()
            for s in sessions:
                session_resolve_dict[s.id] = session

        message_resolve_dict = dict()
        for sym in symbols:
            for msg in sym.messages:
                message_resolve_dict[msg.id] = msg

        field_resolve_dict = dict()
        for sym in symbols:
            for field in sym.getLeafFields():
                field_resolve_dict[field.id] = field


        for case, unresolved in XMLHandler.unresolved_dict.items():
            if case == 'session':
                pass
            elif case == 'fieldDependencies':
                for key, rel_field in unresolved.items():
                    if key in field_resolve_dict.keys():
                        # We get the Field, which belongs in the Dependencies-List of our target Relation Field
                        f = field_resolve_dict[key]
                        # We get the current Fields in the Dependencies-List and add our new field to it
                        curr_Dependencies = rel_field.fieldDependencies
                        curr_Dependencies.append(f)
                        rel_field.fieldDependencies = list(curr_Dependencies)
                        # But the internal field property of the Size Field is still missing so we add that too
                        from netzob.Model.Vocabulary.Domain.Variables.Leafs.Size import Size
                        if isinstance(rel_field, Size):
                            rel_field.fields = curr_Dependencies
            elif case == 'messages':
                for key, session in unresolved.items():
                    if key in message_resolve_dict.keys():
                        msg = message_resolve_dict[key]
                        curr_msgs = session.messages.values()
                        curr_msgs.append(msg)
                        session.messages = [msg]
            else:
                xmlHandler._logger.error("Cannot find a compatible protocol for {}.".format(case))

        symbols.extend(sessions)

        return symbols
