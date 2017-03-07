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
#ifndef CLUSTERBYSNAPPY_H
#define CLUSTERBYSNAPPY_H

#include <snappy-c.h>
#include "libNeedleman.h"

float computeScore(t_message msg1,t_message msg2)
{
  unsigned char * concat;
  unsigned char * output1;
  unsigned char * output2;
  unsigned char * output3;
  size_t output_length1;
  size_t output_length2;
  size_t output_length3;
  int max = 0;
  int min = 0;
  float result = 0.0;

//printf("Step1\n");
  concat = (unsigned char *) malloc ((msg1.len+msg2.len)*sizeof(unsigned char));
  memset(concat,'\0',msg1.len+msg2.len);
  memcpy(concat,msg1.message,msg1.len);
  memcpy(concat+msg1.len,msg2.message,msg2.len);
int i;
/*for(i=0;i<msg1.len+msg2.len;++i){
  //////printf("%02x",concat[i]);
}
//////printf("\n");
for(i=0;i<msg1.len;++i){
  ////printf("%02x",msg1.message[i]);
}
////printf("\n");
for(i=0;i<msg2.len;++i){
  ////printf("%02x",msg2.message[i]);
}*/
////printf("\n");
//printf("Step2\n");
  output_length1 = snappy_max_compressed_length(msg1.len+msg2.len);
  output1 = malloc(output_length1*sizeof(unsigned char));
  memset(output1,'\0',output_length1);

//printf("Step3 \n");
  output_length2 = snappy_max_compressed_length(msg1.len);
  output2 = malloc(output_length2*sizeof(unsigned char));
  memset(output2,'\0',output_length2);

//printf("Step4\n");
  output_length3 = snappy_max_compressed_length(msg2.len);
  output3 = malloc(output_length3*sizeof(unsigned char));
  memset(output3,'\0',output_length3);

//printf("Step5\n");
int res = snappy_compress(concat,msg1.len+msg2.len,output1,&output_length1);
int res2 = snappy_compress(msg1.message,msg1.len,output2,&output_length2);
int res3 = snappy_compress(msg2.message,msg2.len,output3,&output_length3);
//////printf("Signals %d %d %d\n",res,res2,res3);
  if(res == SNAPPY_OK)
  if(res2 == SNAPPY_OK)
  if(res3 == SNAPPY_OK)
    {
     //////printf("Inside \n");
     max = output_length2 > output_length3? output_length2:output_length3;
     min = output_length2 <= output_length3? output_length2:output_length3;
     result = 100.0 * (output_length1 - min) / max;
     result = result < 100 ? result : 100;
     ////////printf("input_length1 %d \n",msg1.len+msg2.len);
     ////////printf("input_length2 %d \n",msg1.len);
     ////////printf("input_length3 %d \n",msg2.len);
     ////////printf("output_length1 %d \n",output_length1);
     ////////printf("output_length2 %d \n",output_length2);
     ////////printf("output_length3 %d \n",output_length3);
     ////////printf("min %d \n",min);
     ////////printf("max %d \n",max);
     ////////printf("Result %f\n\n\n",result);
    }

   //printf("Begin Free\n");
   free(concat);
   //printf("FREEDOnE 1\n");
   free(output1);
   //printf("FREEDOnE 2\n");
   free(output2);
   //printf("FREEDOnE 3\n");
   free(output3);
   //printf("FREEDOnE\n");
   return result;
}
#endif
