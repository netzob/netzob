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
from gettext import gettext as _
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Type.Format import Format
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.Endianess import Endianess
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Filters.Mathematic.Base64Filter import Base64Filter
from netzob.Common.Filters.Mathematic.GZipFilter import GZipFilter
from netzob.Common.Filters.Mathematic.B22Filter import BZ2Filter


class ContextualMenuOnFieldView(object):

    def __init__(self, controller):
        self.controller = controller

    def run(self, event):
        # Build the contextual menu for messages
        self.menu = Gtk.Menu()

        # Add entry to edit field
        item = Gtk.MenuItem(_("Edit field"))
        item.show()
        item.connect("activate", self.controller.displayPopupToEditField_cb)
        self.menu.append(item)

        # Add sub-entries to change the type of a specific column
        subMenu = self.build_encoding_submenu()
        item = Gtk.MenuItem(_("Field visualization"))
        item.set_submenu(subMenu)
        item.show()
        self.menu.append(item)

        # Add sub-entries to add mathematic filters on a  specific column
        subMenuMathematicFilters = self.build_mathematicFilter_submenu()
        item = Gtk.MenuItem(_("Configure mathematic filters"))
        item.set_submenu(subMenuMathematicFilters)
        item.show()
        self.menu.append(item)

        # Add entry to create layer
        item = Gtk.MenuItem(_("Create layer"))
        item.show()
        item.connect("activate", self.controller.displayPopupToCreateLayer_cb)
        self.menu.append(item)

        # Add entry to edit variable
        item = Gtk.MenuItem(_("Edit variable"))
        item.show()
        item.connect("activate", self.controller.displayPopupToEditVariable_cb)
        self.menu.append(item)

        # Add entry to retrieve the field domain of definition
        item = Gtk.MenuItem(_("Field's domain of definition"))
        item.show()
        item.connect("activate", self.controller.displayDomainOfDefinition_cb)
        self.menu.append(item)

        # Add entry to export fields
        item = Gtk.MenuItem(_("Extract fields to a new symbol"))
        item.show()
        item.connect("activate", self.controller.exportSelectedFields_cb)
        self.menu.append(item)

        # Add entry to delete the current message
        item = Gtk.MenuItem(_("Delete message"))
        item.show()
        item.connect("activate", self.controller.deleteMessage_cb)
        self.menu.append(item)

        # Add entries for copy functions
        subMenu = self.build_copy_submenu()
        item = Gtk.MenuItem(_("Copy to clipboard"))
        item.set_submenu(subMenu)
        item.show()
        self.menu.append(item)
        self.menu.popup(None, None, None, None, event.button, event.time)

    #+----------------------------------------------
    #| build_encoding_submenu:
    #|   Build a submenu for field/symbol data visualization.
    #+----------------------------------------------
    def build_encoding_submenu(self):
        menu = Gtk.Menu()

        field = self.controller.field

        # Retrieve all the values in the current field
        cells = self.controller.symbol.getUniqValuesByField(field)

        # Retrieve the selected message and field content
        if self.controller.message is not None:
            # Retrieve content of the field
            field_content = self.controller.message.applyAlignment()[self.controller.field.getIndex()]
        else:
            field_content = None

        # Format submenu
        possible_choices = Format.getPossibleFormats(cells)
        subMenu = Gtk.Menu()
        for value in possible_choices:
            label = value

            # Compute if its activated
            toggled = False
            if field.getFormat() == value:
                toggled = True

            # Compute the label
            if field_content is not None:
                # Get preview of field content
                text_preview = TypeConvertor.encodeNetzobRawToGivenType(field_content, value)
                if len(text_preview) > 10:
                    text_preview = text_preview[:10] + "..."
                label = value + " (" + text_preview + ")"

            # Create the check item
            item = Gtk.CheckMenuItem(label)
            item.set_active(toggled)

            item.show()
            item.connect("activate", self.controller.changeFormat_cb, value)
            subMenu.append(item)
        item = Gtk.MenuItem(_("Format"))
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)

        # Unitsize submenu
        possible_choices = [UnitSize.NONE, UnitSize.BIT, UnitSize.BITS8, UnitSize.BITS16, UnitSize.BITS32, UnitSize.BITS64]
        subMenu = Gtk.Menu()
        for value in possible_choices:

            # Compute if its activated
            toggled = False
            if field.getUnitSize() == value:
                toggled = True

            item = Gtk.CheckMenuItem(value)
            item.set_active(toggled)

            item.show()
            item.connect("activate", self.controller.changeUnitSize_cb, value)
            subMenu.append(item)
        item = Gtk.MenuItem(_("UnitSize"))
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)

        # Sign submenu
        possible_choices = [Sign.SIGNED, Sign.UNSIGNED]
        subMenu = Gtk.Menu()
        for value in possible_choices:

            # Compute if its activated
            toggled = False
            if field.getSign() == value:
                toggled = True

            item = Gtk.CheckMenuItem(value)
            item.set_active(toggled)

            item.show()
            item.connect("activate", self.controller.changeSign_cb, value)
            subMenu.append(item)
        item = Gtk.MenuItem(_("Sign"))
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)

        # Endianess submenu
        possible_choices = [Endianess.BIG, Endianess.LITTLE]
        subMenu = Gtk.Menu()
        for value in possible_choices:
            # Compute if its activated
            toggled = False
            if field.getEndianess() == value:
                toggled = True

            item = Gtk.CheckMenuItem(value)
            item.set_active(toggled)
            item.show()
            item.connect("activate", self.controller.changeEndianess_cb, value)
            subMenu.append(item)
        item = Gtk.MenuItem(_("Endianess"))
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)
        return menu

    #+----------------------------------------------
    #| build_copy_submenu:
    #|   Build a submenu for copy to clipboard?.
    #+----------------------------------------------
    def build_copy_submenu(self):
        # Add entries for copy functions
        copyMenu = Gtk.Menu()
        item = Gtk.MenuItem(_("Raw message"))
        item.show()
        item.connect("activate", self.controller.copyToClipboard_cb, False, False, False)
        copyMenu.append(item)
        item = Gtk.MenuItem(_("Aligned raw message"))
        item.show()
        item.connect("activate", self.controller.copyToClipboard_cb, True, False, False)
        copyMenu.append(item)
        item = Gtk.MenuItem(_("Aligned formatted message"))
        item.show()
        item.connect("activate", self.controller.copyToClipboard_cb, True, True, False)
        copyMenu.append(item)
        item = Gtk.MenuItem(_("Raw field"))
        item.show()
        item.connect("activate", self.controller.copyToClipboard_cb, True, False, True)
        copyMenu.append(item)
        item = Gtk.MenuItem(_("Formatted field"))
        item.show()
        item.connect("activate", self.controller.copyToClipboard_cb, True, True, True)
        copyMenu.append(item)
        return copyMenu

    #+----------------------------------------------
    #| build_mathematicFilter_submenu:
    #|   Build a submenu for field/symbol mathematic filters
    #+----------------------------------------------
    def build_mathematicFilter_submenu(self):
        menu = Gtk.Menu()

        # Retrieve the list of available mathematical filters
        currentWorkspace = self.controller.vocabularyController.getCurrentWorkspace()
        mathematicFilters = currentWorkspace.getMathematicFilters()

        for mathFilter in mathematicFilters:
            toggled = False
            for f in self.controller.field.getMathematicFilters():
                if f.getName() == mathFilter.getName():
                    toggled = True
                    break

            mathFilterItem = Gtk.CheckMenuItem(mathFilter.getName())
            mathFilterItem.set_active(toggled)
            mathFilterItem.connect("activate", self.controller.applyMathematicalFilter_cb, mathFilter)
            mathFilterItem.show()
            menu.append(mathFilterItem)
        return menu
