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
import logging
import os
import datetime
import re
import uuid
from lxml.etree import ElementTree
from lxml import etree
import types

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Vocabulary import Vocabulary
from netzob.Common.Grammar import Grammar
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.XSDResolver import XSDResolver

PROJECT_NAMESPACE = "http://www.netzob.org/project"
COMMON_NAMESPACE = "http://www.netzob.org/common"


def loadProject_0_1(projectFile):
    # Parse the XML Document as 0.1 version
    tree = ElementTree()

    tree.parse(projectFile)

    xmlProject = tree.getroot()

    # Register the namespace
    etree.register_namespace('netzob', PROJECT_NAMESPACE)
    etree.register_namespace('netzob-common', COMMON_NAMESPACE)

    projectID = xmlProject.get('id')
    projectName = xmlProject.get('name', 'none')
    projectCreationDate = TypeConvertor.xsdDatetime2PythonDatetime(xmlProject.get('creation_date'))
    projectPath = xmlProject.get('path')
    project = Project(projectID, projectName, projectCreationDate, projectPath)

    # Parse the configuration
    if xmlProject.find("{" + PROJECT_NAMESPACE + "}configuration") != None:
        projectConfiguration = ProjectConfiguration.loadProjectConfiguration(xmlProject.find("{" + PROJECT_NAMESPACE + "}configuration"), PROJECT_NAMESPACE, "0.1")
        project.setConfiguration(projectConfiguration)

    # Parse the vocabulary
    if xmlProject.find("{" + PROJECT_NAMESPACE + "}vocabulary") != None:
        projectVocabulary = Vocabulary.loadVocabulary(xmlProject.find("{" + PROJECT_NAMESPACE + "}vocabulary"), PROJECT_NAMESPACE, COMMON_NAMESPACE, "0.1", project)
        project.setVocabulary(projectVocabulary)

    # Parse the grammar
    if xmlProject.find("{" + PROJECT_NAMESPACE + "}grammar") != None:
        projectGrammar = Grammar.loadGrammar(xmlProject.find("{" + PROJECT_NAMESPACE + "}grammar"), projectVocabulary, PROJECT_NAMESPACE, "0.1")
        if projectGrammar != None:
            project.setGrammar(projectGrammar)

    return project


#+---------------------------------------------------------------------------+
#| Project:
#|     Class definition of a Project
#+---------------------------------------------------------------------------+
class Project(object):

    # The name of the configuration file
    CONFIGURATION_FILENAME = "config.xml"

    # /!\ WARNING:
    # The dict{} which defines the parsing function associated with each schema
    # is added to the end of the document

    #+-----------------------------------------------------------------------+
    #| Constructor
    #| @param name : name of the project
    #| @param creationDate : date of creation
    #+-----------------------------------------------------------------------+
    def __init__(self, id, name, creationDate, path):
        self.id = id
        self.name = name
        self.creationDate = creationDate
        self.path = path
        self.vocabulary = Vocabulary()
        self.grammar = Grammar()
        self.configuration = ProjectConfiguration.loadDefaultProjectConfiguration()

    def generateXMLConfigFile(self):
        # Register the namespace
        etree.register_namespace('netzob', PROJECT_NAMESPACE)
        etree.register_namespace('netzob-common', COMMON_NAMESPACE)

        # Dump the file
        root = etree.Element("{" + PROJECT_NAMESPACE + "}project")
        root.set("id", str(self.getID()))
        root.set("path", str(self.getPath()))
        # Warning, changed because of project = Project.createProject(self.netzob.getCurrentWorkspace(), projectName)
        if isinstance(self.getCreationDate(), types.TupleType):
            root.set("creation_date", TypeConvertor.pythonDatetime2XSDDatetime(self.getCreationDate()[0]))
        else:
            root.set("creation_date", TypeConvertor.pythonDatetime2XSDDatetime(self.getCreationDate()))
        root.set("name", str(self.getName()))
        # Save the configuration in it
        self.getConfiguration().save(root, PROJECT_NAMESPACE)
        # Save the vocabulary in it
        self.getVocabulary().save(root, PROJECT_NAMESPACE, COMMON_NAMESPACE)
        # Save the grammar in it
        if self.getGrammar() != None:
            self.getGrammar().save(root, PROJECT_NAMESPACE)
        return root

    def saveConfigFile(self, workspace):

        projectPath = os.path.join(os.path.join(workspace.getPath(), self.getPath()))
        projectFile = os.path.join(projectPath, Project.CONFIGURATION_FILENAME)

        logging.info("Save the config file of project " + self.getName() + " in " + projectFile)

        # First we verify and create if necessary the directory of the project
        if not os.path.exists(projectPath):
            logging.info("Creation of the directory " + projectPath)
            os.mkdir(projectPath)
        # We generate the XML Config file
        root = self.generateXMLConfigFile()
        tree = ElementTree(root)
        tree.write(projectFile)

        # Saving the workspace configuration file
