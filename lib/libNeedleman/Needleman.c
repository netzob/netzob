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

//Compilation Windows
//cl -Fe_libNeedleman.pyd -Ox -Ot -openmp -LD /I"C:\Python26\include" /I"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include" libNeedleman.c "C:\Python26\libs\python26.lib" "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\lib\vcomp.lib"

//+---------------------------------------------------------------------------+
//| Import Associated Header
//+---------------------------------------------------------------------------+
#include "Needleman.h"
#include "regex.h"

#ifdef _WIN32
#include <stdio.h>
#include <malloc.h>
#endif





void alignMessages2(t_message *resMessage, Bool doInternalSlick, t_group* group, Bool debugMode) {
  // local variable
  unsigned int numberOfOperations = 0;
  double costOfOperation;
  double status = 0.0;
  int matchstatus = -1;
  char* commonregex=NULL;
  
  // Local variables
  t_message current_message;
  t_message new_message;
  t_score score;
  unsigned int i_message = 0;

  score.s1 = 0;
  score.s2 = 0;
  score.s3 = 0;
  score.value = 0;

  //+------------------------------------------------------------------------+
  // Estimate the number of operation
  //+------------------------------------------------------------------------+
  numberOfOperations = group->len - 1;
  costOfOperation = 100.0 / numberOfOperations;

  // Create a current message (using first message)
  // current message = Align N+1 message with current message
  current_message.len = group->messages[0].len;
  current_message.alignment = group->messages[0].alignment;
  current_message.mask = malloc(group->messages[0].len * sizeof(unsigned char));
  memset(current_message.mask, 0, group->messages[0].len);
  current_message.score = &score;

  // Prepare for the resMessage
  if (group->len == 1) {
    resMessage->len = current_message.len;
    resMessage->mask = current_message.mask;
    resMessage->alignment = current_message.alignment;
    resMessage->score = current_message.score;
  }
  for (i_message=1; i_message < group->len; i_message++) {
    matchstatus = -1;
    // Update the execution status
    if (callbackStatus(0, status, "Consider message %d in the alignment process", i_message) == -1) {
      printf("Error, error while executing C callback.\n");
    }
    if (callbackIsFinish() == 1) {
    	return;
    }
	
	/*initialize the next message*/
    new_message.len = group->messages[i_message].len;
    new_message.alignment = group->messages[i_message].alignment;
    new_message.mask = malloc(group->messages[i_message].len * sizeof(unsigned char));
    memset(new_message.mask, 0, group->messages[i_message].len);

	/*Check if the current common regex is not null. If so, try to match the current message with it*/
	if(commonregex!=NULL)
		matchstatus=matchonly(commonregex,new_message.alignment);
		
    // Align current_message with new_message
    if(matchstatus<0){
    if(commonregex!=NULL){
    	free(commonregex);
    	commonregex = NULL;
    }
    commonregex=alignTwoMessages(resMessage, doInternalSlick, &current_message, &new_message, debugMode);

    free(current_message.mask);
    free(new_message.mask);
    // Copy result in the current message
    current_message.len = resMessage->len;
    current_message.alignment = resMessage->alignment;
    current_message.mask = resMessage->mask;
	}
    //udpate status
    status += costOfOperation;
  }

  // Update the execution status
  if (callbackStatus(0, status, "The %d messages have sucessfully been aligned.", group->len) == -1) {
    printf("Error, error while executing C callback.\n");
  }

  if(commonregex!=NULL){
    	free(commonregex);
    	commonregex = NULL;
    }
  free(group->messages);
}







