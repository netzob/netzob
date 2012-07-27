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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+

from netzob.Common.MMSTD.Dictionary.Types.AbstractType import AbstractType
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import \
    AggregateVariable
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import \
    AlternateVariable
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
from netzob.Common.MMSTD.Dictionary.Variables.ReferencedVariable import \
    ReferencedVariable
from netzob.Common.MMSTD.Dictionary.Variables.RepeatVariable import \
    RepeatVariable
from netzob.UI.Vocabulary.Views.VariableView import VariableTreeView, \
    VariableCreationView


class VariableTreeController:
    """VariableTreeController:
            Controls a variable's tree view display
    """

    def __init__(self, netzob, field):
        """Constructor of VariableTreeController:

                @type netzob: netzob.Common.NetzobGui.NetzobGui
                @param netzob: the main netzob project.
                @type field: netzob.Common.Field.Field
                @param field: the field, the variable of which we want to display.
        """
        self.netzob = netzob
        self.field = field

        self.view = VariableTreeView(self)
        self.registerContent(self.field.getVariable())
        self.initCallbacks()

    def initCallbacks(self):
        """initCallbacks:
                Init the callbacks.
        """
        self.view.getWidg("treeview").connect('button-press-event', self.showMenu)

    def registerContent(self, variable):
        """registerContent:
                Register each variable, their entry in the tree view.
                Fill the tree view of a variable with all its displayable content.

                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable.AbstractVariable
                @param variable: the root variable which content will be displayed.
        """
        self.dictVariable = dict()
        self.dictEntry = dict()

        self.treestore = Gtk.TreeStore(str, str)  # id of the data, description
        self.registerVariable(None, variable)
        self.view.getWidg("treeview").set_model(self.treestore)

    def registerVariable(self, rootEntry, variable):
        """registerVariable:
                Register a variable in the tree view under its root variable (Aggregate or Alternate).
                May be recursive.

                @type rootEntry: Gtk.treerow
                @param rootEntry: the root entry under which we will add this entry.
                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable.AbstractVariable
                @param variable: the variable which will be added to the tree view representation.
        """
        self.dictVariable[str(variable.getID())] = variable
        newEntry = self.treestore.append(rootEntry, [str(variable.getID()), variable.toString()])
        self.dictEntry[str(variable.getID())] = newEntry
        if variable.getVariableType() == AggregateVariable.TYPE or variable.getVariableType() == AlternateVariable.TYPE:
            if variable.getChildren() is not None:
                for child in variable.getChildren():
                    self.registerVariable(newEntry, child)
        if variable.getVariableType() == RepeatVariable.TYPE:
            if variable.getChild() is not None:
                self.registerVariable(newEntry, variable.getChild())

    def showMenu(self, treeview, event):
        """showMenu:
                Called on right click on a variable.

                @param treeview: the treeview which contains the triggering variable.
                @param event: the mouse event which called this function.
        """
        variable = None
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)

            # Retrieve the selected variable
            varid = None
            iter = treeview.get_model().get_iter(path)
            if iter:
                if treeview.get_model().iter_is_valid(iter):
                    varid = treeview.get_model().get_value(iter, 0)

                    if varid is not None:
                        variable = self.dictVariable[varid]
        else:
            # Wrong mouse click
            return

        if variable is None:
            logging.debug(_("Impossible to find the selected variable."))
            return

        # We display the menu for the insertion of sub-elements if its an Aggregate or an Alternative
        self.menu = Gtk.Menu()

        # We can add elements only to node variable.
        if variable.isNode():
            if variable.getVariableType() == RepeatVariable.TYPE:
                # Add an element to a repeat variable will replace the previous one.
                itemAdd = Gtk.MenuItem(_("Edit the sub-element"))
            else:
                itemAdd = Gtk.MenuItem(_("Add a sub-element"))
            itemAdd.connect("activate", VariableCreationController, self, variable, iter, False)
            itemAdd.show()
            self.menu.append(itemAdd)

        itemEdit = Gtk.MenuItem(_("Edit this element"))
        itemEdit.connect("activate", VariableCreationController, self, variable, iter, True)
        itemEdit.show()

        # If we have not click on the root variable, we can remove it. The root variable can be edited. it is way enough.
        if variable.getID() != self.field.getVariable().getID():
            itemRemove = Gtk.MenuItem(_("Remove this element"))
            itemRemove.connect("activate", self.removeVariable, variable)
            itemRemove.show()
            self.menu.append(itemRemove)

        self.menu.append(itemEdit)
        self.menu.popup(None, None, None, None, event.button, event.time)

    def removeVariable(self, item, variable):
        """removeVariable:
                Remove a variable and its presence in the tree view.

                @type item: Gtk.Menuitem
                @param item: the menu item which calls this function.
                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable
                @param variable: the variable that will be removed.
        """
        questionMsg = _("Click yes to confirm the removal of the variable {0}").format(variable.getName())
        md = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result == Gtk.ResponseType.YES:
            # Remove the variable from the global tree.
            motherNode = variable.findMotherNode(self.field.getVariable())
            motherNode.removeChildByID(variable)

            # Remove its entry.
            entry = self.dictEntry[variable.getID()]
            self.treestore.remove(entry)

            # Remove the variable and its entry from dictionaries.
            self.dictEntry.pop(variable.getID())
            self.dictVariable.pop(variable.getID())
        else:
            logging.info(_("The user didn't confirm the deletion of the variable {0}").format(variable.getName()))

    def editVariable(self, variable):
        """editVariable:
                Edit a variable and its representation on the tree row.

                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable
                @param variable: the variable that will be edited.
        """
        questionMsg = _("Click yes to confirm the edition of the variable {0}").format(variable.getName())
        md = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result == Gtk.ResponseType.YES:
            # Edit the variable
            motherNode = variable.findMotherNode(self.field.getVariable())
            motherNode.editChildByID(variable)

            # Update its entry
            entry = self.dictEntry[variable.getID()]
            self.treestore.remove(entry)
            self.registerVariable(self.dictEntry[motherNode.getID()], variable)
        else:
            logging.info(_("The user didn't confirm the edition of the variable {0}").format(variable.getName()))


