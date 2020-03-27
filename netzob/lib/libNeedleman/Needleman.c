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
//cl -Fe_libNeedleman.pyd -Ox -Ot -openmp -LD /I"C:\Python26\include" /I"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include" libNeedleman.c "C:\Python26\libs\python26.lib" "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\lib\vcomp.lib"

//+---------------------------------------------------------------------------+
//| Import Associated Header
//+---------------------------------------------------------------------------+
#include "Needleman.h"

#ifdef _WIN32
#include <stdio.h>
#include <malloc.h>
#endif

void alignMessages(t_message *resMessage, Bool doInternalSlick, unsigned int nbMessages, t_message * messages, Bool debugMode) {
  // local variable
  unsigned int numberOfOperations = 0;
  double costOfOperation;
  double status = 0.0;

  // Local variables
  t_message current_message;
  t_message new_message;
  t_score score;
  unsigned int i_message = 0;

  // Regex returned by the function alignTwoMessages()
  char * regex = NULL;

  score.s1 = 0;
  score.s2 = 0;
  score.s3 = 0;
  score.value = 0;

  //+------------------------------------------------------------------------+
  // Estimate the number of operation
  //+------------------------------------------------------------------------+
  numberOfOperations = nbMessages - 1;
  costOfOperation = 100.0 / numberOfOperations;

  // Create a current message (using first message)
  // current message = Align N+1 message with current message
  current_message.len = messages[0].len;
  current_message.alignment = messages[0].alignment;
  current_message.mask = malloc(messages[0].len * sizeof(unsigned char));
  current_message.semanticTags = malloc(messages[0].len * sizeof(t_semanticTag*));
  for (unsigned int j=0; j<messages[0].len; j++) {
    current_message.semanticTags[j] = malloc(sizeof(t_semanticTag));
    current_message.semanticTags[j]->name = malloc((strlen(messages[0].semanticTags[j]->name)+1) * sizeof(char));
    strcpy(current_message.semanticTags[j]->name, messages[0].semanticTags[j]->name);
  }
  memset(current_message.mask, 0, messages[0].len);
  current_message.score = &score;

  // Prepare for the resMessage
  if (nbMessages == 1) {
    resMessage->len = current_message.len;
    resMessage->mask = current_message.mask;
    resMessage->alignment = current_message.alignment;
    resMessage->score = current_message.score;
    resMessage->semanticTags = current_message.semanticTags;
  }
  for (i_message=1; i_message < nbMessages; i_message++) {
    // Update the execution status
    if (callbackStatus(0, status, "Consider message %d in the alignment process", i_message) == -1) {
      printf("Error, error while executing C callback.\n");
    }
    if (callbackIsFinish() == 1) {
    	return;
    }

    new_message.len = messages[i_message].len;
    new_message.alignment = messages[i_message].alignment;
    new_message.mask = malloc(messages[i_message].len * sizeof(unsigned char));
    new_message.semanticTags = malloc(messages[i_message].len * sizeof(t_semanticTag*));
    for (unsigned int j=0; j<messages[i_message].len; j++) {
      new_message.semanticTags[j] = malloc(sizeof(t_semanticTag));
      new_message.semanticTags[j]->name = malloc((strlen(messages[i_message].semanticTags[j]->name)+1) * sizeof(char));
      strcpy(new_message.semanticTags[j]->name, messages[i_message].semanticTags[j]->name);

    }

    memset(new_message.mask, 0, messages[i_message].len);

    // Align current_message with new_message
    regex = alignTwoMessages(resMessage, doInternalSlick, &current_message, &new_message, debugMode);
    // regex is malloced by the function alignTwoMessages() and we don't need it here
    if(regex)
      free(regex);

    free(current_message.mask);
    free(new_message.mask);
    // Copy result in the current message
    current_message.len = resMessage->len;
    current_message.alignment = resMessage->alignment;
    current_message.mask = resMessage->mask;
    current_message.semanticTags = resMessage->semanticTags;
    //udpate status
    status += costOfOperation;
  }

  // Update the execution status
  if (callbackStatus(0, status, "The %d messages have sucessfully been aligned.", nbMessages) == -1) {
    printf("Error, error while executing C callback.\n");
  }


  free(messages);
}


