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

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import gobject
import logging

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Common.Group import Group
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.TypeIdentifier import TypeIdentifier

#+---------------------------------------------- 
#| C Imports
#+----------------------------------------------
import libNeedleman


#+---------------------------------------------- 
#| Clusterer :
#|     Reorganize a set of groups
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class Clusterer(object):
 
    def __init__(self, netzob, groups, explodeGroups=False):
        self.netzob = netzob
        self.groups = []
        # Create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.Clusterer.py')

        if explodeGroups == False:
            self.groups = groups
            self.log.debug("A number of {0} already aligned groups will be clustered.".format(str(len(groups))))
        else:
            # Create a group for each message
            self.groups = []
            i = 0
            for group in groups :
                for m in group.getMessages():
                    i += 1
                    self.groups.append(Group(str(i), [m], group.getProperties()))
            self.log.debug("A number of {0} messages will be clustered.".format(str(i)))
        
    #+---------------------------------------------- 
    #| retrieveMaxIJ :
    #|   given a list of groups, it computes the 
    #|   the possible two groups which can be merged
    #| @return (i,j,max) (i,j) path in the matrix of 
    #|                   the groups to merge
    #|                    max score of the two groups
    #+----------------------------------------------
    def retrieveEffectiveMaxIJ(self):
        self.log.debug("Computing the associated matrix")
        # Serialize the groups before feeding the C library
        configParser = ConfigurationParser()
        doInternalSlick = configParser.getInt("clustering", "do_internal_slick")
        serialGroups = ""
        format = ""
        typer = TypeIdentifier()
        for group in self.groups:
            if group.getAlignment() != "": # If we already computed the alignement of the group, then use it
                format += "1" + "G"
                messageTmp = ""
                alignmentTmp = ""
                for i in range(0, len(group.getAlignment()), 2):
                    if group.getAlignment()[i:i + 2] == "--":
                        messageTmp += "\xff"
                        alignmentTmp += "\x01"
                    else:
                        messageTmp += typer.toBinary(group.getAlignment()[i:i + 2])
                        alignmentTmp += "\x00"
                format += str(len(group.getAlignment()) / 2) + "M"
                serialGroups += messageTmp
                serialGroups += alignmentTmp
            else:
                format += str(len(group.getMessages())) + "G"
                for m in group.getMessages():
                    format += str(len(m.getReducedStringData()) / 2) + "M"
                    serialGroups += typer.toBinary(m.getReducedStringData()) # The message
#                    print m.getReducedStringData()
                    serialGroups += "".join(['\x00' for x in range(len(m.getReducedStringData()) / 2)]) # The alignement == "\x00" * len(the message), the first time
