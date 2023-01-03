// -*- coding: utf-8 -*-

//+---------------------------------------------------------------------------+
//|          01001110 01100101 01110100 01111010 01101111 01100010            |
//|                                                                           |
//|               Netzob : Inferring communication protocols                  |
//+---------------------------------------------------------------------------+
//| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
//| This program is free software: you can redistribute it and/or modify      |
//| it under the terms of the GNU General Public License as published by      |
//| the Free Software Foundation, either version 3 of the License, or         |
//| (at your option) any later version.                                       |
//|                                                                           |
//| This program is distributed in the hope that it will be useful,           |
//| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
//| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
//| GNU General Public License for more details.                              |
//|                                                                           |
//| You should have received a copy of the GNU General Public License         |
//| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
//+---------------------------------------------------------------------------+
//| @url      : http://www.netzob.org                                         |
//| @contact  : contact@netzob.org                                            |
//| @sponsors : Amossys, http://www.amossys.fr                                |
//|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
//+---------------------------------------------------------------------------+
#ifndef Interface_H
#define Interface_H 
#include "commonLib.h"
#include "commonPythonLib.h"


/**
   serializeMessage:

   This function transform the provided t_message into a Data Transfert Object
   using PyObject.
   @param message: the message to serialize
   @return a PyObject * which represents the provided message
*/
PyObject * serializeMessage(t_message * message);

/**
   SerializeSemanticTags:

   This function transforme the provided tags into a string
   @param serializedTags: a pointer to a not yet allocated string for the result
   @param tags: the semantic tags to parse and transform
   @param nbSemanticTags: the number of semantic tags in tags
   @return unsigned int: the number of tags in the result
**/
unsigned int serializeSemanticTags(char ** serializedTags, t_semanticTag ** tags, unsigned int nbSemanticTags);

unsigned int deserializeMessages(t_group *, char *, unsigned char *, unsigned int, Bool);
unsigned int deserializeGroups(t_groups *, char *, unsigned char *, int, Bool);

//+---------------------------------------------------------------------------+
//| hexdump : for debug purposes
//+---------------------------------------------------------------------------+
void hexdump(unsigned char *bug, int dlen);

//+---------------------------------------------------------------------------+
//| dumpMessage : for debug purposes
//+---------------------------------------------------------------------------+
void dumpMessage(t_message message);

#endif
