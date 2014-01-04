# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
import logging
import os

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobAbstractView import NetzobAbstractView


class ApplicativeDataManagerView(NetzobAbstractView):

    def __init__(self, controller):
        gladeFile = os.path.join("traceManager", "applicativeDataManagerDialog.glade")
        super(ApplicativeDataManagerView, self).__init__(controller, gladeFile, root="applicativeDataManagerWindow", parent=None)
        self._getObjects(['applicativeDataTreeStore', 'applicativeDataTreeView', 'importApplicationDataDialog'])
        self.logger = logging.getLogger(__name__)
        self.refresh()

    def refresh(self):
        self.applicativeDataTreeStore.clear()
        # Fullfill the treeview with current applicative data of the session
        for applicativeData in self.getController().getSession().getApplicativeData():
            self.applicativeDataTreeStore.append([str(applicativeData.getID()), applicativeData.getName(), applicativeData.getType(), applicativeData.getValue()])

    def getSelectedApplicativeData(self):
        """getSelectedApplicativeData:
        Computes user's selection on applicative data treestore and retrives the associated
        applicativeData by their ID.
        @return the list of selected applicative data (list can be empty)"""
        (model, rows) = self.applicativeDataTreeView.get_selection().get_selected_rows()
        selectedApplicativeData = []
        if rows is not None:
            for row in rows:
                applicativeData = self.controller.getSession().getApplicativeDataByID(model[row][0])
                if applicativeData is not None:
                    selectedApplicativeData.append(applicativeData)

        return selectedApplicativeData
