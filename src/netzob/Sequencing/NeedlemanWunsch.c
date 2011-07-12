#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef enum
  {
    FALSE,
    TRUE
  } BOOL;

/*
int computeScore(self, regex) {
        score = 0
        # Default score for an empty regex
        if len(regex) == 0 :
            return score

        nbDynamic = 0
        nbStatic = 0
        for elt in regex:
            if elt.find("(") != -1:
                nbDynamic += 1
            else:
                nbStatic += len(elt)
        
        score = 100.0 / (nbStatic + nbDynamic) * nbStatic
        return score
        

    def getRegex(self, sequences):
        if (len(sequences) < 2) :
            self.log.error("[ERROR] Impossible to compute the regex if at least 2 sequences are not provided.")
            return ([],"")
        
        sequence1 = sequences[0]
        for i in range(1, len(sequences)) :
            sequence2 = sequences[i]    
            regex = self.getRegexWithTwoSequences(sequence1, sequence2)
            
            sequence1 = regex
            
        
        
        i = 0
        start = 0
        result = []
        found = False
        for i in range(0, len(regex)) :
            if (regex[i] == "-"):
                
                if (found == False) :
                    start = i
                
                found = True
            else :
                if (found == True) :
                    found = False
                    nbTiret = i - start
                                   
                    result.append( "(.{," + str(nbTiret) + "})")
                    result.append( regex[i] )
                else :
                    if len(result) == 0:
                        result.append( regex[i] )
                    else:
                        result[-1] += regex[i]
        
        if (found == True) :
            nbTiret = i - start
            result.append( "(.{," + str(nbTiret) + "})" )

        return (result, str(regex))  
	      }    
*/

/*
char *asctohex(self, s) {
  empty = '';
  return empty.join(['%02x' % ord(c) for c in s]);
}
*/

