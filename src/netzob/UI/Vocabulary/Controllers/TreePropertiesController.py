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
#| Global Imports
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
from gi.repository import Gtk
import uuid

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Field import Field
from netzob.UI.Vocabulary.Views.TreePropertiesView import TreePropertiesView
from netzob.Common.ProjectConfiguration import ProjectConfiguration


#+---------------------------------------------------------------------------+
#| TreePropertiesController:
#|     update and generates the treeview and its
#|     treestore dedicated to the properties
#+---------------------------------------------------------------------------+
class TreePropertiesController(object):

    #+-----------------------------------------------------------------------+
    #| Constructor:
    #+-----------------------------------------------------------------------+
    def __init__(self, netzob, vocabularyController):
        self.netzob = netzob
        self.vocabularyController = vocabularyController
        self.log = logging.getLogger('netzob.UI.Vocabulary.Controllers.TreePropertiesController.py')
        self.treeview = None
        self.view = TreePropertiesView(self.netzob)
        self.initCallbacks()

    def initCallbacks(self):
        pass

    def getView(self):
        return self.view

    #+----------------------------------------------
    #| default:
    #|         Update the treestore in normal mode
    #+----------------------------------------------
    def update(self):
        if self.netzob.getCurrentProject() is not None:
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_PROPERTIES)
            if isActive:
                self.view.show()
            else:
                self.view.hide()
                return

        self.view.treestore.clear()

        if self.getSelectedMessage() is None:
            return

        for property in self.getSelectedMessage().getProperties():
            propertyName = str(property[0])
            propertyFormat = str(property[1])
            propertyValue = str(property[2])
            self.view.treestore.append(None, [propertyName, propertyValue, propertyFormat])

    #+----------------------------------------------
    #| clear:
    #|         Clear the class
    #+----------------------------------------------
    def clear(self):
        self.view.treestore.clear()

    #+----------------------------------------------
    #| error:
    #|         Update the treestore in error mode
    #+----------------------------------------------
    def error(self):
        self.log.warning(_("The treeview for the properties is in error mode"))
        pass

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getSelectedMessage(self):
        return self.vocabularyController.treeMessageController.selectedMessage

    def getTreeview(self):
        return self.view.treeview

    def getScrollLib(self):
        return self.view.scroll

    def getWidget(self):
        return self.view.scroll

    #+----------------------------------------------
    #| SETTERS:
    #+----------------------------------------------
    def setTreeview(self, treeview):
        self.view.treeview = treeview

    def setScrollLib(self, scroll):
        self.view.scroll = scroll
