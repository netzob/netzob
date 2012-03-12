// -*- coding: utf-8 -*-

/*
 +---------------------------------------------------------------------------+
 |         01001110 01100101 01110100 01111010 01101111 01100010             | 
 +---------------------------------------------------------------------------+
 | NETwork protocol modeliZatiOn By reverse engineering                      |
 | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
 | @license      : GNU GPL v3                                                |
 | @copyright    : Georges Bossert and Frederic Guihery                      |
 | @url          : http://code.google.com/p/netzob/                          |
 | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
 | @author       : {gbt,fgy}@amossys.fr                                      |
 | @organization : Amossys, http://www.amossys.fr                            |
 +---------------------------------------------------------------------------+
*/

#pragma once

#include <Python.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <omp.h>

/**
 * Definitions of the different ENUM and Types
 */

typedef enum {
	FALSE, TRUE
} BOOL;

typedef struct {
	unsigned short int len; // length of the message
	unsigned char *message; // a message
	unsigned char *mask; // its mask
} t_message;

typedef struct {
	unsigned short int len; // nb of messages in the group
	t_message *messages; // a list of messages
} t_group;

typedef struct {
	unsigned short int len; // size of the regex
	unsigned char *regex; // the actual regex
	unsigned char *mask; // its mask
	float score;
} t_regex;

PyMODINIT_FUNC init_libNeedleman();

void alignTwoSequences(unsigned short int doInternalSlick, t_regex seq1, t_regex seq2, t_regex *regex);
void hexdump(unsigned char *buf, int dlen);
void dumpRegex(t_regex regex);
