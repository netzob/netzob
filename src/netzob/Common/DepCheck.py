# -*- coding: utf-8 -*-

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
#| Global Imports
#+---------------------------------------------------------------------------+
import logging
import sys
from netzob import NetzobResources


class DepCheck(object):
    """Dependency checker.
    Provides multiple static method to check is required and optionnal
    dependency are available."""

    @staticmethod
    def checkRequiredDependency():
        # Check the C extensions
        if not DepCheck.checkCExtensions():
            return False

        return True

    @staticmethod
    def checkCExtensions():
        # Verify we can load the lib Needleman
        try:
            from netzob import _libNeedleman
        except ImportError as e:
            logging.error("Impossible to import the libNeedleman: %s", e)
            return False

        pathToImportedLib = "Unknown path"
        for m in list(sys.modules.keys()):
            if m == "_libNeedleman":
                pathToImportedLib = sys.modules[m].__file__
                logging.debug("Imported _libNeedleman from %s",
                              pathToImportedLib)
        try:
            BIDNeedleman = _libNeedleman.getBID()
            if BIDNeedleman != NetzobResources.BID and NetzobResources.BID != "$BID":
                logging.error("Binary Identifier is %s (expected %s).",
                              BIDNeedleman, NetzobResources.BID)
                logging.error(
                    "The loaded libNeedleman library is deprecated, please rebuild it."
                )
                return False
        except AttributeError:
            logging.error(
                "The _libNeedleman imported (%s) is not the expected one and do not provide all the required methods.",
                pathToImportedLib)
            return False

        # Verify we can load the lib ScoreComputation
        try:
            from netzob import _libScoreComputation
        except ImportError as e:
            logging.error("Impossible to import the libScoreComputation: %s",
                          e)
            return False

        pathToImportedLib = "Unknown path"
        for m in list(sys.modules.keys()):
            if m == "_libScoreComputation":
                pathToImportedLib = sys.modules[m].__file__
                logging.debug("Imported _libScoreComputation from %s",
                              pathToImportedLib)
        try:
            BIDScoreComputation = _libScoreComputation.getBID()
            if BIDScoreComputation != NetzobResources.BID and NetzobResources.BID != "$BID":
                logging.error("Binary Identifier is %s (expected %s).",
                              BIDScoreComputation, NetzobResources.BID)
                logging.error(
                    "The loaded libScoreComputation library is deprecated, please rebuild it."
                )
                return False
        except AttributeError:
            logging.error(
                "The _libScoreComputation imported (%s) is not the expected one and do not provide all the required methods.",
                pathToImportedLib)
            return False

        # Verify we can load the lib Interface
        try:
            from netzob import _libInterface
        except ImportError as e:
            logging.error("Impossible to import the libInterface: %s", e)
            return False

        pathToImportedLib = "Unknown path"
        for m in list(sys.modules.keys()):
            if m == "_libInterface":
                pathToImportedLib = sys.modules[m].__file__
                logging.debug("Imported _libInterface from %s",
                              pathToImportedLib)
        try:
            BIDInterface = _libInterface.getBID()
            if BIDInterface != NetzobResources.BID and NetzobResources.BID != "$BID":
                logging.error("Binary Identifier is %s (expected %s).",
                              BIDInterface, NetzobResources.BID)
                logging.error(
                    "The loaded libInterface library is deprecated, please rebuild it."
                )
                return False
        except AttributeError:
            logging.error(
                "The _libInterface imported (%s) is not the expected one and do not provide all the required methods.",
                pathToImportedLib)
            return False

        # # Verify we can load the lib Regex
        # try:
        #     from netzob import _libRegex
        # except ImportError:
        #     logging.error("Impossible to import the libRegex")
        #     return False

        # pathToImportedLib = "Unknown path"
        # for m in sys.modules.keys():
        #     if m == "_libRegex":
        #         pathToImportedLib = sys.modules[m].__file__
        #         logging.debug("Imported _libRegex from {0}".format(pathToImportedLib))
        # try:
        #     BIDRegex = _libRegex.getBID()
        #     if BIDRegex != NetzobResources.BID and NetzobResources.BID != "$BID":
        #         logging.error("Binary Identifier is {0} (expected {1}).".format(BIDRegex, NetzobResources.BID))
        #         logging.error("The loaded libRegex library is deprecated, please rebuild it.")
        #         return False
        # except AttributeError:
        #     logging.error("The _libScoreComputation imported ({0}) is not the expected one and do not provide all the required methods.".format(pathToImportedLib))
        #     return False

        if NetzobResources.BID == "$BID":
            logging.warning(
                "The current executed python code has not been built using setup.py, hence it's not possible to compare the BID of executed libs."
            )

        return True
