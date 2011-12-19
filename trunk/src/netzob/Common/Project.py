# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
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
from netzob.Common.TypeConvertor import TypeConvertor


PROJECT_NAMESPACE = "http://www.netzob.org/project"

def loadProject_0_1(projectFile):  
    # Parse the XML Document as 0.1 version
    tree = ElementTree()
    
    tree.parse(projectFile)
    
    xmlProject = tree.getroot()
    # Register the namespace (2 way depending of the version)
   
    try :
        etree.register_namespace('netzob', PROJECT_NAMESPACE)
    except AttributeError :
        etree._namespace_map[PROJECT_NAMESPACE] = 'netzob'
    
    projectID = xmlProject.get('id')
    projectName = xmlProject.get('name', 'none')
    projectCreationDate = TypeConvertor.xsdDatetime2PythonDatetime(xmlProject.get('creation_date'))
    projectPath = xmlProject.get('path')
    project = Project(projectID, projectName, projectCreationDate, projectPath)
  
    # Parse the configuration
    if xmlProject.find("{" + PROJECT_NAMESPACE + "}configuration") != None :
        projectConfiguration = ProjectConfiguration.loadProjectConfiguration(xmlProject.find("{" + PROJECT_NAMESPACE + "}configuration"), PROJECT_NAMESPACE, "0.1")
        project.setConfiguration(projectConfiguration)
    
    # Parse the vocabulary
    if xmlProject.find("{" + PROJECT_NAMESPACE + "}vocabulary") != None :
        projectVocabulary = Vocabulary.loadVocabulary(xmlProject.find("{" + PROJECT_NAMESPACE + "}vocabulary"), PROJECT_NAMESPACE, "0.1")
        project.setVocabulary(projectVocabulary)
        
    # Parse the grammar
    if xmlProject.find("{" + PROJECT_NAMESPACE + "}grammar") != None :
        projectGrammar = Grammar.loadGrammar(xmlProject.find("{" + PROJECT_NAMESPACE + "}grammar"), projectVocabulary, PROJECT_NAMESPACE, "0.1")
        project.setGrammar(projectGrammar)
    
    return project    
    

