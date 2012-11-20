# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 AMOSSYS                                                |
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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk
from RelationsMakerView import RelationsMakerView
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
import uuid
from netzob.Common.MMSTD.Dictionary.DataTypes.HexWordType import HexWordType
from netzob.Common.MMSTD.Dictionary.Variables.ComputedRelationVariable import ComputedRelationVariable
from netzob.Common.MMSTD.Dictionary.RelationTypes.SizeRelationType import SizeRelationType
from netzob.Common.Field import Field

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class RelationsMakerController(object):
    """RelationsMakerController:
            Manage the creation of relations.
    """

    def __init__(self, netzob, MINEController, relations):
        """Constructor of the RelationsMakerController:

                @type netzob: netzob instance
                @param netzob: the MINE main controller
        """
        self.mineController = MINEController
        self.netzob = netzob
        self.relations = relations
        self.view = RelationsMakerView(self, self.netzob, relations)

    def run(self):
        """run:
            Show the plugin view.
        """
        self.update()

    def update(self):
        self.view.show()

    def applyButton_clicked_cb(self, widget):
        """applyButton_clicked_cb:
        Callback executed when the user applies the displayed relations"""

        relation = self.view.getSelectedRelation()
        if relation is None:
            logging.info("No computed relations")
            return

        (type, startField, startTypeField, endField, endTypeField, score, idRelationRel) = relation

        if type != "SizeRelation":
            logging.warning("Only support Size Relation")
            return

        if startTypeField == "s":
            sizeField = endField
            payloadField = startField
        else:
            payloadField = endField
            sizeField = startField

        logging.debug("Create Fields")
        # Create the payload field becomes a layer
        layerField = Field("Payload", payloadField.getRegex(), payloadField.getSymbol())
        layerField.addField(payloadField)

        parentField = payloadField.getParentField()
        indexField = parentField.getLocalFields().index(payloadField)
        parentField.getLocalFields().remove(payloadField)
        parentField.getLocalFields().insert(indexField, layerField)

        logging.info("Creates variables")
        symbol = startField.getSymbol()

        # Create variables for start and end fields
        variablePayloadType = HexWordType(None, 4, 10, None)
        variablePayload = DataVariable(uuid.uuid4(), "Payload", True, True, variablePayloadType, None)

        variableSizeFieldType = SizeRelationType(2, None, None, None)
        variableSizeField = ComputedRelationVariable(uuid.uuid4(), "Size Field", True, True, variableSizeFieldType, variablePayload.getID(), symbol)

        sizeField.setVariable(variableSizeField)
        payloadField.setVariable(variablePayload)

        vocabularyController = self.mineController.getVocabularyController()
        vocabularyController.restart()

        self.view.destroy()

    def cancelButton_clicked_cb(self, widget):
        """cancelButton_clicked_cb:
        Callback executed when the user cancel the relations maker"""
        self.view.destroy()
