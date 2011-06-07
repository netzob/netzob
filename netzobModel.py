#!/usr/bin/ python
# coding: utf8

import os
import gtk
import xml.dom.minidom


class NetzobModel:
    def __init__(self):
        self.directoryPath = ""
        self.captures = []
        self.sequenceCapture = gtk.ListStore(int)
        
    def clear(self):
        self.directoryPath = ""
        self.captures = []

    def fillCaptures(self):
        for f in os.listdir(self.directoryPath):
            if f == '.svn':
                continue
            capture = CaptureModel(self.directoryPath + "/" + f)
            i = capture.fillCapture()
            self.captures.append( capture  )
        for j in range(i):
            self.sequenceCapture.append([j])


class CaptureModel:
    def __init__(self, path):
        self.path = path
        self.messages = [] # [numSequence, proto, sourceIp, sourcePort, targetIp, targetPort, timestamp, data]

    def clear(self):
        self.path = ""
        self.messages = []

    def fillCapture(self):
        i = 0
        if self.path != "":
            print self.path
            dom = xml.dom.minidom.parse(self.path)
            messages = dom.getElementsByTagName("data")
            for message in messages:
                i += 1
                for node in message.childNodes:
                    self.messages.append( {'data' : node.data.split() } )
        return i



if __name__ == "__main__":
    print "### Unit Test ###"
