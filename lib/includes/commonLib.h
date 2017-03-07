// -*- coding: utf-8 -*-

//+---------------------------------------------------------------------------+
//|          01001110 01100101 01110100 01111010 01101111 01100010            |
//|                                                                           |
//|               Netzob : Inferring communication protocols                  |
//+---------------------------------------------------------------------------+
//| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
#ifndef commonLib_H
#define commonLib_H 

//+---------------------------------------------------------------------------+
//| Imports
//+---------------------------------------------------------------------------+
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

// Definition of a semantic tag
typedef struct {
  char* name;
} t_semanticTag;

// Definition of a message :
typedef struct {
  unsigned int len; // length of the message
  unsigned char *alignment; // a alignment/message
  unsigned char *mask; // its mask
  t_semanticTag **semanticTags; // an array of pointer over semantic tags. One could be attached on each half-byte of the alignment.
  char* uid;
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
static const short int MATCH = 5;
static const short int SEMANTIC_MATCH = 30;
static const short int MISMATCH = -5;

static const short int GAP = 0;
static const short int BLEN = 10;
// Consts for the definition of a mask
static const unsigned char END = 2;
static const unsigned char DIFFERENT = 1;
static const unsigned char EQUAL = 0;

#endif
