# -*- coding: utf-8 -*-

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


#-------------------------------------------------------------------------------
# Global Imports
#-------------------------------------------------------------------------------
from gettext import gettext as _
import logging
from lxml import etree


#-------------------------------------------------------------------------------
# PeachExport:
#    Utility for exporting netzob information
# in Peach pit file.
#-------------------------------------------------------------------------------
class PeachExport:

    #---------------------------------------------------------------------------
    # Constructor:
    #---------------------------------------------------------------------------
    def __init__(self, netzob):
        AbstractExporter.__init__(self, "PEACH EXPORT")
        self.netzob = netzob

    #---------------------------------------------------------------------------
    # getXMLDefinition:
    #     Returns part of the Peach pit file (XML definition)
    #     TODO: Return the entire Peach pit file
    #     @return a string containing the xml def.
    #---------------------------------------------------------------------------
    def getXMLDefinition(self):
        xmlRoot = etree.Element("root")
        self.translateVocabularyInPeachDataModels(xmlRoot)

        # TODO(stateful fuzzer): take into account the inferred grammar.
        self.makePeachStateModel(xmlRoot)
        tree = ElementTree(root)
        result = etree.tostring(tree, pretty_print=True)
        return result

    def getXMLDefinition(self, SymbolID):
        xmlRoot = etree.Element("root")
        self.translateVocabularyInPeachDataModels(xmlRoot)

        # TODO(stateful fuzzer): take into account the inferred grammar.
        self.makePeachStateModel(xmlRoot)
        tree = ElementTree(root)
        result = etree.tostring(tree, pretty_print=True)
        return result

    #---------------------------------------------------------------------------
    # translateVocabularyInPeachDataModels:
    #    Transform the inferred vocabulary in as many Peach data models as there
    #    are symbols.
    #    @param xmlFather: xml tree father of the current element.
    #---------------------------------------------------------------------------
    def translateVocabularyInPeachDataModels(self, xmlFather):
        project = self.netzob.getCurrentProject()
        vocabulary = project.getVocabulary()

        # One single data model is created for all symbols.
        # TODO(stateful fuzzer): make one data model for each symbol.
        xmlDataModel = etree.SubElement(xmlFather, "DataModel", name=symbol.getName())
        for symbol in vocabulary.getSymbols():
            # Each symbol is translated in a Peach data model
            self.translateSymbolInPeachDataModel(xmlFather, symbol)

    #---------------------------------------------------------------------------
    # translateSymbolInPeachDataModel:
    #    Transform a netzob symbol in a Peach data model.
    #    @param xmlFather: xml tree father of the current element.
    #    @param symbol: the given symbol that will be transform.
    #---------------------------------------------------------------------------
    def translateSymbolInPeachDataModel(self, xmlFather, symbol):
        for field in symbol.getFields():
            # We exclude separator fields
            if self.getAlignmentType() == "delimiter":
                if field.isStatic():
                    continue

            # Each field is translated in a blob (non-formatted data field in Peach)
            # TODO: sharpen this step so as to have Strings and numbers and not only blob.

            # Static fields become non-mutable token in Peach
            if field.isStatic():
                xmlField = etree.SubElement(xmlDataModel, "Blob", name=field.getName(), valueType="hex", value=field.getRegex(), token="true", mutable="false")

            else:
                # TODO: manage accurately the length.
                xmlField = etree.SubElement(xmlDataModel, "Blob", name=field.getName(), valueType="hex")

    def makePeachStateModel(self, xmlFather):
        xmlStateModel = etree.SubElement(xmlFather, "StateModel", name="simpleStateModel", initialState="Initial")

        # We create one state which will output fuzzed data.
        # TODO(stateful fuzzer): Make one state model for each state of the protocol.
        xmlState = etree.SubElement(xmlStateModel, "State", name="Initial")
        xmlAction = etree.SubElement(xmlState, "Action", type="output")

        # xml link to the previously made data model.
        xmlDataModel = etree.SubElement(xmlAction, "DataModel", ref="request")
        xmlData = etree.SubElement(xmlAction, "Data", name="data")
