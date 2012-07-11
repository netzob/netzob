# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#| Global Imports                                                            |
#+---------------------------------------------------------------------------+
import logging
import gtk
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Local Imports                                                             |
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.Extensions.GlobalMenuExtension import GlobalMenuExtension
from netzob.Common.Menu import Menu
from netzob_plugins.Exporters.PeachExporter.PeachExportController import PeachExportController


class GlobalMenuEntryPoint(GlobalMenuExtension):
    """
        GlobalMenuEntryPoint:
            Entry points in the menu for the peach exporter plugin.

    """

    def __init__(self, netzob):
        """
            Constructor of GlobalMenuEntryPoint:

                @type netzob: netzob.NetzobGUI.NetzobGUI
                @param netzob: the main netzob project.

        """
        self.netzob = netzob

    def getMenuEntries(self):
        """
            getMenuEntries:

                @return type: string tuple list
                @return: the menu entry points.

        """
        menuEntries = [
                       (Menu.PATH_PROJECT_EXPORTPROJECT + "/" + _("Peach pit file"), None, self.executeAction, 0, None)
                       ]
        return menuEntries

    def executeAction(self, widget, data):
        """
            executeAction:
                Launch the Peach exporter GUI.

                @type widget: Gtk.widget
                @param widget: Not used.
                @type data:
                @param data: Not used.

        """
        PeachExportController(self.netzob)