char* alignTwoMessages(t_message * resMessage, Bool doInternalSlick, t_message * message1, t_message * message2, Bool debugMode){
  // local variables
  short int ** matrix = NULL;
  unsigned int i = 0;
  unsigned int j = 0;

  // Construction of the matrix
  short int elt1, elt2, elt3, max, eltL, eltD, eltT;
  // Levenshtein distance
  //  float levenshtein = 0.0;
  float scoreAlignment = 0;

  unsigned int maxLen = 0;
  // Traceback
  unsigned char * contentMessage1 = NULL;
  unsigned int * mapMessage1 = NULL;
  unsigned char * maskMessage1 = NULL;

  unsigned char * contentMessage2 = NULL;
  unsigned char * maskMessage2 = NULL;
  unsigned int * mapMessage2 = NULL;
  unsigned int iReg1 = 0;
  unsigned int iReg2 = 0;

  // Computing resMessage
  unsigned char *tmpMessage  = NULL;
  unsigned char *tmpMessageMask = NULL;
  t_semanticTag **tmpMessageTags = NULL;

  // Score computation
  unsigned int nbDynTotal = 0;
  unsigned int nbDynCommon = 0;

  // Regex returned by the function
  char * regex = NULL;

  // DEBUG DISPLAY OF MESSAGES
  if (debugMode == TRUE) {
    displayMessage(message1);
    displayMessage(message2);
  }

  //+------------------------------------------------------------------------+
  // Create and initialize the matrix
  //+------------------------------------------------------------------------+
  matrix = (short int**) malloc( sizeof(short int*) * (message1->len + 1) );
  for (i = 0; i < (message1->len + 1); i++) {
    matrix[i] = (short int*) calloc( (message2->len + 1), sizeof(short int) );
  }

  //+------------------------------------------------------------------------+
  // Fullfill the matrix given the two messages
  //+------------------------------------------------------------------------+
  // Parralelization:
  unsigned int nbDiag = 0;
  unsigned int nbBlock = 0; // Depends on which diagonal we are on
  unsigned int minLen = 0;
  unsigned int firsti = 0;
  unsigned int firstj = 0;
  unsigned int diagloop = 0;
  unsigned int blockLoop = 0;
  unsigned int iblock = 0;
  unsigned int jblock = 0;
  unsigned int maxLoopi = 0;
  unsigned int maxLoopj = 0;
  unsigned int lastRow = 0;
  unsigned int lastColumn = 0;
  int maxScoreMatrix = 0;

  lastRow = ((message1->len+1)/BLEN) * BLEN;
  lastColumn = ((message2->len+1)/BLEN) * BLEN;

  nbDiag  = (message1->len+1)/BLEN + (message2->len+1)/BLEN + ((message1->len+1)%BLEN!=0); // reminder: BLEN = blocklength

  minLen = message1->len+1 <= message2->len+1 ? message1->len+1 : message2->len+1;
  maxLen = message1->len+1 > message2->len+1 ? message1->len+1 : message2->len+1;

  // Begin loop over diagonals
  for (diagloop = 0; diagloop < nbDiag; diagloop++){
  	//printf("Diag n %d\n",diagloop);
    for (blockLoop = 0;blockLoop <= nbBlock; blockLoop++){
	  //printf("Block n %d\n",blockLoop);
	  //(iblock,jblock are moving from the bottom left of the current diagonal to the top right)
      iblock = firsti - blockLoop * BLEN;
      jblock = firstj + blockLoop * BLEN;
      maxLoopi = iblock + BLEN <= message1->len + 1? iblock + BLEN:message1->len + 1;
      maxLoopj = jblock + BLEN <= message2->len + 1? jblock + BLEN:message2->len + 1;

      for(i = iblock;i < maxLoopi; i++){

        for(j = jblock; j < maxLoopj; j++){
          if (i > 0 && j > 0){
            elt1 = matrix[i - 1][j - 1];

	    elt1 += getSimilarityScore(message1, message2, i, j);
            elt2 = matrix[i][j - 1] + GAP;
            elt3 = matrix[i - 1][j] + GAP;
            max = elt1 > elt2 ? elt1 : elt2;
            max = max > elt3 ? max : elt3;
	    matrix[i][j] = max;
	    if (max > maxScoreMatrix) {
	      maxScoreMatrix = max;
	    }

	  }//printf("%d,\t",matrix[i][j]);
       }
       //printf("\n");
     }//End for iblock
    }//End for blockLoop

   //Actualize the number of block for the next time
   if (diagloop < minLen/BLEN){
      nbBlock++;
   }
   else if (diagloop > maxLen/BLEN){
      nbBlock--;
   }

   //Actualise the first position of the cursor (bottom left of the next diagonal)
   if (firsti != lastRow) // If we are not at the last row
        firsti = firsti + BLEN ;

   else if (firstj != lastColumn) // Else If we are not at the last column
        firstj += BLEN;


  }//End for diagloop

  // Compute score of the alignment (ratio regarding the max score these two payloads could have get if they were equals)
  unsigned int lenSmallestPayload = message2->len > message1->len ? message1->len : message2->len;
  float maxScore = lenSmallestPayload * MATCH;
  scoreAlignment = (100.0f / maxScore) * (float) maxScoreMatrix;
  if (scoreAlignment > 100.0f) {
    scoreAlignment = 100.0f;
  } else if (scoreAlignment < 0.0f) {
    scoreAlignment = 0.0f;
  }
  //levenshtein = MATCH*(float)matrix[message1->len][message2->len] / maxLen;
  //float levcop = matrix[message1->len][message2->len];
  //levenshtein = levenshtein * 10 / maxLen;

  //+------------------------------------------------------------------------+
  // Traceback into the matrix
  //+------------------------------------------------------------------------+
  //finish = FALSE;
  contentMessage1 = calloc( message1->len + message2->len, sizeof(unsigned char));
  mapMessage1 = calloc( message1->len + message2->len, sizeof(unsigned int));
  maskMessage1 = calloc( message1->len + message2->len, sizeof(unsigned char));

  contentMessage2 = calloc( message1->len + message2->len, sizeof(unsigned char));
  mapMessage2 = calloc( message1->len + message2->len, sizeof(unsigned int));
  maskMessage2 = calloc( message1->len + message2->len, sizeof(unsigned char));

  if (contentMessage1 == NULL) {
    printf("Error while trying to allocate memory for variable : contentMessage1.\n");
    goto end;
  }
  if (contentMessage2 == NULL) {
    printf("Error while trying to allocate memory for variable : contentMessage2.\n");
    goto end;
  }
  if (maskMessage1 == NULL) {
    printf("Error while trying to allocate memory for variable : maskMessage1.\n");
    goto end;
  }
  if (maskMessage2 == NULL) {
    printf("Error while trying to allocate memory for variable : maskMessage2.\n");
    goto end;
  }
  // Fullfill the mask with END like filling it with a '\0'
  memset(maskMessage1, END, (message1->len + message2->len) * sizeof(unsigned char));
  memset(maskMessage2, END, (message1->len + message2->len) * sizeof(unsigned char));

  // Prepare variables for the traceback
  iReg1 = message1->len + message2->len - 1;
  iReg2 = iReg1;
  i = message1->len;
  j = message2->len;

  // DIAGONAL (almost) TRACEBACK
  while ((i > 0) && (j > 0)) {
    eltL = matrix[i][j - 1];
    eltD = matrix[i - 1][j - 1];
    eltT = matrix[i - 1][j];

    if ((eltL > eltD) && (eltL > eltT)) {
      --j;

      contentMessage1[iReg1] = 0xf1;
      maskMessage1[iReg1] = DIFFERENT;

      if( message2->mask[j] == EQUAL) {
        contentMessage2[iReg2] = message2->alignment[j];
        maskMessage2[iReg2] = EQUAL;
      }
      else {
        contentMessage2[iReg2] = 0xf1;
        maskMessage2[iReg2] = DIFFERENT;
      }
    } else if ((eltT >= eltL) && (eltT > eltD)) {
      --i;

      contentMessage2[iReg2] = 0xf2;
      maskMessage2[iReg2] = DIFFERENT;

      if( message1->mask[i] == EQUAL) {
        contentMessage1[iReg1] = message1->alignment[i];
        maskMessage1[iReg1] = EQUAL;
      }
      else {
        contentMessage1[iReg1] = 0xf2;
        maskMessage1[iReg1] = DIFFERENT;
      }
    } else {
      --i;
      --j;

      if(message1->mask[i] == EQUAL) {
        contentMessage1[iReg1] = message1->alignment[i];
        maskMessage1[iReg1] = EQUAL;
      }
      else {
        contentMessage1[iReg1] = 0xf2;
        maskMessage1[iReg1] = DIFFERENT;
      }

      if(message2->mask[j] == EQUAL) {
        contentMessage2[iReg2] = message2->alignment[j];
        maskMessage2[iReg2] = EQUAL;
      }
      else {
        contentMessage2[iReg2] = 0xf2;
        maskMessage2[iReg2] = DIFFERENT;
      }
    }
    mapMessage1[iReg1]=i;
    mapMessage2[iReg2]=j;
    --iReg1;
    --iReg2;
  }



  // THE DIAGONAL IS FINISH WE CLOSE THE
  // TRACEBACK BY GOING TO THE EXTREME TOP
  while (i > 0) {
    --i;
    contentMessage2[iReg2] = 0xf3;
    maskMessage2[iReg2] = DIFFERENT;

    if(message1->mask[i] == EQUAL) {
      contentMessage1[iReg1] = message1->alignment[i];
      maskMessage1[iReg1] = EQUAL;
    }
    else {
      contentMessage1[iReg1] = 0xf3;
      maskMessage1[iReg1] = DIFFERENT;
    }
    mapMessage1[iReg1]=i;
    mapMessage2[iReg2]=j;
    --iReg1;
    --iReg2;

  }

  // THE DIAGONAL IS FINISH WE CLOSE THE
  // TRACEBACK BY GOING TO THE EXTREME LEFT
  while (j > 0) {
    --j;
    contentMessage1[iReg1] = 0xf4;
    maskMessage1[iReg1] = DIFFERENT;

    if(message2->mask[j] == EQUAL) {
      contentMessage2[iReg2] = message2->alignment[j];
      maskMessage2[iReg2] = EQUAL;
    }
    else {
      contentMessage2[iReg2] = 0xf4;
      maskMessage2[iReg2] = DIFFERENT;
    }

    mapMessage1[iReg1]=i;
    mapMessage2[iReg2]=j;

    --iReg1;
    --iReg2;
  }

  if (debugMode == TRUE) {
    // Display the mapping between alignement and message half-bytes
    printf("Mapping : ");
    for( i = 0; i < message1->len + message2->len; i++) {
      unsigned int iTag = mapMessage1[i];
      unsigned int jTag = mapMessage2[i];

      char * tagNameMessage1 = NULL;
      char * tagNameMessage2 = NULL;
      if (iTag >= message1->len || message1->semanticTags[iTag] == NULL
	  ||  message1->semanticTags[iTag]->name == NULL) {
	tagNameMessage1 = "None";
      } else {
	tagNameMessage1 = message1->semanticTags[iTag]->name;
      }

      if (jTag >= message2->len || message2->semanticTags[jTag] == NULL
	  || message2->semanticTags[jTag]->name == NULL) {
	tagNameMessage2 = "None";
      } else {
	tagNameMessage2 = message2->semanticTags[jTag]->name;
      }
      if (strcmp(tagNameMessage1, "None") != 0 || strcmp(tagNameMessage2, "None") != 0) {
	printf("%d) 1=%d [%s], 2=%d [%s], \n", i, iTag, tagNameMessage1, jTag, tagNameMessage2);
      }
    }
  }


  // For debug only
  if (debugMode == TRUE) {
    printf("(1)Alig : ");
    for( i = 0; i < message1->len + message2->len; i++) {
      if(maskMessage1[i] == EQUAL ) {
        printf("%02x", (unsigned char) contentMessage1[i]);
      } else if ( maskMessage2[i] == END ) {
        //printf("##");
      } else {
        printf("--");
      }
    }
    printf("\n");
    printf("(2)Alig : ");
    for( i = 0; i < message1->len + message2->len; i++) {
      if( maskMessage2[i] == EQUAL ) {
        printf("%02x", (unsigned char) contentMessage2[i]);
      } else if ( maskMessage2[i] == END ) {
        //printf("##");
      } else {
        printf("--");
      }
    }
    printf("\n");
  }

  // Compute the common alignment
  char hexrepr[3];
  int sizereg = 100000;//(int)(levcop/10)*2+(int)(levcop/10)+2;
  int regind = 0;
  tmpMessage = calloc(message1->len + message2->len, sizeof(unsigned char));
  tmpMessageMask = malloc((message1->len + message2->len) * sizeof(unsigned char));
  memset(tmpMessageMask, END, (message1->len + message2->len) * sizeof(unsigned char));
  tmpMessageTags = malloc((message1->len + message2->len) * sizeof(t_semanticTag*));
  for (i=0; i<message1->len + message2->len; i++){
    tmpMessageTags[i] = malloc(sizeof(t_semanticTag));
    tmpMessageTags[i]->name = NULL;
  }

  regex= malloc( sizereg* sizeof(char));
  memset(regex, 0, sizereg);

  if (debugMode == TRUE) {
    printf("Compute the common alignment:\n");
  }

  i = 0;
  while (i < message1->len + message2->len) {

    // Fetch the semantic tag of the two messages
    unsigned int iTag = mapMessage1[i];
    unsigned int jTag = mapMessage2[i];
    char * tagNameMessage1 = NULL;
    char * tagNameMessage2 = NULL;
    char * tagNewMessage = NULL;

    if (iTag >= message1->len || message1->semanticTags[iTag] == NULL
	||  message1->semanticTags[iTag]->name == NULL) {
      tagNameMessage1 = "None";
    } else {
      tagNameMessage1 = message1->semanticTags[iTag]->name;
    }
    if (jTag >= message2->len || message2->semanticTags[jTag] == NULL || message2->semanticTags[jTag]->name == NULL) {
      tagNameMessage2 = "None";
    } else {
      tagNameMessage2 = message2->semanticTags[jTag]->name;
    }

    if (strcmp(tagNameMessage1, tagNameMessage2) == 0) {
      tagNewMessage = tagNameMessage1;
    } else {
      tagNewMessage = "None";
    }
    tmpMessageTags[i]->name = tagNewMessage;


    if ((maskMessage1[i] == END) || (maskMessage2[i] == END)) {
      if(regind==0){
	regex[0] ='.';
	regind++;
      }
      else if(regex[regind-1] !='.'){
	regex[regind] ='.';
	regind++;
      }
      tmpMessage[i] = 0xf9;
      tmpMessageMask[i] = END;
    }
    else if ((maskMessage1[i] == EQUAL) && (maskMessage2[i] == EQUAL) && (contentMessage1[i] == contentMessage2[i])) {
      tmpMessage[i] = contentMessage1[i];
      sprintf(hexrepr,"%02x",contentMessage1[i]);
      sprintf(regex+regind,"%02x",contentMessage1[i]);
      //regex[regind] = hexrepr[1];
      //regex[regind+1] = hexrepr[0];
      regind+=2;
      tmpMessageMask[i] = EQUAL;
    }
    else {
      if(regind==0){
	regex[0] ='.';
	regind++;
      }
      else if(regex[regind-1] !='.'){
	regex[regind] ='.';
	regind++;
      }
      tmpMessage[i] = 0xf5;
      tmpMessageMask[i] = DIFFERENT;

      nbDynTotal += 1;
      if ((maskMessage1[i] == EQUAL) && (maskMessage2[i] == EQUAL)) {
	nbDynCommon += 1;
      }
    }
    i++;
  }
  //printf("%f\n",levcop);

  /*if(regex!=NULL){
  	  printf("REGEX %s\n",regex);
	  //free(regex);
	  //printf("FREE \n");
	  }*/
  // Try to (optionally) slick the alignment
  if(doInternalSlick == TRUE) {
    if(message1->len + message2->len > 0) {
      for(i = 1; i < message1->len + message2->len - 1; i++) {
	if( tmpMessageMask[i] == EQUAL ) {
	  if( tmpMessageMask[i - 1] == DIFFERENT ) {
	    if( tmpMessageMask[i + 1] == DIFFERENT ) {
	      tmpMessage[i] = 0xf6;
	      tmpMessageMask[i] = DIFFERENT;
	    }
	  }
        }
      }
    }
  }

  // Create the alignment based on obtained data
  // Remove the first # of the alignment (where mask = END)
  // Retrieve the shortest possible alignment
  i = 0;
  while( tmpMessageMask[i] == END )
    i++;

  // Store the results
  resMessage->len = message1->len + message2->len - i;
  resMessage->alignment = malloc(resMessage->len * sizeof(unsigned char));
  resMessage->mask = malloc(resMessage->len * sizeof(unsigned char));
  resMessage->semanticTags = malloc(resMessage->len * sizeof(t_semanticTag *));
  // default semantic tag is "None"
  for (j=0; j<resMessage->len; j++) {
    resMessage->semanticTags[j] = malloc(sizeof(t_semanticTag));
    if (tmpMessageTags[i+j] == NULL || strcmp(tmpMessageTags[i+j]->name, "None") == 0) {
      resMessage->semanticTags[j]->name = "None";
    } else {
      resMessage->semanticTags[j]->name = tmpMessageTags[i+j]->name;
    }

    //strcpy(resMessage->semanticTags[j]->name, tmpMessageTags[i+j]->name);
  }
  // TODO: (fgy) free resMessage.mask and resMessage.alignment
  memcpy(resMessage->alignment, tmpMessage + i, resMessage->len);
  memcpy(resMessage->mask, tmpMessageMask + i, resMessage->len);



  // Compute the scores of similarity, using the resMessage
  if (debugMode == TRUE) {
    displayMessage(resMessage);
    printf("Result  : ");
    for( i = 0; i < resMessage->len; i++) {
      if(resMessage->mask[i] == EQUAL ) {
        printf("%02x", (unsigned char) resMessage->alignment[i]);
      } else if ( resMessage->mask[i] == END ) {
        //printf("##");
      } else {
        printf("--");
      }
    }
    printf("\n");
  }


  // COMPUTE THE SCORES
  resMessage->score->s1 = getScoreRatio(resMessage);
  resMessage->score->s2 = getScoreDynSize(nbDynTotal, nbDynCommon);
  resMessage->score->s3 = scoreAlignment;

  if (debugMode == TRUE) {
    printf("Score ratio : %0.2f.\n", resMessage->score->s1);
    printf("Score DynSize : %0.2f.\n", resMessage->score->s2);
    printf("Score Rang : %0.2f.\n", resMessage->score->s3);
  }

end:
  // Room service
  if(matrix) {
    for (i = 0; i < (message1->len + 1); i++) {
      if(matrix[i]) {
	free(matrix[i]);
      }
    }
    free(matrix);
  }
  if(contentMessage1) {
    free(contentMessage1);
  }
  if(contentMessage2) {
    free(contentMessage2);
  }
  if(maskMessage1) {
    free(maskMessage1);
  }
  if(maskMessage2) {
    free(maskMessage2);
  }
  if(mapMessage1) {
    free(mapMessage1);
  }
  if(mapMessage2) {
    free(mapMessage2);
  }
  if(tmpMessage) {
    free(tmpMessage);
  }
  if(tmpMessageMask) {
    free(tmpMessageMask);
  }
  if(tmpMessageTags) {
    for (i = 0; i < message1->len + message2->len; i++) {
      if(tmpMessageTags[i]) {
	free(tmpMessageTags[i]);
      }
    }
    free(tmpMessageTags);
  }

  return regex;
}


