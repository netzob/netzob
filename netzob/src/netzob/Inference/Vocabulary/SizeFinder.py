import binascii
import collections
import io
import sys


#+----------------------------------------------
#| Local Imports
#+----------------------------------------------

from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt import Alt
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Size import Size

@NetzobLogger
class SizeFinder(object):
    """Provides multiple algorithms to find Size Relation in messages of a symbol (searches inside fields).
    """

    def __init__(self):
        pass

    @staticmethod
    @typeCheck(AbstractField)
    def findOnSymbol(symbol,create_fields=False,baseIndex = 0):
        """Find exact relations between fields in the provided
        symbol/field.

        :param symbol: the symbol in which we are looking for relations
        :type symbol: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        """

        cf = SizeFinder()
        return cf.executeOnSymbol(symbol,create_fields,baseIndex)


    @typeCheck(AbstractField)
    def executeOnSymbol(self,symbol,create_fields=False , baseIndex = 0):
        """Find IP fields of the provided symbol. Symbol must have messages to extract IP's from layer 3
        """
        self.__seek_size(symbol,create_fields,baseIndex)

    def __seek_size(self,symbol,create_fields = False, baseIndex = 0):
        message_relation_dict = dict()
        for key,message in enumerate(symbol.messages):
            results = self.__core_find(message.data)
            # Change stdout to get message print in buffer
            old_stdout = sys.stdout
            sys.stdout = buffer1 = io.StringIO()
            print(message)
            sys.stdout = old_stdout
            # Print results using click
            self._logger.debug("Results with false positives for [Message] : \n" + buffer1.getvalue() + "\n")
            self._logger.debug("[Number of results found] : " + str(results.total_length) + "\n")
            self._logger.debug("Result indexes in message: \n ")
            self._logger.debug("[Left to right search] : " + str(results.SizeLR) + "\n")
            self._logger.debug("[Right to left search] : " + str(results.SizeRL) + "\n")
            print('\n')
            message_relation_dict[str(key)] = results
        lengthLR = 0
        lengthRL = 0
        for key,value in message_relation_dict.items():
            if len(value.SizeLR) > lengthLR :
                lengthLR = len(value.SizeLR)
                longestLR = key
            if len(value.SizeRL) > lengthRL :
                lengthRL = len(value.SizeRL)
                longestRL = key
        results_LR = self.__delete_false_positives(message_relation_dict,message_relation_dict[longestLR].SizeLR,True)
        results_RL = self.__delete_false_positives(message_relation_dict,message_relation_dict[longestRL].SizeRL,False)
        #Delete all values that are under the base index
        results_LR = self.__delete_before_baseIndex(results_LR,baseIndex)
        results_RL = self.__delete_before_baseIndex(results_RL,baseIndex)
        self._logger.debug("Results : \n")
        self._logger.debug("[Left to right search] : " + str(results_LR) + "\n")
        self._logger.debug("[Right to left search] : " + str(results_RL) + "\n")
        if create_fields:
            if results_LR:
                self.__create_fields(symbol,results_LR)
            if results_RL:
                self.__create_fields(symbol,results_RL)

    def __delete_before_baseIndex(self,results,baseIndex):
        for value in results:
            if value[0] <= baseIndex:
                results.remove(value)
                self.__delete_before_baseIndex(results,baseIndex)
            else:
                continue
        return results

    def __create_fields(self,symbol,results):
        size_of_size = 1
        for result in results:
            field_to_split,maxSize,indexInField = self.__getFieldFromIndex(result[0],symbol)
            self._logger.debug("[Field to split] : " + field_to_split.name + "\n")
            first_field_dep ,maxSizefd, indexInFieldfd = self.__getFieldFromIndex(result[1],symbol)
            if indexInFieldfd != 0:
                #Create a subfield in the first_field_dependency
                values_first_field_dep = first_field_dep.getValues()
                if len(set(values_first_field_dep)) > 1:
                    #Alt field
                    values_first_field_dep_before = []
                    values_first_field_dep_after = []
                    for value in values_first_field_dep:
                        values_first_field_dep_before.append(value[:int(indexInFieldfd/8)])
                        values_first_field_dep_after.append(value[int(indexInFieldfd/8):])
                    first_field_dep_before = Field(domain = Alt(values_first_field_dep_before),
                                                   name = first_field_dep.name + "-0")
                    first_field_dep_after = Field(domain = Alt(values_first_field_dep_after),
                                                  name = first_field_dep.name + "-1")
                else:
                    #Static field
                    value = values_first_field_dep[0]
                    value_first_field_dep_before = value[:indexInFieldfd]
                    value_first_field_dep_after = value[indexInFieldfd:]
                    first_field_dep_before = Field(domain = Raw(value_first_field_dep_before),
                                               name = first_field_dep.name + "-0")
                    first_field_dep_after = Field(domain = Raw(value_first_field_dep_after),
                                              name = first_field_dep.name + "-1")
                first_field_dep.fields = [first_field_dep_before, first_field_dep_after]
            self._logger.debug("[First field dependency] : " + first_field_dep.name + "\n")
            field_dep = self.__get_field_dep(symbol,first_field_dep)
            #Check if static or Alt:
            values_before = []
            values_after = []
            field_to_split_values = field_to_split.getValues()
            if len(set(field_to_split_values)) > 1:
                #Alt field
                for value in field_to_split_values:
                    values_before.append(value[:int(indexInField/8)])
                    values_after.append(value[int(indexInField/8)+size_of_size:])
                #AltField before =>
                altField_before_Size = Field(domain = Alt(values_before),name = field_to_split.name + "-Before_SizeF")
                altField_after_Size = Field(domain = Alt(values_after),name = field_to_split.name + "-After_Size")
                sizeField = Field(domain = Size(field_dep),name = field_to_split.name + "-Size")
                field_to_split.fields = [altField_before_Size,sizeField,altField_after_Size]
            else:
                #Static field
                value_before = field_to_split_values[0][:int(indexInField/8)]
                value_after = field_to_split_values[0][int(indexInField/8)+size_of_size:]
                staticField_before_Size = Field(domain = Raw(value_before), name = field_to_split.name + "-Before_SizeF")
                staticField_after_Size = Field(domain = Raw(value_after), name = field_to_split.name + "-After_Size")
                sizeField = Field(domain = Size(field_dep), name = field_to_split.name + "-Size")
                field_to_split.fields = [staticField_before_Size, sizeField, staticField_after_Size]

    def __get_field_dep(self,symbol,first_field):
        field_dep = []
        afterff = False
        for field in symbol.fields:
            if field == first_field:
                if field.fields:
                    subfields = True
                afterff = True
            if afterff:
                if subfields:
                    field_dep.append(field.fields[1])
                    subfields = False
                else:
                    field_dep.append(field)
        return field_dep

    @typeCheck(dict)
    def __delete_false_positives(self,message_relation_dict,baseMessage,LR=True):
    ####Delete false positives####
    #If we don't find the size relation in every message we consider it a false positive
        result_list = []
        for value in baseMessage:
            keepValue = True
            for key,result in message_relation_dict.items():
                if LR:
                    result1 = result.SizeLR
                else:
                    result1 = result.SizeRL
                if value not in result1:
                    keepValue = False
            if keepValue:
                result_list.append(value)
        return result_list

    @typeCheck(bytes)
    def __core_find(self,message):
        # Define results structure
        relation_index_list =[] #list of tuples (index of size domain, index of first field in which starts the size domain field dependencies)
        results = collections.namedtuple('Results',['SizeLR','SizeRL','total_length'])
        #Search from left to right (=> length is length of data)
        results.SizeLR = self.__recursive_find(message,message,relation_index_list)
        #Search from right to left (=> length is length of header)
        relation_index_list = []
        results.SizeRL = self.__recursive_find(message[::-1],message[::-1],relation_index_list)
        #Get the index on non reversed string
        for index,result in enumerate(results.SizeRL) :
            results.SizeRL[index] =(len(message) - result[0] - 1, result[1])
        #Delete repeated values:
        for result1 in results.SizeLR:
            if result1 in results.SizeRL :
                results.SizeRL.remove(result1)
        #Compute number of results
        results.total_length = len(results.SizeRL) + len(results.SizeLR)
        return results

    def __recursive_find(self,totalmessage,workstring,index_list):
        #Suppose the size is coded on one byte
        size_of_size = 1
        #Transform length of workstring to byte string
        length = self.__hex_to_bytes(hex(len(workstring[size_of_size:])))
        if length ==  b'\x00':
            #length is null which means we are probably at the end of workstring
            return index_list
        if index_list:
            #Already found a size field. We now search what is after that size field
            res_index = totalmessage.find(length,index_list[-1][0])
        else:
            #No size field found yet. We search the whole string
            res_index = totalmessage.find(length)
        if res_index == -1:
            #Check if we're done looking => workstring is one
            if len(workstring) == 1:
                return index_list
            #Nothing found => We increment by one and look again
            workstring = workstring[1:]
            return self.__recursive_find(totalmessage,workstring, index_list)
        else:
            # One match, looking for next match
            #Calculate the index of workstring in message
            related_index = len(totalmessage) - len(workstring) + 1
            # This is a protection to make sure we're not computing size of fields before the size
            if res_index <= related_index:
                #This protection avoids a stack overflow by breaking out of loop
                if index_list and (res_index,related_index) == index_list[-1]:
                    return index_list
                #Store index of result and index of first size dependency field as tuple in list
                index_list.append((res_index,related_index))
                # DIVIDE workstring and apply find again
                workstring = workstring[res_index + size_of_size:]
                # Call function again
                # Put itteration counter back to 0
                return self.__recursive_find(totalmessage,workstring, index_list)
            else:
                if len(workstring) == 1:
                    return index_list
                # Nothing found => We increment by one and look again
                workstring = workstring[1:]
                return self.__recursive_find(totalmessage, workstring, index_list)

    @typeCheck(str)
    def __hex_to_bytes(self,hexString):
        """Transforms a string obtained from hex method to a byte string"""
        #Remove 0X at beginning
        hexString = hexString[2:]
        try:
            bytesString = binascii.unhexlify(hexString)
        except:
            bytesString = binascii.unhexlify("0"+hexString)
        return bytesString

    def __getFieldFromIndex(self, index,symbol):
        """
        This method tries to return the Field that the index from a message belongs to. It also returns the MaxSize of the Field
        and the value of this index inside the field

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
            if maxSize is None:
                maxSize = 0
            totalSize += maxSize
            if index < (totalSize / 8):
                indexInField = (index * 8 ) - (totalSize-maxSize)
                return field, maxSize, indexInField