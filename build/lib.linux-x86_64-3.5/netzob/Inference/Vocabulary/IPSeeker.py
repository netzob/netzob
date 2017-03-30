import binascii
import collections
import socket
import io
import sys


#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob import _libRelation
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.AbstractType import AbstractType
from netzob.Model.Types.Raw import Raw
from netzob.Model.Types.Integer import Integer
from netzob.Model.Vocabulary.AbstractField import AbstractField
from  netzob.Model.Vocabulary.Domain.Variables.Leafs.CRC32 import CRC32

from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt import Alt

@NetzobLogger
class IPSeeker(object):
    """Provides multiple algorithms to find IP in messages.

    >>> import binascii
    >>> from netzob.all import *
    >>> samples = [b"0007ff2f000000000000", b"0011ffaaaaaaaaaaaaaabbcc0010000000000000", b"0012ffddddddddddddddddddddfe1f000000000000"]
    >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
    >>> symbol = Symbol(messages=messages)
    >>> Format.splitStatic(symbol)
    >>> rels = RelationFinder.findOnFields(symbol.fields[1], symbol.fields[3])
    >>> print(len(rels))
    1
    >>> for rel in rels:
    ...     print(rel["relation_type"] + " between " + rel["x_field"].name + ":" + rel["x_attribute"] + \
            " and " + rel["y_field"].name + ":" + rel["y_attribute"])
    SizeRelation between Field-1:value and Field-3:size

    >>> rels = RelationFinder.findOnSymbol(symbol)
    >>> print(len(rels))
    1
    >>> for rel in rels:
    ...     print(rel["relation_type"] + " between fields " + str([x.name for x in rel["x_fields"]]) + ":" + rel["x_attribute"] + \
            " and fields " + str([y.name for y in rel["y_fields"]]) + ":" + rel["y_attribute"])
    SizeRelation between fields ['Field-1']:value and fields ['Field-3']:size

    """

    def __init__(self):
        pass

    @staticmethod
    @typeCheck(AbstractField)
    def findOnSymbol(symbol,create_fields=False):
        """Find exact relations between fields in the provided
        symbol/field.

        :param symbol: the symbol in which we are looking for relations
        :type symbol: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        """

        cf = CRCFinder()
        return cf.executeOnSymbol(symbol,create_fields)


    @typeCheck(AbstractField)
    def executeOnSymbol(self,symbol,create_fields):
        """Find IP fields of the provided symbol. Symbol must have messages to extract IP's from layer 3
        """
        ip = symbol.messages[0].l3DestinationAddress
        self.__seek_ip(ip,symbol,create_fields)
        ip = symbol.messages[0].l3SourceAddress
        self.__seek_ip(ip, symbol, create_fields)


    def __seek_ip(self,ip, symbol,create_fields = False):

        #Convert IP to hex value:
        hexipstring = binascii.hexlify(socket.inet_aton(ip))
        hexipstring =  binascii.unhexlify(hexipstring)
        index_list = []
        for message in symbol.messages:
            results = self.__core_find(message.data,hexipstring,index_list)
            #Change stdout to get message print in buffer
            old_stdout = sys.stdout
            sys.stdout = buffer1 = io.StringIO()
            print(message)
            sys.stdout = old_stdout
            #Print results using click
            self._logger.debug("Results for [Message] : \n" + buffer1.getvalue() + "\n")
            self._logger.debug("[Number of results found] : " + str(results.total_length) + "\n")
            self._logger.debug("Result indexes in message: \n ")
            self._logger.debug("[Whole IP Big Endian] : " +  str(results.full_be) +"\n" )
            self._logger.debug("[Three last terms of IP Big Endian] : " + str(results.one_less_be) + "\n" )
            self._logger.debug("[Two last terms of IP Big Endian] : " + str(results.two_less_be)  + "\n" )
            self._logger.debug("[Whole IP Little Endian] : " + str(results.full_le) + "\n"  )
            self._logger.debug("[Three last terms of IP Little Endian] : " + str(results.one_less_le) + "\n" )
            self._logger.debug("[Two last terms of IP Little Endian] : " + str(results.two_less_le) + "\n" )
            print('\n')
            if create_fields:
                self._logger.debug("Attempting to create new fields")
                if symbol.fields:
                    self._logger.debug("Refining search to fields...")
                    for field in symbol.fields:
                        subfield_index_list = []
                        field_values = field.getValues()
                        number_of_values = len(set(field_values))
                        # Get field length
                        max_length = max([len(i) for i in field_values])
                        # Check if values in messages are different for need to create an alternative field or a simple raw field (above 1 if several values):
                        if number_of_values > 1:
                            # More than one value => MUST CREATE ALT FIELD
                            # TODO
                            pass
                        else:
                            mess = field_values[0]
                            field_result = self.__core_find(mess,hexipstring,index_list)
                            if field_result.full_be or field_result.one_less_be or field_result.two_less_be or field_result.full_le or field_result.one_less_le or field_result.two_less_le :
                            # Searchstring not always split in between fields => Need to create subfields
                                self._logger.debug("Searchstring inside fields, creating subfields...")
                                # Create field dict which contains fields and index
                                fields_dict = dict()
                                if number_of_values > 1:
                                    #More than one value => MUST CREATE ALT FIELD
                                    #TODO
                                    pass
                                else:
                                    #Can create simple static subfield
                                    for i in field_result.full_be:
                                        fields_dict[i] = Field(name = 'FullIpBe'+ str(i),domain = Raw(hexipstring))
                                        subfield_index_list.append(i)
                                        subfield_index_list.append(i + 4)
                                    for i in field_result.one_less_be:
                                        fields_dict[i] = Field(name='ThreeTIpBe' + str(i), domain=Raw(hexipstring[1:]))
                                        subfield_index_list.append(i)
                                        subfield_index_list.append(i + 3)
                                    for i in field_result.two_less_be:
                                        fields_dict[i] = Field(name='TwoTIpBe' + str(i), domain=Raw(hexipstring[2:]))
                                        subfield_index_list.append(i)
                                        subfield_index_list.append(i + 2)
                                    for i in field_result.full_le:
                                        fields_dict[i]= Field(name='FullIpLe' + str(i), domain=Raw(hexipstring[::-1]))
                                        subfield_index_list.append(i)
                                        subfield_index_list.append(i + 4)
                                    for i in field_result.one_less_le:
                                        fields_dict[i] = Field(name='ThreeTIpLe' + str(i), domain=Raw(hexipstring[1:][::-1]))
                                        subfield_index_list.append(i)
                                        subfield_index_list.append(i + 3)
                                        fields_dict[i] = Field(name='TwoTIpLe' + str(i), domain=Raw(hexipstring[2:][::-1]))
                                        subfield_index_list.append(i)
                                        subfield_index_list.append(i + 2)
                                    #Sort list in order
                                    subfield_index_list.append(max_length)
                                    subfield_index_list.insert(0,0)
                                    #Remove duplicates (there shouldn't be any!)
                                    subfield_index_list = list(set(subfield_index_list))
                                    subfield_index_list = sorted(subfield_index_list, key=int)
                                    #Create static field for every two elements of the subfield index_list as they represent beginning and end
                                    for i,x in enumerate(subfield_index_list):
                                        #Check if index is pair
                                        if(i%2 == 0):
                                        #Create static field and store it's beginning index in the structure
                                            try:
                                                fields_dict[x] = Field(name='Field' + str(i), domain=Raw(
                                                    field_values[0][subfield_index_list[i]:subfield_index_list[i + 1]]))
                                            except:
                                                fields_dict[x] = Field(name='Field' + str(i),
                                                                       domain=Raw(field_values[0][subfield_index_list[i]:]))
                                        else:
                                        # Don't do shit
                                            pass
                                    #Create a list of all subfields in order
                                    od = collections.OrderedDict(sorted(fields_dict.items()))
                                    field_list = list(od.values())
                                if not field.fields:
                                    #No subfields
                                    field.fields = field_list
                                else:
                                    #Already contains subfields. We need to just insert our IP subfields in it.
                                    #Get the indexes of Fields which have a name other than FieldX (where X is a number)
                                    only_Ip_fields_dict = dict()
                                    for index,element in fields_dict.items():
                                        if not element.name[:5] == "Field":
                                           only_Ip_fields_dict[index] = element
                                    #Find to which field these indexes belong to in the old symbol
                                    for index,element in only_Ip_fields_dict.items():
                                        new_field_dict = dict()
                                        field_to_split,maxSize,indexInField = self.__getFieldFromIndex(index,field)
                                        indexInField = int(indexInField/8)
                                        new_field_dict[indexInField] = element
                                        if field_to_split.getValues()[0][:indexInField]:
                                            new_field_dict[0] = Field(name='FieldBeforeIp' + str(index),
                                              domain=Raw(field_to_split.getValues()[0][:indexInField]))
                                        new_field_dict[indexInField] = element
                                        #Get Size of the IP Field
                                        minSize, sizeIp = element.domain.dataType.size
                                        sizeIp = int(sizeIp/8)
                                        if field_to_split.getValues()[0][indexInField + sizeIp:] :
                                            new_field_dict[indexInField+sizeIp] = Field(name='FieldAfterIp' + str(index),
                                              domain=Raw(field_to_split.getValues()[0][indexInField + sizeIp:]))
                                        od = collections.OrderedDict(sorted(new_field_dict.items()))
                                        field_list = list(od.values())
                                        #DELETE EMPTY DOMAIN FIELDS
                                        field_to_split.fields = field_list
                            else:
                                #Searchstring always split in between other fields => Delete fields and create new ones Or just return indexes, and let user redefine fields manually
                                # symbol.fields = []
                                self._logger.debug("Searchstring in between fields...")
                                self._logger.debug("[1] : Delete all fields and replace by IPFIELDS"+ "\n")
                                self._logger.debug("[ANY] : Just print the index in the message"+ "\n")
        return


    def __core_find(self,message, hexipstring, index_list):
        # Define results structure
        results = collections.namedtuple('Results',
                                         ['full_be', 'one_less_be', 'two_less_be', 'full_le', 'one_less_le', 'two_less_le',
                                          'total_length'])
        results.full_be = self.__recursive_find(message, index_list, hexipstring)
        index_list = []
        results.one_less_be = self.__recursive_find(message, index_list, hexipstring[1:])
        index_list = []
        results.two_less_be = self.__recursive_find(message, index_list, hexipstring[2:])
        index_list = []
        # little endian search
        results.full_le = self.__recursive_find(message, index_list, hexipstring[::-1])
        index_list = []
        results.one_less_le = self.__recursive_find(message, index_list, hexipstring[1:][::-1])
        index_list = []
        results.two_less_le = self.__recursive_find(message, index_list, hexipstring[2:][::-1])
        # Remove results from one byte less searches in two bytes less searches
        for value in results.one_less_be:
            if value + 1 in results.two_less_be:
                results.two_less_be.remove(value + 1)
            if value in results.two_less_be:
                results.two_less_be.remove(value)
            if value in results.one_less_le:
                results.one_less_le.remove(value)
            if value in results.two_less_le:
                results.two_less_le.remove(value)
        for value in results.one_less_le:
            if value + 1 in results.two_less_le:
                results.two_less_le.remove(value + 1)
            if value in results.two_less_le:
                results.two_less_le.remove(value)
        for value in results.two_less_be:
            if value in results.two_less_le:
                results.two_less_le.remove(value)
        # Remove results from full bytes searches in one and two bytes less searches
        for value in results.full_be:
            if value + 1 in results.one_less_be:
                results.one_less_be.remove(value + 1)
                if value + 2 in results.two_less_be:
                    results.two_less_be.remove(value + 2)
            if value in results.one_less_be:
                results.one_less_be.remove(value)
                if value in results.two_less_be:
                    results.two_less_be.remove(value)
        for value in results.full_le:
            if value + 1 in results.one_less_le:
                results.one_less_le.remove(value + 1)
                if value + 2 in results.two_less_le:
                    results.two_less_le.remove(value + 2)
            if value in results.one_less_le:
                results.one_less_le.remove(value)
                if value in results.two_less_le:
                    results.two_less_le.remove(value)
                    # Remove results from LE wich are already in BE
            if value in results.full_be:
                results.full_le.remove(value)
        results.total_length = len(results.full_be) + len(results.full_le) + len(results.one_less_be) + len(
            results.two_less_be) + len(results.one_less_le) + len(results.two_less_le)
        return results

    def __recursive_find(self,workstring, index_list, hexipstring,add_length = 0):
        res_index = workstring.find(hexipstring)
        if res_index == -1:
            # NOTHING FOUND
            return index_list
        else:
            # One match, looking for next match
            # STORE INDEX IN LIST
            if index_list:
                # List not empty, already has and index
                index_list.append(index_list[-1] + res_index + add_length)
            else:
                index_list.append(res_index+add_length)
            # DIVIDE workstring and apply find again
            workstring = workstring[res_index + len(hexipstring):]
            # Call function again
            return self.__recursive_find(workstring, index_list, hexipstring,len(hexipstring))

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
            totalSize += maxSize
            if index < (totalSize / 8):
                # Compute the index of the CRC relative to the field
                #field_index = totalSize - (8 * index)
                #field_index = totalSize - field_index
                #indexInField = (8 * index) - field_index
                field_index = totalSize - maxSize
                indexInField = (index * 8 ) - (totalSize-maxSize)
                return field, maxSize, indexInField