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

#ifndef	Needleman_H
#define Needleman_H

//+---------------------------------------------------------------------------+
//| Imports
//+---------------------------------------------------------------------------+
//Check if have compile with -DCCALLFORDEBUG option (means we want to analyse the C program without python modules"
#ifndef CCALLFORDEBUG
#include "libInterface.h" //only needed for the callback status
#else
#include "Interface.h"
#endif
#include "commonLib.h"
#include <math.h>

//+---------------------------------------------------------------------------+
//|  alignMessages : align a group of messages and get their common regex
//+---------------------------------------------------------------------------+
void alignMessages(t_message * resMessage, Bool doInternalSlick, unsigned int nbMessages, t_message * messages, Bool debugMode);

//+---------------------------------------------------------------------------+
//| alignTwoMessages : align 2 messages and get common regex
//+---------------------------------------------------------------------------+
char* alignTwoMessages(t_message * resMessage, Bool doInternalSlick, t_message * message1, t_message * message2, Bool debugMode);

/*!
 * @function getSimilarityScore
 * @abstract Computes the similarity score of (message1[i], message2[j])
 * @discussion This function replaces the old MATCH and MISMATCH score and returns a semantic score
 */
short int getSimilarityScore(t_message * message1, t_message * message2, unsigned int i, unsigned j);

//+---------------------------------------------------------------------------+
//| Scores : functions for their computations
//+---------------------------------------------------------------------------+
float getScoreRatio(t_message *);
float getScoreDynSize(unsigned int, unsigned int);
float computeDistance(t_score *);

/*!
 * @function displayMessage
 * @abstract Display in the console the content of specified message (its data and attributes)
 * @param the message to display
 */
void displayMessage(t_message *);

#endif
