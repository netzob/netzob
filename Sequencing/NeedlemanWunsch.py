#!/usr/bin/python
# coding: utf8
#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
from numpy  import *

#+---------------------------------------------- 
#| NeedlemanWunsch :
#|     Dedicated to sequence alignment
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class NeedlemanWunsch:
    
    #+---------------------------------------------- 
    #| Constructor :
    #| no actions 
    #+----------------------------------------------   
    def __init__(self):
        pass
    
    #+---------------------------------------------- 
    #| computeScore :
    #|     Computes the score of a given regex 
    #| @param regex : the regex for which the score is computed
    #| @return the score   
    #+---------------------------------------------- 
    def computeScore(self, regex):
        score = 0
        if (len(regex)==0) :
            return score
        
        nbStatic = len(regex.replace("(.*)", ""))
        nbDynamic = (len(regex) - nbStatic) / 4
        score = 100.0 / (nbStatic+nbDynamic) * nbStatic 
        return score
    
    
    #+---------------------------------------------- 
    #| getRegex :
    #|     Computes the regex for the given sequences 
    #| @param sequences : a list containing all the sequences
    #|                    to align
    #| @return the regex
    #+---------------------------------------------- 
    def getRegex(self, sequences):
        if (len(sequences)<2) :
            print "[ERROR] Impossible to compute the regex if at least 2 sequences are not provided."
            return ""
        
        sequence1 = sequences[0]
        
        for i in range(1,len(sequences)) :
            sequence2 = sequences[i]            
            regex = self.getRegexWithTwoSequences(sequence1, sequence2)
            sequence1 = regex
        return regex    
    
        
    #+---------------------------------------------- 
    #| getRegex :
    #|     Computes the regex for the given sequences 
    #| @param sequence1 : sequence 1
    #| @param sequence2 : sequence 2
    #| @return the regex
    #+---------------------------------------------- 
    def getRegexWithTwoSequences(self, sequence1, sequence2):
          match = 1
          mismatch = -1
          gap = 0
        
          # initiliaze the matrix
          matrix = zeros((len(sequence1) + 1, len(sequence2) + 1))
          
          # fullfill the matrix
          for i in range(1, len(sequence1) + 1) :              
              for j in range(1, len(sequence2) + 1) :
                  
                  # Matrix[i][j] = MAXIMUM (
                  # elt1 :         Matrix[i-1][j-1] + match/mismatch(Matrix[i][j]),
                  # elt2 :         Matrix[i][j-1]   + gap,
                  # elt3 :         Matrix[i-1][j]   + gap)
                  
                  elt1 = matrix[i - 1][j - 1]
                  if (sequence1[i - 1] == sequence2[j - 1]) :
                      elt1 = elt1 + match
                  else :
                      elt1 = elt1 + mismatch
                  
                  elt2 = matrix[i][j - 1] + gap
                  
                  elt3 = matrix[i - 1][j] + gap
                  
                  matrix[i][j] = max(max(elt1, elt2), elt3)
          
          # Traceback
          finish = False
          i = len(sequence1)
          j = len(sequence2)
          
          regex1 = ""
          regex2 = ""
          
          
          while (not finish) :
              eltL = matrix[i][j - 1]
              eltD = matrix[i-1][j-1]
              eltT = matrix[i - 1][j]
              if (eltL > eltD and eltL > eltT) :
                  j=j-1  
                  regex1 = "-"+regex1
                  regex2 = sequence2[j]+regex2
              elif (eltT >= eltL and eltT > eltD) :
                  i=i-1  
                  regex2 = "-"+regex2
                  regex1 = sequence1[i]+regex1
              else :
                  i=i-1
                  j=j-1
                  regex1 = sequence1[i]+regex1
                  regex2 = sequence2[j]+regex2
         
              if (i==0 or j==0) :
                  finish = True 
          
          # Computes the first version of the regex
          if len(regex1)!=len(regex2) :
              print "[ERROR] Computed alignment is not good !"
              return ""
          
          regex = ""
          saved1 = ""
          saved2 = ""
          for i in range(0,len(regex1)) :
              if (regex1[i]!=regex2[i]) :
                  if (i<len(regex1)-1 and regex1[i+1]==regex2[i+1]) :
                      
                      
                      saved1=saved1+regex1[i]
                      saved2=saved2+regex2[i]
                      
                      saved1 = saved1.replace("-","").replace("(", "").replace(")","").replace("*", "")
                      saved2 = saved2.replace("-","").replace("(", "").replace(")", "").replace("*", "")
                      if (len(saved1)>0 or len(saved2)>0) :
#                        regex = regex+"*("                        
#                        if (len(saved1)>0) :
#                            regex = regex+saved1
#                            if (len(saved2)>0) :
#                                regex = regex+"|"
#                        if (len(saved2)>0) :
#                            regex = regex +saved2
#                        regex = regex + ")"
                         regex = regex + "(.*)"
#                     print "Saved = {0}".format(saved1)
#                     print "Saved = {0}".format(saved2)
                      saved1 = ""
                      saved2 = ""
                  else :
#                      print "save : {0};{1}".format(regex1[i], regex2[i])
                      saved1=saved1+regex1[i]
                      saved2=saved2+regex2[i]
              else :
                  regex = regex+regex1[i]
              
          return regex  
                  
                  
                  
                 
                                                        
          
          
#+---------------------------------------------- 
#| UNIT TESTS
#+----------------------------------------------
if __name__ == "__main__":
    sequence1 = "bonjour you where do you come from!"
    #sequence1 = "bonjour *(you|me) where *(do|will) you *(c|g)o*(me from)!"
    #sequence1 = "bonjour *(you|me)*(me) where *(do|will)*(will) you *(c|g)*(g)o*(me from)!"
    #sequence1 = "bonjour  where  you o!"
    sequence2 = "bonjour me where will you go!"
    sequence3 = "bonjour tii where do you come from!"
    sequence4 = "bonjour aaaaaaaa, your are not welcome in my world on xxx.xxx.xxx.xxx"
    sequences = []
    sequences.append(sequence1)
    sequences.append(sequence2)
    sequences.append(sequence3)
    #sequences.append(sequence4)
    alignor = NeedlemanWunsch()
    regex = alignor.getRegex(sequences)   
    score = alignor.computeScore(regex)
    print regex
    print "Score : {0}".format(score)
