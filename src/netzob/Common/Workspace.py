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
#| Standard library imports
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
import os
import datetime
import re
from lxml.etree import ElementTree
from lxml import etree
import shutil
import uuid


#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.XSDResolver import XSDResolver
from netzob.Common.ImportedTrace import ImportedTrace
from netzob.Common.Functions.Transformation.Base64Function import Base64Function
from netzob.Common.Functions.Transformation.GZipFunction import GZipFunction
from netzob.Common.Functions.Transformation.BZ2Function import BZ2Function
from netzob.Common.Functions.RenderingFunction import RenderingFunction

WORKSPACE_NAMESPACE = "http://www.netzob.org/workspace"
COMMON_NAMESPACE = "http://www.netzob.org/common"


def loadWorkspace_0_1(workspacePath, workspaceFile):

    # Parse the XML Document as 0.1 version
    tree = ElementTree()

    tree.parse(workspaceFile)
    xmlWorkspace = tree.getroot()
    wsName = xmlWorkspace.get('name', 'none')
    wsCreationDate = TypeConvertor.xsdDatetime2PythonDatetime(xmlWorkspace.get('creation_date'))

    # Parse the configuration to retrieve the main paths
    xmlWorkspaceConfig = xmlWorkspace.find("{" + WORKSPACE_NAMESPACE + "}configuration")
    pathOfTraces = xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}traces").text

    pathOfLogging = None
    if xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}logging") is not None and xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}logging").text is not None and len(xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}logging").text) > 0:
        pathOfLogging = xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}logging").text

    pathOfPrototypes = None
    if xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}prototypes") is not None and xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}prototypes").text is not None and len(xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}prototypes").text) > 0:
        pathOfPrototypes = xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}prototypes").text

    lastProject = None
    if xmlWorkspace.find("{" + WORKSPACE_NAMESPACE + "}projects") is not None:
        xmlProjects = xmlWorkspace.find("{" + WORKSPACE_NAMESPACE + "}projects")
        if xmlProjects.get("last", "none") != "none":
            lastProject = xmlProjects.get("last", "none")

    # Instantiation of the workspace
    workspace = Workspace(wsName, wsCreationDate, workspacePath, pathOfTraces, pathOfLogging, pathOfPrototypes)

    # Load the already imported traces
    if xmlWorkspace.find("{" + WORKSPACE_NAMESPACE + "}traces") is not None:
        xmlTraces = xmlWorkspace.find("{" + WORKSPACE_NAMESPACE + "}traces")
        for xmlTrace in xmlTraces.findall("{" + WORKSPACE_NAMESPACE + "}trace"):
            trace = ImportedTrace.loadTrace(xmlTrace, WORKSPACE_NAMESPACE, COMMON_NAMESPACE, "0.1", workspace.getPathOfTraces())
            if trace is not None:
                workspace.addImportedTrace(trace)

    # Reference the projects
    if xmlWorkspace.find("{" + WORKSPACE_NAMESPACE + "}projects") is not None:
        for xmlProject in xmlWorkspace.findall("{" + WORKSPACE_NAMESPACE + "}projects/{" + WORKSPACE_NAMESPACE + "}project"):
            project_path = xmlProject.get("path")
            workspace.referenceProject(project_path)
            if project_path == lastProject and lastProject is not None:
                workspace.referenceLastProject(lastProject)

    # Reference the functions
    if xmlWorkspace.find("{" + WORKSPACE_NAMESPACE + "}functions") is not None:
        for xmlFunction in xmlWorkspace.findall("{" + WORKSPACE_NAMESPACE + "}functions/{" + WORKSPACE_NAMESPACE + "}function"):
            function = RenderingFunction.loadFromXML(xmlFunction, WORKSPACE_NAMESPACE, "0.1")
            if function is not None:
                workspace.addCustomTransformationFunction(function)

    enableBugReporting = False
    if xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}enable_bug_reporting") is not None and xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}enable_bug_reporting").text is not None and len(xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}enable_bug_reporting").text) > 0:
        val = xmlWorkspaceConfig.find("{" + WORKSPACE_NAMESPACE + "}enable_bug_reporting").text
        if val == "true":
            enableBugReporting = True
    workspace.setEnableBugReporting(enableBugReporting)

    return workspace


