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

#pragma once

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

// Definition of a score vector
typedef struct {
  float s1;
  float s2;
  float s3;
  float value;
} t_score;

// Definition of a message :
typedef struct {
  unsigned int len; // length of the message
  unsigned char *alignment; // a alignment/message
  unsigned char *mask; // its mask
  t_score *score;
} t_message;

//Definition of a group of messages
typedef struct {
  unsigned int len; // nb of messages in the group
  t_message *messages; // a list of messages
  float * scores; //list of score allready computed.
} t_group;

// Definition of a group of group (a group of symbol)
typedef struct {
  unsigned int len; // nb of group
  t_group *groups; // a list of group
} t_groups;

typedef struct {
  int i;  // group1 number
  int j;  // group2 number
  float score; // score of equivalence between group1 and group2
} t_equivalentGroup;

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
//| py_getHighestEquivalentGroup : Python wrapper for getHighestEquivalentGroup
//+---------------------------------------------------------------------------+
static PyObject* py_getHighestEquivalentGroup(PyObject* self, PyObject* args);
void getHighestEquivalentGroup(t_equivalentGroup * result, Bool doInternalSlick, int nbGroup, t_groups* groups, Bool debugMode);

//+---------------------------------------------------------------------------+
//| py_alignMessages : Python wrapper for alignMessages
//+---------------------------------------------------------------------------+
static PyObject* py_alignMessages(PyObject* self, PyObject* args);
void alignMessages(t_message * resMessage, Bool doInternalSlick, unsigned int nbMessages, t_group* messages, Bool debugMode);

//+---------------------------------------------------------------------------+
//| py_alignTwoMessages : Python wrapper for alignTwoMessages
//+---------------------------------------------------------------------------+
static PyObject* py_alignTwoMessages(PyObject* self, PyObject* args);
int alignTwoMessages(t_message * resMessage, Bool doInternalSlick, t_message * message1, t_message * message2, Bool debugMode);

//+---------------------------------------------------------------------------+
//| py_deserializeMessages : Python wrapper for deserializeMessages
//+---------------------------------------------------------------------------+
static PyObject* py_deserializeMessages(PyObject* self, PyObject* args);
unsigned int deserializeMessages(t_group *, unsigned char *, int, unsigned char *, int, int, Bool);

//+---------------------------------------------------------------------------+
//| py_deserializeMGroups : Python wrapper for deserializeGroups
//+---------------------------------------------------------------------------+
static PyObject* py_deserializeGroups(PyObject* self, PyObject* args);
unsigned int deserializeGroups(t_groups *, unsigned char *, int, unsigned char *, int, int, Bool);

//+---------------------------------------------------------------------------+
//| initLibNeedleman : Python will use this function to init the module
//+---------------------------------------------------------------------------+
PyMODINIT_FUNC init_libNeedleman(void);

//+---------------------------------------------------------------------------+
//| Scores : functions for their computations
//+---------------------------------------------------------------------------+
float getScoreRatio(t_message *);
float getScoreDynSize(unsigned int, unsigned int);
float getScoreRang(t_message *);
float computeDistance(t_score *);

//+---------------------------------------------------------------------------+
//| hexdump : for debug purposes
//+---------------------------------------------------------------------------+
void hexdump(unsigned char *bug, int dlen);

//+---------------------------------------------------------------------------+
//| dumpMessage : for debug purposes
//+---------------------------------------------------------------------------+
void dumpMessage(t_message message);

