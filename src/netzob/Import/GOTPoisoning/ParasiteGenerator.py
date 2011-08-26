#!/usr/bin/python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+
#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging.config
import os


#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from ...Common import ConfigurationParser

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| ParasiteGenerator :
#|     Describes and generates a GOT parasite
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class ParasiteGenerator():
    
    def __init__(self, tmp_folder):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Import.GOTPoisoning.ParasiteGenerator.py')
        # temporary folder
        self.tmp_folder = tmp_folder
        # list of functions to hijacked
        self.hijackedFunctions = []
        
    #+-----------------------------------------------------------------------+
    #| addAnHijackedFunctions
    #|     Include a new function in the pool of function to hijack
    #| @param function HijackedFunction to include
    #+-----------------------------------------------------------------------+   
    def addAnHijackedFunctions(self, function) :
        self.hijackedFunctions.append(function)
        
    #+-----------------------------------------------------------------------+
    #| getSourceCode
    #|    Generates source code of the parasite
    #| @return a string which contains the source code
    #+-----------------------------------------------------------------------+ 
    def getSourceCode(self):
        # add the header
        sourceCode = self.getSourceCodeHeader() + "\n\n"
        # add the definitions of IO functions
        sourceCode += self.getSourceCodeOfWriteFunction() + "\n\n"
        # add the parasite core functions
        sourceCode += self.getSourceCodeParasiteCoreFunctions()        
        return sourceCode
    
    def writeParasiteToFile(self):
        source = self.getSourceCode()    
        print source    
        file = open(self.tmp_folder + "/libNetzob.c", 'w')
        file.write(source)
        file.close()
        
    def compileParasite(self):
        f = os.popen("gcc -fPIC -c " + self.tmp_folder + "/libNetzob.c" + " -nostdlib -o " + self.tmp_folder + "/libNetzob.o")
        for i in f.readlines():
            print "GCC:", i,
    
    def linkParasite(self):
        f = os.popen("ld -shared -o " + self.tmp_folder + "/libNetzob.so.1.0 " + self.tmp_folder + "/libNetzob.o")
        for i in f.readlines():
            print "LD:", i,
            
    def getParasitesSignature(self):
        signatures = []
        for func in self.hijackedFunctions :
            f = os.popen("objdump -d " + self.tmp_folder + "/libNetzob.so.1.0")
            signature = []
            flag = False
            sizeSignature = 10
            for line in f.readlines():
                if line.endswith("<netzobParasite_" + func.getName() + ">:\n"):
                    flag = True 
                elif flag == True and sizeSignature > 0:
                    tmp = line.split("\t")[1]
                    for t in tmp.split() :
                        if sizeSignature > 0 :
                            signature.append(t)
                        sizeSignature = sizeSignature - 1
            signatures.append(signature)
        return signatures   
        
    
    
    def getSourceCodeOfWriteFunction(self):
        function = '''
static int _open(char * filename) {
    /**
     * sys_open :
     * %eax <- 5
     * %ebx <- const char *
     * %ecx <- int
     * %edx <- int
     */
    long id_fd;
    
    __asm__ __volatile__
    (        "pushl %%ebx\\n\\t"        // sauvegarde EBX
            "movl %%esi,%%ebx\\n\\t"    // on met ESI dans EBX
            "mov $1089, %%cl\\n\\t"        // on set le flag
            "mov $422, %%dx\\n\\t"
            "int $0x80\\n\\t"
            "popl %%ebx"
            :"=a" (id_fd) //EAX
            :"a" (SYS_open),
            "S" ((long) filename),//ESI
            "d" ((long) 0)//EDX
    );

    if (id_fd >= 0) {
        return (int) id_fd;
    }
    return -1;
}

static void _close(int fd) {

    /**
     * sys_close :
     * %eax <- 6
     * %ebx <- fd
     */
    __asm__ __volatile__
    (        "pushl %%ebx\\n\\t"        // sauvegarde EBX
            "movl %%esi,%%ebx\\n\\t"    // on met ESI dans EBX
            "int $0x80\\n\\t"
            "popl %%ebx"
            : /* no output */
            :"a" (SYS_close),
            "S" ((long) fd)//ESI
    );

}

static int _write(int fd, void *buf, int count) {
    long ret;

    __asm__ __volatile__
    (
            "pushl %%ebx\\n\\t"
            "movl %%esi,%%ebx\\n\\t"
            "int $0x80\\n\\t"
            "popl %%ebx"
            :"=a" (ret)
            :"a" (SYS_write),
            "S" ((long) fd),
            "c" ((long) buf),
            "d" ((long) count)
    );
    if (ret >= 0) {
        return (int) ret;
    }
    return -1;
}        
'''
        return function
    
    def getSourceCodeParasiteCoreFunctions(self):
        coreFunctions = ""
        
        for function in self.hijackedFunctions :
            coreFunctions += function.getParasiteFunctionDeclaration() + "\n{\n" + function.getSource() + "\n}\n"
        
        return coreFunctions
        
    def getFunctions(self):
        return self.hijackedFunctions    
        
        
    
    #+-----------------------------------------------------------------------+
    #| getSourceCodeHeader
    #|    Generates the header of the source code
    #| @return a string which contains the header of the source code
    #+-----------------------------------------------------------------------+    
    def getSourceCodeHeader(self):
        header = '''//+---------------------------------------------------------------------------+
//|         01001110 01100101 01110100 01111010 01101111 01100010             | 
//+---------------------------------------------------------------------------+
//| NETwork protocol modeliZatiOn By reverse engineering                      |
//| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
//|      : GNU GPL v3                                                |
//| @copyright    : Georges Bossert and Frederic Guihery                      |
//| @url          : http://code.google.com/p/netzob/                          |
//| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
//| @author       : {gbt,fgy}@amossys.fr                                      |
//| @organization : Amossys, http://www.amossys.fr                            |
//+---------------------------------------------------------------------------+
#include <sys/syscall.h>
#include <sys/types.h>

'''
        # Add the prototypes of the functions
        for function in self.hijackedFunctions :
            header += "// " + function.getPrototype() + "\n"
            header += function.getParasitePrototype() + ";\n"
            
        
        return header   
