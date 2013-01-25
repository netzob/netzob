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

#ifndef scoreComputation_H
#define scoreComputation_H

//+---------------------------------------------------------------------------+
//| Imports
//+---------------------------------------------------------------------------+
//Check if have compile with -DCCALLFORDEBUG option (means we want to analyse the C program without python modules"
#ifndef CCALLFORDEBUG
#include "libInterface.h"
#else
#include "Interface.h"
#endif
#include "commonLib.h"

#include "Needleman.h"

void getHighestEquivalentGroup(t_equivalentGroup * result, Bool doInternalSlick, int nbGroups, t_groups* groups, Bool debugMode);
void getHighestEquivalentGroup2(t_equivalentGroup * result, Bool doInternalSlick, int nbMessage, t_message* messages, Bool debugMode, float** scoreMatrix);

#endif