#                    print "".join( ['\x00' for x in range(len(m.getReducedStringData()) / 2)] ).encode("hex")

        # Execute the Clustering part in C :) (thx fgy)
        (i_max, j_max, maxScore) = libNeedleman.getMatrix(doInternalSlick, len(self.groups), format, serialGroups)
        return (i_max, j_max, maxScore)
    
    def retrieveMaxIJ(self):
        return self.retrieveEffectiveMaxIJ()
    
    def mergeGroups(self):
        self.mergeEffectiveGroups()
    
    def mergeEffectiveGroups(self):
        # retrieves the following parameters from the configuration file
        configParser = ConfigurationParser()
        nbIteration = configParser.getInt("clustering", "nbIteration")        
        min_equivalence = configParser.getFloat("clustering", "equivalence_threshold")
        self.log.debug("Re-Organize the groups (nbIteration={0}, min_equivalence={1})".format(nbIteration, min_equivalence))

        gobject.idle_add(self.resetProgressBar)
        progressionStep = 1.0 / nbIteration
        for iteration in range(0, nbIteration) :                 
            self.log.debug("Iteration {0} started...".format(str(iteration)))
            # Create the score matrix for each group
            (i_maximum, j_maximum, maximum) = self.retrieveEffectiveMaxIJ()

            """
            ## Just for debug purpose
            for group in self.groups:
                group.buildRegexAndAlignment()
                compiledRegex = re.compile("".join( group.getRegex() ))
                for message in group.getMessages():
#                    print message.getStringData()
                    data = message.getStringData()
                    m = compiledRegex.match(data)
                    if m == None:
                        print "".join( group.getRegex() )
                        print message.getStringData()
                        print "PAN"
                    else:
                        pass
            """   


            gobject.idle_add(self.doProgressBarStep, progressionStep)
            self.log.debug("Searching for the maximum of equivalence.")
            if (maximum >= min_equivalence) :
                self.log.info("Merge the column/line {0} with the column/line {1} ; score = {2}".format(str(i_maximum), str(j_maximum), str(maximum)))
                self.mergeEffectiveRowCol(i_maximum, j_maximum)        
            else :
                self.log.info("Stopping the clustering operation since the maximum found is {0} (<{1})".format(str(maximum), str(min_equivalence)))
                break

        # Compute the regex/alignment of each group
        gobject.idle_add(self.resetProgressBar)
        progressionStep = 1.0 / len(self.groups)
        for g in self.groups :
            g.buildRegexAndAlignment()
            gobject.idle_add(self.doProgressBarStep, progressionStep)
        gobject.idle_add(self.resetProgressBar)
    
    #+---------------------------------------------- 
    #| mergeOrphanGroups :
    #|   try to merge orphan groups by progressively
    #|   reducing the taken into account size of msgs
    #+----------------------------------------------  
    def mergeOrphanGroups(self):
        self.log.debug("Merge the orphan groups computed")
        
        leftReductionFactor = 0
        rightReductionFactor = 0
        currentReductionIsLeft = False
        increment = 10
        
        while leftReductionFactor < 80 and rightReductionFactor < 80 :
            
            # First we retrieve the current orphans
            orphans = []
            tmp_groups = []
            # extract orphans
            for group in self.groups :
                if len(group.getMessages()) == 1 :
                    orphans.append(group)
            # create a tmp groups array where groups will be added once computed    
            for group in self.groups :
                if len(group.getMessages()) > 1 :
                    tmp_groups.append(group)
            
            if len(orphans) <= 1 :
                self.log.info("Number of orphan groups : {0}. The orphan merging op. is finished !".format(len(orphans)))
                break;

            self.groups = orphans            
            if currentReductionIsLeft :
                leftReductionFactor = leftReductionFactor + increment
                # Reduce the size of the messages by 50% from the left
                for orphan in self.groups:
                    orphan.getMessages()[0].setLeftReductionFactor(leftReductionFactor)

                self.log.warning("Start to merge orphans reduced by {0}% from the left".format(str(leftReductionFactor)))
                self.mergeEffectiveGroups()
                currentReductionIsLeft = False
                
            if not currentReductionIsLeft :
                rightReductionFactor = rightReductionFactor + increment
                # Reduce the size of the messages from the right
                for orphan in self.groups:
                    orphan.getMessages()[0].setRightReductionFactor(rightReductionFactor)

                self.log.warning("Start to merge orphans reduced by {0}% from the right".format(str(rightReductionFactor)))
                self.mergeEffectiveGroups()
                currentReductionIsLeft = True
            
        
            for orphan in self.groups :
                tmp_groups.append(orphan)
            self.groups = tmp_groups 

        # Compute the regex/alignment of each group
        gobject.idle_add(self.resetProgressBar)
        progressionStep = 1.0 / len(self.groups)
        for g in self.groups :
            g.buildRegexAndAlignment()
            gobject.idle_add(self.doProgressBarStep, progressionStep)
        gobject.idle_add(self.resetProgressBar)

    #+---------------------------------------------- 
    #| mergeRowCol :
    #|   Merge the groups i and j in the "groups" structure
    #+----------------------------------------------    
    def mergeEffectiveRowCol(self, i_maximum, j_maximum):
        # Extract groups i and j
        if i_maximum > j_maximum:
            group1 = self.groups.pop(i_maximum)
            group2 = self.groups.pop(j_maximum)
        else:
            group2 = self.groups.pop(j_maximum)
            group1 = self.groups.pop(i_maximum)

        # Merge the groups i and j
        messages = []
        messages.extend(group1.getMessages())
        messages.extend(group2.getMessages())
        newGroup = Group(group1.getName() + group2.getName(), messages, group1.getProperties())
                    
        # Append th new group to the "groups" structure
        self.groups.append(newGroup)
    
    def mergeRowCol(self, i_maximum, j_maximum):
        self.mergeEffectiveRowCol(i_maximum, j_maximum)
        

    #+---------------------------------------------- 
    #| doProgressBarStep :
    #+----------------------------------------------    
    def doProgressBarStep(self, step):
        pass