#+---------------------------------------------------------------------------+
#| Project :
#|     Class definition of a Project
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class Project(object):
    
    # The name of the configuration file
    CONFIGURATION_FILENAME = "config.xml"
    
    # /!\ WARNING :
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
        self.grammar = None
        self.configuration = ProjectConfiguration.loadDefaultProjectConfiguration()
        
    
    
    def generateXMLConfigFile(self):
        
        # Register the namespace (2 way depending of the version)
        try :
            etree.register_namespace('netzob', PROJECT_NAMESPACE)
        except AttributeError :
            etree._namespace_map[PROJECT_NAMESPACE] = 'netzob'
        
        # Dump the file
        root = etree.Element("{" + PROJECT_NAMESPACE + "}project")
        root.set("id", str(self.getID()))
        root.set("path", str(self.getPath()))
        # Warning, changed because of project = Project.createProject(self.netzob.getCurrentWorkspace(), projectName)
        if isinstance(self.getCreationDate(), types.TupleType) :
            root.set("creation_date", TypeConvertor.pythonDatetime2XSDDatetime(self.getCreationDate()[0]))
        else :
            root.set("creation_date", TypeConvertor.pythonDatetime2XSDDatetime(self.getCreationDate()))
        root.set("name", str(self.getName()))
        # Save the configuration in it
        self.getConfiguration().save(root, PROJECT_NAMESPACE)
        # Save the vocabulary in it
        self.getVocabulary().save(root, PROJECT_NAMESPACE)
        # Save the grammar in it
        if self.getGrammar() != None :
            self.getGrammar().save(root, PROJECT_NAMESPACE)
        return root
       
    def saveConfigFile(self, workspace):     
           
        projectPath = os.path.join(os.path.join(workspace.getPath(), "projects"), self.getPath())
        projectFile = os.path.join(projectPath, Project.CONFIGURATION_FILENAME)
        
        logging.info("Save the config file of project " + self.getName() + " in " + projectFile)
        
        # First we verify and create if necessary the directory of the project
        if not os.path.exists(projectPath) :
            logging.info("Creation of the directory " + projectPath)
            os.mkdir(projectPath)
        # We generate the XML Config file
        root = self.generateXMLConfigFile()
        tree = ElementTree(root)
        tree.write(projectFile)

    
    def hasPendingModifications(self, workspace):
        result = True
        
        # TODO : Some errors may occur here...
        try :
            tree = ElementTree(self.generateXMLConfigFile())
            currentXml = etree.tostring(tree)
            
            tree.parse(os.path.join(os.path.join(os.path.join(workspace.getPath(), "projects"), self.getPath()), Project.CONFIGURATION_FILENAME))
            xmlProject = tree.getroot()
            oldXml = etree.tostring(xmlProject)
            
            if currentXml == oldXml :
                result = False
        except :
            pass
        
        
        return result
       
        
    @staticmethod
    def createProject(workspace, name):
        idProject = str(uuid.uuid4())
        path = idProject + "/"
        creationDate = datetime.datetime.now()
        project = Project(idProject, name, creationDate, path)
        # Creation of the config file
        project.saveConfigFile(workspace)
        # Register the project in the workspace
        workspace.referenceProject("projects/" + project.getPath())
        workspace.saveConfigFile()
        
        return project
        
        
    @staticmethod
    def loadProject(workspace, projectDirectory):    
        projectFile = os.path.join(os.path.join(workspace.getPath(), projectDirectory), Project.CONFIGURATION_FILENAME)
        
        # verify we can open and read the file
        if projectFile == None :
            return None
        # is the projectFile is a file
        if not os.path.isfile(projectFile) :
            logging.warn("The specified project's configuration file (" + str(projectFile) + ") is not valid : its not a file.")
            return None
        # is it readable
        if not os.access(projectFile, os.R_OK) :
            logging.warn("The specified project's configuration file (" + str(projectFile) + ") is not readable.")
            return None
        
        # We validate the file given the schemas
        for xmlSchemaFile in Project.PROJECT_SCHEMAS.keys() :            
            xmlSchemaPath = os.path.join(ResourcesConfiguration.getStaticResources(), xmlSchemaFile)
            # If we find a version which validates the XML, we parse with the associated function
            if Project.isSchemaValidateXML(xmlSchemaPath, projectFile) :
                logging.info("The file " + str(projectFile) + " validates the project configuration file.")
                parsingFunc = Project.PROJECT_SCHEMAS[xmlSchemaFile]
                project = parsingFunc(projectFile)
                if project != None :
                    return project
            else:
                logging.warn("not valid")
        return None
        
    

        
    
        
     
    @staticmethod
    def isSchemaValidateXML(schemaFile, xmlFile):
        # is the schema is a file
        if not os.path.isfile(schemaFile) :
            logging.warn("The specified schema file (" + str(schemaFile) + ") is not valid : its not a file.")
            return False
        # is it readable
        if not os.access(schemaFile, os.R_OK) :
            logging.warn("The specified schema file (" + str(schemaFile) + ") is not readable.")
            return False
        
        schemaF = open(schemaFile, "r")
        schemaContent = schemaF.read()
        schemaF.close()
        
        if schemaContent == None or len(schemaContent) == 0:
            logging.warn("Impossible to read the schema file (no content found in it)")
            return False
        
        schema_root = etree.XML(schemaContent)
        schema = etree.XMLSchema(schema_root)
        
        # We parse the given XML file
        try :
            xmlRoot = etree.parse(xmlFile)
            try :
                schema.assertValid(xmlRoot)
                return True
            except :
                log = schema.error_log
                error = log.last_error
                logging.warn(error)
                return False
            
        except etree.XMLSyntaxError, e:
            log = e.error_log.filter_from_level(etree.ErrorLevels.FATAL)
            logging.warn(log)
        
        
        
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
    
    def setName(self, name):
        self.name = name
        
    def setCreationDate(self, creationDate):
        self.creationDate = creationDate
    
    def setConfiguration(self, conf):
        self.configuration = conf
    
    def setVocabulary(self, voc):
        self.vocabulary = voc

    def setGrammar(self, grammar):
        self.grammar = grammar
