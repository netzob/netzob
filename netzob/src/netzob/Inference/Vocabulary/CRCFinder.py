import binascii
import collections

from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt import Alt
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Variables.Leafs.CRC32 import CRC32


@NetzobLogger
class CRCFinder(object):
    r"""Provides multiple algorithms to find CRC in messages of a symbol (searches inside fields).

    CRC32 Little endian of all the fields that follow
    >>> from netzob.all import *
    >>> message1 = RawMessage(data=b'\xc5k@@\x003\x00\n|\xd9\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81\x8c\x00\x1b\x00\x00\x00\x16\x00\x00\x00\x18\x00\x00\x00JK\x98\x9eU\xcd\x10\x00\x01\x00\x03\x00\xfc\xf7\xe1\x82\x04\x00\x00\x00\x1a\x10\x00\x00\x15\x02\x00\x01')
    >>> message2 = RawMessage(data=b'\xc5k@@\x003\x00\n|\xd9\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81\x8c\x00\xa8\x00\x00\x00)\x00\x00\x00\x18\x00\x00\x00\xbe=\xcd\xd8U\xcd\x0c\x00\x01\x00\x03\x00\xfc\xf7\xe1\x82\x08\x00\x00\x00\x01\x84\x80\x00\xfc\xf7\xe1\x82')
    >>> message3 = RawMessage(data=b'\xc5k@@\x003\x00\n|\xd9\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81\x84\x00\xae\x00\x00\x00.\x00\x00\x00\x18\x00\x00\x00\xd6j\xc4aU\xcd\x0c\x00\x01\x00\x03\x00\xd9?\x91\xa8\x08\x00\x00\x00\x01\x84\x80\x00\xd9?\x91\xa8')
    >>> messages = [message1,message2,message3]
    >>> symbol = Symbol(messages=messages)
    >>> Format.splitStatic(symbol)
    >>> seeker = CRCFinder()
    >>> seeker.findOnSymbol(symbol=symbol,create_fields=True)
    >>> print(symbol)# doctest: +NORMALIZE_WHITESPACE
    Source | Destination | Field-0                                                      | Field-1 | Field-2 | Field-3 | Field-4        | Field-5 | Field-6                        | CRC32_LE36   | Field-8 | Field-9 | Field-10               | Field-11      | Field-12       | Field-13       | Field-14 | Field-15
    ------ | ----------- | ------------------------------------------------------------ | ------- | ------- | ------- | -------------- | ------- | ------------------------------ | ------------ | ------- | ------- | ---------------------- | ------------- | -------------- | -------------- | -------- | ------------------
    None   | None        | 'Åk@@\x003\x00\n|Ù\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81' | '\x8c'  | '\x00'  | '\x1b'  | '\x00\x00\x00' | '\x16'  | '\x00\x00\x00\x18\x00\x00\x00' | 'JK\x98\x9e' | 'UÍ'    | '\x10'  | '\x00\x01\x00\x03\x00' | 'ü÷á\x82\x04' | '\x00\x00\x00' | '\x1a\x10\x00' | '\x00'   | '\x15\x02\x00\x01'
    None   | None        | 'Åk@@\x003\x00\n|Ù\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81' | '\x8c'  | '\x00'  | '¨'     | '\x00\x00\x00' | ')'     | '\x00\x00\x00\x18\x00\x00\x00' | '¾=ÍØ'       | 'UÍ'    | '\x0c'  | '\x00\x01\x00\x03\x00' | 'ü÷á\x82\x08' | '\x00\x00\x00' | '\x01\x84\x80' | '\x00'   | 'ü÷á\x82'
    None   | None        | 'Åk@@\x003\x00\n|Ù\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81' | '\x84'  | '\x00'  | '®'     | '\x00\x00\x00' | '.'     | '\x00\x00\x00\x18\x00\x00\x00' | 'ÖjÄa'       | 'UÍ'    | '\x0c'  | '\x00\x01\x00\x03\x00' | 'Ù?\x91¨\x08' | '\x00\x00\x00' | '\x01\x84\x80' | '\x00'   | 'Ù?\x91¨'
    ------ | ----------- | ------------------------------------------------------------ | ------- | ------- | ------- | -------------- | ------- | ------------------------------ | ------------ | ------- | ------- | ---------------------- | ------------- | -------------- | -------------- | -------- | ------------------

    CRC32 Little endian of the form cafebabe0000deadbeef where 0000 is then replaced by CRC

    >>> from netzob.all import *
    >>> message1 = RawMessage(data=b'\xc5k@@\x003\x00\n|\xd9\x80\x04\x00\n|\n\x90\x00\x00\x00\xc4\x00\x01\x01\x0e\xd2E~x\x00\x00\x00')
    >>> message2 = RawMessage(data=b'\xc5k@@\x003\x00\n|\xd9\x80\x04\x00\n|\n\x90\x00\x00\x00\xc4\x00\x01\x01\xf7\x15\xc6\xad\t\x00\x00\x00')
    >>> message3 = RawMessage(data=b'\xc5k@@\x003\x00\n|\xd9\x80\x04\x00\n|\n\x90\x00\x00\x00\xc4\x00\x01\x01\x87jk8\x11\x00\x00\x00')
    >>> messages = [message1,message2,message3]
    >>> symbol = Symbol(messages=messages)
    >>> Format.splitStatic(symbol)
    >>> seeker = CRCFinder()
    >>> seeker.findOnSymbol(symbol=symbol,create_fields=True)
    >>> print(symbol)# doctest: +NORMALIZE_WHITESPACE
    Source | Destination | Field-0                                                           | CRC32_mid_LE24 | Field-1 | Field-2
    ------ | ----------- | ----------------------------------------------------------------- | -------------- | ------- | --------------
    None   | None        | 'Åk@@\x003\x00\n|Ù\x80\x04\x00\n|\n\x90\x00\x00\x00Ä\x00\x01\x01' | '\x0eÒE~'      | 'x'     | '\x00\x00\x00'
    None   | None        | 'Åk@@\x003\x00\n|Ù\x80\x04\x00\n|\n\x90\x00\x00\x00Ä\x00\x01\x01' | '÷\x15Æ\xad'   | '\t'    | '\x00\x00\x00'
    None   | None        | 'Åk@@\x003\x00\n|Ù\x80\x04\x00\n|\n\x90\x00\x00\x00Ä\x00\x01\x01' | '\x87jk8'      | '\x11'  | '\x00\x00\x00'
    ------ | ----------- | ----------------------------------------------------------------- | -------------- | ------- | --------------

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
    def executeOnSymbol(self, symbol,create_fields):
        """Find crc32 relations between fields of the provided symbol. Symbol must have messages
        """
        for message in symbol.messages:
            results = collections.namedtuple('Results', ['CRC_be', 'CRC_le', 'CRC_mid_be', 'CRC_mid_le'])
            field_results = collections.namedtuple('Results', ['CRC_be', 'CRC_le', 'CRC_mid_be', 'CRC_mid_le'])
            searched_string = message.data
            #TODO add right to left search (here is only left to right => Not found if it's CRC of header)
            results.CRC_be, results.CRC_le = self._search_CRC(searched_string)
            results.CRC_mid_be, results.CRC_mid_le = self._search_mid_CRC(searched_string)
            self._logger.debug("Found the following results:")
            self._logger.debug("CRC_BE : " + str(results.CRC_be) + "")
            self._logger.debug("CRC_LE : " + str(results.CRC_le) + "")
            self._logger.debug("CRC_mid_be : " + str(results.CRC_mid_be) + "")
            self._logger.debug("CRC_mid_le : " + str(results.CRC_mid_le) + "")
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
                    field_results.CRC_be, field_results.CRC_le = self._search_CRC(val)
                    field_results.CRC_mid_be, field_results.CRC_mid_le = self._search_mid_CRC(val)
                    if field_results.CRC_be or field_results.CRC_le or field_results.CRC_mid_be or field_results.CRC_mid_le:
                        # If refining the search gives results => The CRC and the elements that are used for the CRC are all inside one field
                        # Hence we create subfields
                        self._logger.debug("Found the following results in fields:")
                        self._logger.debug("CRC_BE : " + str(field_results.CRC_be) + "")
                        self._logger.debug("CRC_LE : " + str(field_results.CRC_le) + "")
                        self._logger.debug("CRC_mid_be : " + str(field_results.CRC_mid_be) + "")
                        self._logger.debug("CRC_mid_le : " + str(field_results.CRC_mid_le) + "")
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
                        # CRC and arguments always split in between other fields => Delete fields and create new ones Or just return indexes, and let user redefine fields manually
                        #Step1: Find field corresponding to index result
                        #Step2: Check if field is not CRC (if all values of size 4)
                        #Step2.a: If, then just change field name
                        #Step3 : See if end of CRC still in field
                        #Step3.A : if still in field, deleter field and create new CRC field as well as two other fields
                        #Step3.B: If not, delete the two fields and create new CRC field as well as two other fields
                        if results.CRC_le:
                            self.__automate_field_creation(results.CRC_le,symbol,endianness='little')
                        elif results.CRC_be:
                            self.__automate_field_creation(results.CRC_be,symbol,endianness='big')
                        elif results.CRC_mid_be:
                            self.__automate_mid_field_creation(results.CRC_mid_be,symbol,endianness='big')
                        elif results.CRC_mid_le:
                            self.__automate_mid_field_creation(results.CRC_mid_le, symbol, endianness='little')
                        else:
                            self._logger.debug('Did not succeed creating fields')


            else:
                self._logger.debug("Symbol has no fields. Creating new ones...")
        else:
            self._logger.debug("Sorry, no CRC found")


    def _search_CRC(self,searched_string):
        """
        Looks for a CRC in BE and LE. The CRC is computed thanks to all the data following the CRC

        :param searched_string: The string we are working on
        :return: found_BE_CRCS_index as int,found_LE_CRCS_index as int
        """
        found_BE_CRCS_index = []
        found_LE_CRCS_index = []
        i = 0  # Start search index
        while i + 5 < len(searched_string) - 1:
            # LITTLE ENDIAN BASIC SEARCH
            try:
                compared = bytes.fromhex(hex(binascii.crc32(searched_string[i + 4:]))[2:])[::-1]
            except:
                compared = bytes.fromhex('0' + hex(binascii.crc32(searched_string[i + 4:]))[2:])[::-1]
            if searched_string[i:i + 4] == compared:
                self._logger.debug(compared)
                self._logger.debug("Found a CRC, adding it to found_LE_CRCS_index[]!")
                found_LE_CRCS_index.append(i)
            # BIG ENDIAN BASIC SEARCH
            try:
                compared = bytes.fromhex(hex(binascii.crc32(searched_string[i + 4:][::-1]))[2:])[::-1]
            except:
                compared = bytes.fromhex('0' + hex(binascii.crc32(searched_string[i + 4:][::-1]))[2:])[::-1]
            if searched_string[i:i+4] == compared :
                self._logger.debug("Found a LE CRC, adding to found_BE_CRCS_index[]!")
                found_BE_CRCS_index.append(i)
            i += 1
        return found_BE_CRCS_index,found_LE_CRCS_index


    def _search_mid_CRC(self,searched_string):
        """
        Looks for a CRC of the value b'\xca\xfe\x00\x00\x00\x00\xba\xbe', the b'\x00\x00\x00\x00' is then replaced by the computed CRC in the message.
        Return values are the index results of the search in little and big endian

        :param searched_string: A Raw string in which we look for the CRC
        :return: found_BE_CRCS_index as int,found_LE_CRCS_index as int
        """
        found_BE_CRCS_index = []
        found_LE_CRCS_index = []
        i = 0  # Start search index
        while i + 6 < len(searched_string):
            # BIG ENDIAN BASIC SEARCH
            try:
                compared = bytes.fromhex(hex(binascii.crc32(searched_string[i-5:i-1] + b'\x00\x00\x00\x00' + searched_string[i+3:i+7]))[2:])
            except:
                compared = bytes.fromhex('0' + hex(binascii.crc32(searched_string[i-5:i-1] + b'\x00\x00\x00\x00' + searched_string[i+3:i+7]))[2:])
            if searched_string[i-1:i + 3] == compared:
                self._logger.debug("Found a CRC, adding it to found_BE_CRCS_index[]!")
                found_BE_CRCS_index.append(i-1)
            # LITTLE ENDIAN BASIC SEARCH
            compared = compared[::-1]
            if searched_string[i-1:i+3] == compared :
                self._logger.debug("Found a LE CRC, adding to found_LE_CRCS_index[]!")
                found_LE_CRCS_index.append(i-1)
            i += 1
        return found_BE_CRCS_index,found_LE_CRCS_index


    def __getFieldFromIndex(self, index,symbol):
        """
        This method tries to return the Field an index from a message belongs to.

        :param index: An int. The index of a value in a message belonging to a symbol
        :param symbol: The symbol we are working on
        :return: Field object, maxSize as int, field_index as int
        """
        #field_dict = dict()
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
                crcIndexInField = (8 * index) - field_index
                return field, maxSize, crcIndexInField


    def __define_field(self,val_set,field):
        """

        :param val_set: A set of values in the field
        :param field: The field containing the CRC
        :return: new_field: A new field (Alt or Raw)
        """
        if len(val_set) > 1:
            # More than one value, create Alt Fields
            domain_list = []
            for value in val_set:
                domain_list.append(Raw(value))
            new_field = Field(name=field.name, domain=Alt(domain_list))
        else:
            # Only one value, create static Fields
            new_field = Field(name=field.name, domain=Raw(val_set.pop()))
        return new_field

    def __automate_field_creation(self,results,symbol,endianness):
        """
        This method attempts to create a CRC field. It creates either a big or little
        endian CRC relation field using all the following fields to compute the CRC.

        :param results: list of CRC indexes
        :param symbol: The symbol in wich we want to define CRC fields
        :param endianness: A string stating the endianness of the CRC, should either be "big" or "little"
        """
        domain_field_list = []
        subfields = []
        for crcindex in results:
            searchedfield, field_size, field_index = self.__getFieldFromIndex(crcindex, symbol)
            # Get all the fields after the current field (to define the CRC domain Relation
            afterField = False
            for f in symbol.fields:
                if afterField:
                    domain_field_list.append(f)
                elif f.name == searchedfield.name:
                    afterField = True
            if field_size / 8 == 4:
                # Is the field just CRC or more?
                if endianness == 'little':
                    searchedfield.name = "CRC32_LE" + str(crcindex)
                else:
                    searchedfield.name = "CRC32_BE" + str(crcindex)
                searchedfield.domain = CRC32(domain_field_list, endianness=endianness)
            elif field_size > 4:
                # The Field is the CRC and something else.
                if field_index == 0:
                    # CRC at beginning of field. Create new fields after CRC
                    # Create a list of possible values
                    val_list = []
                    for val in searchedfield.getValues():
                        val_list.append(val[4:])
                        # Make a set
                    val_set = set(val_list)
                    newf = self.__define_field(val_set,searchedfield)
                    domain_field_list.insert(0, newf)
                    if endianness == 'little':
                        crc32field = Field(name="CRC32_LE" + str(crcindex), domain=CRC32(domain_field_list,endianness=endianness))
                    else:
                        crc32field = Field(name="CRC32_BE" + str(crcindex), domain=CRC32(domain_field_list,endianness=endianness))
                    subfields.append(crc32field)
                    subfields.append(newf)
                elif field_index / 8 + 4 == field_size / 8:
                    # CRC at end of field. Create new fields before CRC
                    # Create a list of possible values
                    val_list = []
                    for val in searchedfield.getValues():
                        val_list.append(val[:field_index])
                        # Make a set
                    val_set = set(val_list)
                    newf = self.__define_field(val_set,searchedfield)
                    if endianness == 'little':
                        crc32field = Field(name="CRC32_LE" + str(crcindex), domain=CRC32(domain_field_list,endianness=endianness))
                    else:
                        crc32field = Field(name="CRC32_BE" + str(crcindex), domain=CRC32(domain_field_list,endianness=endianness))
                    subfields.append(newf)
                    subfields(crc32field)
                else:
                    # CRC in the middle. Create new fields before and after CRC
                    val_list1 = []
                    val_list2 = []
                    for val in searchedfield.getValues():
                        val_list1.append(val[4:])
                        val_list2.append(val[:field_index])
                    # Make a set
                    val_set1 = set(val_list1)
                    val_set2 = set(val_list2)
                    newf1 = self.__define_field(val_set1,searchedfield)
                    newf2 = self.__define_field(val_set2,searchedfield)
                    domain_field_list.insert(0, newf2)
                    if endianness == 'little':
                        crc32field = Field(name="CRC32_LE" + str(crcindex), domain=CRC32(domain_field_list,endianness=endianness))
                    else:
                        crc32field = Field(name="CRC32_BE" + str(crcindex), domain=CRC32(domain_field_list,endianness=endianness))
                    subfields.append(newf1)
                    subfields.append(crc32field)
                    subfields.append(newf2)
                searchedfield.fields = subfields

    def __automate_mid_field_creation(self, results, symbol, endianness):
        """
                This method attempts to create a CRC field. It creates either a big or little endian CRC relation field using
                 the value b'\xca\xfe\x00\x00\x00\x00\xba\xbe' to compute the CRC
                , the b'\x00\x00\x00\x00' is then replaced by the computed CRC in the message.

                :param results: list of CRC indexes
                :param symbol: The symbol in wich we want to define CRC fields
                :param endianness: A string stating the endianness of the CRC, should either be "big" or "little"
                """
        domain_field_list = []
        subfields = []
        for crcindex in results:
            searchedfield, field_size, field_index = self.__getFieldFromIndex(crcindex, symbol)
            # Get all the fields after the current field (to define the CRC domain Relation
            afterField = False

            if field_size / 8 == 4:
                for i,f in enumerate(symbol.fields):
                    if f.name == searchedfield.name:
                        domain_field_list.append(symbol.fields[i-1])
                        domain_field_list.append(symbol.fields[i+1])
                # Is the field just CRC or more?
                if endianness == 'little':
                    searchedfield.name = "CRC32_mid_LE" + str(crcindex)
                else:
                    searchedfield.name = "CRC32_mid_BE" + str(crcindex)
                searchedfield.domain = CRC32(domain_field_list, endianness=endianness)
            elif field_size > 4:
                # The Field is the CRC and something else.
                if field_index == 0:
                    # CRC at beginning of field. Create new fields after CRC
                    # Create a list of possible values
                    val_list = []
                    for val in searchedfield.getValues():
                        val_list.append(val[4:])
                        # Make a set
                    val_set = set(val_list)
                    newf = self.__define_field(val_set,searchedfield)
                    #Compute second field (the one before the CRC
                    val_list = [] #List containing the first four bytes used to compute CRC32 (the 4 bytes prior to the CRC)
                    temp_field_list = []
                    for prevalue in symbol.getValues():
                        prevalue = prevalue[crcindex - 4:crcindex]
                        val_list.append(prevalue)
                    val_list = set(val_list)
                    for i, f in enumerate(symbol.fields):
                        if f.name == searchedfield.name:
                            prevField,minSize,maxSize = self.__getFieldFromIndex(crcindex - 1,symbol)
                            if maxSize >= 4:
                                #The four bytes are contained in only one field. We create a subfield
                                newf2 = self.__define_field(val_list, temp)
                            else:
                                #The four bytes are split into several fields. We delete all thes fields and create a new field and insert it at the index of the first of these fields in symbol.fields()
                                for j in range(1,4):
                                    try:
                                        prevField, minSize, maxSize = self.__getFieldFromIndex(crcindex - j, symbol)
                                    except:
                                        pass
                                    temp_field_list.append(prevField)
                                    temp_field_set = set(temp_field_list) #All the fields containing the four bytes
                                    for fiel in temp_field_set:
                                        miny = 99999
                                        stuffToDel = []
                                        for y,fol in enumerate(symbol.fields):
                                            if fol == fiel:
                                                if y < miny:
                                                    miny = y
                                                    stuffToDel.append(y)
                                                    temp = symbol.fields[y]
                    newf2 = self.__define_field(val_list,temp)
                    domain_field_list.append(newf2)
                    domain_field_list.append(Field(domain=Raw(b'\x00\x00\x00\x00')))
                    domain_field_list.append(newf)
                    if endianness == 'little':
                        crc32field = Field(name="CRC32_mid_LE" + str(crcindex),
                                           domain=CRC32(domain_field_list, endianness=endianness))
                    else:
                        crc32field = Field(name="CRC32_mid_BE" + str(crcindex),
                                           domain=CRC32(domain_field_list, endianness=endianness))
                    subfields.append(crc32field)
                    subfields.append(newf)
                elif field_index / 8 + 4 == field_size / 8:
                    # CRC at end of field. Create new fields before CRC
                    # Create a list of possible values
                    val_list = []
                    for val in searchedfield.getValues():
                        val_list.append(val[:field_index])
                        # Make a set
                    val_set = set(val_list)
                    newf = self.__define_field(val_set,searchedfield)
                    #Compute second field (the one after the CRC
                    val_list = [] #List containing the last four bytes used to compute CRC32 (the 4 bytes after the CRC)
                    temp_field_list = []
                    for prevalue in symbol.getValues():
                        prevalue = prevalue[crcindex:crcindex+4]
                        val_list.append(prevalue)
                    val_list = set(val_list)
                    for i, f in enumerate(symbol.fields):
                        if f.name == searchedfield.name:
                            prevField,minSize,maxSize = self.__getFieldFromIndex(crcindex + 1,symbol)
                            if maxSize >= 4:
                                #The four bytes are contained in only one field. We create a subfield
                                newf2 = self.__define_field(val_list,temp)
                            else:
                                #The four bytes are split into several fields. We delete all thes fields and create a new field and insert it at the index of the first of these fields in symbol.fields()
                                for j in range(1,4):
                                    prevField, minSize, maxSize = self.__getFieldFromIndex(crcindex + j, symbol)
                                    temp_field_list.append(prevField)
                                    temp_field_list = set(temp_field_list) #All the fields containing the four bytes
                                    for fiel in set(temp_field_list):
                                        miny = 99999
                                        for y,fol in enumerate(symbol.fields):
                                            if fol == fiel:
                                                if y < miny:
                                                    miny = y
                                                    temp = symbol.fields[y]
                                                del symbol.fields[y]
                                        symbol.fields[miny] = self.__define_field(val_list,temp)
                    newf2 = self.__define_field(val_list,temp)
                    domain_field_list.append(newf)
                    domain_field_list.append(Field(domain=Raw(b'\x00\x00\x00\x00')))
                    domain_field_list.append(newf2)
                    if endianness == 'little':
                        crc32field = Field(name="CRC32_mid_LE" + str(crcindex),
                                           domain=CRC32(domain_field_list, endianness=endianness))
                    else:
                        crc32field = Field(name="CRC32_mid_BE" + str(crcindex),
                                           domain=CRC32(domain_field_list, endianness=endianness))
                    subfields.append(newf)
                    subfields.append(crc32field)
                else:
                    # CRC in the middle. Create new fields before and after CRC
                    val_list1 = []
                    val_list2 = []
                    for val in searchedfield.getValues():
                        val_list1.append(val[4:])
                        val_list2.append(val[:field_index])
                    # Make a set
                    val_set1 = set(val_list1)
                    val_set2 = set(val_list2)
                    newf1 = self.__define_field(val_set1,searchedfield)
                    newf2 = self.__define_field(val_set2,searchedfield)
                    domain_field_list.insert(0, newf2)
                    if endianness == 'little':
                        crc32field = Field(name="CRC32_LE" + str(crcindex),
                                           domain=CRC32(domain_field_list, endianness=endianness))
                    else:
                        crc32field = Field(name="CRC32_BE" + str(crcindex),
                                           domain=CRC32(domain_field_list, endianness=endianness))
                    subfields.append(newf1)
                    subfields.append(crc32field)
                    subfields.append(newf2)
                searchedfield.fields = subfields