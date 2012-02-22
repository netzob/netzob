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

#ifndef __libNeedleman_header
#define __libNeedleman_header

//+---------------------------------------------------------------------------+
//| Imports
//+---------------------------------------------------------------------------+
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>


//+---------------------------------------------------------------------------+
//| Enumerations and complex types
//+---------------------------------------------------------------------------+
typedef enum { FALSE, TRUE } Bool;

// Definition of a message :
typedef struct {
  unsigned short int len; // length of the message
  unsigned char *message; // a message
  unsigned char *mask; // its mask
} t_message;

//Definition of a group of messages
typedef struct {
  unsigned short int len; // nb of messages in the group
  t_message *messages; // a list of messages
} t_group;

//Definition of a aligned set of messages
typedef struct {
  unsigned short int len; // size of the regex
  unsigned char *regex; // the actual regex
  unsigned char *mask; // its mask
  float score;
} t_regex;

// Cost definitions for the alignment
const short int MATCH = 10;
const short int MISMATCH = -10;
const short int GAP = 0;

// Consts for the definition of a mask
const unsigned char END = 2;
const unsigned char DIFFERENT = 1;
const unsigned char EQUAL = 0;


//+---------------------------------------------------------------------------+
//| python_callback : The ref to the python callback function
//+---------------------------------------------------------------------------+
static PyObject *python_callback = NULL;
int callbackStatus(double percent, char* message, ...);

//+---------------------------------------------------------------------------+
//| py_alignMessages : Python wrapper for alignMessages
//+---------------------------------------------------------------------------+
static PyObject* py_alignMessages(PyObject* self, PyObject* args);
void alignMessages(t_regex * regex, Bool doInternalSlick, unsigned short int nbMessages, t_group* messages, Bool debugMode);

//+---------------------------------------------------------------------------+
//| py_alignTwoMessages : Python wrapper for alignTwoMessages
//+---------------------------------------------------------------------------+
static PyObject* py_alignTwoMessages(PyObject* self, PyObject* args);
int alignTwoMessages(t_regex * regex, Bool doInternalSlick, t_regex * regex1, t_regex * regex2, Bool debugMode);

//+---------------------------------------------------------------------------+
//| py_deserializeMessages : Python wrapper for deserializeMessages
//+---------------------------------------------------------------------------+
static PyObject* py_deserializeMessages(PyObject* self, PyObject* args);
unsigned short int deserializeMessages(t_group *, unsigned char *, int, unsigned char *, int, int, Bool);

//+---------------------------------------------------------------------------+
//| initLibNeedleman : Python will use this function to init the module
//+---------------------------------------------------------------------------+
void initlibNeedleman(void);

//+---------------------------------------------------------------------------+
//| hexdump : for debug purposes
//+---------------------------------------------------------------------------+
int hexdump(unsigned char *bug, int dlen);

//+---------------------------------------------------------------------------+
//| dumpRegex : for debug purposes
//+---------------------------------------------------------------------------+
void dumpRegex(t_regex regex);


static PyMethodDef libNeedleman_methods[] = {
  {"alignMessages", py_alignMessages, METH_VARARGS},
  {"alignTwoMessages", py_alignTwoMessages, METH_VARARGS},
  {"deserializeMessages", py_deserializeMessages, METH_VARARGS},
  {NULL, NULL}
};

#endif