float getScoreRatio(t_message * message) {
  // Computing score of the alignment
  float nbDynamic = 0.0f;
  float nbStatic = 0.0f;
  Bool inDyn = FALSE;
  int i=0;
  float result = 0;

  for (i = (message->len - 1); i >= 1; --i) {
    if (message->mask[i] == END) {
      break;
    }
    if (message->mask[i] == EQUAL) {
      if (inDyn == TRUE) {
        nbDynamic = nbDynamic + 1.0f;
        inDyn = FALSE;
      }
      nbStatic = nbStatic + 1.0f;
    } else if (message->mask[i] == DIFFERENT) {
      inDyn = TRUE;
    }
  }
  if (inDyn == TRUE)
    nbDynamic = nbDynamic + 1.0f;
  if(nbStatic == 0){
    result = 0;
  }
  else {
  result = 100.0 / (nbStatic + nbDynamic) * nbStatic;
  }
  return result;
}
float getScoreDynSize(unsigned int nbDynTotal, unsigned int nbDynCommon) {
  // Compute score of common dynamic elements
  float result = 0;
  if(nbDynTotal == 0) {
    result = 100;
  }
  else {
    result = (100.0 - 1) / nbDynTotal * nbDynCommon;
  }
  return result;
}

/**
   computeDistance:
   This function computes a distance given a set of scores

   @param score : the scores to merge
  @return the distance
*/
float computeDistance(t_score * score) {
  float result = 0;
  result = sqrt((1.0 * pow(score->s1,2) + 1.0 * pow(score->s2,2) + 1.0 * pow(score->s3,2))/3.0);
  return result;
}


