'''
Created on 13 mai 2011

@author: gbt

Arguments: alphabetAbstractor.py <input directory> <output file> 
> alphabetAbstractor.py resources/raws/ resources/raws.xml)

'''
import sys
import os
from Resources import netzobModel

       
def combinations_with_replacement(iterable, r):
    "combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC"
    # number items returned:  (n+r-1)! / r! / (n-1)!
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    indices = [0] * r
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i:] = [indices[i] + 1] * (r - i)
        yield tuple(pool[i] for i in indices)    
    


if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print "Error, verify usage alphabetAbstractor.py <input directory> <output file>"
        exit(1)
    else :
        ''' 
        Retrieves all the files and parse them
        '''
        inputModel = netzobModel.netzobModel()
        inputModel.directoryPath = sys.argv[1]
        inputModel.fillCaptures()
        
        datas = []
        for capture in inputModel.captures :  
            for message in capture.messages :
                datas.append(message['data'])      
        

        
        
        
        for size in range(0,len(datas)) :
            print "size = {0}/{1}".format(size, len(datas))
            for  t in combinations_with_replacement(datas, size) :
                pass
        
 