void getRegexWithTwoSequences(const unsigned char seq1[],
			      unsigned short int seq1len,
			      const unsigned char seq2[],
			      unsigned short int seq2len) {
  short int match = 10;
  short int mismatch = -10;
  short int gap = 0;

  // initiliaze the matrix with 0
  short int matrix[seq1len][seq2len];
  unsigned short int i = 0;
  unsigned short int j = 0;
  memset(matrix, 0, sizeof(short int) * seq1len * seq2len);

  // fill the matrix
  short int elt1, elt2, elt3, max, eltL, eltD, eltT;
  BOOL finish;
  for(i = 1; i < seq1len ; i++) {
    for(j = 1; j < seq2len ; j++) {
      /*
	# Matrix[i][j] = MAXIMUM (
	# elt1 :         Matrix[i-1][j-1] + match/mismatch(Matrix[i][j]),
	# elt2 :         Matrix[i][j-1]   + gap,
	# elt3 :         Matrix[i-1][j]   + gap)
      */
      elt1 = matrix[i - 1][j - 1];
      if(seq1[i - 1] == seq2[j - 1])
	elt1 += match;
      else
	elt1 += mismatch;
      elt2 = matrix[i][j - 1] + gap;
      elt3 = matrix[i - 1][j] + gap;

      max = elt1 > elt2 ? elt1 : elt2;
      max = max > elt3 ? max : elt3;
      matrix[i][j] = max;
    }
  }

  /*
  for(i = 0; i < seq1len ; i++) {
    for(j = 0; j < seq2len ; j++)
      printf("%02x ", matrix[i][j]);
    printf("\n");
  }
  printf("\n");
  */
   
  // Traceback
  finish = FALSE;
  unsigned char *regex1 = malloc((seq1len + seq2len) * sizeof(unsigned char));
  unsigned char *regex2 = malloc((seq1len + seq2len) * sizeof(unsigned char));
  unsigned char *regex1Mask = malloc((seq1len + seq2len) * sizeof(unsigned char));
  unsigned char *regex2Mask = malloc((seq1len + seq2len) * sizeof(unsigned char));
  // TODO: (fgy) handle errors on malloc operation
  memset(regex1, 0x00, (seq1len + seq2len) * sizeof(unsigned char));
  memset(regex2, 0x00, (seq1len + seq2len) * sizeof(unsigned char));
  memset(regex1Mask, 0x00, (seq1len + seq2len) * sizeof(unsigned char));
  memset(regex2Mask, 0x00, (seq1len + seq2len) * sizeof(unsigned char));
  unsigned short int iReg1 = seq1len + seq2len - 1;
  unsigned short int iReg2 = seq1len + seq2len - 1;

  i = seq1len - 1;
  j = seq2len - 1;
  while( finish != TRUE ) {
    eltL = matrix[i][j - 1];
    eltD = matrix[i - 1][j - 1];
    eltT = matrix[i - 1][j];

    printf(" %02x %02x %02x \n", eltL, eltD, eltT);

    if ((eltL > eltD) && (eltL > eltT)) {
      --j;
      regex1[iReg1] = 0xff;
      regex1Mask[iReg1] = 1;
      regex2[iReg2] = seq2[j];
      printf(" L:%02x\n",seq2[j]);
      --iReg1;
      --iReg2;
     }
    else if ((eltT >= eltL) && (eltT > eltD)){
      --i;
      regex2[iReg2] = 0xff;
      regex2Mask[iReg2] = 1;
      regex1[iReg1] = seq1[i];
      printf(" T:%02x\n",seq1[i]);
      --iReg1;
      --iReg2;
    }
    else{
      --i;
      --j;
      regex1[iReg1] = seq1[i];
      printf(" D:%02x\n",seq1[i]);
      printf(" D:%02x\n",seq2[j]);
      regex2[iReg2] = seq2[j];
      --iReg1;
      --iReg2;
    }
         
    if (i == 0 || j == 0)
      finish = TRUE;
  }


  for(j = 0; j < seq1len + seq2len ; j++)
    printf("%02x ", regex1Mask[j]);
  printf("\n");

  for(j = 0; j < seq1len + seq2len ; j++)
    printf("%02x ", regex1[j]);
  printf("\n\n");

  for(j = 0; j < seq1len + seq2len ; j++)
    printf("%02x ", regex2[j]);
  printf("\n");

  for(j = 0; j < seq1len + seq2len ; j++)
    printf("%02x ", regex2Mask[j]);
  printf("\n\n");


  // Computes the first version of the regex
  unsigned char *regex = malloc((seq1len + seq2len) * sizeof(unsigned char));
  unsigned char *regexMask = malloc((seq1len + seq2len) * sizeof(unsigned char));
  // TODO: (fgy) handle errors on malloc operation
  memset(regex, 0x00, (seq1len + seq2len) * sizeof(unsigned char));
  memset(regexMask, 0x00, (seq1len + seq2len) * sizeof(unsigned char));
  unsigned short int iReg = seq1len + seq2len - 1;

  i = seq1len + seq2len - 1;
  while ( i > 0 ) {
    if( regex1[i] != regex2[i] ) { // TODO: (fgy) use the Masks !
      regex[iReg] = 0xff;
      regexMask[iReg] = 1;
      --iReg;
    }
    else {
      regex[iReg] = regex1[i];
      --iReg;
    }
    --i;
  }

  for(j = 0; j < seq1len + seq2len ; j++)
    printf("%02x ", regexMask[j]);
  printf("\n");

  for(j = 0; j < seq1len + seq2len ; j++)
    printf("%02x ", regex[j]);
  printf("\n\n");

  free( regex1 );
  free( regex2 );
  free( regex1Mask );
  free( regex2Mask );
  // TODO: (fgy) avoid double freeing
}


void main(){
  // the first element of each sequence should be the same
  char seq1[] = {0xff, 0x31, 0x32, 0x36, 0x36, 0x37, 0x38, 0x39};
  char seq2[] = {0xff, 0x31, 0x32, 0x37, 0x38, 0x31, 0x31, 0x31, 0x39};
  getRegexWithTwoSequences(seq1, 8, seq2, 9);
}

/*    
    regex = alignor.getRegex(sequences)   
    score = alignor.computeScore("".join(regex))
    print regex
    print "Score : {0}".format(score)
    compiledRegex = re.compile("".join(regex))
    for seq in sequences :
        m = compiledRegex.match(seq)
        if (m == None) :
            print "doesn't match for seq : {0}".format(seq)
        else :
            print "match for seq :  {0}".format(seq)
            nbGroup = len(m.groups())
            print "Number of groups : {0}".format(nbGroup)
*/         
