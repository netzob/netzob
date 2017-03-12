#-*- coding: utf-8 -*-

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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
import abc

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class AbstractMementoCreator(object, metaclass=abc.ABCMeta):
    """Parent class of objects to save for Undo/Redo.
    
    This abstract class must be inherited by all the objects which need to be saved for Undo/Redo processes.
    These objects have to provide two methods, storeInMemento and restoreFromMemento both used to save and restore current state of the object."""

    @abc.abstractmethod
    def storeInMemento(self):
        """This method creates a memento to represent the current state of object.
        
        This memento should be stored in the UndoRedo action stack and might be used as a parameter of the restoreFromMemento method.
        
        :returns: the created memento representing current object
        :rtype: netzob.Common.Utils.UndoRedo.AbstractMemento.AbstractMemento
        
        """
        return

    @abc.abstractmethod
    def restoreFromMemento(self, memento):
        """This method restores current object internals with provided memento.

        The provided memento should be created by the storeInMemento method and represents the current object.
        It returns the current state of the object before the restore operation
        
        :param memento: memento containing internals to set in current object to restore it.
        :type memento: netzob.Common.Utils.UndoRedo.AbstractMemento.AbstractMemento
        :returns: the memento of current object before executing the restore process
        :rtype: netzob.Common.Utils.UndoRedo.AbstractMemento.AbstractMemento
        
        """
        return
