
import difflib

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt import Alt

@NetzobLogger
class headerDetector(object):
    r"""Provides multiple algorithms to find headers in symbols wich already have fields.

        This example detects the header based on a field type separator such as CRC32,Size or InternetChecksum
        #TODO implement Value as a Field separator
        >>> from netzob.all import *
        >>> message1 = RawMessage(data=b'\xc5k@@\x003\x00\n|\xd9\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81\x8c\x00\x1b\x00\x00\x00\x16\x00\x00\x00\x18\x00\x00\x00JK\x98\x9eU\xcd\x10\x00\x01\x00\x03\x00\xfc\xf7\xe1\x82\x04\x00\x00\x00\x1a\x10\x00\x00\x15\x02\x00\x01')
        >>> message2 = RawMessage(data=b'\xc5k@@\x003\x00\n|\xd9\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81\x8c\x00\xa8\x00\x00\x00)\x00\x00\x00\x18\x00\x00\x00\xbe=\xcd\xd8U\xcd\x0c\x00\x01\x00\x03\x00\xfc\xf7\xe1\x82\x08\x00\x00\x00\x01\x84\x80\x00\xfc\xf7\xe1\x82')
        >>> message3 = RawMessage(data=b'\xc5k@@\x003\x00\n|\xd9\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81\x84\x00\xae\x00\x00\x00.\x00\x00\x00\x18\x00\x00\x00\xd6j\xc4aU\xcd\x0c\x00\x01\x00\x03\x00\xd9?\x91\xa8\x08\x00\x00\x00\x01\x84\x80\x00\xd9?\x91\xa8')
        >>> messages = [message1,message2,message3]
        >>> symbol = Symbol(messages=messages)
        >>> Format.splitStatic(symbol)
        >>> seeker = CRCFinder()
        >>> seeker.findOnSymbol(symbol=symbol,create_fields=True)
        >>> field_separator = "CRC32"
        >>> header_seeker = headerDetector(field=True,fieldType=field_separator)
        >>> header_seeker.findOnSymbols([symbol])
        >>> print(symbol)# doctest: +NORMALIZE_WHITESPACE
        Source | Destination | Field-0_HEADER                                               | Field-1_HEADER | Field-2_HEADER | Field-3_HEADER | Field-4_HEADER | Field-5_HEADER | Field-6_HEADER                 | CRC32_LE36   | Field-8 | Field-9 | Field-10               | Field-11      | Field-12       | Field-13       | Field-14 | Field-15
        ------ | ----------- | ------------------------------------------------------------ | -------------- | -------------- | -------------- | -------------- | -------------- | ------------------------------ | ------------ | ------- | ------- | ---------------------- | ------------- | -------------- | -------------- | -------- | ------------------
        None   | None        | 'Åk@@\x003\x00\n|Ù\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81' | '\x8c'         | '\x00'         | '\x1b'         | '\x00\x00\x00' | '\x16'         | '\x00\x00\x00\x18\x00\x00\x00' | 'JK\x98\x9e' | 'UÍ'    | '\x10'  | '\x00\x01\x00\x03\x00' | 'ü÷á\x82\x04' | '\x00\x00\x00' | '\x1a\x10\x00' | '\x00'   | '\x15\x02\x00\x01'
        None   | None        | 'Åk@@\x003\x00\n|Ù\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81' | '\x8c'         | '\x00'         | '¨'            | '\x00\x00\x00' | ')'            | '\x00\x00\x00\x18\x00\x00\x00' | '¾=ÍØ'       | 'UÍ'    | '\x0c'  | '\x00\x01\x00\x03\x00' | 'ü÷á\x82\x08' | '\x00\x00\x00' | '\x01\x84\x80' | '\x00'   | 'ü÷á\x82'
        None   | None        | 'Åk@@\x003\x00\n|Ù\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81' | '\x84'         | '\x00'         | '®'            | '\x00\x00\x00' | '.'            | '\x00\x00\x00\x18\x00\x00\x00' | 'ÖjÄa'       | 'UÍ'    | '\x0c'  | '\x00\x01\x00\x03\x00' | 'Ù?\x91¨\x08' | '\x00\x00\x00' | '\x01\x84\x80' | '\x00'   | 'Ù?\x91¨'
        ------ | ----------- | ------------------------------------------------------------ | -------------- | -------------- | -------------- | -------------- | -------------- | ------------------------------ | ------------ | ------- | ------- | ---------------------- | ------------- | -------------- | -------------- | -------- | ------------------

        This example detects the header based on a value separator
        >>> from netzob.all import *
        >>> message1 = RawMessage(data=b'CMDencrypt#\x06\x00\x00\x00abcdef')
        >>> message2 = RawMessage(data=b'CMDencrypt#\n\x00\x00\x00123456test')
        >>> messages = [message1,message2]
        >>> symbol = Symbol(messages=messages)
        >>> Format.splitDelimiter(symbol,ASCII("#"))
        >>> separator_field = Field(domain=ASCII("#"))
        >>> seeker = headerDetector(separator=True,separatorValue=separator_field)
        >>> seeker.findOnSymbols([symbol])
        >>> print(symbol)# doctest: +NORMALIZE_WHITESPACE
        Source | Destination | Field-0_HEADER | Field-sep-23 | Field-2
        ------ | ----------- | -------------- | ------------ | --------------------------
        None   | None        | 'CMDencrypt'   | '#'          | '\x06\x00\x00\x00abcdef'
        None   | None        | 'CMDencrypt'   | '#'          | '\n\x00\x00\x00123456test'
        ------ | ----------- | -------------- | ------------ | --------------------------

    """

    def __init__(self,ratio = False,ratioValue = 0.6,field = False,fieldType = None,separator = False,separatorValue = None):
        self.ratio = ratio
        self.ratioValue = ratioValue
        self.field = field
        self.fieldType = fieldType
        self.separator = separator
        self.separatorValue = separatorValue


    @typeCheck(list)
    def findOnSymbols(self,symbols):
        """Attempts to identify header and data fields in provided list of symbols

        :param symbol: the symbol in which we are looking for relations
        :type symbol: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        """
        if self.ratio:
            return self.__executeRatioOnSymbols(symbols)
        elif self.field:
            return self.__executeFieldOnSymbols(symbols)
        elif self.separator:
            return self.__executeValueOnSymbols(symbols)
        else:
            raise "Please select a type of search!"


    @typeCheck(list)
    def __executeRatioOnSymbols(self,symbols):
        """
          Identify header and data fields in provided list of symbols
        Args:
            symbols:

        Returns: True or False

        """
        header_list = []
        header = []
        average_length = [0]
        for i,symbol in enumerate(symbols):
            symbol = symbols[0]
            for j in range(i+1,len(symbols)):
                sym = symbols[j]
                if header:
                    header_list.append(len(header))
                    header = []
                for k,field in enumerate(symbol.fields):
                    symbol_field_values,symbol_field_averageLength = self.getPossibleValues(field)
                    sym_field_values = [b""]
                    if len(symbol_field_values) == 1:
                        m = 0
                        while len(sym_field_values[0]) < len(symbol_field_values[0]):
                            possibleValues,sym_field_averageLength = self.getPossibleValues(sym.fields[k + m])
                            sym_field_values[0] += possibleValues[0]
                            m + 1
                    else:
                        for l in range(0,len(symbol_field_values)- 1):
                            m = 0
                            try:
                                while len(sym_field_values[l]) < len(symbol_field_values[l]):
                                    possibleValues,sym_field_averageLength = self.getPossibleValues(sym.fields[k + m])
                                    sym_field_values[l] +=possibleValues[l]
                                    m + 1
                            except:
                                break
                    #sym_field_values = self.__getPossibleValues(sym.fields[k])
                    sm = difflib.SequenceMatcher(None, sym_field_values, symbol_field_values)
                    if sm.ratio() >= self.ratioValue :
                        self._logger.warning("Match at:" + str(sm.ratio()))
                        self._logger.warning("Between:" + str(sym_field_values) + "and" + str(symbol_field_values))
                        header.append(field)
                        try:
                            average_length[i] += symbol_field_averageLength
                        except:
                            average_length.append(symbol_field_averageLength)
                    else:
                        self._logger.warning("No Match at:" + str(sm.ratio()))
                        self._logger.warning("Between:" + str(sym_field_values) + "and" + str(symbol_field_values))
                        break
        self._logger.warning("Computing the end index of header...")
        total_length = int(sum(average_length)/len(average_length))
        number_of_fields_in_header = int(sum(header_list)/len(header_list))
        if number_of_fields_in_header >= 1 :
            self._logger.warning("The index: " + str(total_length) + " is probably the end of the header")
            self._logger.warning("Renaming fields")
            for symbol in symbols:
                try:
                    last_field_header,maxSize,indexInField = self.getFieldFromIndex(total_length,symbol)
                except:
                    pass
                for field in symbol.fields:
                    if field.name == last_field_header.name:
                        field.name += "_HEADER"
                        break
                    else:
                        field.name += "_HEADER"
            return True
        else:
            self._logger.warning("Sorry, I don't think there's a header in there")
            return False

    @typeCheck(list)
    def __executeFieldOnSymbols(self, symbols):
        for symbol in symbols:
            self.__rename_header_field_type(symbol)

    def __rename_header_field_type(self,symbol):
        for field in symbol.fields:
            if field.fields:
                # Field has subfields => Relation in there?
                for fiel in field.fields:
                    if fiel.domain.varType == self.fieldType:
                        return
                    fiel.name += "_HEADER"
            else:
                if field.domain.varType == self.fieldType:
                    return
            field.name += "_HEADER"




    @typeCheck(list)
    def __executeValueOnSymbols(self, symbols):
        for symbol in symbols:
            for field in symbol.fields:
                if hasattr(field.domain,"children"):
                    children_length = []
                    for child in field.domain.children:
                        if child.currentValue is not None:
                            children_length.append(child)
                    if len(children_length) == 1:
                        if children_length[0].currentValue ==self.separatorValue.domain.currentValue:
                            break
                    else:
                        raise "Too many children in Alt field to be parsed correctly"#feel fre to implement
                else:
                    if field.domain.currentValue == self.separatorValue.domain.currentValue:
                        break
                field.name+="_HEADER"

    @typeCheck(Field)
    def getPossibleValues(self,field):
        """
            Returns all the values a domain can take as well
            as the average length of the value
        Args:
            field:  netzob.Model.Vocabulary.Field

        Returns:
                possibleValues: list
                averageLength: int
        """
        possibleValues=[]
        averageLength = 0
        if isinstance(field.domain,Alt):
            #Field has children
            for child in field.domain.children:
                childValue = child.currentValue.tobytes()
                possibleValues.append(childValue)
                averageLength += len(childValue)
            averageLength = int(averageLength/len(field.domain.children))
        else:
            #Field has no children
            value = field.domain.currentValue.tobytes()
            possibleValues.append(value)
            averageLength = len(value)
        return possibleValues, averageLength

    def getFieldFromIndex(self, index,symbol):
        """
        This method tries to return the Field an index from a message belongs to.

        :param index: An int. The index of a value in a message belonging to a symbol
        :param symbol: The symbol we are working on
        :return: Field object, maxSize as int, field_index as int
        """
        totalSize = 0
        for field in symbol.fields:
            # Check if normal or Alt field:
            try:
                # If Alt field we get the min and max size for each children
                minSize, maxSize = (0, 0)
                for child in field.domain.children:
                    if child.dataType.size[1] > maxSize:
                        maxSize = child.dataType.size[1]
                    if child.dataType.size[0] < minSize or minSize == 0:
                        minSize = child.dataType.size[0]
            except:
                minSize, maxSize = field.domain.dataType.size
            totalSize += maxSize
            if index < (totalSize / 8):
                # Compute the index of the CRC relative to the field
                field_index = totalSize - (8 * index)
                field_index = totalSize - field_index
                IndexInField = (8 * index) - field_index
                return field, maxSize, IndexInField

    @property
    def ratio(self):
        """A boolean for ratio based searches

        :type: :bool
        """
        if self.__ratio is not None:
            return self.__ratio
        else:
            return None

    @ratio.setter
    @typeCheck(bool)
    def ratio(self, ratio):
        if ratio is None:
            raise TypeError("Ratio can't be none!")
        self.__ratio = ratio

    @property
    def ratioValue(self):
        """The ratio value.

        :type: :float
        """
        if self.__ratioValue is not None:
            return self.__ratioValue
        else:
            return None

    @ratioValue.setter
    @typeCheck(float)
    def ratioValue(self, ratioValue):
        if not 0 < ratioValue < 1:
            raise TypeError("RatioValue out of bounds")
        self.__ratioValue = ratioValue

    @property
    def field(self):
        """A boolean to indicate if we're doing a field based search or not.

        :type: :bool
        """
        if self.__field is not None:
            return self.__field
        else:
            return None

    @field.setter
    @typeCheck(bool)
    def field(self, field):
        if field is None:
            raise TypeError("Field can't be none!")
        self.__field = field

    @property
    def fieldType(self):
        """The type of field relation the field separator has

        :type: :str
        """
        return self.__fieldType

    @fieldType.setter
    @typeCheck(str)
    def fieldType(self, fieldType):
        self.__fieldType = fieldType


    @property
    def separator(self):
        """A boolean to indicate if we're doing a separator based search or not.

        :type: :bool
        """
        if self.__separator is not None:
            return self.__separator
        else:
            return None


    @separator.setter
    @typeCheck(bool)
    def separator(self, separator):
        if separator is None:
            raise TypeError("Field can't be none!")
        self.__separator = separator

    @property
    def separatorValue(self):
        """The type of field relation the field separator has

        :type: :str
        """
        if self.__separatorValue is not None:
            return self.__separatorValue
        else:
            return None

    @separatorValue.setter
    @typeCheck(Field)
    def separatorValue(self, separatorValue):
        self.__separatorValue = separatorValue