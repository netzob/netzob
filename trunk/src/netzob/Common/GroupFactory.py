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
import array
import binascii
import logging.config
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
import ConfigurationParser
from Group import Group

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| GroupFactory :
#|     Factory dedicated to the manipulation of a group
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| XML Definition :
#| <group id="" name="" score="" alignment="">
#|     <messages>
#|         <message id="" />
#|         <message id="" />
#|         <message id="" />
#|         ...
#|     </messages>
#|     <columns>
#|         <column name="">
#|             <regex></regex>
#|             <selectedType></selectedType>
#|             <tabulation></tabulation>
#|             <description></description>
#|             <color></color>
#|         </column>
#|         ...
#|     </columns>
#| </group>
#+---------------------------------------------------------------------------+
class GroupFactory():
    
    @staticmethod
    #+-----------------------------------------------------------------------+
    #| saveInXML
    #|     Generate an XML representation of a group
    #| @return a string which include the xml definition of the group
    #+-----------------------------------------------------------------------+    
    def saveInXML(group):
        root = ElementTree.Element("group")
        # ID
        root.set("id", str(group.getID()))
        # Name
        root.set("name", group.getName())
        # Alignement
        root.set("alignment", group.getAlignment())
        # Score
        root.set("score", str(group.getScore()))
        
        # Messages
        messagesXML = ElementTree.SubElement(root, "messages")
        for message in group.getMessages() :
            messageXML = ElementTree.SubElement(messagesXML, "message")
            messageXML.set("id", str(message.getID()))
        
        # Columns
        columnsXML = ElementTree.SubElement(root, "columns")
        for column in group.getColumns() :
            columnXML = ElementTree.SubElement(columnsXML, "column")
            columnXML.set("name", column['name'])
            
            regexXML = ElementTree.SubElement(columnXML, "regex")
            regexXML.text = column['regex'].strip()
            
            selectedTypeXML = ElementTree.SubElement(columnXML, "selectedType")
            selectedTypeXML.text = column['selectedType']
            
            tabulationXML = ElementTree.SubElement(columnXML, "tabulation")
            tabulationXML.text = column['tabulation']
            
            descriptionXML = ElementTree.SubElement(columnXML, "description")
            descriptionXML.text = column['description']
            
            colorXML = ElementTree.SubElement(columnXML, "color")
            colorXML.text = column['color']
            
        return ElementTree.tostring(root)
    
    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML :
    #|     Function which parses an XML and extract from it
    #[     the definition of a group
    #| @param rootElement: XML root of the group
    #| @param messages: list of messages
    #| @return an instance of a Groups
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, messages):        
        # First we verify rootElement is a group
        if rootElement.tag != "group" :
            raise NameError("The parsed xml doesn't represent a group.")
        # Then we verify its has a valid id
        if rootElement.get("id", "-1") == "-1" :
            raise NameError("The parsed group doesn't include its ID.")
        
        # Parse ID, NAME, ALIGNMENT, SCORE
        groupID = rootElement.get("id", "-1")
        groupName = rootElement.get("name", "None")
        groupAlignment = rootElement.get("alignement", "")
        groupScore = rootElement.get("score", "0")
        
        groupMessages = []
        
        # Parse messages and attach the associated
        for xmlMessage in rootElement.findall("messages/message") :
            messageID = xmlMessage.get("id", "-1")
            print "searching for mesage " + messageID
            for msg in messages :
                if str(msg.getID()) == messageID :
                    groupMessages.append(msg)
        
        # Parse columns
        groupColumns = []  
        iCol = 0      
        for xmlColumn in rootElement.findall("columns/column") :
            columnName = xmlColumn.get("name", "None")
            # Regex
            if xmlColumn.find("regex") != None :
                columnRegex = xmlColumn.find("regex").text
            else :
                columnRegex = ""
            # SelectedType
            if xmlColumn.find("selectedType") != None :
                columnSelectedType = xmlColumn.find("selectedType").text
            else :
                columnSelectedType = ""
            # Tabulation
            if xmlColumn.find("tabulation") != None :
                columnTabulation = xmlColumn.find("tabulation").text
                if columnTabulation == None :
                    columnTabulation = 0
                else :
                    columnTabulation = int(columnTabulation)
            else :
                columnTabulation = 0
            # Description
            if xmlColumn.find("description") != None :
                columnDescription = xmlColumn.find("description").text
            else :
                columnDescription = ""
            # Color
            if xmlColumn.find("color") != None :
                columnColor = xmlColumn.find("color").text
            else :
                columnColor = ""
            
            groupColumns.insert(iCol, {'name' : columnName,
                                        'regex' : columnRegex.strip(),
                                        'selectedType' : columnSelectedType,
                                        'tabulation' : columnTabulation,
                                        'description' : columnDescription,
                                        'color' : columnColor
                                        })
            iCol = iCol + 1
            
            
        group = Group(groupName, []) 
        group.setID(groupID)
        group.setAlignment(groupAlignment)
        group.setColumns(groupColumns)
        group.setScore(groupScore)
        group.addMessages(groupMessages)
        return group
    
    
