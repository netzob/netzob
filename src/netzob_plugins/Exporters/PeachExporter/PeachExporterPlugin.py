# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#| Global Imports                                                            |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
import uuid
import random

#+---------------------------------------------------------------------------+
#| Local Imports                                                             |
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.ExporterPlugin import ExporterPlugin
from netzob_plugins.Exporters.PeachExporter.EntryPoints.GlobalMenuEntryPoint import GlobalMenuEntryPoint
from netzob_plugins.Exporters.PeachExporter.PeachExportController import PeachExportController


class PeachExporterPlugin(ExporterPlugin):
    """
        PeachExporterPlugin:
            Export netzob symbols into Peach pit files.
            Simplify the construction of a fuzzer with Peach.

    """
    __plugin_name__ = "PeachExporter"
    __plugin_version__ = "0.1"
    __plugin_description__ = _("Provide the possibility to export netzob symbols to Peach pit files.")
    __plugin_author__ = "Benjamin Dufour <benjamin.dufour@amossys.fr>"

    def __init__(self, netzob):
        """
            Constructor of PeachExporterPlugin:

                @type netzob: netzob.NetzobGUI.NetzobGUI
                @param netzob: the main netzob project.

        """
        ExporterPlugin.__init__(self, netzob)
        self.entryPoints = [GlobalMenuEntryPoint(self.getNetzob())]

    def getName(self):
        """
            getName:

                @return type: string
                @return: the plugin name.

        """
        return self.__plugin_name__

    def getVersion(self):
        """
            getVersion:

            @return type: string
            @return: the plugin version.

        """
        return self.__plugin_version__

    def getDescription(self):
        """
            getDescription:

            @return type: string
            @return: a plugin description.

        """
        return self.__plugin_description__

    def getAuthor(self):
        """
            getAuthor:

            @return type: string
            @return: the plugin author.

        """
        return self.__plugin_author__

    def getEntryPoints(self):
        """
            getEntryPoints:

            @return type: netzob_plugins.Exporters.PeachExporter.EntryPoints.GlobalMenuEntryPoint.GlobalMenuEntryPoint
            @return: the plugin entry point, so it can be linked to the netzob project.

        """
        return self.entryPoints

    def setVal(self, val):
        """
            setVal:
                Useless function.

            @type val:
            @param val:

        """
        self.val = val
