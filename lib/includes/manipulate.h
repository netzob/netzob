// -*- coding: utf-8 -*-

//+---------------------------------------------------------------------------+
//|          01001110 01100101 01110100 01111010 01101111 01100010            |
//|                                                                           |
//|               Netzob : Inferring communication protocols                  |
//+---------------------------------------------------------------------------+
//| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
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
#ifndef MANIPULATE_H
#define MANIPULATE_H
#include "struct.h"

void dealloc(void**);
int freeSubfields(Subfield *sub);
void freeFields(Fields* fields, int indFields);
void freeFieldsCompletly(Fields* fields, int indFields);
void freeTokens(char** tokenarray,int begin,int end);

int newField(Fields* field,int isStatic, char* add, char* token,int maxlimit,int groupindex);
Subfield* newSubfield( unsigned int offset, char* v,int isStatic, int* min, int* max,int maxlimit,int groupindex);
int addSubfield(Fields* field, char* token,int maxlimit,int groupindex);

void setAdd(Fields* field,char* add);
void setFieldvalue(Fields* field);
void setFieldBorder(Fields* fields,int min, int max);

int parseVariableFields(char *pAdd, int* m, int* M);
void adjustfield(Fields* field);
int isStatic(char *regex,int var);

void doerrormessage(char *errormsg,int errorcode);

#endif
