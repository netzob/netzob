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
#| InjectorGenerator :
#|     Describes and generates a GOT Injector
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class InjectorGenerator():
    
    def __init__(self, tmp_folder, parasite):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Capturing.GOTPoisoning.InjectorGenerator.py')
        # temporary folder
        self.tmp_folder = tmp_folder
        # parasite generator
        self.parasite = parasite
        
        # configure
        self.libName = "libtest.so.1.0"
        self.libPath = "/lib/libtest.so.1.0"
        self.shellcode = self.produceShellCode()
        
    #+-----------------------------------------------------------------------+
    #| produceShellCode
    #|     Generates the shellcode in function of :
    #|     - the path of the parasite lib
    #|     - 
    #| @param function HijackedFunction to include
    #+-----------------------------------------------------------------------+ 
    def produceShellCode(self):
        shellcode = ["e9", "3b", "00", "00", "00", "31", "c9", "b0", "05", "5b", "31", "c9", "cd", "80", "83", "ec"
        , "18", "31", "d2", "89", "14", "24", "c7", "44", "24", "04", "00", "20", "00", "00", "c7", "44"
        , "24", "08", "07", "00", "00", "00", "c7", "44", "24", "0c", "02", "00", "00", "00", "89", "44"
        , "24", "10", "89", "54", "24", "14", "b8", "5a", "00", "00", "00", "89", "e3", "cd", "80", "cc"
        , "e8", "c0", "ff", "ff", "ff"]
        
        
        for x in self.libPath :
            shellcode.append(hex(ord(x))[2:]) 
        shellcode.append("00")
        return shellcode
    
    def getSourceCode(self):
        source = '''//+---------------------------------------------------------------------------+
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
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/ptrace.h>
#include <sys/mman.h>
#include <elf.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>
#include <signal.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/syscall.h>
 
#define ORIG_EAX 11
#define MAXBUF 255
 
/* memrw() request to modify global offset table */
#define MODIFY_GOT 1
 
/* memrw() request to patch parasite */
/* with original function address */
#define INJECT_TRANSFER_CODE 2
'''
        source = source + "#define EVILLIB \"" + self.getLibName() + "\"\n"
        source = source + "#define EVILLIB_FULLPATH \"" + self.getLibPath() + "\"\n" 
        source += '''
 
/* should be getting lib mmap size dynamically */
/* from map file; this #define is temporary */
#define LIBSIZE 5472 
 
/* struct to get symbol relocation info */
struct linking_info
{
        char name[256];
        int index;
        int count;
        uint32_t offset;
};
 
struct segments
{
    unsigned long text_off;
    unsigned long text_len;
    unsigned long data_off;
    unsigned long data_len;
} segment;
unsigned long original;
extern int getstr;
 
unsigned long text_base;
unsigned long data_segment;
char static_sysenter = 0; 

/* make sure to put your shared lib in /lib and name it libtest.so.1.0 */
char mmap_shellcode[] = \"'''
        source = source + self.getShellCode()
        source = source + '''\";
 
/* the signature for our evil function in our shared object */ 
/* we use the first 8 bytes of our function code */
/* make sure this is modified based on your parasite (evil function) */ 
unsigned char evilsig[] = "'''
        source = source + self.getParasiteSignature()
        source = source + '''\"; 

'''
        return source
        
    
    
    def writeInjectorToFile(self):
        source = self.getSourceCode()
        print source
        
        
    def getLibName(self):
        return self.libName
    def getLibPath(self):
        return self.libPath    
    def getShellCode(self):
        return "\\x" + "\\x".join(self.shellcode)
    def getParasiteSignature(self):
        return "\\x" + "\\x".join(self.parasite.getParasitesSignature()[0])

   