void alignMessages(t_message *resMessage, Bool doInternalSlick, t_group* group, Bool debugMode) {
  // local variable
  unsigned int numberOfOperations = 0;
  double costOfOperation;
  double status = 0.0;

  // Local variables
  t_message current_message;
  t_message new_message;
  t_score score;
  unsigned int i_message = 0;

  score.s1 = 0;
  score.s2 = 0;
  score.s3 = 0;
  score.value = 0;

  //+------------------------------------------------------------------------+
  // Estimate the number of operation
  //+------------------------------------------------------------------------+
  numberOfOperations = group->len - 1;
  costOfOperation = 100.0 / numberOfOperations;

  // Create a current message (using first message)
  // current message = Align N+1 message with current message
  current_message.len = group->messages[0].len;
  current_message.alignment = group->messages[0].alignment;
  current_message.mask = malloc(group->messages[0].len * sizeof(unsigned char));
  memset(current_message.mask, 0, group->messages[0].len);
  current_message.score = &score;

  // Prepare for the resMessage
  if (group->len == 1) {
    resMessage->len = current_message.len;
    resMessage->mask = current_message.mask;
    resMessage->alignment = current_message.alignment;
    resMessage->score = current_message.score;
  }
  for (i_message=1; i_message < group->len; i_message++) {
    // Update the execution status
    if (callbackStatus(0, status, "Consider message %d in the alignment process", i_message) == -1) {
      printf("Error, error while executing C callback.\n");
    }
    if (callbackIsFinish() == 1) {
    	return;
    }

    new_message.len = group->messages[i_message].len;
    new_message.alignment = group->messages[i_message].alignment;
    new_message.mask = malloc(group->messages[i_message].len * sizeof(unsigned char));
    memset(new_message.mask, 0, group->messages[i_message].len);

    // Align current_message with new_message
    alignTwoMessages(resMessage, doInternalSlick, &current_message, &new_message, debugMode);

    free(current_message.mask);
    free(new_message.mask);
    // Copy result in the current message
    current_message.len = resMessage->len;
    current_message.alignment = resMessage->alignment;
    current_message.mask = resMessage->mask;

    //udpate status
    status += costOfOperation;
  }

  // Update the execution status
  if (callbackStatus(0, status, "The %d messages have sucessfully been aligned.", group->len) == -1) {
    printf("Error, error while executing C callback.\n");
  }


  free(group->messages);
}