short int getSimilarityScore(t_message * message1, t_message * message2, unsigned int i, unsigned j) {
  short int result = 0;
  char * msg1SemanticTag = "None";
  char * msg2SemanticTag = "None";

  //retrieve semantic token of messages
  if (message1->semanticTags != NULL && i < message1->len && message1->semanticTags[i] != NULL && message1->semanticTags[i]->name != NULL) {
      msg1SemanticTag = message1->semanticTags[i]->name;
  }
  if (message2->semanticTags != NULL && j < message2->len && message2->semanticTags[j] != NULL && message2->semanticTags[j]->name != NULL) {
      msg2SemanticTag = message2->semanticTags[j]->name;
  }
  // Computes if its semanticaly close
  if (strcmp(msg1SemanticTag, "None") != 0 && strcmp(msg1SemanticTag, msg2SemanticTag) == 0) {
    result = SEMANTIC_MATCH;
  }
  if ( (message1->mask[i - 1] == 0) && (message2->mask[j - 1] == 0) && (message1->alignment[i - 1] == message2->alignment[j - 1])) {
    result += MATCH;
  } else {
    result += MISMATCH;
  }
  return result;
}


void displayMessage(t_message * message) {
  unsigned int i=0;
  printf("Data : ");
  for (i=0; i< message->len; i++) {
    printf("%02x", (unsigned char) message->alignment[i]);
  }
  printf("\n");
  printf("Tags : ");
  for (i=0; i< message->len; i++) {
    if (message->semanticTags != NULL && message->semanticTags[i] != NULL && message->semanticTags[i]->name != NULL && strcmp(message->semanticTags[i]->name, "None") != 0) {
      printf("(%d)%s;", i, message->semanticTags[i]->name);
    } else {
      printf("..");
    }
  }
  printf("\n");
}
