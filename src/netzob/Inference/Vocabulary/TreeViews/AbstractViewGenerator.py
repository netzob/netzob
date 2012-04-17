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
import logging

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| AbstractTreeViewgenerator:
#|   abstract treeview
#+---------------------------------------------------------------------------+
class AbstractViewGenerator():

    #+-----------------------------------------------------------------------+
    #| Constructor:
    #| @param id : id of the view
    #| @param name : name of the view
    #+-----------------------------------------------------------------------+
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.active = False
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Vocabulary.TreeViews.AbstractViewGenerator.py')

    #+-----------------------------------------------------------------------+
    #| getWidget
    #|     Abstract method to retrieve the associated widget
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def getWidget(self):
        self.log.error("The view class doesn't have an associated getWidget !")
        raise NotImplementedError("The view class doesn't have an associated getWidget !")

    #+-----------------------------------------------------------------------+
    #| show
    #|   Display the widget
    #+-----------------------------------------------------------------------+
    def show(self):
        self.activate()
        self.getWidget().show_all()

    #+-----------------------------------------------------------------------+
    #| hide
    #|   Hide the widget
    #+-----------------------------------------------------------------------+
    def hide(self):
        self.deactivate()
        self.getWidget().hide_all()

    #+-----------------------------------------------------------------------+
    #| GETTERS & SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def isActive(self):
        return self.active

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
