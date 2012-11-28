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
#| Standard library imports
#+----------------------------------------------
from gettext import gettext as _
import os.path
import logging
import shutil

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob import NetzobResources
from netzob.Common.Workspace import Workspace


class ResourcesConfigurationException(Exception):
    pass


class ResourcesConfiguration(object):
    """Configure and verify all the resources"""

    LOCALFILE = ".netzob"
    DELIMITOR_LOCALFILE = "="
    VAR_WORKSPACE_LOCALFILE = "workspace"
    VAR_API_KEY_LOCALFILE = "reporterApiKey"

    @staticmethod
    #+----------------------------------------------
    #| initializeResources:
    #+----------------------------------------------
    def initializeResources():
        # We search for the
        # STATIC resources (images, documentations, ...)
        # USER resources (workspaces, configurations, ...)

        # Normaly, on first execution only the static path exists (created
        # during the installation process)
        # While, on everyday execution, both the static and the userpath should exists

        staticPath = ResourcesConfiguration.verifyStaticResources()
        if staticPath is None:
            logging.fatal("The static resources were not found !")
            return False
        return True

    @staticmethod
    def generateUserFile(worskpace, apiKey=None):
        """Write the path to the workspace and the apiKey (if provided)
        to the netzob configuration associated with user (~/.netzob)."""
        # the user has specified its home directory so we store it in
        # a dedicated local file
        localFilePath = os.path.join(os.path.expanduser("~"), ResourcesConfiguration.LOCALFILE)
        # create or update the content
        localFile = open(localFilePath, 'w')
        localFile.write(ResourcesConfiguration.VAR_WORKSPACE_LOCALFILE + ResourcesConfiguration.DELIMITOR_LOCALFILE + str(os.path.abspath(worskpace)) + '\n\r')
        if apiKey is not None:
            localFile.write(ResourcesConfiguration.VAR_API_KEY_LOCALFILE + ResourcesConfiguration.DELIMITOR_LOCALFILE + str(apiKey) + '\n\r')
        localFile.close()

    @staticmethod
    def saveAPIKey(apiKey):
        """Save the provided API key in the configuration file of the user.
        It retrieves the value of the workspace from the current file and rewrite it
        to include the api key."""
        localFilePath = os.path.join(os.path.expanduser("~"), ResourcesConfiguration.LOCALFILE)
        workspaceDir = ResourcesConfiguration.extractWorkspaceDirFromFile(localFilePath)
        if workspaceDir is not None:
            ResourcesConfiguration.generateUserFile(workspaceDir, apiKey)
            return True
        return False

    @staticmethod
    def createWorkspace(path):
        logging.info("Hosting workspace on " + str(path))
        # we do nothing if a global config file already exists
        if os.path.isfile(os.path.join(path, Workspace.CONFIGURATION_FILENAME)):
            return
        else:
            workspace = Workspace.createWorkspace(_("New Workspace"), path)
            return workspace

    @staticmethod
    def verifyStaticResources():
        staticPath = NetzobResources.STATIC_DIR
        if staticPath == "":
            return None
        localStaticPath = NetzobResources.LOCAL_STATIC_DIR
        if localStaticPath == "":
            return None

        logging.debug("  System static path declared: " + staticPath)
        logging.debug("  Local static path declared: " + localStaticPath)
        if (os.path.isdir(localStaticPath)):
            logging.debug("  Static path used: " + localStaticPath)
            return localStaticPath
        elif (os.path.isdir(staticPath)):
            logging.debug("  Static path used: " + staticPath)
            return staticPath

        return None

    @staticmethod
    def verifyAndReturnWorkspaceDir():
        # the user has specified its home directory so we store it in
        # a dedicated local file
        localFilePath = os.path.join(os.path.expanduser("~"), ResourcesConfiguration.LOCALFILE)
        logging.debug("  Local configuration file used: " + str(localFilePath))
        workspacePath = ResourcesConfiguration.extractWorkspaceDirFromFile(localFilePath)
        logging.debug("  Workspace path declared in configuration file: " + str(workspacePath))

        # Workspace not declared
        if workspacePath is None:
            logging.debug("  Workspace path declared does not exist: " + str(workspacePath))
            return None
        # is the workspace a directory
        if not os.path.isdir(workspacePath):
            logging.warn("  The specified workspace's path (" + str(workspacePath) + ") is not valid : its not a directory.")
            return None
        # is it readable
        if not os.access(workspacePath, os.R_OK):
            logging.warn("  The specified workspace's path (" + str(workspacePath) + ") is not readable.")
            return None
        # is it writable
        if not os.access(workspacePath, os.W_OK):
            logging.warn("  The specified workspace's path (" + str(workspacePath) + ") is not writable.")
            return None

        logging.debug("  Workspace R/W access is valid: " + str(workspacePath))
        return workspacePath

    @staticmethod
    def extractWorkspaceDirFromFile(localFilePath):
        workspacePath = None
        if os.path.isfile(localFilePath):
            localFile = open(localFilePath, 'r')

            for line in localFile:
                strippedLine = line.rstrip('\n\r')
                indexDelimitor = strippedLine.find(ResourcesConfiguration.DELIMITOR_LOCALFILE)
                if indexDelimitor > 0 and strippedLine[:indexDelimitor] == ResourcesConfiguration.VAR_WORKSPACE_LOCALFILE and len(strippedLine[indexDelimitor + 1:]) > 0:
                    workspacePath = strippedLine[indexDelimitor + 1:]
                    break
            localFile.close()
        return workspacePath

    @staticmethod
    def extractAPIKeyDefinitionFromLocalFile():
        localFilePath = os.path.join(os.path.expanduser("~"), ResourcesConfiguration.LOCALFILE)
        apiKey = None
        if os.path.isfile(localFilePath):
            localFile = open(localFilePath, 'r')

            for line in localFile:
                strippedLine = line.strip('\n\r')
                indexDelimitor = strippedLine.find(ResourcesConfiguration.DELIMITOR_LOCALFILE)
                if indexDelimitor > 0 and strippedLine[:indexDelimitor] == ResourcesConfiguration.VAR_API_KEY_LOCALFILE and len(strippedLine[indexDelimitor + 1:]) > 0:
                    apiKey = strippedLine[indexDelimitor + 1:]
                    break
            localFile.close()
        return apiKey

    @staticmethod
    def getStaticResources():
        if (os.path.isdir(NetzobResources.LOCAL_STATIC_DIR)):
            return NetzobResources.LOCAL_STATIC_DIR
        elif (os.path.isdir(NetzobResources.STATIC_DIR)):
            return NetzobResources.STATIC_DIR

    @staticmethod
    def getPluginsStaticResources():
        if (os.path.isdir(NetzobResources.LOCAL_PLUGINS_STATIC_DIR)):
            return NetzobResources.LOCAL_PLUGINS_STATIC_DIR
        elif (os.path.isdir(NetzobResources.PLUGINS_STATIC_DIR)):
            return NetzobResources.PLUGINS_STATIC_DIR
        else:
            raise ResourcesConfigurationException(_("Unable to find plugins static resources."))

    @staticmethod
    def getWorkspaceDir():
        if NetzobResources.WORKSPACE_DIR is None:
            return ResourcesConfiguration.verifyAndReturnWorkspaceDir()
        else:
            return NetzobResources.WORKSPACE_DIR

    @staticmethod
    def getLocaleLocation():
        if (os.path.isdir(NetzobResources.LOCAL_LOCALES_DIR)):
            return NetzobResources.LOCAL_LOCALES_DIR
        elif (os.path.isdir(NetzobResources.LOCALES_DIR)):
            return NetzobResources.LOCALES_DIR
