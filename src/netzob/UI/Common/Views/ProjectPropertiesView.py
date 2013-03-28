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

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
from locale import gettext as _
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


class ProjectPropertiesView(object):

    def __init__(self, controller, parent=None):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(),
                                                "ui",
                                                "projectPropertiesDialog.glade"))
        self._getObjects(self.builder,
                         ["projectPropertiesDialog",
                          "closebutton",

                          # Properties tab
                          "projectNameEntry",
                          "projectDescriptionEntry",
                          "propertiesFormatCombobox",
                          "propertiesUnitsizeCombobox",
                          "propertiesSignCombobox",
                          "propertiesEndianessCombobox",

                          # Details tab
                          "projectDetailName",
                          "projectDetailDescription",
                          "projectDetailCreationDate",
                          "projectDetailSymbols",
                          "projectDetailMessages",
                          "projectDetailsFields",
                          "projectDetailWorkspace",
                          "projectDetailFormat",
                          "projectDetailUnitSize",
                          "projectDetailSign",
                          "projectDetailEndianess",
                          ])

        self.controller = controller
        self.projectPropertiesDialog.set_transient_for(parent)

        self.projectNameEntry.set_text(controller.currentProject.getName())

        desc = controller.currentProject.getDescription()
        if desc:
            self.projectDescriptionEntry.set_text(desc)

        # Finally, connect signals to the controller
        self.builder.connect_signals(self.controller)

    def refreshProjectProperties(self,
                                 name,
                                 description,
                                 date,
                                 symbols,
                                 messages,
                                 fields,
                                 workspace):
        self.projectDetailName.set_text(name)

        if description:
            self.projectDetailDescription.set_text(description)

        currentDate = ""
        if date:
            currentDate = date.strftime("%c")
        self.projectDetailCreationDate.set_text(currentDate)

        self.projectDetailSymbols.set_text(str(symbols))
        self.projectDetailMessages.set_text(str(messages))
        self.projectDetailsFields.set_text(str(fields))
        self.projectDetailWorkspace.set_text(str(workspace))
        self.projectDetailFormat.set_text(self.controller.projectFormat)
        self.projectDetailUnitSize.set_text(self.controller.projectSize)
        self.projectDetailSign.set_text(self.controller.projectSign)
        self.projectDetailEndianess.set_text(self.controller.projectEndianess)

    def _getObjects(self, builder, objectsList):
        for obj in objectsList:
            setattr(self, obj, builder.get_object(obj))

    def run(self):
        self.projectPropertiesDialog.show_all()

    def destroy(self):
        self.projectPropertiesDialog.destroy()

    def initializeComboBoxes(self,
                             formats, projectFormat,
                             sizes, projectSize,
                             signs, projectSign,
                             endianesses, projectEndianess):

        # Format
        model = self.propertiesFormatCombobox.get_model()
        for frmt in formats:
            itr = model.append([frmt])
            if frmt == projectFormat:
                self.propertiesFormatCombobox.set_active_iter(itr)

        # UnitSize
        model = self.propertiesUnitsizeCombobox.get_model()
        for size in sizes:
            itr = model.append([size])
            if size == projectSize:
                self.propertiesUnitsizeCombobox.set_active_iter(itr)

        # Sign
        model = self.propertiesSignCombobox.get_model()
        for sign in signs:
            itr = model.append([sign])
            if sign == projectSign:
                self.propertiesSignCombobox.set_active_iter(itr)

        # Endianess
        model = self.propertiesEndianessCombobox.get_model()
        for endianess in endianesses:
            itr = model.append([endianess])
            if endianess == projectEndianess:
                self.propertiesEndianessCombobox.set_active_iter(itr)
