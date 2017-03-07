
from netzob.all import *
import sys

sys.setrecursionlimit(10000)

messages_session1 = PCAPImporter.readFile("/home/warsang/zipfile/Push_Program1.pcap").values()
messages_session2 = PCAPImporter.readFile("/home/warsang/zipfile/Push_Program2.pcap").values()
#messages_session2 = PCAPImporter.readFile("/home/warsang/Downloads/target_src_v1_session2.pcap").values()

messages = messages_session1 + messages_session2

for message in messages:
    print(message)
symbol = Symbol(messages = messages)

#Format.splitDelimiter(symbol,HexaString("00"))

#print(symbol._str_debug())

