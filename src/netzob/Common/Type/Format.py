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

import logging


#+----------------------------------------------
#| Format representation of data
#+----------------------------------------------
class Format():
    # Primary formats
    BINARY = "binary"
    OCTAL = "octal"
    DECIMAL = "decimal"
    HEX = "hex"
    STRING = "string"
    FLOAT = "float"
    NUM = "num"
    ALPHA = "alpha"
    ALPHA_NUM = "alphanum"
    ASCII = "ascii"
    BASE64_ENC = "base64enc"
    BASE64_DEC = "base64dec"

    formatVisualizationUnitSizes = {BINARY: 1, HEX: 4, STRING: 8}

    # Complex formats
    IP = "ip"

    @staticmethod
    #+---------------------------------------------------------------------------+
    #| getSupportedFormats:
    #|     Returns an array composed of the names of primary supported formats
    #|     for the visualization of messages
    #+---------------------------------------------------------------------------+
    def getSupportedFormats():
        return [Format.BINARY, Format.OCTAL, Format.DECIMAL, Format.HEX, Format.STRING]

    @staticmethod
    #+---------------------------------------------------------------------------+
    #| getExtendedSupportedFormats:
    #|     Returns an array composed of the names of all supported formats
    #|     for the visualization of messages
    #+---------------------------------------------------------------------------+
    def getExtendedSupportedFormats():
        return [Format.BINARY, Format.OCTAL, Format.DECIMAL, Format.HEX, Format.STRING, Format.IP]

    @staticmethod
    def getUnitSize(format):
        if format in Format.formatVisualizationUnitSizes:
            return Format.formatVisualizationUnitSizes[format]
        else:
            return None
