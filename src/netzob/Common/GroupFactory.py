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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Group import Group
from lxml import etree


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
        root = etree.Element("group")
        # ID
        root.set("id", str(group.getID()))
        # Name
        root.set("name", group.getName())
        # Alignement
        root.set("alignment", group.getAlignment())
        # Score
        root.set("score", str(group.getScore()))
        
        # Messages
        messagesXML = etree.SubElement(root, "messages")
        for message in group.getMessages() :
            messageXML = etree.SubElement(messagesXML, "message")
            messageXML.set("id", str(message.getID()))
        
        # Columns
        columnsXML = etree.SubElement(root, "columns")
        for column in group.getColumns() :
            columnXML = etree.SubElement(columnsXML, "column")
            columnXML.set("name", column['name'])
            
            regexXML = etree.SubElement(columnXML, "regex")
            regexXML.text = column['regex'].strip()
            
            selectedTypeXML = etree.SubElement(columnXML, "selectedType")
            selectedTypeXML.text = column['selectedType']
            
            tabulationXML = etree.SubElement(columnXML, "tabulation")
            tabulationXML.text = column['tabulation']
            
            descriptionXML = etree.SubElement(columnXML, "description")
            descriptionXML.text = column['description']
            
            colorXML = etree.SubElement(columnXML, "color")
            colorXML.text = column['color']
            
        return etree.tostring(root)
    
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
    
    
