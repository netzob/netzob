
import binascii
import collections
import IPython

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
from  netzob.Model.Vocabulary.Domain.Variables.Leafs import CRC32


@NetzobLogger
class CRCFinder(object):
    """Provides multiple algorithms to find CRC in messages.

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
    def findOnSymbol(symbol):
        """Find exact relations between fields in the provided
        symbol/field.

        :param symbol: the symbol in which we are looking for relations
        :type symbol: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        """

        cf = CRCFinder()
        return cf.executeOnSymbol(symbol)


    @typeCheck(AbstractField)
    def executeOnSymbol(self, symbol,create_fields = False):
        """Find crc32 relations between fields of the provided symbol. Symbol must have messages
        """
        create_fields = True
        for message in symbol.messages:
            results = collections.namedtuple('Results', ['CRC_be', 'CRC_le', 'CRC_mid_be', 'CRC_mid_le'])
            field_results = collections.namedtuple('Results', ['CRC_be', 'CRC_le', 'CRC_mid_be', 'CRC_mid_le'])
            searched_string = message.data
            results.CRC_be, results.CRC_le = self.search_CRC(searched_string)
            results.CRC_mid_be, results.CRC_mid_le = self.search_mid_CRC(searched_string)
            self._logger.critical("Found the following results:")
            self._logger.critical("CRC_BE : " + str(results.CRC_be) + "")
            self._logger.critical("CRC_LE : " + str(results.CRC_le) + "")
            self._logger.critical("CRC_mid_be : " + str(results.CRC_mid_be) + "")
            self._logger.critical("CRC_mid_le : " + str(results.CRC_mid_le) + "")
        if create_fields and results:
            self._logger.debug("Refining search to fields...")
            if symbol.fields:
                for field in symbol.fields:
                    field_values = field.getValues()
                    number_of_values = len(set(field_values))
                    # Get field length
                    max_length = max([len(i) for i in field_values])
                    val = field_values[0] # Does not matter if field is Static or ALT, it always follows the same scheme.
                    fields_dict = dict()
                    field_results.CRC_be, field_results.CRC_le = self.search_CRC(val)
                    field_results.CRC_mid_be, field_results.CRC_mid_le = self.search_mid_CRC(val)
                    if field_results.CRC_be or field_results.CRC_le or field_results.CRC_mid_be or field_results.CRC_mid_le:
                        # If refining the search gives results => The CRC and the elements that are used for the CRC are all inside one field
                        # Hence we create subfields
                        self._logger.critical("Found the following results in fields:")
                        self._logger.critical("CRC_BE : " + str(field_results.CRC_be) + "")
                        self._logger.critical("CRC_LE : " + str(field_results.CRC_le) + "")
                        self._logger.critical("CRC_mid_be : " + str(field_results.CRC_mid_be) + "")
                        self._logger.critical("CRC_mid_le : " + str(field_results.CRC_mid_le) + "")
                        if max_length > 4:
                            # More than one value (ALT FIELDS) => Need to resize field to CRC and add ALT Fields around
                            # Will need to create the CRC field and static/ALT fields around it.
                            #STEP1: Get all possible values. Already in field_values variable.
                            #STEP2:CREATE ALT fields
                            #Step3: Create CRC field
                            for i in field_results.CRC_be:
                                #fields_dict[i + 5] = Field(name = 'FieldafterCRC'+str(i),domain = )
                                #fields_dict[i] = Field(name = 'CRC32_BE'+ str(i),domain = CRC32())
                                subfield_index_list.append(i)
                                subfield_index_list.append(i + 4)
                            #for i in field_results.CRC_le:

                            #for i in field_results.CRC_mid_be:
                            #for i in field_results.CRC_mid_le:

                            #TODO
                            pass
                        else:
                            # Field is only the CRC so we replace it by a CRC relation field
                            #TODO
                            pass
                    else:
                        print(symbol)
                        # CRC and arguments always split in between other fields => Delete fields and create new ones Or just return indexes, and let user redefine fields manually
                        #Step1: Find field corresponding to index result
                        #Step2: Check if field is not CRC (if all values of size 4)
                        #Step2.a: If, then just change field name
                        #Step3 : See if end of CRC still in field
                        #Step3.A : if still in field, deleter field and create new CRC field as well as two other fields
                        #Step3.B: If not, delete the two fields and create new CRC field as well as two other fields
                        if results.CRC_be:
                            for crcindex in results.CRC_be:
                                searchedfield = self.getFieldFromIndex(crcindex,symbol)
                                print(index)
                                pass

            else:
                self._logger.debug("Symbol has no fields. Creating new ones...")
        else:
            self._logger.debug("Sorry, no CRC found")

    def search_CRC(self,searched_string):
        found_BE_CRCS_index = []
        found_LE_CRCS_index = []
        i = 0  # Start search index
        while i + 5 < len(searched_string) - 1:
            # BIG ENDIAN BASIC SEARCH
            try:
                compared = bytes.fromhex(hex(binascii.crc32(searched_string[i + 4:]))[2:])[::-1]
            except:
                compared = bytes.fromhex('0' + hex(binascii.crc32(searched_string[i + 4:]))[2:])[::-1]
            if searched_string[i:i + 4] == compared:
                self._logger.critical(compared)
                self._logger.debug("Found a CRC, adding it to found_BE_CRCS_index[]!")
                found_BE_CRCS_index.append(i)
            # LITTLE ENDIAN BASIC SEARCH
            try:
                compared = bytes.fromhex(hex(binascii.crc32(searched_string[i + 4:][::-1]))[2:])[::-1]
            except:
                compared = bytes.fromhex('0' + hex(binascii.crc32(searched_string[i + 4:][::-1]))[2:])[::-1]
            if searched_string[i:i+4] == compared :
                self._logger.debug("Found a LE CRC, adding to found_LE_CRCS_index[]!")
                found_LE_CRCS_index.append(i)
            i += 1
        return found_BE_CRCS_index,found_LE_CRCS_index

    def search_mid_CRC(self,searched_string):
        found_BE_CRCS_index = []
        found_LE_CRCS_index = []
        i = 0  # Start search index
        while i + 6 < len(searched_string):
            # BIG ENDIAN BASIC SEARCH
            try:
                compared = bytes.fromhex(hex(binascii.crc32(searched_string[i-5:i-1] + b'\x00\x00\x00\x00' + searched_string[i+3:i+7]))[2:])
            except:
                compared = bytes.fromhex('0' + hex(binascii.crc32(searched_string[i-5:i-1] + b'\x00\x00\x00\x00' + searched_string[i+3:i+7]))[2:])
            if searched_string[i:i + 4] == compared:
                self._logger.debug("Found a CRC, adding it to found_BE_CRCS_index[]!")
                found_CRCS_index.append(i)
            # LITTLE ENDIAN BASIC SEARCH
            compared = compared[::-1]
            if searched_string[i-1:i+3] == compared :
                self._logger.debug("Found a LE CRC, adding to found_LE_CRCS_index[]!")
                found_LE_CRCS_index.append(i-1)
            i += 1
        return found_BE_CRCS_index,found_LE_CRCS_index

    def getFieldFromIndex(self, index,symbol):
        #field_dict = dict()
        totalSize = 0
        for field in symbol.fields:
            #Check if normal or Alt field:
            try:
                #If Alt field we get the min and max size for each children
                minSize, maxSize = (0,0)
                for child in field.domain.children:
                    if child.dataType.size[1] > maxSize:
                        maxSize = child.dataType.size[1]
                    if child.dataType.size[0] < minSize or minSize == 0:
                        minSize = child.dataType.size[0]
            except:
                minSize,maxSize = field.domain.dataType.size
            totalSize += maxSize
            if index < (totalSize/8):
                return field
             #field_dict[field] = minSize,maxSize
        #pass