class WorkspaceException(Exception):
    pass


class Workspace(object):
    """Class definition of a Workspace"""

    # The name of the configuration file
    CONFIGURATION_FILENAME = "workspace.xml"

    # /!\ WARNING:
    # The dict{} which defines the parsing function associated with each schema
    # is added to the end of the document

    #+-----------------------------------------------------------------------+
    #| Constructor
    #| @param path : path of the workspace
    #+-----------------------------------------------------------------------+
    def __init__(self, name, creationDate, path, pathOfTraces, pathOfLogging, pathOfPrototypes, lastProjectPath=None, importedTraces={}):
        self.name = name
        self.path = os.path.abspath(path)
        self.creationDate = creationDate
        self.projects_path = []
        self.pathOfTraces = os.path.join(self.path, pathOfTraces)
        self.pathOfLogging = os.path.join(self.path, pathOfLogging)
        self.pathOfPrototypes = os.path.join(self.path, pathOfPrototypes)
        self.lastProjectPath = lastProjectPath
        self.importedTraces = importedTraces
        self.customTransformationFunctions = []
        self.enableBugReporting = False

    def getNameOfProjects(self):
        nameOfProjects = []
        for project_path in self.getProjectsPath():
            from netzob.Common.Project import Project
            projectName = Project.getNameOfProject(self, project_path)
            if projectName is not None:
                nameOfProjects.append((projectName, project_path))
        return nameOfProjects

    def getProjects(self):
        projects = []
        for project_path in self.getProjectsPath():
            from netzob.Common.Project import Project
            project = Project.loadProject(self, project_path)
            if project is not None:
                projects.append(project)
        return projects

    def getLastProject(self):
        if self.lastProjectPath is None:
            return None

        from netzob.Common.Project import Project
        project = Project.loadProject(self, self.lastProjectPath)
        return project

    def setEnableBugReporting(self, enable):
        self.enableBugReporting = enable

    def referenceLastProject(self, lastProject):
        self.lastProjectPath = lastProject

    def getImportedTraces(self):
        return self.importedTraces.values()

    def getImportedTrace(self, traceId):
        """Retrieve a specific trace, which identifier is traceId."""

        try:
            return self.importedTraces[traceId]
        except KeyError:
            raise WorkspaceException("Unable to find the requested trace ({0})".format(traceId))

    def addImportedTrace(self, importedTrace):
        self.importedTraces.update({importedTrace.id: importedTrace})

    def removeImportedTrace(self, importedTrace):
        ImportedTrace.deleteTrace(importedTrace, self.pathOfTraces)
        self.importedTraces.pop(importedTrace.id)

    def newEmptyImportedTrace(self, name, description=""):
        """This function is in charge of creating an empty
        `ImportedTrace`.

        :param name: 'name' of the new trace.
        :param description (optional): description of the new
        trace."""

        newTrace = ImportedTrace(str(uuid.uuid4()),
                                 datetime.datetime.now(),
                                 "UNKNOWN",
                                 description,
                                 name)

        self.addImportedTrace(newTrace)

        return newTrace

    def mergeImportedTraces(self, traceIds, name, keep=True):
        """This methods allows to merge multiple traces. The merged
        traces gets a new unique id.

        If the 'keep' parameter is True, a copy of the initial traces
        is kept.

        We retrieve the 'ImportedTrace' object from its ID. Then we
        merge all traces' messages and sessions into a new
        'ImportedTrace'."""

        messages = {}
        sessions = {}
        names = []
        types = []

        for traceId in traceIds:
            trace = self.getImportedTrace(traceId)

            messages.update(trace.messages)
            sessions.update(trace.sessions)
            names.append("'{0}'".format(trace.name))

            # If the type is already a multiple type merge, types are
            # comma separated values.
            types.extend(trace.type.split(";"))

            if keep is False:
                self.removeImportedTrace(trace)

        # The type of the new trace is a list of the multiple types of
        # the traces to be merged.
        newTraceType = "{0}".format(";".join(set(types)))
        description = "Merge of traces {0} and {1}".format(', '.join(names[:-1]), names[-1])

        newTrace = ImportedTrace(str(uuid.uuid4()),
                                 datetime.datetime.now(),
                                 newTraceType,
                                 description,
                                 name)
        newTrace.messages = messages
        newTrace.sessions = sessions

        self.addImportedTrace(newTrace)

        return newTrace

    def getTransformationFunctions(self):
        """Computes and returns the list of available functions"""

        functions = []
        functions.append(Base64Function(_("Base64 Function")))
        functions.append(GZipFunction(_("GZip Function")))
        functions.append(BZ2Function(_("BZ2 Function")))
        functions.extend(self.customTransformationFunctions)
        return functions

    def getCustomFunctions(self):
        return self.customTransformationFunctions

    def addCustomTransformationFunction(self, function):
        found = False
        for f in self.customTransformationFunctions:
            if f.getName() == function.getName():
                found = True
                break
        if not found:
            self.customTransformationFunctions.append(function)

    #+-----------------------------------------------------------------------+
    #| referenceProject:
    #|     reference a project in the workspace
    #+-----------------------------------------------------------------------+
    def referenceProject(self, project_path):
        path = project_path
        if not path in self.projects_path:
            self.projects_path.append(path)
        else:
            logging.warn("The project declared in {0} is already referenced in the workspace.". format(path))

    def dereferenceProject(self, project_path):
        if not project_path in self.projects_path:
            raise WorkspaceException("The project '{0}' is not declared in the workspace".format(project_path))

        self.projects_path.remove(project_path)

    def saveConfigFile(self, overrideTraces=[]):
        """This functions allows to save the current (and only)
        instance of the Workspace. You can supply a list of traces
        that should be written on-disk through the `overrideTraces`
        variable. This allows to override specific traces that where
        modified.

        :param overrideTraces: a list of trace identifiers that should
        be written on-disk, even if they already exists.
        """

        workspaceFile = os.path.join(self.path, Workspace.CONFIGURATION_FILENAME)

        logging.info("Save the config file of the workspace {0} in {1}".format(self.getName(), workspaceFile))

        # Register the namespace
        etree.register_namespace('netzob', WORKSPACE_NAMESPACE)
        etree.register_namespace('netzob-common', COMMON_NAMESPACE)

        # Dump the file
        root = etree.Element("{" + WORKSPACE_NAMESPACE + "}workspace")
        root.set("creation_date", TypeConvertor.pythonDatetime2XSDDatetime(self.getCreationDate()))
        root.set("name", str(self.getName()))

        xmlWorkspaceConfig = etree.SubElement(root, "{" + WORKSPACE_NAMESPACE + "}configuration")

        relTracePath = os.path.relpath(self.getPathOfTraces(), self.path)
        xmlTraces = etree.SubElement(xmlWorkspaceConfig, "{" + WORKSPACE_NAMESPACE + "}traces")
        xmlTraces.text = str(self.getPathOfTraces())

        xmlLogging = etree.SubElement(xmlWorkspaceConfig, "{" + WORKSPACE_NAMESPACE + "}logging")
        xmlLogging.text = str(self.getPathOfLogging())

        xmlPrototypes = etree.SubElement(xmlWorkspaceConfig, "{" + WORKSPACE_NAMESPACE + "}prototypes")
        xmlPrototypes.text = str(self.getPathOfPrototypes())

        xmlPrototypes = etree.SubElement(xmlWorkspaceConfig, "{" + WORKSPACE_NAMESPACE + "}enable_bug_reporting")
        xmlPrototypes.text = str(self.enableBugReporting).lower()

        xmlWorkspaceProjects = etree.SubElement(root, "{" + WORKSPACE_NAMESPACE + "}projects")
        for projectPath in self.getProjectsPath():
            xmlProject = etree.SubElement(xmlWorkspaceProjects, "{" + WORKSPACE_NAMESPACE + "}project")
            xmlProject.set("path", projectPath)

        xmlWorkspaceImported = etree.SubElement(root, "{" + WORKSPACE_NAMESPACE + "}traces")
        for importedTrace in self.getImportedTraces():
            # overrideTraces variable contains the list of
            # ImportedTraces that should be overriden. This is useful
            # in case of message removal for example.
            forceOverride = (importedTrace.id in overrideTraces)

            importedTrace.save(xmlWorkspaceImported, WORKSPACE_NAMESPACE, COMMON_NAMESPACE,
                               os.path.join(self.path, self.getPathOfTraces()), forceOverride)

        xmlWorkspaceFunctions = etree.SubElement(root, "{" + WORKSPACE_NAMESPACE + "}functions")
        for function in self.getCustomFunctions():
            function.save(xmlWorkspaceFunctions, WORKSPACE_NAMESPACE)

        tree = ElementTree(root)
        tree.write(workspaceFile, pretty_print=True)

    @staticmethod
    def createWorkspace(name, path):
        tracesPath = "traces"
        projectsPath = "projects"
        prototypesPath = "prototypes"
        loggingPath = "logging"
        pathOfLogging = "logging/logging.conf"

        # we create a "traces" directory if it doesn't yet exist
        if not os.path.isdir(os.path.join(path, tracesPath)):
            os.mkdir(os.path.join(path, tracesPath))

        # we create a "projects" directory if it doesn't yet exist
        if not os.path.isdir(os.path.join(path, projectsPath)):
            os.mkdir(os.path.join(path, projectsPath))

        # we create the "prototypes" directory if it doesn't yet exist
        if not os.path.isdir(os.path.join(path, prototypesPath)):
            os.mkdir(os.path.join(path, prototypesPath))
            # we upload in it the default repository file
            from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
            staticRepositoryPath = os.path.join(os.path.join(ResourcesConfiguration.getStaticResources(), "defaults"), "repository.xml.default")
            shutil.copy(staticRepositoryPath, os.path.join(os.path.join(path, prototypesPath), "repository.xml"))

        # we create the "logging" directory if it doesn't yet exist
        if not os.path.isdir(os.path.join(path, loggingPath)):
            os.mkdir(os.path.join(path, loggingPath))
            # we upload in it the default repository file
            from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
            staticLoggingPath = os.path.join(os.path.join(ResourcesConfiguration.getStaticResources(), "defaults"), "logging.conf.default")
            shutil.copy(staticLoggingPath, os.path.join(os.path.join(path, loggingPath), "logging.conf"))

        workspace = Workspace(name, datetime.datetime.now(), path, tracesPath, pathOfLogging, prototypesPath)
        workspace.saveConfigFile()

        return workspace

    @staticmethod
    def isFolderAValidWorkspace(workspacePath):
        """Computes if the provided folder
        represents a valid (and loadable) workspace
        @return: None if the workspace is loadable or the error message if not valid
        """
        if workspacePath is None:
            return _("The workspace's path ({0}) is incorrect.".format(workspacePath))
        workspaceFile = os.path.join(workspacePath, Workspace.CONFIGURATION_FILENAME)

        # verify we can open and read the file
        if workspaceFile is None:
            return _("The workspace's configuration file can't be find (No workspace path given).")
        # is the workspaceFile is a file
        if not os.path.isfile(workspaceFile):
            return _("The specified workspace's configuration file ({0}) is not valid: its not a file.".format(workspaceFile))
        # is it readable
        if not os.access(workspaceFile, os.R_OK):
            return _("The specified workspace's configuration file ({0}) is not readable.".format(workspaceFile))

        for xmlSchemaFile in Workspace.WORKSPACE_SCHEMAS.keys():
            from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
            xmlSchemaPath = os.path.join(ResourcesConfiguration.getStaticResources(), xmlSchemaFile)
            # If we find a version which validates the XML, we parse with the associated function
            if Workspace.isSchemaValidateXML(xmlSchemaPath, workspaceFile):
                return None
        return _("The specified workspace is not valid according to the XSD definitions.")

    @staticmethod
    def loadWorkspace(workspacePath):
        """Load the workspace declared in the
        provided directory
        @type workspacePath: str
        @var workspacePath: folder to load as a workspace
        @return a tupple with the workspace or None if not valid and the error message"""

        errorMessage = Workspace.isFolderAValidWorkspace(workspacePath)
        if errorMessage is not None:
            logging.warn(errorMessage)
            return (None, errorMessage)

        workspaceFile = os.path.join(workspacePath, Workspace.CONFIGURATION_FILENAME)
        logging.debug("  Workspace configuration file found: " + str(workspaceFile))
        # We validate the file given the schemas
        for xmlSchemaFile in Workspace.WORKSPACE_SCHEMAS.keys():
            from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
            xmlSchemaPath = os.path.join(ResourcesConfiguration.getStaticResources(), xmlSchemaFile)
            # If we find a version which validates the XML, we parse with the associated function
            if Workspace.isSchemaValidateXML(xmlSchemaPath, workspaceFile):
                logging.debug("  Workspace configuration file " + str(workspaceFile) + " is valid against XSD scheme " + str(xmlSchemaPath))
                parsingFunc = Workspace.WORKSPACE_SCHEMAS[xmlSchemaFile]
                workspace = parsingFunc(workspacePath, workspaceFile)
                if workspace is not None:
                    return (workspace, None)
            else:
                logging.fatal("The specified Workspace file is not valid according to the XSD found in %s." % (xmlSchemaPath))

        return (None, _("An unknown error prevented to open the workspace."))

    @staticmethod
    def isSchemaValidateXML(schemaFile, xmlFile):
        # is the schema is a file
        if not os.path.isfile(schemaFile):
            logging.warn("The specified schema file (" + str(schemaFile) + ") is not valid : its not a file.")
            return False
        # is it readable
        if not os.access(schemaFile, os.R_OK):
            logging.warn("The specified schema file (" + str(schemaFile) + ") is not readable.")
            return False

        schemaF = open(schemaFile, "r")
        schemaContent = schemaF.read()
        schemaF.close()

        if schemaContent is None or len(schemaContent) == 0:
            logging.warn("Impossible to read the schema file (no content found in it)")
            return False

        # Extended version of an XSD validator
        # Create an xmlParser for the schema
        schemaParser = etree.XMLParser()
        # Register a resolver (to locate the other XSDs according to the path of static resources)
        xsdResolver = XSDResolver()
        xsdResolver.addMapping("common.xsd", os.path.join(os.path.dirname(schemaFile), "common.xsd"))

        schemaParser.resolvers.add(xsdResolver)
        schemaParsed = etree.parse(schemaContent, parser=schemaParser)
        schema = etree.XMLSchema(schemaParsed)

        try:
            xmlRoot = etree.parse(xmlFile)
            schema.assertValid(xmlRoot)
            return True
        except Exception as e:
            logging.warn(e)
            log = schema.error_log
            error = log.last_error
            logging.warn(error)
            return False
        return False

    # Dictionary of workspace versions, must be sorted by version DESC
    WORKSPACE_SCHEMAS = {"xsds/0.1/Workspace.xsd": loadWorkspace_0_1}

    def getName(self):
        return self.name

    def getCreationDate(self):
        return self.creationDate

    def getPath(self):
        return self.path

    def getProjectsPath(self):
        return self.projects_path

    def getPathOfTraces(self):
        return self.pathOfTraces

    def getPathOfLogging(self):
        return self.pathOfLogging

    def getPathOfPrototypes(self):
        return self.pathOfPrototypes
