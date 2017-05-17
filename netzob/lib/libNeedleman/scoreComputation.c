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

//Compilation Windows
//cl -Fe_libScoreComputation.pyd -Ox -Ot -openmp -LD /I"C:\Python26\include" /I"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include" libScoreComputation.c "C:\Python26\libs\python26.lib" "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\lib\vcomp.lib"

//+---------------------------------------------------------------------------+
//| Import Associated Header
//+---------------------------------------------------------------------------+
#include "scoreComputation.h"
#ifdef _WIN32
#include <stdio.h>
#include <malloc.h>
#endif

/**
   computeSimilarityMatrix:

   This functions computes a matrix which contains the similarity scores
   between the provided messages
   @param nbMessage: the number of provided messages in the param messages
   @param messages: a list containing messages to work with
   @param debug: activate or deactive debug messages
   @param scoreMatrix: a double-dimension array where the matrix score will be stored
*/
void computeSimilarityMatrix(int nbMessage, t_message* messages, Bool debugMode, float** scoreMatrix) {
  int i;
  t_message tmpResultMessage;
  t_score score;

  // local variable
  int p = 0;

  /**
     Stops the execution if user requested so
  */
  if (callbackIsFinish() == 1) {
    return;
  }

  /**
     We loop over each different couple of messages
     messages[i] and messages [p] with i < p
     (diag. superior matrix)
  */
  for (i = 0; i < nbMessage; i++) {
    /**
     Stops the execution if user requested so
    */
    if (callbackIsFinish() == 1) {
      return;
    }

    for (p = i + 1; p < nbMessage; p++) {
      /**
	 Computes the NeedlemanScore between messages i and p
	 result is stored in the matrix[i][p]
      */
      tmpResultMessage.len = 0;
      score.s1 = 0;
      score.s2 = 0;
      score.s3 = 0;
      tmpResultMessage.score = &score;

      if (debugMode) {
	printf("Align two messages (%d, %d)\n", i, p);
      }

      char * regex = alignTwoMessages(&tmpResultMessage, FALSE, &messages[i], &messages[p], debugMode);
      if (debugMode) {
	printf("Regex = %s\n", regex);
      }
      free(regex);
      scoreMatrix[i][p] = computeDistance(tmpResultMessage.score);
    }

    /**
       Update the current status
    */
    double val = (double) 100.0 * (i * nbMessage + nbMessage - 1) / ((nbMessage - 1) * (nbMessage + 1));
    if (callbackStatus(0,val,"Building Status (%.2lf %%)",(float) val) == -1) {
      printf("Error, error while executing C callback.\n");
    }
  }
}