#        new_val = self.netzob.progressBar.get_fraction() + step
#        self.netzob.progressBar.set_fraction(new_val)

    #+---------------------------------------------- 
    #| resetProgressBar :
    #+----------------------------------------------
    def resetProgressBar(self):
        pass
#        self.netzob.progressBar.set_fraction(0)

    #+---------------------------------------------- 
    #| GETTER/SETTER :
    #+----------------------------------------------
    def getGroups(self):
        return self.groups

"""        
#+---------------------------------------------- 
#| UNIT TESTS
#+----------------------------------------------
if __name__ == "__main__":
    sequence1 = "bonjour  where  you o!"
    sequence2 = "bonjour me where will you go!"
    sequence3 = "bonjour tii where do you come from!"
    sequence4 = "bonsoir aaaaaaaa, your are not welcome in my world on 192.168.0.10"
    sequence5 = "bonsoir bbbbbb, your are not welcome in my world on 10.12.131.12"
    sequence6 = "bonsoir ccccccc, your are not welcome in my world on 85.45.56.96"
    sequences = []
    
#    alignor = NeedlemanWunsch.NeedlemanWunsch()
#    sequences.append(alignor.asctohex(sequence1))
#    sequences.append(alignor.asctohex(sequence2))
#    sequences.append(alignor.asctohex(sequence3))
#    sequences.append(alignor.asctohex(sequence4))
#    sequences.append(alignor.asctohex(sequence5))
    sequences.append("d901ffffbe8512cd2c00ff020100000000d533012805000000c00000020000000000000000000000881300000200000002000000")
    sequences.append("cc01ffffc98512cd2c00ff0201000000bf9874012805010000c00000020000000000000000000000881300000200000002000000")
    sequences.append("d901ffffef8612cd2c00ff020100000000d533012805000000c00000020000000000000000000000881300000200000002000000")
    sequences.append("cc01ffff048712cd2c00ff0201000000bf9874012805010000c00000020000000000000000000000881300000200000002000000")
    sequences.append("d902000048e29fda1400ff0102000000f7dac70001000000be8512cd3400ff0301000000080532012805f30000c00000020000000000000000000000881300000200000002000000dbb20e50f7d7ce8a")
    sequences.append("d901f300378712cd1400ff0101000000bf9874000100000048e29fda")
    sequences.append("cc02010054e29fda1400ff01020000000070b10001000000c98512cd3400ff0301000000080509012805ec0100c00000020000000000000000000000881300000200000002000000dbb20e50f7dbce8a")
    sequences.append("d901f300478712cd0c00ff040200000000966701")
    sequences.append("cc01ec01478712cd1400ff0102000000009667000100000054e29fda")
    sequences.append("cc01ec014f8712cd0c00ff04020000000043a201")
    sequences.append("4301fffff48912cd2c00ff0201000000000000012805000000c00000020000000000000000000000881300000200000002000000")
    sequences.append("4301ffff248b12cd2c00ff0201000000000000012805000000c00000020000000000000000000000881300000200000002000000")
    sequences.append("43020000586d9dda1400ff01010000000976c80001000000f48912cd3400ff03010000000976c8012805a90028050000020000000f0000001f000000881300000200000002000000dbb20e500011440f")
#    sequences.append("4301a900a28b12cd1400ff01010000000000000001000000586d9dda")
#    sequences.append("4301a900b18b12cd5200010601000000000000010e504600b69adb3220b7323de03a57237a76469ebd2f1583b33de8332efd2c13849d4bcb24ba19182ad554a802c19562471dafcec52a26d85d7018f002fd75b8b7b715d5")
#    sequences.append("43010000846e9dda3400ff03010000000976c8012805a90028050000020000000f0000001f000000881300000200000002000000dbb20e500011440f")
#    sequences.append("4301a900b88c12cd1400ff01010000000000000001000000846e9dda")
#    sequences.append("4301a9004a8d12cd5200010601000000000000010e504600b69adb3220b7323de03a57237a76469ebd2f1583b33de8332efd2c13849d4bcb24ba19182ad554a802c19562471dafcec52a26d85d7018f002fd75b8b7b715d5")
#    sequences.append("430100001a6f9dda14000101010000000976c80001000000b18b12cd")
#    sequences.append("430100001d6f9ddaa203010601000000000000010e509603b69adb322aa2323d994eae6038abb858c7b13f954c53efb0aea51be4f23c9268588c94dd741509a26036bda6823cd98f7d8f2b9a0773068657e0a9f363bad6ddbb045a66806f9fa8367a22ac1ec78fd1ad225d207f2e63cede503372ca27ba5c706eb2224e85bc3b29726a7207732db457e0a9f363bad6ddbb045a66806f9fa8367a22acb5078fd1fda8045b7f2ec5e3de503372ca27ba5c706eb2220921bc3b096ee42225c83af15d8e9389944a62862c86114f171ec3a8deb2d6ba15b8f9d58ae53ffd9a6eed3b86c20049ca270a04706eb222e76abc3bc2d1c61a903965f02bbf3ea2572a6cf04569d10dd8598366d7cf3ce5bb9674a914aa58dc0223b6f22fda9a74ca27180c706eb22232f0bc3b46ca5d945ed067e9fed658537513fb4c358b92c2c65d1b9f48006dcd98a2c0c81245e44f3631e3259d0a7c62ca270597706eb222e4d5bc3b649668c3049ca8d1ef11f5a66abdd05d377b0adf672114416608aca932f65e87f627609ff319636fcb4f27dfca278b69706eb222b0b1bc3b83083474535d35c54eeb408004b627570a6bc95d5eaa4a4dc7ba40ef1f6aec1005625a2d63ab641a0c019b7fca27136d706eb2225e45bc3b65fbf8a8713fe99680a72c2742990949e07202621f08b6ce2ecaead2a4138f3b50ed9111bef8bffa991703cbca279655706eb222efd5bc3b95f8d653218048416dcf66651fd996cb38d8af435a9570982a1d9492cb3de79c91cdfd860c8bcf63535e1144ca27c4db706eb2227c35bc3b7812095848d6419f63d715d5e73782fc957b8a055b2c27f2afae1c54ce324be434d3673ca9a2aae53d9a907dca27632b706eb2221195bc3b06d44c0a272f7689445b93cf3b6abd7efbaca85a78ee0ef6cc9094f81ed28708f2b935a1e46e80fda0abf49eca27c35f706eb222e94ebc3bea0c99180031be08450b1421546045ddecae990a715b948cc985becc61451b020dab0fe8a55126e7bd746186ca27969d706eb2224b76bc3b8e6588a25357e8c652998d8c27c5f87c4df9f57c10d1675e68c5f81ff15c5b62906aef759f771d89392563e39eb808f5465e47481df03d44996a806d1f3e8ec51a7e9ba5557e41701dea1a20ce43c3ea0e8a981d340f5b55fa988686b5aa2a83c74e7a4e97b781d3965af20525cccd3cf44751bf84a4299824ad8f51d16f5c30bad8ac54c7ae8d667eb568e9799b4967dc78705e02fc4c1d05b18645ca279e4a706eb222885fbc3b1059cc211a0630575a65d065e7fabf48bfffd4d7b7b77a270000b7b7")
#    sequences.append("430100001d6f9dda0c00ff04020000005710fc01")
#    sequences.append("4302a9004a8d12cd140001010100000000000000010000001d6f9dda1400ff010000000000000000020000001d6f9dda")
    messages = []
    for sequence in sequences :
        msg = Message.Message()
        msg.setData(sequence)
        messages.append(msg)    
    group = Group.Group("group", messages)    
    
    print "Execution started..."
    # Measure the time for clustering
    start_time = time.clock()
    
    clusterer = Clusterer(True)
    groups = clusterer.reOrganize([group])
    
    end_time = time.clock()
    print "Execution time : {0}".format((end_time - start_time))
    
    
    for group in groups :
        print "[+] Group " + group.getName()
        print "\t+ " + group.getRegex()
        print "\t+ " + group.getAlignment()
        for message in group.getMessages() :
            print "\t- " + message.getStringData()

    print "-----------------------"  
    # retry an optimization process
    clusterer = Clusterer(True)
    for g in clusterer.reOrganizeGroups(groups) :
        print "[+] Group " + g.getName()
        print "\t+ " + g.getRegex()
        print "\t+ " + g.getAlignment()
        for message in g.getMessages() :
            print "\t- " + message.getStringData()
#            print "\t: " + binascii.unhexlify(''.join(message.getStringData().split()))
"""
