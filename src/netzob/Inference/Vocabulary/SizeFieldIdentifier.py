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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
import logging
import struct

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+----------------------------------------------
#| SizeFieldIdentifier:
#|     Search for size fields among provided symbols
#+----------------------------------------------
class SizeFieldIdentifier(object):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self):
        self.inProgress = False

    def estimateDurationOfSearch(self, symbols):
        duration = 0
        # len(symbol.getFields())

        return duration

    def updateProgressBar(self, message, increase):
        if increase:
            pass
        else:
            pass
        logging.debug("message : {0}".format(message))

    def search(self, symbols, results):
        self.results = results
        self.inProgress = True
        logging.debug("Start the identification of size fields among {0} symbols".format(str(len(symbols))))
        # Search in each symbol
        for symbol in symbols:
            self.updateProgressBar("Working on symbol {0}".format(symbol.getName()), False)
            self.searchInSymbol(symbol)
            self.updateProgressBar(None, True)

    def getPotentialSizeFields(self, symbol):
        sizeFields = []
        for field in symbol.getFields():
            if not field.isStatic(): # Means the element is static, so we assume it's not a good candidate
                sizeFields.append(field)

        # We pre-calculate the size values
        sizeCellsByField = {}
        for sizeField in sizeFields:
            sizeCellsByField[ sizeField ] = []
            cells = symbol.getCellsByField(sizeField)
            for cell in cells:
                sizeCellsByField[ sizeField ].append( self.getEncodedSizes( cell ) )
        return sizeCellsByField

    #+----------------------------------------------
    #| getEncodedSizes:
    #|   param cell
    #|   return A dict that contains tuples (little-endian, big-endian) of encoded size
    #+----------------------------------------------
    def getEncodedSizes(self, cell):
        res = {}
        # Loop over different possible encoding of size field
        for n in [4, 2, 1]:
            # Handle big and little endian for size field of 1, 2 and 4 octets length
            rawMsgSize = TypeConvertor.netzobRawToPythonRaw(cell[:n * 2])

            # We take the tiniest encoding form
            if len(rawMsgSize) == 1:
                expectedSizeType = "B"
            elif len(rawMsgSize) == 2:
                expectedSizeType = "H"
            elif len(rawMsgSize) == 4:
                expectedSizeType = "I"
            else:  # Do not consider size field with len > 4
                break

            # We want both little and big endian version of the size
            (expectedSizeLE,) = struct.unpack("<" + expectedSizeType, rawMsgSize)
            (expectedSizeBE,) = struct.unpack(">" + expectedSizeType, rawMsgSize)
            res[len(rawMsgSize)] = (expectedSizeLE, expectedSizeBE)
        return res

    def getPotentialPayloads(self, symbol, start, stop):
        # Initialize the aggregate of messages
        aggregateCellsData = []
        for l in range(len( symbol.getMessages() )):
            aggregateCellsData.append("")

        # Fill the aggregate of messages from fieldStart to fieldStop
        for iField in range(start, stop):
            # Retrieve current cells
            cells = symbol.getCellsByField( symbol.getFieldByIndex( iField ) )
            for l in range(len( cells )):
                aggregateCellsData[l] += cells[l]
        return aggregateCellsData

    """
    def getPotentialExtendedPayloads(self, symbol):
        res = []
        j = 0

        # We cover each field and aggregate them for a potential payload
        while j < len(symbol.getFields()):

            # Initialize the aggregate of messages from fieldJ to fieldK
            aggregateCellsData = []
            for l in range(len( symbol.getMessages() )):
                aggregateCellsData.append("")

            # Fill the aggregate of messages and try to compare its length with the current expected length
            k = j
            while k < len(symbol.getFields()):
                    if k != j:
                        for l in range(len(sizeCells)):
                            aggregateCellsData[l] += symbol.getCellsByField(symbol.getFieldByIndex(k))[l]

                    # We try to aggregate the successive right sub-parts of j if it's a static column
                    if symbol.getFieldByIndex(j).isStatic():
                        lenJ = len(symbol.getFieldByIndex(j).getRegex())
                        stop = 0
                    else:
                        lenJ = 2
                        stop = 0

                    for m in range(lenJ, stop, -2):

                            for nbMsg in range(len( symbol.getMessages() )):
                                if symbol.getFieldByIndex(j).isStatic():
                                    targetData = symbol.getFieldByIndex(j).getRegex()[lenJ - m:] + aggregateCellsData[nbMsg]
                                else:
                                    targetData = symbol.getCellsByField(symbol.getFieldByIndex(j))[nbMsg] + aggregateCellsData[nbMsg]

                                    for (encodedSizeLE, encodedSizeBE) in dictEncodedSizes:
                                        if (expectedSizeLE != len(targetData) / 2) and (expectedSizeBE != len(targetData) / 2):
                                            res = False
                                            break
                k += 1
            j += 1

        return res
    """

    def searchInSymbol(self, symbol):
        # First we verify there are at least 2 fields :)
        if len(symbol.getFields()) <= 1:
            return

        # We retrieve the potential size fields
        sizeCellsByField = self.getPotentialSizeFields(symbol)

        # We loop over each aggregate of fieldStart to fieldEnd to search for associated size
        start = 0
        while start < len(symbol.getFields()) - 1:

            for end in range(start + 1, len(symbol.getFields()) + 1):
                # We retrieve the potential payloads
                payloads = self.getPotentialPayloads(symbol, start, end)

                # We retrieve the values of the potential size fields
                for (aField, sizeCells) in sizeCellsByField.items():
                    # And search for associated payload
                    res = True
                    resCnt = 0
                    for l in range(len(payloads)):
                        payloadLen = len( payloads[l] )
                        encodedSizes = sizeCells[l]
                        for (key, value) in encodedSizes.items():
                            (le, be) = value
                            if le == 0:
                                continue

                            payloadLen = payloadLen / 2

                            if (payloadLen) == le:
                                resCnt += 1
                            elif (payloadLen) == be:
                                resCnt += 1
                        if resCnt != len(payloads[:l + 1]):
                            res = False
                            break
                    if res == True:
                        self.results.append([aField.getIndex(), key * 2, start, -1, end - 1, -1, "Found potential size field (col " + str(aField.getIndex()) + "[:" + str(key * 2) + "]) for an aggregation of data field (col " + str(start) + " to col " + str(end - 1) + ")"])
            start += 1

    def getResults(self):
        return self.results

    def cancel(self):
        self.inProgress = True