#        workspace.saveConfigFile()

    def hasPendingModifications(self, workspace):
        result = True

        # TODO : Some errors may occur here...
        try:
            tree = ElementTree(self.generateXMLConfigFile())
            currentXml = etree.tostring(tree)

            tree.parse(os.path.join(os.path.join(os.path.join(workspace.getPath(), "projects"), self.getPath()), Project.CONFIGURATION_FILENAME))
            xmlProject = tree.getroot()
            oldXml = etree.tostring(xmlProject)

            if currentXml == oldXml:
                result = False
        except:
            pass

        return result

    @staticmethod
    def createProject(workspace, name):
        idProject = str(uuid.uuid4())
        path = "projects/" + idProject + "/"
        creationDate = datetime.datetime.now()
        project = Project(idProject, name, creationDate, path)
        # Creation of the config file
        project.saveConfigFile(workspace)
        # Register the project in the workspace
        workspace.referenceProject(project.getPath())
        workspace.saveConfigFile()

        return project

    @staticmethod
    def getNameOfProject(workspace, projectDirectory):
        projectFile = os.path.join(os.path.join(workspace.getPath(), projectDirectory), Project.CONFIGURATION_FILENAME)

        # verify we can open and read the file
        if projectFile == None:
            return None
        # is the projectFile is a file
        if not os.path.isfile(projectFile):
            logging.warn("The specified project's configuration file (" + str(projectFile) + ") is not valid : its not a file.")
            return None
        # is it readable
        if not os.access(projectFile, os.R_OK):
            logging.warn("The specified project's configuration file (" + str(projectFile) + ") is not readable.")
            return None

        # We validate the file given the schemas
        for xmlSchemaFile in Project.PROJECT_SCHEMAS.keys():
            xmlSchemaPath = os.path.join(ResourcesConfiguration.getStaticResources(), xmlSchemaFile)
            # If we find a version which validates the XML, we parse with the associated function
            if Project.isSchemaValidateXML(xmlSchemaPath, projectFile):
                logging.debug("The file " + str(projectFile) + " validates the project configuration file.")
                tree = ElementTree()
                tree.parse(projectFile)
                xmlProject = tree.getroot()
                # Register the namespace
                etree.register_namespace('netzob', PROJECT_NAMESPACE)
                etree.register_namespace('netzob-common', COMMON_NAMESPACE)

                projectName = xmlProject.get('name', 'none')

                if projectName != None and projectName != 'none':
                    return projectName
            else:
                logging.warn("The project declared in file (" + projectFile + ") is not valid")
        return None

    @staticmethod
    def loadProject(workspace, projectDirectory):
        projectFile = os.path.join(os.path.join(workspace.getPath(), projectDirectory), Project.CONFIGURATION_FILENAME)

        # verify we can open and read the file
        if projectFile == None:
            return None
        # is the projectFile is a file
        if not os.path.isfile(projectFile):
            logging.warn("The specified project's configuration file (" + str(projectFile) + ") is not valid : its not a file.")
            return None
        # is it readable
        if not os.access(projectFile, os.R_OK):
            logging.warn("The specified project's configuration file (" + str(projectFile) + ") is not readable.")
            return None

        # We validate the file given the schemas
        for xmlSchemaFile in Project.PROJECT_SCHEMAS.keys():
            xmlSchemaPath = os.path.join(ResourcesConfiguration.getStaticResources(), xmlSchemaFile)
            # If we find a version which validates the XML, we parse with the associated function
            if Project.isSchemaValidateXML(xmlSchemaPath, projectFile):
                logging.debug("The file " + str(projectFile) + " validates the project configuration file.")
                parsingFunc = Project.PROJECT_SCHEMAS[xmlSchemaFile]
                project = parsingFunc(projectFile)
                if project != None:
                    logging.info("Loading project '" + str(project.getName()) + "' from workspace.")
                    return project
            else:
                logging.warn("The project declared in file (" + projectFile + ") is not valid")
        return None

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

        if schemaContent == None or len(schemaContent) == 0:
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
        # We parse the given XML file
        try:
            xmlRoot = etree.parse(xmlFile)
            try:
                schema.assertValid(xmlRoot)
                return True
            except:
                log = schema.error_log
                error = log.last_error
                logging.debug(error)
                return False

        except etree.XMLSyntaxError, e:
            log = e.error_log.filter_from_level(etree.ErrorLevels.FATAL)
            logging.debug(log)

        return False

    # Dictionary of projects versions, must be sorted by version DESC
    PROJECT_SCHEMAS = {"xsds/0.1/Project.xsd": loadProject_0_1}

    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getCreationDate(self):
        return self.creationDate

    def getPath(self):
        return self.path

    def getVocabulary(self):
        return self.vocabulary

    def getGrammar(self):
        return self.grammar

    def getConfiguration(self):
        return self.configuration

    def setID(self, id):
        self.id = id

    def setName(self, name):
        self.name = name

    def setPath(self, path):
        self.path = path

    def setCreationDate(self, creationDate):
        self.creationDate = creationDate

    def setConfiguration(self, conf):
        self.configuration = conf

    def setVocabulary(self, voc):
        self.vocabulary = voc

    def setGrammar(self, grammar):
        self.grammar = grammar
