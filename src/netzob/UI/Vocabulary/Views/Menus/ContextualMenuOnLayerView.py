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


class ContextualMenuOnLayerView(object):

    def __init__(self, controller, multipleLayers=False):
        self.controller = controller
        self.multipleLayers = multipleLayers

    def run(self, event):
        # Build the contextual menu for messages
        self.menu = Gtk.Menu()

        # Add entry to edit layer
        if self.multipleLayers is False:
            item = Gtk.MenuItem(_("Edit layer"))
            item.show()
            item.connect("activate", self.controller.renameLayer_cb)
            self.menu.append(item)

        # Add sub-entries for partitioning
        if self.multipleLayers is False:
            subMenu = self.build_partitioning_submenu()
            item = Gtk.MenuItem(_("Partitioning"))
            item.set_submenu(subMenu)
            item.show()
            self.menu.append(item)

        # Add sub-entries to change the type of a specific column
        subMenu = self.build_encoding_submenu()
        item = Gtk.MenuItem(_("Visualization"))
        item.set_submenu(subMenu)
        item.show()
        self.menu.append(item)

        # Add sub-entries to manage transformation functions
        # Add sub-entries to add transformation functions on a  specific column
        if self.multipleLayers is False:
            subMenuTransformationFunctions = self.build_transformation_functions_submenu()
            item = Gtk.MenuItem(_("Transformation Functions"))
            item.set_submenu(subMenuTransformationFunctions)
            item.show()
            self.menu.append(item)

        # Add entry to delete layer
        item = Gtk.MenuItem(_("Delete layer"))
        item.show()
        item.connect("activate", self.controller.deleteLayer_cb)
        self.menu.append(item)

        self.menu.popup(None, None, None, None, event.button, event.time)

    def build_transformation_functions_submenu(self):
        """Create a GTK submenu which contains
        entries to edit the transformation functions
        of selected layer"""
        menu = Gtk.Menu()

        # Retrieve the list of available transformation functions
        currentWorkspace = self.controller.vocabularyController.getCurrentWorkspace()
        transformationFunctions = currentWorkspace.getTransformationFunctions()

        messages = self.controller.layers[0].getMessages()
        # Fetch all the functions attach to messages of current layer (either symbol of fieldLayer)
        functionsInMessages = []
        for function in self.controller.layers[0].getSymbol().getField().getTransformationFunctions():
            if not function in functionsInMessages:
                functionsInMessages.append(function)

        for transformationFunction in transformationFunctions:
            toggled = False
            for f in functionsInMessages:
                if f.getName() == transformationFunction.getName():
                    toggled = True
                    break

            transformationFunctionItem = Gtk.CheckMenuItem(transformationFunction.getName())
            transformationFunctionItem.set_active(toggled)
            transformationFunctionItem.connect("activate", self.controller.applyTransformationFunction_cb, transformationFunction)
            transformationFunctionItem.show()
            menu.append(transformationFunctionItem)

        customFunction = Gtk.MenuItem(_("Create your Function"))
        customFunction.connect("activate", self.controller.createCustomFunction_cb)
        customFunction.show()
        menu.append(customFunction)

        menu.show_all()
        return menu

    def build_encoding_submenu(self):
        """Create a GTK menu which contains
        entries to edit the visualizations formats of
        selected layer"""
        menu = Gtk.Menu()

        # Format submenu
        possible_choices = Format.getSupportedFormats()
        subMenu = Gtk.Menu()
        for value in possible_choices:
            # Compute if its activated
            toggled = False
            if self.multipleLayers is False:
                if self.controller.layers[0].getFormat() == value:
                    toggled = True

            # Create the check item
            item = Gtk.CheckMenuItem(value)
            item.set_active(toggled)
            item.show()
            item.connect("activate", self.controller.changeFormat_cb, value)
            subMenu.append(item)
        item = Gtk.MenuItem(_("Format"))
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)

        # Unitsize submenu
        possible_choices = [UnitSize.NONE, UnitSize.BITS4, UnitSize.BITS8, UnitSize.BITS16, UnitSize.BITS32, UnitSize.BITS64]
        subMenu = Gtk.Menu()
        for value in possible_choices:
            # Compute if its activated
            toggled = False
            if self.multipleLayers is False:
                if self.controller.layers[0].getUnitSize() == value:
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
            if self.multipleLayers is False:
                if self.controller.layers[0].getSign() == value:
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
            if self.multipleLayers is False:
                if self.controller.layers[0].getEndianess() == value:
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

    def build_partitioning_submenu(self):
        """Create a GTK menu which contains
        entries for partitioning fields"""
        menu = Gtk.Menu()

        # Sequence alignment
        item = Gtk.MenuItem(_("Sequence alignment"))
        item.connect("activate", self.controller.sequenceAlignment_cb)
        item.show()
        menu.append(item)

        # Force partitionment
        item = Gtk.MenuItem(_("Force partitionment"))
        item.connect("activate", self.controller.forcePartitionment_cb)
        item.show()
        menu.append(item)

        # Simple partitionment
        item = Gtk.MenuItem(_("Simple partitionment"))
        item.connect("activate", self.controller.simplePartitionment_cb)
        item.show()
        menu.append(item)

        # Smooth partitionment
        item = Gtk.MenuItem(_("Smooth partitionment"))
        item.connect("activate", self.controller.smoothPartitionment_cb)
        item.show()
        menu.append(item)

        # Reset partitionment
        item = Gtk.MenuItem(_("Reset partitionment"))
        item.connect("activate", self.controller.resetPartitionment_cb)
        item.show()
        menu.append(item)

        return menu