char* alignTwoMessages(t_message * resMessage, Bool doInternalSlick, t_message * message1, t_message * message2, Bool debugMode){
  // local variables
  short int **matrix;
  unsigned int i = 0;
  unsigned int j = 0;

  // Construction of the matrix
  short int elt1, elt2, elt3, max, eltL, eltD, eltT;
  // Levenshtein distance
  float levenshtein = 0.0;
  unsigned int maxLen = 0;
  // Traceback
  unsigned char *contentMessage1;
  unsigned char *contentMessage2;
  unsigned char *maskMessage1;
  unsigned char *maskMessage2;
  unsigned int iReg1 = 0;
  unsigned int iReg2 = 0;

  // Computing resMessage
  unsigned char *tmpMessage;
  unsigned char *tmpMessageMask;

  // Score computation
  unsigned int nbDynTotal = 0;
  unsigned int nbDynCommon = 0;

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
  unsigned int lastIndex1 = 0;
  unsigned int iblock = 0;
  unsigned int jblock = 0;
  unsigned int maxLoopi = 0;
  unsigned int maxLoopj = 0;
  unsigned int lastRow = 0;
  unsigned int lastColumn = 0;
  
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
            if ( (message1->mask[i - 1] == 0) && (message2->mask[j - 1] == 0) && (message1->alignment[i - 1] == message2->alignment[j - 1])) {
              //printf("++++++++++++%02x %02x\n",message1->alignment[i - 1],message2->alignment[j - 1]);
              elt1 += MATCH;
            } else {
              //printf("------------%02x %02x\n",message1->alignment[i - 1],message2->alignment[j - 1]);
              elt1 += MISMATCH;
            } 
            elt2 = matrix[i][j - 1] + GAP;
            elt3 = matrix[i - 1][j] + GAP;
            max = elt1 > elt2 ? elt1 : elt2;
            max = max > elt3 ? max : elt3;
	    	matrix[i][j] = max;
	    	
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
  
  
  levenshtein = MATCH*(float)matrix[message1->len][message2->len] / maxLen;
  float levcop = matrix[message1->len][message2->len];
  //levenshtein = levenshtein * 10 / maxLen;

  //+------------------------------------------------------------------------+
  // Traceback into the matrix
  //+------------------------------------------------------------------------+
  //finish = FALSE;
  contentMessage1 = calloc( message1->len + message2->len, sizeof(unsigned char));
  contentMessage2 = calloc( message1->len + message2->len, sizeof(unsigned char));
  maskMessage1 = calloc( message1->len + message2->len, sizeof(unsigned char));
  maskMessage2 = calloc( message1->len + message2->len, sizeof(unsigned char));

  if (contentMessage1 == NULL) {
    printf("Error while trying to allocate memory for variable : contentMessage1.\n");
    return -1;
  }
  if (contentMessage2 == NULL) {
    printf("Error while trying to allocate memory for variable : contentMessage2.\n");
    return -1;
  }
  if (maskMessage1 == NULL) {
    printf("Error while trying to allocate memory for variable : maskMessage1.\n");
    return -1;
  }
  if (maskMessage2 == NULL) {
    printf("Error while trying to allocate memory for variable : maskMessage2.\n");
    return -1;
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
    --iReg1;
    --iReg2;
  }

  // For debug only
  if (debugMode == TRUE) {
    printf("Message 1 : ");
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
    printf("Message 2 : ");
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
  char* regex=NULL;
  char hexrepr[3];
   //printf("taille %lf\n",levcop);
  //printf("taille %d\n",(int)(levcop/10)*2+(int)(levcop/10)+2);
  int sizereg = 100000;//(int)(levcop/10)*2+(int)(levcop/10)+2;
  int regind = 0;
  tmpMessage = calloc(message1->len + message2->len, sizeof(unsigned char));
  tmpMessageMask = malloc((message1->len + message2->len) * sizeof(unsigned char));
  memset(tmpMessageMask, END, (message1->len + message2->len) * sizeof(unsigned char));
  regex= malloc( sizereg* sizeof(char));
  memset(regex, 0, sizereg);

  i = 0;
  while (i < message1->len + message2->len) {
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
  // TODO: (fgy) free resMessage.mask and resMessage.alignment
  memcpy(resMessage->alignment, tmpMessage + i, resMessage->len);
  memcpy(resMessage->mask, tmpMessageMask + i, resMessage->len);


  // Compute the scores of similarity, using the resMessage
  if (debugMode) {
    printf("Result    : ");
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
  resMessage->score->s3 = levenshtein;

  if (debugMode) {
    printf("Score ratio : %0.2f.\n", resMessage->score->s1);
    printf("Score DynSize : %0.2f.\n", resMessage->score->s2);
    printf("Score Rang : %0.2f.\n", resMessage->score->s3);
  }


  // Room service
  for (i = 0; i < (message1->len + 1); i++) {
  /*if(!(i%BLEN)){
  	//printf("----------------------------------------------------------------------------------\n");
  }
     for(j = 0; j < (message2->len + 1); j++) {
     if(!(j%BLEN))
  		//printf("|\t",matrix[i][j]);   
  printf("%d,\t",matrix[i][j]);
  
  }
  printf("\n");
  */
    free( matrix[i] );
  }
  free( matrix );
  free(contentMessage1);
  free(contentMessage2);
  free(maskMessage1);
  free(maskMessage2);
  free(tmpMessage);
  free(tmpMessageMask);
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
float getScoreRang(t_message * message) {
  float result = 0;
  
  return result;
}
float computeDistance(t_score * score) {
  float result = 0;
  result = sqrt(0.0 * pow(score->s1,2) + 0.0 * pow(score->s2,2) + 1.0 * pow(score->s3,2));
  return result;
}
  
