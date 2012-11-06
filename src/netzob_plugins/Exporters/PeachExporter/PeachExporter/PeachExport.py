# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 AMOSSYS                                                |
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
#| Global Imports                                                            |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
from lxml import etree
import string
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local Imports                                                             |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Memory import Memory


class PeachExport(object):
    """PeachExport:
            Utility for exporting netzob information into Peach pit file.
            Simplify the construction of a fuzzer with Peach.
    """

    def __init__(self, netzob):
        """Constructor of PeachExport:

                @type netzob: netzob.NetzobGUI.NetzobGUI
                @param netzob: the main netzob project.
        """
        self.netzob = netzob
        self.variableOverRegex = True
        self.mutateStaticFields = True

    def getPeachDefinition(self, symbolID, entireProject):
        """getXMLDefinition:
                Returns the Peach pit file (XML format) made on the  netzob information.

                @type symbolID: integer
                @param symbolID: a number which identifies the symbol the xml definition of which we need.
                @type entireProject: boolean
                @param entireProject: true if we want to see the Peach definition of the whole project, false elsewhere.
                @rtype: string
                @return: the string representation of the generated Peach xml pit file.
        """
        logging.debug("Targeted symbolID: {0}".format(str(symbolID)))
        # TODO(stateful fuzzer): Make one state model for each state of the protocol.
        xmlRoot = etree.Element("Peach")
        xmlInclude = etree.SubElement(xmlRoot, "Include", ns="default", src="file:defaults.xml")
        xmlImport = etree.SubElement(xmlRoot, "Import")
        xmlImport.attrib["import"] = "PeachzobAddons"

        if entireProject:
            self.makeAllDataModels(xmlRoot)
            self.makeAllStateModels(xmlRoot)

        else:
            project = self.netzob.getCurrentProject()
            vocabulary = project.getVocabulary()
            symbols = vocabulary.getSymbols()
            resSymbol = None
            for symbol in symbols:
                if str(symbol.getID()) == symbolID:
                    resSymbol = symbol
                    break
            if resSymbol == None:
                logging.warning("Impossible to retrieve the symbol having the id {0}".format(str(symbolID)))
                return None
            else:
                self.makeADataModel(xmlRoot, symbol, 0)
                self.makeAStateModel(xmlRoot)

        xmlAgent = etree.SubElement(xmlRoot, "Agent", name="DefaultAgent")
        xmlCommentAgent = etree.Comment("TODO: Configure the Agents.")
        xmlAgent.append(xmlCommentAgent)

        xmlTest = etree.SubElement(xmlRoot, "Test", name="DefaultTest")
        xmlCommentTest1 = etree.Comment('TODO: Enable Agent <Agent ref="TheAgent"/> ')
        xmlCommentTest2 = etree.Comment("TODO: Configure the test. The following lines are given in example.")
        xmlTest.append(xmlCommentTest1)
        xmlTest.append(xmlCommentTest2)
        xmlTestStateModel = etree.SubElement(xmlTest, "StateModel", ref="SimpleStateModel")
        xmlPublisher = etree.SubElement(xmlTest, "Publisher")
        xmlPublisher.attrib["class"] = "udp.Udp"
        xmlParamHost = etree.SubElement(xmlPublisher, "Param", name="host", value="0.0.0.0")
        xmlParamPort = etree.SubElement(xmlPublisher, "Param", name="port", value="0000")

        xmlRun = etree.SubElement(xmlRoot, "Run", name="DefaultRun")
        xmlCommentRun = etree.Comment("TODO: Configure the run.")
        xmlRun.append(xmlCommentRun)
        xmlLogger = etree.SubElement(xmlRun, "Logger")
        xmlLogger.attrib["class"] = "logger.Filesystem"
        xmlParamLogger = etree.SubElement(xmlLogger, "Param", name="path", value="logs")
        xmlTestRed = etree.SubElement(xmlRun, "Test", ref="DefaultTest")

        tree = etree.ElementTree(xmlRoot)
        toStringedTree = etree.tostring(tree, pretty_print=True)

        # Remove the first line:
        splittedToStringedTree = toStringedTree.split("\n")
        splittedToStringedTree = splittedToStringedTree[1:]
        toStringedTree = "\n".join(splittedToStringedTree)
        # Add strings not well managed by lxml.
        result = '<?xml version="1.0" encoding="utf-8"?>\n'
        result = result + '<Peach xmlns="http://phed.org/2008/Peach" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://phed.org/2008/Peach /peach/peach.xsd">\n'
        result = result + toStringedTree
        return result

    def makeAllDataModels(self, xmlFather):
        """makeAllDataModels:
                Transform every single netzob symbol into Peach data model.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element
        """
        project = self.netzob.getCurrentProject()
        vocabulary = project.getVocabulary()

        dataModelid = 0
        for symbol in vocabulary.getSymbols():
            # Each symbol is translated in a Peach data model
            self.makeADataModel(xmlFather, symbol, dataModelid)
            dataModelid = dataModelid + 1

    def makeADataModel(self, xmlFather, symbol, dataModelid):
        """makeADataModel:
                Dissect a netzob symbol in order to extract essential data for the making of Peach fields in its data Model

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element.
                @type symbol: netzob.common.Symbol.symbol
                @param symbol: the given symbol that will be dissected.
                @type dataModelid: integer
                @param dataModelid: a number that identifies the data model.
        """
        xmlDataModel = etree.SubElement(xmlFather, "DataModel", name=("dataModel{0}").format(str(dataModelid)))
        for field in symbol.getExtendedFields():
            xmlField = None

            #-----------------------------------#
            # Variable/Defaultvalue Management: #
            #-----------------------------------#
            if self.variableOverRegex:
                logging.debug("The fuzzing is based on variables.")
                variable = field.getVariable()
                if variable is None:
                    variable = field.getDefaultVariable(symbol)

                # We retrieve the values of the variable in text format.
                typedValueLists = self.getRecVariableTypedValueLists(variable)
                logging.debug("The field {0} has the value {1}.".format(field.getName(), str(typedValueLists)))

                # We count the subfields for the selected field. Aggregate variable can cause multiple subfields.
                subLength = 0
                for typedValueList in typedValueLists:
                    subLength = max(subLength, len(typedValueList))

                logging.debug("Sublength: {0}.".format(str(subLength)))
                # We create one Peach subfield for each netzob subfield.
                xmlFields = []
                # For each subfield.
                for i in range(subLength):
                    # We retrieve the peach type of the field for Peach to be as efficient and precise as possible.
                    peachType = self.getPeachFieldType(typedValueLists, i)
                    xmlFields.append(etree.SubElement(xmlDataModel, peachType, valueType="hex", name=("{0}_{1}").format(field.getName(), i)))
                    # We write down all possible values the subfield can have.
                    paramValues = []
                    for typedValueList in typedValueLists:
                        # If we have such a field. (The double list typedValueLists is lacunar)
                        if len(typedValueList) > i:
                            # We add a peach version of the netzob type in order to translate the subfield properly.
                            paramValues.append(self.netzobTypeToPeachType(typedValueList[i][0]) + "," + self.bitarray2hex(typedValueList[i][1]))
                    if len(paramValues) > 1:
                        # If there is several possible values, we use a fixup.
                        xmlOrFixup = etree.SubElement(xmlFields[i], "Fixup")
                        xmlOrFixup.attrib["class"] = "PeachzobAddons.Or"
                        # We transform the bitarray list into an hex string understandable by Peach.
                        formattedValue = ""
                        for paramValue in paramValues:
                            formattedValue = ("{0}; {1}").format(formattedValue, paramValue)
                        formattedValue = formattedValue[2:]  # Remove the '; ' prefix.
                        xmlOrFixupValueParam = etree.SubElement(xmlOrFixup, "Param", name="values", value=formattedValue)
                    elif len(paramValues) == 1:
                        # We assume that fields that has only one value are "static".
                        formattedValue = (string.split(paramValues[0], ","))[1]
                        xmlFields[i].attrib["value"] = formattedValue
                        if not self.mutateStaticFields:
                            xmlFields[i].attrib["mutable"] = "false"

            #-------------------#
            # Regex management: #
            #-------------------#
            else:
                logging.debug("The fuzzing is based on regexes.")
                peachType = self.getPeachFieldTypeFromNetzobFormat(field)
                if field.isStatic():
                    if peachType == "Number":
                        xmlField = etree.SubElement(xmlDataModel, peachType, name=field.getName(), value=str(self.hexstring2int(field.getRegex())))
                    else:
                        xmlField = etree.SubElement(xmlDataModel, peachType, name=field.getName(), valueType="hex", value=field.getRegex())
                    if not self.mutateStaticFields:
                        xmlField.attrib["mutable"] = "false"
                else:
                    # Fields not declared static in netzob are assumed to be dynamic, have a random default value and are mutable.
                    # We assume that the regex is composed of a random number of fixed and dynamic (.{n,p}, .{,n} and .{n}) subregexs. Each subregex will have its own peach subfield.
                    # We will illustrate it with the following example "(abcd.{m,n}efg.{,o}.{p}hij)"
                    regex = field.getRegex()
                    if (regex != "()"):
                        regex = regex[1:len(regex) - 1]  # regex = "abcd.{m,n}efg.{,o}.{p}hij"

                        splittedRegex = []
                        for lterm in string.split(regex, ".{"):
                                for rterm in string.split(lterm, "}"):
                                    splittedRegex.append(rterm)  # splittedRegex = ["abcd", "m,n", "efg", ",o", "", "p", "hij"]
                                    logging.debug("The field {0} has the splitted Regex = {1}".format(field.getName(), str(splittedRegex)))

                        for i in range(len(splittedRegex)):
                            # Dynamic subfield (splittedRegex will always contain dynamic subfields in even position).
                            if (i % 2) == 1:
                                fieldLength = 0
                                if splittedRegex[i].find(",") == -1:  # regex = {n}
                                    fieldMaxLength = int(splittedRegex[i])
                                    fieldMinLength = fieldMaxLength
                                elif splittedRegex[i].find(",") == 0:  # regex = {,p}
                                    fieldMaxLength = int((splittedRegex[i])[1:len(splittedRegex[i])])
                                    fieldMinLength = 0
                                else:  # regex = {n,p}
                                    fieldMaxLength = int(string.split(splittedRegex[i], ",")[1])
                                    fieldMinLength = int(string.split(splittedRegex[i], ",")[0])
                                # The given field length is the length in half-bytes.
                                fieldMaxLength = (fieldMaxLength + 1) / 2
                                fieldMinLength = fieldMinLength / 2
                                xmlField = etree.SubElement(xmlDataModel, peachType, name=("{0}_{1}").format(field.getName(), i))
                                xmlRanStringFixup = etree.SubElement(xmlField, "Fixup")
                                xmlRanStringFixup.attrib["class"] = "PeachzobAddons.RandomField"
                                xmlRSFParamMinlen = etree.SubElement(xmlRanStringFixup, "Param", name="minlen", value=str(fieldMinLength))
                                xmlRSFParamMaxlen = etree.SubElement(xmlRanStringFixup, "Param", name="maxlen", value=str(fieldMaxLength))
                                xmlRSFType = etree.SubElement(xmlRanStringFixup, "Param", name="type", value=peachType)
                            else:
                                # Static subfield.
                                if splittedRegex[i] != "":
                                    xmlField = etree.SubElement(xmlDataModel, peachType, name=("{0}_{1}").format(field.getName(), i), valueType="hex", value=splittedRegex[i])
                                    logging.debug("The field {0} has a static subfield of value {1}.".format(field.getName(), splittedRegex[i]))
                                    if not self.mutateStaticFields:
                                        xmlField.attrib["mutable"] = "false"
                    else:
                        # If the field's regex is (), we add a null-length Peach field type.
                        xmlField = etree.SubElement(xmlDataModel, "Blob", name=field.getName(), length=0)
                        logging.debug("The field {0} is empty.".format(field.getName()))

    def bitarray2hex(self, abitarray):
        """bitarray2hex:
                Transform a bitarray in a pure hex string.

                @type abitarray: bitarray.bitarray
                @param abitarray: the given bitarray which is transformed.
                @rtype: string
                @return: the hex translation of the bitarray.
        """
        return (abitarray.tobytes()).encode('hex')

    def bitarray2str(self, abitarray):
        """bitarray2str:
                Transform a bitarray in a 'u string.

                @type abitarray: bitarray.bitarray
                @param abitarray: the given bitarray which is transformed.
                @rtype: string
                @return: the 'u string translation of the bitarray.
        """
        return (abitarray.tobytes())

    def hexstring2int(self, hexstring):
        """hexstring2int:
            Transform a hexstring in an int. A hexstring is like "1234deadbeef"

            @type hexstring: string
            @param hextring: the given hexstring which is trasnformed in int.
            @rtype: integer
            @return: the integer extracted from the hex string 'hexstring'
        """
        return int('0x' + hexstring, 16)

    def netzobTypeToPeachType(self, netzobType):
        """netzobTypeToPeachType:
            Transform a netzob variable type (Word, IPv4Variable, Decimal Word ...) in a Peach field type (Number, String, Blob).

            @type netzobType: string
            @param netzobType: a netzob type.
            @rtype: string
            @return: the associated peach type.
        """
        peachType = ""
        if netzobType == "DecimalWord":
            peachType = "Number"
        elif netzobType == "Word" or netzobType == "IPv4Variable":
            peachType = "String"
        else:
            peachType = "Blob"
        return peachType

    def getRecVariableTypedValueLists(self, variable):
        """getRecVariableTypedValueLists:
                Find the value(s) and its(their) type of a variable. May be recursive.

                @type variable: netzob.common.MMSTD.Dictionary.Variable.variable
                @param variable: the given variable which values are searched.
                @rtype: (string, bitarray.bitarray) list list.
                @return: the list, representing aggregations, of lists, representing alternations, of couple (type of a leaf variable, value (in bitarray) of leaf variable).
        """
        logging.debug("<[ variable  : {0}.".format(str(variable.getName())))
        variableType = variable.getTypeVariable()
        typedValueLists = []  # List of list of couple type-value.
        if variableType == "Aggregate":
            for child in variable.getChildren():
                # We concatenate the double lists at the lower level (inner list).
                logging.debug("fatherValueLists: {0}.".format(str(typedValueLists)))
                typedValueLists = self.concatVariableValues(typedValueLists, self.getRecVariableTypedValueLists(child))

        elif variableType == "Alternate":
            for child in variable.getChildren():
                # We simply concatenate the two double lists as simple list.
                for value in self.getRecVariableTypedValueLists(child):
                    typedValueLists.append(value)
        elif variableType == "ReferencedVariable":
            # We retrieve the typedValueLists of the pointed variable. Referenced variable are variable pointing to another variable.
            vocabulary = self.netzob.getCurrentProject().getVocabulary()
            pointedVariable = variable.getPointedVariable(vocabulary)
            typedValueLists = self.getRecVariableTypedValueLists(pointedVariable)
        else:
            # We add the variable type and its binary value as a singleton list in the higher list.
            vocabulary = self.netzob.getCurrentProject().getVocabulary()
            memory = Memory(vocabulary.getVariables())
            value = variable.getValue(False, vocabulary, memory)
            if value is not None:
                typedValueLists.append([(variableType, value[0])])
        # typedValueLists = [[("Word", "a")], [("Word", "b"), ("Word", "c"), ("Word", "e")], [("Word", "d"), ("Word", "e")]]
        # <=> variable = a + bce + de
        logging.debug("typedValueLists  : {0}.".format(str(typedValueLists)))
        logging.debug("variable  : {0}. ]>".format(str(variable.getName())))
        return typedValueLists

    def concatVariableValues(self, fatherValueLists, sonValueLists):
        """concatVariableValues:
                Insert the values of a son to its father's in such a way that the global form (aggregation of alternation) is respected.
                From an aerial point of view, we concatenate both father and son's inner list in a double list. This concatenation stays in the inner list.

                @type fatherValueLists: (string, bitarray.bitarray) list list.
                @param fatherValueLists: the preexisting father double list.
                @type fatherValueLists: (string, bitarray.bitarray) list list.
                @param fatherValueLists: the son double list to be inserted.
                @rtype: (string, bitarray.bitarray) list list.
                @return: the double list resulting of the concatenation.
        """
        finalValueLists = []
        if len(fatherValueLists) == 0:
            #initialization
            finalValueLists = sonValueLists
        for fvl in fatherValueLists:
            for svl in sonValueLists:
                midvl = fvl + svl
                logging.debug("concatVariableValues : midvl before: {0}.".format(str(midvl)))
                finalValueLists.append(midvl)
                logging.debug("concatVariableValues : midvl after: {0}.".format(str(finalValueLists)))

        return finalValueLists

    def getPeachFieldType(self, typedValueLists, index):
        """getPeachFieldType:
                Get the peach type (Blob, String or Number) of the current field. This type is determined through the majority of the type of an alternation.

                @type typedValueLists: (string, bitarray.bitarray) list list.
                @param typedValueLists: a double list composed of aggregation of alternation, we search transversely among an alternation the majority type.
                @type index: integer
                @param index: an index pointing to the targeted alternation.
                @rtype: string
                @return: the majority type of the targeted alternation.
        """
        peachType = ""
        for typedValueList in typedValueLists:
            # The hierarchy is Blob > String > Number
            if typedValueList[index][0] == "DecimalWord":
                if peachType != "Blob" and peachType != "String" and peachType != "Number":
                    peachType = "Number"
            elif typedValueList[index][0] == "Word" or typedValueList[index][0] == "IPv4Variable":
                if peachType != "Blob" and peachType != "String":
                    peachType = "String"
            else:
                if peachType != "Blob":
                    peachType = "Blob"
                    break
        if peachType == "":
            # Eventual default value.
            peachType = "Blob"
        return peachType

    def getPeachFieldTypeFromNetzobFormat(self, field):
        """getPeachFieldTypeFromNetzobFormat:
            Get the peach type (Blob, String or Number) of the current field from the netzob visualization format (string, decimal, octal, hex or binary).

            @type field: netzob.Common.Field.Field
            @param field: the given field which peach type is being searched.
            @rtype: string
            @return: the peach field type.
        """
        peachType = ""
        format = field.getFormat()
        logging.debug("Format of the field {0} is {1}.".format(field.getName(), format))
        if format == "string":
            peachType = "String"
        elif format == "decimal":
            peachType = "Number"
        else:
            peachType = "Blob"
        return peachType

    def makeAllStateModels(self, xmlFather):
        """makeAllStateModels:
                Create a Peach state model. Create one state by data model and chain it to the previously created one.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element.
        """
        xmlStateModel = etree.SubElement(xmlFather, "StateModel", name="SimpleStateModel", initialState="state0")
        # There is always at least one state, the first state which is naturally called state0 and is the initial state.

        project = self.netzob.getCurrentProject()
        vocabulary = project.getVocabulary()
        stateid = 0
        xmlState = None
        # We make one state by symbol. So, all symbols will be fuzz-tested sequentially and equally.
        for symbol in vocabulary.getSymbols():
            # If the current state has a precursor, we link them from older to newer.
            if xmlState is not None:
                xmlAction = etree.SubElement(xmlState, "Action", type="changeState", ref=("state{0}").format(stateid))
            xmlState = self.makeAState(xmlStateModel, stateid)
            stateid = stateid + 1

    def makeAStateModel(self, xmlFather):
        """makeAStateModel:
                Create a Peach state model with only one state.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element.
        """
        xmlStateModel = etree.SubElement(xmlFather, "StateModel", name="SimpleStateModel", initialState="state0")
        project = self.netzob.getCurrentProject()
        vocabulary = project.getVocabulary()
        xmlState = self.makeAState(xmlStateModel, 0)

    def makeAState(self, xmlFather, stateid):
        """makeAState:
                Create one state which will output data formatted according to a previously created data model.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element.
                @type stateid: integer
                @param stateid: a number that identifies the state in the state model and links to the proper data model.
                @rtype: lxml.etree.element
                @return: a Peach state in xml format.
        """
        # We create one state which will output fuzzed data.
        xmlState = etree.SubElement(xmlFather, "State", name=("state{0}").format(str(stateid)))
        xmlAction = etree.SubElement(xmlState, "Action", type="output")

        # xml link to the previously made data model.
        xmlDataModel = etree.SubElement(xmlAction, "DataModel", ref=("dataModel{0}").format(str(stateid)))
        xmlData = etree.SubElement(xmlAction, "Data", name="data")
        return xmlState

    def setVariableOverRegex(self, value):
        """setVariableOverRegex:
                Setter for variableOverRegex.

            @type value: boolean
            @param value: the new value of variableOverRegex.
        """
        self.variableOverRegex = value

    def setMutateStaticFields(self, value):
        """setMutateStaticFields:
                Setter for mutateStaticFields.

            @type value: boolean
            @param value: the new value of mutateStaticFields.
        """
        self.mutateStaticFields = value
