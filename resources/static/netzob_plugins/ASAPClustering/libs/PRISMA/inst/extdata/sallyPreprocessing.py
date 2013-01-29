#!/usr/bin/python
import sys
from optparse import OptionParser

usage = "usage: %prog in.sally out.fsally"
parser = OptionParser(usage)

(options, args) = parser.parse_args()

if len(args) != 2:
    parser.print_help()
    sys.exit()

sallyIn = file(sys.argv[1])
sallyOut = file(sys.argv[2], "w")
# skip first line
sallyIn.readline()
allNgrams = {}
count = 0
for l in sallyIn:
    count += 1
    if count % 1000 == 0: 
        print(count)
    info = l.split(" ")
    if info[0] == "":
        curNgrams = []
    else:
        curNgrams = [ngramInfo.split(":")[1] for ngramInfo in info[0].split(",")]
        allNgrams.update(allNgrams.fromkeys(curNgrams))
    sallyOut.write("%s\n" % " ".join(curNgrams))
sallyOut.write("%s\n" % " ".join(allNgrams.keys()))
sallyOut.close()
sallyIn.close()
