#!/usr/bin/ python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import gtk
import os
import gobject
import pygtk
from Sequencing.Clusterer import Clusterer
pygtk.require('2.0')

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
import TraceParser
import MessageGroup

#+---------------------------------------------- 
#| TracesExtractor :
#|     manage the extraction of messages from traces
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class TracesExtractor(object):
    #+---------------------------------------------- 
    #| Constructor :
    #| @param path: path of the directory containing traces to parse 
    #+----------------------------------------------   
    def __init__(self, zob):
        self.zob = zob
        self.path = self.zob.tracePath
    
    #+---------------------------------------------- 
    #| Parse :
    #| @update the groups paramter with the computed groups of messages
    #+----------------------------------------------   
    def parse(self, groups, uiNotebook):
        print "[INFO] Extract traces from directory {0}".format(self.path)
        
        # Retrieves all the files to parse
        files = []
        for file in os.listdir(self.path):
            filePath = self.path + "/" + file
            
            if file == '.svn':
                print "[INFO] Do not parse file {0}".format(filePath)
            else :
                files.append(file)
        
        # compute the progression step
        progressionStep = 1.0 / len(files)        
        
        tmp_groups = []
        # Parse each file
        for file in files :
            yield True
            filePath = self.path + "/" + file
            traceParser = TraceParser.TraceParser(filePath)
            # Append retrieved message to the final list
            tmpMessages = []
            tmpMessages = traceParser.parse()
            # Save the extracted messages in a dedicated group
            group = MessageGroup.MessageGroup(file, tmpMessages)
#            # Compute the regex
#            group.computeRegex()
#            # Compute the score
#            group.computeScore()
            
            # Now we try to reoganize eveything
            clusterer = Clusterer()
            for g in clusterer.reOrganize([group]) :
                groups.append(g)
            
            
            
            self.doProgressBarStep(progressionStep)
            

        #Once files parsed, reset the progressBar
        self.resetProgressBar()
        
        
        
        
        for group in groups :
            print "Group {0}".format(group.getName())
            for message in group.getMessages() :
                print message.getStringData()
        
        uiNotebook.update()
        yield False
        
        
    #+---------------------------------------------- 
    #| doProgressBarStep :
    #+----------------------------------------------    
    def doProgressBarStep(self, step):
        new_val = self.zob.progressBar.get_fraction() + step
        self.zob.progressBar.set_fraction(new_val)
        
    #+---------------------------------------------- 
    #| resetProgressBar :
    #+----------------------------------------------
    def resetProgressBar(self):
        self.zob.progressBar.set_fraction(0)
