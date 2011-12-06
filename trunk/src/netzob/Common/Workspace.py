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

from lxml import etree
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from xml.etree.ElementTree import ElementTree


#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


def loadWorkspace_0_1(workspacePath, workspaceFile):  
    
    namespaceWorkspace = "http://www.netzob.org/workspace"
    
    # Parse the XML Document as 0.1 version
    tree = ElementTree()
    
    tree.parse(workspaceFile)
    xmlWorkspace = tree.getroot()
    wsName = xmlWorkspace.get('name', 'none')
    wsCreationDate = Workspace.parse_timestamp(xmlWorkspace.get('creation_date'))
  
    # Parse the configuration to retrieve the main paths
    xmlWorkspaceConfig = xmlWorkspace.find("{" + namespaceWorkspace + "}configuration")
    pathOfTraces = xmlWorkspaceConfig.find("{" + namespaceWorkspace + "}traces").text
    
    pathOfLogging = None
    if xmlWorkspaceConfig.find("{" + namespaceWorkspace + "}logging") != None and xmlWorkspaceConfig.find("{" + namespaceWorkspace + "}logging").text != None and len(xmlWorkspaceConfig.find("{" + namespaceWorkspace + "}logging").text) > 0:
        pathOfLogging = xmlWorkspaceConfig.find("{" + namespaceWorkspace + "}logging").text
        
    pathOfPrototypes = None
    if xmlWorkspaceConfig.find("{" + namespaceWorkspace + "}prototypes") != None and xmlWorkspaceConfig.find("{" + namespaceWorkspace + "}prototypes").text != None and len(xmlWorkspaceConfig.find("{" + namespaceWorkspace + "}prototypes").text) > 0:
        pathOfPrototypes = xmlWorkspaceConfig.find("{" + namespaceWorkspace + "}prototypes").text
    
    # Instantiation of the workspace
    workspace = Workspace(wsName, wsCreationDate, workspacePath, pathOfTraces, pathOfLogging, pathOfPrototypes)
    
    # Load the projects
    if xmlWorkspace.find("{" + namespaceWorkspace + "}projects") != None :
        for xmlProject in xmlWorkspace.findall("{" + namespaceWorkspace + "}projects/{" + namespaceWorkspace + "}project") :
            project_path = xmlProject.get("path")
            workspace.referenceProject(project_path)
    
    return workspace    
    





#+---------------------------------------------------------------------------+
#| Workspace :
#|     Class definition of a Workspace
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class Workspace(object):
    
    # The name of the configuration file
    CONFIGURATION_FILENAME = "workspace.xml"
    
    # /!\ WARNING :
    # The dict{} which defines the parsing function associated with each schema
    # is added to the end of the document
    
    #+-----------------------------------------------------------------------+
    #| Constructor
    #| @param path : path of the workspace
    #+-----------------------------------------------------------------------+
    def __init__(self, name, creationDate, path, pathOfTraces, pathOfLogging, pathOfPrototypes):
        self.name = name
        self.path = path
        self.creationDate = creationDate
        self.projects_path = []
        self.pathOfTraces = pathOfTraces
        self.pathOfLogging = pathOfLogging
        self.pathOfPrototypes = pathOfPrototypes
        
           
        
    #+-----------------------------------------------------------------------+
    #| referenceProject :
    #|     reference a project in the workspace
    #+-----------------------------------------------------------------------+
    def referenceProject(self, project_path):
        if not project_path in self.projects_path :
            self.projects_path.append(project_path)
        else :
            logging.warn("The project declared in " + project_path + " is already referenced in the workspace.")
        
        
    @staticmethod
    def loadWorkspace(workspacePath):    
        
        workspaceFile = os.path.join(workspacePath, Workspace.CONFIGURATION_FILENAME)
        
        # verify we can open and read the file
        if workspaceFile == None :
            return None
        # is the workspaceFile is a file
        if not os.path.isfile(workspaceFile) :
            logging.warn("The specified workspace's configuration file (" + str(workspaceFile) + ") is not valid : its not a file.")
            return None
        # is it readable
        if not os.access(workspaceFile, os.R_OK) :
            logging.warn("The specified workspace's configuration file (" + str(workspaceFile) + ") is not readable.")
            return None
        
        # We validate the file given the schemas
        for xmlSchemaFile in Workspace.WORKSPACE_SCHEMAS.keys() :            
            xmlSchemaPath = os.path.join(ResourcesConfiguration.getStaticResources(), xmlSchemaFile)
            # If we find a version which validates the XML, we parse with the associated function
            if Workspace.isSchemaValidateXML(xmlSchemaPath, workspaceFile) :
                logging.debug("The file " + str(xmlSchemaPath) + " validates the workspace configuration file.")
                parsingFunc = Workspace.WORKSPACE_SCHEMAS[xmlSchemaFile]
                workspace = parsingFunc(workspacePath, workspaceFile)
                if workspace != None :
                    return workspace
        
        return None
        
    

        
        
    
    @staticmethod
    def parse_timestamp(s):
        """Returns (datetime, tz offset in minutes) or (None, None)."""
        m = re.match(""" ^
        (?P<year>-?[0-9]{4}) - (?P<month>[0-9]{2}) - (?P<day>[0-9]{2})
        T (?P<hour>[0-9]{2}) : (?P<minute>[0-9]{2}) : (?P<second>[0-9]{2})
        (?P<microsecond>\.[0-9]{1,6})?
        (?P<tz>
          Z | (?P<tz_hr>[-+][0-9]{2}) : (?P<tz_min>[0-9]{2})
        )?
        $ """, s, re.X)
        if m is not None:
            values = m.groupdict()
            if values["tz"] in ("Z", None):
                tz = 0
            else:
                tz = int(values["tz_hr"]) * 60 + int(values["tz_min"])
            if values["microsecond"] is None:
                values["microsecond"] = 0
            else:
                values["microsecond"] = values["microsecond"][1:]
                values["microsecond"] += "0" * (6 - len(values["microsecond"]))
            values = dict((k, int(v)) for k, v in values.iteritems()
                              if not k.startswith("tz"))
            try:
                return datetime.datetime(**values), tz
            except ValueError:
                pass
            return None, None    
        
        
        
     
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
        
        try :
            xmlRoot = etree.parse(xmlFile)
            schema.assertValid(xmlRoot)
            return True
        except :
            log = schema.error_log
            error = log.last_error
            logging.info(error)
            return False
        return False
    
    # Dictionary of workspace versions, must be sorted by version DESC
    WORKSPACE_SCHEMAS = {"xsds/0.1/Workspace.xsd": loadWorkspace_0_1}   
    

    
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
    
