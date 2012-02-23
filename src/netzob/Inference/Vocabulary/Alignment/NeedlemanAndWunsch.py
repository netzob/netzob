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
#| Global Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| C Imports
#+---------------------------------------------------------------------------+
import libNeedleman
from netzob.Common.Field import Field

#+---------------------------------------------------------------------------+
#| NeedlemanAndWunsch:
#|     Supports the use of N&W alignment in Netzob
#+---------------------------------------------------------------------------+
class NeedlemanAndWunsch(object):
    
    def __init__(self, cb_status=None):
        self.cb_status = cb_status
    
    #+-----------------------------------------------------------------------+
    #| cb_executionStatus
    #|     Callback function called by the C extension to provide info on status
    #| @param donePercent a float between 0 and 100 included
    #| @param currentMessage a str which represents the current alignment status
    #+-----------------------------------------------------------------------+
    def cb_executionStatus(self, donePercent, currentMessage):
        if self.cb_status == None :
            print "[Alignment status] " + str(donePercent) + "% " + currentMessage
        else :
            self.cb_status(donePercent, currentMessage)
    
    
    #+-----------------------------------------------------------------------+
    #| alignSymbol
    #|     Default alignment of messages declared in a Symbol
    #| @param the symbol
    #| @returns (alignment, score) 
    #+-----------------------------------------------------------------------+
    def alignSymbol(self, symbol, doInternalSlick, defaultFormat):
        messages = symbol.getMessages()
        # We execute the alignment
        (alignment, score) = self.align(doInternalSlick, messages)
        
        # We update the regex based on the results
        self.buildRegexFromAlignment(symbol, alignment, defaultFormat)
    
    #+-----------------------------------------------------------------------+
    #| align
    #|     Default alignment of messages
    #| @param messages a list of AbstractMessages
    #| @returns (alignment, score) 
    #+-----------------------------------------------------------------------+
    def align(self, doInternalSlick, messages):
        # First we serialize the two messages
        (serialMessages, format) = TypeConvertor.serializeMessages(messages)
        
        debug = False
        (score, regex, mask) = libNeedleman.alignMessages(doInternalSlick, len(messages), format, serialMessages, self.cb_executionStatus, debug)
        alignment = self.deserializeAlignment(regex, mask)
        return (alignment, score)
   
    #+-----------------------------------------------------------------------+
    #| alignTwoMessages
    #|     Default alignment of two messages
    #| @param message1 the first message to align
    #| @param message2 the second message to align
    #| @returns (alignment, score) 
    #+-----------------------------------------------------------------------+
    def alignTwoMessages(self, doInternalSlick, message1, message2):
        # First we serialize the two messages
        (serialMessages, format) = TypeConvertor.serializeMessages([message1, message2])
        
        debug = False
        (score, regex, mask) = libNeedleman.alignTwoMessages(doInternalSlick, format, serialMessages, debug)
        alignment = self.deserializeAlignment(regex, mask)
        
        return (score, alignment)
        
        
    #+-----------------------------------------------------------------------+
    #| deserializeMessages
    #|     Useless (functionally) function created for testing purposes
    #| @param messages a list of AbstractMessages
    #| @returns number Of Deserialized Messages
    #+-----------------------------------------------------------------------+
    def deserializeMessages(self, messages): 
        # First we serialize the messages
        (serialMessages, format) = TypeConvertor.serializeMessages(messages)
        
        debug = False
        return libNeedleman.deserializeMessages(len(messages), format, serialMessages, debug)
        
        
    #+-----------------------------------------------------------------------+
    #| deserializeAlignment
    #|     Transforms the C extension results in a python readable way
    #| @param regex the C returned regex
    #| @param mask the C returned mask
    #| @returns the python alignment
    #+-----------------------------------------------------------------------+    
    def deserializeAlignment(self, regex, mask): 
        align = ""
        i = 0
        for c in mask:
            if c != '\x02':
                if c == '\x01':
                    align += "--"
                else:
                    align += regex[i:i + 1].encode("hex")
            i += 1
        return align
        
        
    def buildRegexFromAlignment(self, symbol, align, defaultFormat):
               
        # Build regex from alignment
        i = 0
        start = 0
        regex = []
        found = False
        for i in range(len(align)):
            if (align[i] == "-"):
                if (found == False):
                    start = i
                    found = True
            else:
                if (found == True):
                    found = False
                    nbTiret = i - start
                    regex.append("(.{," + str(nbTiret) + "})")
                    regex.append(align[i])
                else:
                    if len(regex) == 0:
                        regex.append(align[i])
                    else:
                        regex[-1] += align[i]
        if (found == True):
            nbTiret = i - start
            regex.append("(.{," + str(nbTiret) + "})")
            
        iField = 0
        symbol.cleanFields()
        for regexElt in regex:
            field = Field("Field " + str(iField), iField, regexElt)
            # Use the default protocol type for representation
            field.setFormat(defaultFormat)
            symbol.addField(field)
            iField = iField + 1
       
        # We look for useless fields
        doLoop = True
        # We loop until we don't pop any field
        while doLoop == True:
            doLoop = False
            for field in symbol.getFields():
                # We try to see if this field produces only empty values when applied on messages
                messagesValuesByField = symbol.getMessagesValuesByField(field)
                messagesValuesByField = "".join(messagesValuesByField)
                if messagesValuesByField == "":
                    symbol.getFields().pop(field.getIndex())  # We remove this useless field
                    # Adpat index of the following fields, before breaking
                    for fieldNext in symbol.getFields():
                        if fieldNext.getIndex() > field.getIndex():
                            fieldNext.setIndex(fieldNext.getIndex() - 1)
                    doLoop = True
                    break
        
        