class VariableCreationController:
    """VariableCreationController:
            Manage a view that allow the user to modify/create a variable by specifying each of its field.
    """

    def __init__(self, item, treeController, variable, rootEntry, editOverCreate):
        """Constructor of DataVariable:
                Called by a click on the tree view of all variables.

                @type item: Gtk.Menuitem
                @param item: the menu item that calls this constructor.
                @type treeController: VariableTreeController
                @param treeController: the controller of the tree view which cause this controller's view to appear.
                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable
                @param variable: the variable that will be modified/to which we will add a child.
                @type rootEntry: Gtk.treerow
                @param rootEntry: the root entry associates to the variable in the treestore.
                @type editOverCreate: boolean
                @param editOverCreate: True if we want to edit the selected variable, false if we want to create a new variable.
        """
        self.treeController = treeController
        self.netzob = self.treeController.netzob
        self.variable = variable
        self.rootEntry = rootEntry
        self.editOverCreate = editOverCreate
        self.view = VariableCreationView(self)
        self.initCallBacks()
        self.runDialog()

    def initCallBacks(self):
        """initCallbacks:
                Init the callbacks.
        """
        self.view.getWidg("variableTypeCombo").connect('changed', self.updateOptions)

    def updateOptions(self, widget=None):
        """updateOptions:
                Update the shown options of the variable creation view to set visible only those which are useful.

                @type widget: Gtk.widget
                @param widget: the widget which modification calls this function.
        """
        strVarType = self.view.getWidg("variableTypeCombo").get_active_text()

        # Node variable
        if strVarType == AggregateVariable.TYPE or strVarType == AlternateVariable.TYPE:
            self.view.getWidg("valueLabel").set_visible(False)
            self.view.getWidg("typeLabel").set_visible(False)
            self.view.getWidg("minLabel").set_visible(False)
            self.view.getWidg("maxLabel").set_visible(False)

            self.view.getWidg("valueEntry").set_visible(False)
            self.view.getWidg("typeCombo").set_visible(False)
            self.view.getWidg("minSpin").set_visible(False)
            self.view.getWidg("maxSpin").set_visible(False)

        # Data variable
        elif strVarType == DataVariable.TYPE:
            self.view.getWidg("valueLabel").set_text("Original Value")
            self.view.getWidg("minLabel").set_text("Minimum number of characters")
            self.view.getWidg("maxLabel").set_text("Maximum number of characters")

            self.view.getWidg("valueLabel").set_visible(True)
            self.view.getWidg("typeLabel").set_visible(True)
            self.view.getWidg("minLabel").set_visible(True)
            self.view.getWidg("maxLabel").set_visible(True)

            self.view.getWidg("valueEntry").set_visible(True)
            self.view.getWidg("typeCombo").set_visible(True)
            self.view.getWidg("minSpin").set_visible(True)
            self.view.getWidg("maxSpin").set_visible(True)

        # Pointing variable
        elif strVarType == ReferencedVariable.TYPE:
            self.view.getWidg("valueLabel").set_text("Pointed ID")

            self.view.getWidg("valueLabel").set_visible(True)
            self.view.getWidg("typeLabel").set_visible(False)
            self.view.getWidg("minLabel").set_visible(False)
            self.view.getWidg("maxLabel").set_visible(False)

            self.view.getWidg("valueEntry").set_visible(True)
            self.view.getWidg("typeCombo").set_visible(False)
            self.view.getWidg("minSpin").set_visible(False)
            self.view.getWidg("maxSpin").set_visible(False)

        # Repeat variable
        elif strVarType == RepeatVariable.TYPE:
            self.view.getWidg("minLabel").set_text("Minimum number of iterations")
            self.view.getWidg("maxLabel").set_text("Maximum number of iterations")

            self.view.getWidg("valueLabel").set_visible(False)
            self.view.getWidg("typeLabel").set_visible(False)
            self.view.getWidg("minLabel").set_visible(True)
            self.view.getWidg("maxLabel").set_visible(True)

            self.view.getWidg("valueEntry").set_visible(False)
            self.view.getWidg("typeCombo").set_visible(False)
            self.view.getWidg("minSpin").set_visible(True)
            self.view.getWidg("maxSpin").set_visible(True)

        else:
            self.view.getWidg("valueLabel").set_visible(False)
            self.view.getWidg("typeLabel").set_visible(False)
            self.view.getWidg("minLabel").set_visible(False)
            self.view.getWidg("maxLabel").set_visible(False)

            self.view.getWidg("valueEntry").set_visible(False)
            self.view.getWidg("typeCombo").set_visible(False)
            self.view.getWidg("minSpin").set_visible(False)
            self.view.getWidg("maxSpin").set_visible(False)

    def runDialog(self):
        """runDialog:
                Run a dialog that allows to modify each definition field of a variable.
        """
        dialog = self.view.getWidg("dialog")
        dialog.show_all()

        if self.editOverCreate:
            # We writes the former values of the variable.
            self.view.getWidg("nameEntry").set_text(self.variable.getName())
            self.view.getWidg("mutableCheck").set_active(self.variable.isMutable())
            self.view.getWidg("randomCheck").set_active(self.variable.isRandom())
            self.setComboText(self.view.getWidg("variableTypeCombo"), self.variable.getVariableType())

            if self.variable.getVariableType() == DataVariable.TYPE:
                self.view.getWidg("valueEntry").set_text(self.variable.bin2str(self.variable.getOriginalValue()))
                self.setComboText(self.view.getWidg("typeCombo"), self.variable.getType().getType())
                self.view.getWidg("minSpin").set_text(str(self.variable.getMinChars()))
                self.view.getWidg("maxSpin").set_text(str(self.variable.getMaxChars()))

            if self.variable.getVariableType() == ReferencedVariable.TYPE:
                self.view.getWidg("valueEntry").set_text(self.variable.getPointedID())

            if self.variable.getVariableType() == RepeatVariable.TYPE:
                self.view.getWidg("minSpin").set_text(str(self.variable.getNumberIterations()[0]))
                self.view.getWidg("maxSpin").set_text(str(self.variable.getNumberIterations()[1]))

        self.updateOptions()
        self.view.getWidg("applyButton").connect("clicked", self.validateChanges, dialog)
        dialog.run()

    def validateChanges(self, widget, dialog):
        """validateChanges:
                Validate the changes that a user has done on a variable.
                Called by a click on the apply button.

                @type widget: Gtk.widget
                @param widget: the widget which calls this function.
                @type dialog: Gtk.dialog
                @param dialog: the dialog which widget calls this function.
        """
        if self.editOverCreate:
            id = self.variable.getID()
        else:
            id = str(uuid.uuid4())

        name = self.view.getWidg("nameEntry").get_text()
        mutable = self.view.getWidg("mutableCheck").get_active()
        random = self.view.getWidg("randomCheck").get_active()
        strVarType = self.view.getWidg("variableTypeCombo").get_active_text()

        variable = None
        # Aggregate variable
        if strVarType == AggregateVariable.TYPE:
            variable = AggregateVariable(id, name, mutable, random)

        # Alternate Variable
        if strVarType == AlternateVariable.TYPE:
            variable = AlternateVariable(id, name, mutable, random)

        # Repeat Variable
        if strVarType == RepeatVariable.TYPE:
            minIterations = int(self.view.getWidg("minSpin").get_text())
            maxIterations = int(self.view.getWidg("maxSpin").get_text())
            variable = RepeatVariable(id, name, mutable, random, None, minIterations, maxIterations)

        # Data variable
        if strVarType == DataVariable.TYPE:
            originalValue = str(self.view.getWidg("valueEntry").get_text())
            vtype = AbstractType.makeType(self.view.getWidg("typeCombo").get_active_text())
            minChars = int(self.view.getWidg("minSpin").get_text())
            maxChars = int(self.view.getWidg("maxSpin").get_text())
            variable = DataVariable(id, name, mutable, random, vtype, originalValue, minChars, maxChars)

        # Pointing variable
        if strVarType == ReferencedVariable.TYPE:
            pointedID = str(self.view.getWidg("valueEntry").get_text())
            variable = ReferencedVariable(id, name, mutable, random, pointedID)

        if variable is not None:
            self.treeController.field.getSymbol().setDefault(False)
            if self.editOverCreate:
                # We transform a node variable into a node variable.
                if (self.variable.getVariableType() == AggregateVariable.TYPE or self.variable.getVariableType() == AlternateVariable.TYPE) and (variable.getVariableType() == AggregateVariable.TYPE or variable.getVariableType() == AlternateVariable.TYPE):
                    children = self.variable.getChildren()
                    self.variable = variable
                    for child in children:
                        self.variable.addChild(child)
                # We transform a repeat variable into a node variable.
                elif (self.variable.getVariableType() == RepeatVariable.TYPE) and (variable.getVariableType() == AggregateVariable.TYPE or variable.getVariableType() == AlternateVariable.TYPE):
                    child = self.variable.getChild()
                    self.variable = variable
                    self.variable.addChild(child)
                # We transform a repeat variable into a repeat variable.
                elif (self.variable.getVariableType() == RepeatVariable.TYPE) and (variable.getVariableType() == RepeatVariable.TYPE):
                    child = self.variable.getChild()
                    self.variable = variable
                    self.variable.setChild(child)
                # We do not manage/save children.
                else:
                    self.variable = variable
                self.treeController.editVariable(variable)
            else:
                self.variable.addChild(variable)
                self.treeController.treestore.append(self.rootEntry, [str(variable.getID()), variable.toString()])
                self.treeController.dictVariable[str(variable.getID())] = variable
        dialog.destroy()

    def setComboText(self, combo, text):
        model = combo.get_model()
        iter = model.get_iter_first()
        while True:
            if str(model[iter][0]) == text:
                combo.set_active_iter(iter)
                break
            if model.iter_next(iter) is not None:
                iter = model.iter_next(iter)
            else:
                break
