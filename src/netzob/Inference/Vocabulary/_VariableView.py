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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
from gettext import gettext as _
from gi.repository import Gtk
from netzob.Common.MMSTD.Dictionary.Types.BinaryType import BinaryType
from netzob.Common.MMSTD.Dictionary.Types.DecimalWordType import DecimalWordType
from netzob.Common.MMSTD.Dictionary.Types.HexWordType import HexWordType
from netzob.Common.MMSTD.Dictionary.Types.IPv4WordType import IPv4WordType
from netzob.Common.MMSTD.Dictionary.Types.WordType import WordType
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import \
    AggregateVariable
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import \
    AlternateVariable
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
from netzob.Common.MMSTD.Dictionary.Variables.ReferencedVariable import \
    ReferencedVariable
from netzob.Common.MMSTD.Dictionary.Variables.RepeatVariable import \
    RepeatVariable
from netzob.Common.Type.Format import Format
import gi
import logging
import uuid
gi.require_version('Gtk', '3.0')

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------


#+----------------------------------------------
#| VariableView:
#|     Class dedicated to host the creation of a variable
#+----------------------------------------------
class VariableView(object):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, netzob, field, variableId, variableName, defaultValue=None):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Vocabulary.VariableView.py')
        self.netzob = netzob
        self.project = self.netzob.getCurrentProject()
        self.varId = variableId
        self.varName = variableName
        self.field = field
        self.defaultValue = defaultValue
        self.datas = dict()

        # Add the initial Aggregate
        self.rootVariable = AggregateVariable(variableId, self.varName, True, False, None)
        if self.defaultValue is not None:
            self.rootVariable.addChild(self.defaultValue)

    def display(self):
        # We display the dedicated dialog for the creation of a variable
        self.dialog = Gtk.Dialog(title=_("Creation of a variable"), flags=0, buttons=None)

        # Create the main panel
        self.panel = Gtk.Table(rows=2, columns=3, homogeneous=False)

        self.treestore = Gtk.TreeStore(str, str)  # id of the data, description
        self.treeview = Gtk.TreeView(self.treestore)
        self.treeview.connect('button-press-event', self.showMenu)
        # messages list
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll.show()
        self.scroll.set_size_request(200, 300)
        self.scroll.add(self.treeview)
        self.scroll.show()

        self.lvcolumn = Gtk.TreeViewColumn(_("Description of the variable"))
        self.lvcolumn.set_sort_column_id(1)
        cell = Gtk.CellRendererText()
        self.lvcolumn.pack_start(cell, True)
        self.lvcolumn.add_attribute(cell, "text", 1)
        self.treeview.append_column(self.lvcolumn)
        self.treeview.show()

        self.panel.attach(self.scroll, 0, 2, 0, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.show()

        # Create button
        createButton = Gtk.Button(_("Create"))
        createButton.show()
        createButton.connect("clicked", self.createVariable)

        self.panel.attach(createButton, 0, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # We register the default values
        self.registerVariable(None, self.rootVariable, "Root")

    def registerVariable(self, rootEntry, variable, name):
        self.log.debug("Register: {0}".format(str(name)))
        self.datas[str(variable.getID())] = variable
        newEntry = self.treestore.append(rootEntry, [str(variable.getID()), name])
        if variable.getType() == AggregateVariable.TYPE or variable.getType() == AlternateVariable.TYPE:
            for child in variable.getChildren():
                self.registerVariable(newEntry, child, child.getName())

        self.dialog.vbox.pack_start(self.panel, True, True, 0)
        self.dialog.show()

    def createVariable(self, button):
        # We register the root variable as the variable of specified field
        self.field.setVariable(self.rootVariable)
        self.dialog.destroy()

        # Update UI
        page = self.netzob.getCurrentNotebookPage()
        if page is not None:
            page.update()

    def showMenu(self, treeview, event):
        rootVariable = None
        if event.type == Gtk.EventType.BUTTON_PRESS and event.button == 3:
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)

            # Retrieve the selected variable
            variable_id = None
            aIter = treeview.get_model().get_iter(path)
            if aIter:
                if treeview.get_model().iter_is_valid(aIter):
                    variable_id = treeview.get_model().get_value(aIter, 0)

                    for varid in self.datas.keys():
                        if varid == variable_id:
                            rootVariable = self.datas[varid]

        if rootVariable is None:
            self.log.debug("Impossible to find the selected variable.")
            return

        # We display the menu for the insertion of sub-elements if its an Aggregate or an Alternative
        self.menu = Gtk.Menu()

        subElementMenu = Gtk.Menu()

        # Word Variable
        itemWord = Gtk.MenuItem(_("Word"))
        itemWord.show()
        itemWord.connect("activate", self.addWord, rootVariable, aIter)
        subElementMenu.append(itemWord)

        # Decimal Word Variable
        itemDecimalWord = Gtk.MenuItem(_("Decimal Word"))
        itemDecimalWord.show()
        itemDecimalWord.connect("activate", self.addDecimalWord, rootVariable, aIter)
        subElementMenu.append(itemDecimalWord)

        # IPv4 Word Variable
        itemIPv4 = Gtk.MenuItem(_("IPv4 Word"))
        itemIPv4.show()
        itemIPv4.connect("activate", self.addIPv4Word, rootVariable, aIter)
        subElementMenu.append(itemIPv4)

        # MAC Word Variable
        itemMAC = Gtk.MenuItem(_("MAC Word"))
        itemMAC.show()
        itemMAC.connect("activate", self.addMACWord, rootVariable, aIter)
        subElementMenu.append(itemMAC)

        # Hexadecimal Variable
        itemHex = Gtk.MenuItem(_("Hexadecimal Word"))
        itemHex.show()
        itemHex.connect("activate", self.addHexWord, rootVariable, aIter)
        subElementMenu.append(itemHex)

        # Binary Variable
        itemBinary = Gtk.MenuItem(_("Binary"))
        itemBinary.show()
        itemBinary.connect("activate", self.addBinary, rootVariable, aIter)
        subElementMenu.append(itemBinary)

        # Integer Variable
        itemInteger = Gtk.MenuItem(_("Integer"))
        itemInteger.show()
        itemInteger.connect("activate", self.addInteger, rootVariable, aIter)
        subElementMenu.append(itemInteger)

        # Aggregate Variable
        itemAggregate = Gtk.MenuItem(_("Aggregate"))
        itemAggregate.show()
        itemAggregate.connect("activate", self.addAggregate, rootVariable, aIter)
        subElementMenu.append(itemAggregate)

        # Alternate Variable
        itemAlternate = Gtk.MenuItem(_("Alternative"))
        itemAlternate.show()
        itemAlternate.connect("activate", self.addAlternate, rootVariable, aIter)
        subElementMenu.append(itemAlternate)

        # Referenced Variable
        itemRef = Gtk.MenuItem(_("Referenced Variable"))
        itemRef.show()
        itemRef.connect("activate", self.addReferencedVariable, rootVariable, aIter)
        subElementMenu.append(itemRef)

        # Repeat Variable
        itemRepeat = Gtk.MenuItem(_("Repeat Variable"))
        itemRepeat.show()
        itemRepeat.connect("activate", self.addRepeatVariable, rootVariable, aIter)
        subElementMenu.append(itemRepeat)

        item = Gtk.MenuItem(_("Add a sub-element"))
        item.set_submenu(subElementMenu)
        item.show()

        self.menu.append(item)
        self.menu.popup(None, None, None, None, event.button, event.time)

    def addBinary(self, event, rootVariable, rootEntry):
        # Display the form for the creation of a Binary variable
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK, None)
        dialog.set_markup(_("Definition of the Binary Variable"))

        # Create the ID of the new variable
        varID = str(uuid.uuid4())
        variableID = str(varID)

        mainTable = Gtk.Table(rows=3, columns=2, homogeneous=False)
        # parent id of the variable
        variablePIDLabel = Gtk.Label(label=_("Parent ID:"))
        variablePIDLabel.show()
        variablePIDValueLabel = Gtk.Label(label=str(rootVariable.getID()))
        variablePIDValueLabel.set_sensitive(False)
        variablePIDValueLabel.show()
        mainTable.attach(variablePIDLabel, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variablePIDValueLabel, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # id of the variable
        variableIDLabel = Gtk.Label(label=_("ID:"))
        variableIDLabel.show()
        variableIDValueLabel = Gtk.Label(label=variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Original Value
        originalValueLabel = Gtk.Label(label=_("Original value:"))
        originalValueLabel.show()
        originalValueEntry = Gtk.Entry()
        originalValueEntry.show()
        mainTable.attach(originalValueLabel, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(originalValueEntry, 1, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Constraints label
        constraintsLabel = Gtk.Label(label=_("Constraints when parsing / generating"))
        constraintsLabel.show()
        mainTable.attach(constraintsLabel, 0, 2, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # start Value
        minBitsLabel = Gtk.Label(label=_("Minimum number of bits:"))
        minBitsLabel.show()
        minBitsEntry = Gtk.Entry()
        minBitsEntry.show()
        mainTable.attach(minBitsLabel, 0, 1, 4, 5, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(minBitsEntry, 1, 2, 4, 5, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # end Value
        maxBitsLabel = Gtk.Label(label=_("Maximum number of bits:"))
        maxBitsLabel.show()
        maxBitsEntry = Gtk.Entry()
        maxBitsEntry.show()
        mainTable.attach(maxBitsLabel, 0, 1, 5, 6, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(maxBitsEntry, 1, 2, 5, 6, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != Gtk.ResponseType.OK:
            dialog.destroy()
            return

        # Creation of the variable (binary)
        # original value :
        originalValue = originalValueEntry.get_text()
        if len(originalValue) == 0:
            originalValue = None

        # constraints
        minSize = int(minBitsEntry.get_text())
        maxSize = int(maxBitsEntry.get_text())

        binVariable = DataVariable(varID, "binary", True, False, BinaryType(), originalValue, minSize, maxSize)
        rootVariable.addChild(binVariable)

        self.datas[str(binVariable.getID())] = binVariable

        self.treestore.append(rootEntry, [str(binVariable.getID()), binVariable.getUncontextualizedDescription()])

        # We close the current dialog
        dialog.destroy()

    def addHexadecimal(self, event, rootVariable, rootEntry):
        # Display the form for the creation of an Hexadecimal variable
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK, None)
        dialog.set_markup(_("Definition of the Hexadecimal Variable"))

        # Create the ID of the new variable
        varID = str(uuid.uuid4())
        variableID = str(varID)

        mainTable = Gtk.Table(rows=3, columns=2, homogeneous=False)
        # parent id of the variable
        variablePIDLabel = Gtk.Label(label=_("Parent ID:"))
        variablePIDLabel.show()
        variablePIDValueLabel = Gtk.Label(label=str(rootVariable.getID()))
        variablePIDValueLabel.set_sensitive(False)
        variablePIDValueLabel.show()
        mainTable.attach(variablePIDLabel, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variablePIDValueLabel, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # id of the variable
        variableIDLabel = Gtk.Label(label=_("ID:"))
        variableIDLabel.show()
        variableIDValueLabel = Gtk.Label(label=variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Original Value
        originalValueLabel = Gtk.Label(label=_("Original value:"))
        originalValueLabel.show()
        originalValueEntry = Gtk.Entry()
        originalValueEntry.show()
        mainTable.attach(originalValueLabel, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(originalValueEntry, 1, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Constraints label
        constraintsLabel = Gtk.Label(label=_("Constraints when parsing / generating"))
        constraintsLabel.show()
        mainTable.attach(constraintsLabel, 0, 2, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # start Value
        minBitsLabel = Gtk.Label(label=_("Minimum number of hex (0xf=1):"))
        minBitsLabel.show()
        minBitsEntry = Gtk.Entry()
        minBitsEntry.show()
        mainTable.attach(minBitsLabel, 0, 1, 4, 5, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(minBitsEntry, 1, 2, 4, 5, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # end Value
        maxBitsLabel = Gtk.Label(label=_("Maximum number of hex:"))
        maxBitsLabel.show()
        maxBitsEntry = Gtk.Entry()
        maxBitsEntry.show()
        mainTable.attach(maxBitsLabel, 0, 1, 5, 6, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(maxBitsEntry, 1, 2, 5, 6, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != Gtk.ResponseType.OK:
            dialog.destroy()
            return

        # Creation of the variable (binary)
        # original value :
        originalValue = originalValueEntry.get_text()
        if len(originalValue) == 0:
            originalValue = None

        # constraints
        minSize = int(minBitsEntry.get_text())
        maxSize = int(maxBitsEntry.get_text())

        hexVariable = DataVariable(varID, "hexadecimal", True, False, HexWordType(), originalValue, minSize, maxSize)
        rootVariable.addChild(hexVariable)

        self.datas[str(hexVariable.getID())] = hexVariable

        self.treestore.append(rootEntry, [str(hexVariable.getID()), hexVariable.getUncontextualizedDescription()])

        # We close the current dialog
        dialog.destroy()

    def addAlternate(self, event, rootVariable, rootEntry):
        # Display the form for the creation of a word variable
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK, None)
        dialog.set_markup(_("Definition of the Alternative"))

        # Create the ID of the new variable
        variableID = str(uuid.uuid4())

        mainTable = Gtk.Table(rows=3, columns=2, homogeneous=False)
        # parent id of the variable
        variablePIDLabel = Gtk.Label(label=_("Parent ID:"))
        variablePIDLabel.show()
        variablePIDValueLabel = Gtk.Label(label=str(rootVariable.getID()))
        variablePIDValueLabel.set_sensitive(False)
        variablePIDValueLabel.show()
        mainTable.attach(variablePIDLabel, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variablePIDValueLabel, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # id of the variable
        variableIDLabel = Gtk.Label(label=_("ID:"))
        variableIDLabel.show()
        variableIDValueLabel = Gtk.Label(label=variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # name of the variable
        variableValueLabel = Gtk.Label(label=_("Name:"))
        variableValueLabel.show()
        variableValueEntry = Gtk.Entry()
        variableValueEntry.show()
        mainTable.attach(variableValueLabel, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableValueEntry, 1, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != Gtk.ResponseType.OK:
            dialog.destroy()
            return

        # We retrieve the name of the variable
        varName = variableValueEntry.get_text()

        # Creation of the aggregate id, name, mutable, value):
        alternateVariable = AlternateVariable(variableID, varName, True, False, None)
        rootVariable.addChild(alternateVariable)

        self.datas[str(alternateVariable.getID())] = alternateVariable

        self.treestore.append(rootEntry, [str(alternateVariable.getID()), _("Alternate")])

        # We close the current dialog
        dialog.destroy()

    def addAggregate(self, event, rootVariable, rootEntry):
        # Display the form for the creation of a word variable
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK, None)
        dialog.set_markup(_("Definition of the Aggregate"))

        # Create the ID of the new variable
        variableID = str(uuid.uuid4())

        mainTable = Gtk.Table(rows=3, columns=2, homogeneous=False)
        # parent id of the variable
        variablePIDLabel = Gtk.Label(label=_("Parent ID:"))
        variablePIDLabel.show()
        variablePIDValueLabel = Gtk.Label(label=str(rootVariable.getID()))
        variablePIDValueLabel.set_sensitive(False)
        variablePIDValueLabel.show()
        mainTable.attach(variablePIDLabel, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variablePIDValueLabel, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # id of the variable
        variableIDLabel = Gtk.Label(label=_("ID:"))
        variableIDLabel.show()
        variableIDValueLabel = Gtk.Label(label=variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # name of the variable
        variableValueLabel = Gtk.Label(label=_("Name:"))
        variableValueLabel.show()
        variableValueEntry = Gtk.Entry()
        variableValueEntry.show()
        mainTable.attach(variableValueLabel, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableValueEntry, 1, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != Gtk.ResponseType.OK:
            dialog.destroy()
            return

        # We retrieve the name of the variable
        varName = variableValueEntry.get_text()

        # Creation of the aggregate id, name, mutable, value):
        aggregateVariable = AggregateVariable(variableID, varName, True, False, None)
        rootVariable.addChild(aggregateVariable)

        self.datas[str(aggregateVariable.getID())] = aggregateVariable

        self.treestore.append(rootEntry, [str(aggregateVariable.getID()), _("Aggregate")])

        # We close the current dialog
        dialog.destroy()

    def addWord(self, event, rootVariable, rootEntry):
        # Display the form for the creation of a word variable
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK, None)
        dialog.set_markup(_("Definition of the WORD"))

        # Create the ID of the new variable
        variableID = str(uuid.uuid4())

        mainTable = Gtk.Table(rows=3, columns=2, homogeneous=False)
        # parent id of the variable
        variablePIDLabel = Gtk.Label(label=_("Parent ID:"))
        variablePIDLabel.show()
        variablePIDValueLabel = Gtk.Label(label=str(rootVariable.getID()))
        variablePIDValueLabel.set_sensitive(False)
        variablePIDValueLabel.show()
        mainTable.attach(variablePIDLabel, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variablePIDValueLabel, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # id of the variable
        variableIDLabel = Gtk.Label(label=_("ID:"))
        variableIDLabel.show()
        variableIDValueLabel = Gtk.Label(label=variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # name of the variable
        variableNameLabel = Gtk.Label(label=_("Name:"))
        variableNameLabel.show()
        variableNameEntry = Gtk.Entry()
        variableNameEntry.show()
        mainTable.attach(variableNameLabel, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableNameEntry, 1, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # value of the variable
        variableValueLabel = Gtk.Label(label=_("Value:"))
        variableValueLabel.show()
        variableValueEntry = Gtk.Entry()
        variableValueEntry.show()
        mainTable.attach(variableValueLabel, 0, 1, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableValueEntry, 1, 2, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != Gtk.ResponseType.OK:
            dialog.destroy()
            return

        # We retrieve the value of the variable
        varName = variableNameEntry.get_text()
        varValue = variableValueEntry.get_text()

        if len(varValue) == 0:
            varValue = None

        # Creation of the word id, name, mutable, value):
        wordVariable = DataVariable(variableID, varName, True, False, WordType(), varValue, len(varValue), len(varValue))
        rootVariable.addChild(wordVariable)

        self.datas[str(wordVariable.getID())] = wordVariable

        self.treestore.append(rootEntry, [str(wordVariable.getID()), wordVariable.getUncontextualizedDescription()])

        # We close the current dialog
        dialog.destroy()

    def addDecimalWord(self, event, rootVariable, rootEntry):
        # Display the form for the creation of a word variable
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK, None)
        dialog.set_markup(_("Definition of the Decimal WORD"))

        # Create the ID of the new variable
        variableID = str(uuid.uuid4())

        mainTable = Gtk.Table(rows=3, columns=2, homogeneous=False)
        # parent id of the variable
        variablePIDLabel = Gtk.Label(label=_("Parent ID:"))
        variablePIDLabel.show()
        variablePIDValueLabel = Gtk.Label(label=str(rootVariable.getID()))
        variablePIDValueLabel.set_sensitive(False)
        variablePIDValueLabel.show()
        mainTable.attach(variablePIDLabel, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variablePIDValueLabel, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # id of the variable
        variableIDLabel = Gtk.Label(label=_("ID:"))
        variableIDLabel.show()
        variableIDValueLabel = Gtk.Label(label=variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # value of the variable
        variableValueLabel = Gtk.Label(label=_("Value:"))
        variableValueLabel.show()
        variableValueEntry = Gtk.Entry()
        variableValueEntry.show()
        mainTable.attach(variableValueLabel, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableValueEntry, 1, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != Gtk.ResponseType.OK:
            dialog.destroy()
            return

        # We retrieve the value of the variable
        varValue = variableValueEntry.get_text()

        # Creation of the word id, name, mutable, value):

        decimalwordVariable = DataVariable(variableID, "decimal word", True, False, DecimalWordType(), varValue, len(varValue), len(varValue))
        rootVariable.addChild(decimalwordVariable)

        self.datas[str(decimalwordVariable.getID())] = decimalwordVariable

        self.treestore.append(rootEntry, [str(decimalwordVariable.getID()), decimalwordVariable.getUncontextualizedDescription()])

        # We close the current dialog
        dialog.destroy()

    def addIPv4(self, event, rootVariable, rootEntry):
        # Display the form for the creation of an IPv4 variable
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK, None)
        dialog.set_markup(_("Definition of the IPv4 Variable"))

        # Create the ID of the new variable
        varID = str(uuid.uuid4())
        variableID = str(varID)

        mainTable = Gtk.Table(rows=3, columns=2, homogeneous=False)
        # parent id of the variable
        variablePIDLabel = Gtk.Label(label=_("Parent ID:"))
        variablePIDLabel.show()
        variablePIDValueLabel = Gtk.Label(label=str(rootVariable.getID()))
        variablePIDValueLabel.set_sensitive(False)
        variablePIDValueLabel.show()
        mainTable.attach(variablePIDLabel, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variablePIDValueLabel, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # id of the variable
        variableIDLabel = Gtk.Label(label=_("ID:"))
        variableIDLabel.show()
        variableIDValueLabel = Gtk.Label(label=variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Original Value
        originalValueLabel = Gtk.Label(label=_("Original value:"))
        originalValueLabel.show()
        originalValueEntry = Gtk.Entry()
        originalValueEntry.show()
        mainTable.attach(originalValueLabel, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(originalValueEntry, 1, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Constraints label
        constraintsLabel = Gtk.Label(label=_("Constraints when parsing / generating"))
        constraintsLabel.show()
        mainTable.attach(constraintsLabel, 0, 2, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # start Value
        startValueLabel = Gtk.Label(label=_("Start:"))
        startValueLabel.show()
        startValueEntry = Gtk.Entry()
        startValueEntry.show()
        mainTable.attach(startValueLabel, 0, 1, 4, 5, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(startValueEntry, 1, 2, 4, 5, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # end Value
        endValueLabel = Gtk.Label(label=_("End:"))
        endValueLabel.show()
        endValueEntry = Gtk.Entry()
        endValueEntry.show()
        mainTable.attach(endValueLabel, 0, 1, 5, 6, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(endValueEntry, 1, 2, 5, 6, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Format label
        hdrFormatLabel = Gtk.Label(label=_("Representation"))
        hdrFormatLabel.show()
        mainTable.attach(hdrFormatLabel, 0, 2, 7, 8, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Format Value
        formatValueLabel = Gtk.Label(label=_("Format:"))
        formatValueLabel.show()
        formatValueCombo = Gtk.ComboBoxText.new_with_entry()
        formatValueCombo.show()
        formatValueComboStore = Gtk.ListStore(str)  # format name
        formatValueCombo.set_model(formatValueComboStore)
        # We retrieve all the existing variables in the project
        formatValueCombo.get_model().append([Format.HEX])
        formatValueCombo.get_model().append([Format.ASCII])
        mainTable.attach(formatValueLabel, 0, 1, 8, 9, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(formatValueCombo, 1, 2, 8, 9, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != Gtk.ResponseType.OK:
            dialog.destroy()
            return

        # Creation of the variable (ipv4)
        # original value :
        originalValue = originalValueEntry.get_text()
        if len(originalValue) == 0:
            originalValue = None

        # constraints
        startValue = startValueEntry.get_text()
        if len(startValue) == 0:
            startValue = None
        endValue = endValueEntry.get_text()
        if len(endValue) == 0:
            endValue = None

        # format
        format = formatValueCombo.get_model().get_value(formatValueCombo.get_active_iter(), 0)
        ipVariable = DataVariable(varID, "ipv4", True, False, IPv4WordType(), originalValue, startValue, endValue, format)
        rootVariable.addChild(ipVariable)

        self.datas[str(ipVariable.getID())] = ipVariable

        self.treestore.append(rootEntry, [str(ipVariable.getID()), ipVariable.getUncontextualizedDescription()])

        # We close the current dialog
        dialog.destroy()

    def addReferencedVariable(self, event, rootVariable, rootEntry):
        # Display the form for the creation of a word variable
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK, None)
        dialog.set_markup(_("Definition of the ReferencedVariable"))

        # Create the ID of the new variable
        variableID = str(uuid.uuid4())

        mainTable = Gtk.Table(rows=3, columns=2, homogeneous=False)
        # parent id of the variable
        variablePIDLabel = Gtk.Label(label=_("Parent ID:"))
        variablePIDLabel.show()
        variablePIDValueLabel = Gtk.Label(label=str(rootVariable.getID()))
        variablePIDValueLabel.set_sensitive(False)
        variablePIDValueLabel.show()
        mainTable.attach(variablePIDLabel, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variablePIDValueLabel, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # id of the variable
        variableIDLabel = Gtk.Label(label=_("ID:"))
        variableIDLabel.show()
        variableIDValueLabel = Gtk.Label(label=variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Selection of the variable
        varLabel = Gtk.Label(label=_("Referenced Variable:"))
        varLabel.show()
        self.varCombo = Gtk.ComboBoxText.new_with_entry()
        self.varCombo.show()
        self.varStore = Gtk.ListStore(str, str)  # description, id,
        self.varCombo.set_model(self.varStore)

        # We retrieve all the existing variables in the project
        existingVariables = self.project.getVocabulary().getVariables()
        for existingVariable in existingVariables:
            self.varCombo.get_model().append([existingVariable.getUncontextualizedDescription(), existingVariable.getID()])

        mainTable.attach(varLabel, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.varCombo, 1, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != Gtk.ResponseType.OK:
            dialog.destroy()
            return

        idReferencedVariable = self.varCombo.get_model().get_value(self.varCombo.get_active_iter(), 1)
        referencedVariable = ReferencedVariable(str(uuid.uuid4()), "Ref", True, False, idReferencedVariable)
        rootVariable.addChild(referencedVariable)

        self.datas[str(referencedVariable.getID())] = referencedVariable
        self.treestore.append(rootEntry, [str(referencedVariable.getID()), referencedVariable.getUncontextualizedDescription()])

        # We close the current dialog
        dialog.destroy()
