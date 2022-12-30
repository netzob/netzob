.. currentmodule:: netzob

.. _discover_features:

Discover features of Netzob
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

   This tutorial for Netzob 1.x is currently slighlty obsolete, and should be updated to the Netzob API 2.x.

This tutorial presents the main features of Netzob regarding the
inference of message formats and grammar of a simple toy protocol. The
described features cover the following capabilities:

-  Import of a PCAP file
-  Format message inference

 -  Partitionment of messages following a specific delimiter
 -  Regroupment of messages following a specific key field
 -  Partitionment of a subset a each message following a sequence aligment
 -  Search for relationships in each group of messages
 -  Modification of the format message to apply found relationships

-  Grammar inference

 -  Generation of an automaton with one main state according to a captured sequence of messages
 -  Generation of an automaton with a sequence of states according to a captured sequence of messages
 -  Generation of a Prefix Tree Acceptor (PTA) automaton according to a captured sequence of messages

-  Traffic generation and fuzzing

 -  Generation of messages following the inferred message format of each group and through visiting the inferred automata
 -  Fuzzing of an implementation by generating altered message formats

Retrieve Netzob and resources.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At first, retrieve the source code of Netzob::

  $ git clone https://dev.netzob.org/git/netzob

Then, you can retrieve the source code of the toy protocol implementation used in this tutorial, as well as some PCAP files of sequences of messages.

-  `Toy protocol implementation <https://dev.netzob.org/attachments/download/179/tutorial_netzob_v1.tar.gz>`_
-  `PCAP of sequence 1 <https://dev.netzob.org/attachments/download/182/target_src_v1_session1.pcap>`_
-  `PCAP of sequence 2 <https://dev.netzob.org/attachments/download/181/target_src_v1_session2.pcap>`_
-  `PCAP of sequence 3 <https://dev.netzob.org/attachments/download/180/target_src_v1_session3.pcap>`_

Import messages from a PCAP file.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Reading packets from a PCAP file is done through the PCAPImporter.readFile() static function. This function can optionally take more parameters to specify a BPF filter, the import layer or the number of packets to capture::

  from netzob.all import *

  messages_session1 = PCAPImporter.readFile("target_src_v1_session1.pcap").values()
  messages_session2 = PCAPImporter.readFile("target_src_v1_session2.pcap").values()

  messages = messages_session1 + messages_session2

  for message in messages:
      print(message)

The output is::

  [1388154953.32 127.0.0.1:57831->127.0.0.1:4242] 'CMDidentify#\x07\x00\x00\x00Roberto'
  [1388154953.32 127.0.0.1:4242->127.0.0.1:57831] 'RESidentify#\x00\x00\x00\x00\x00\x00\x00\x00'
  [1388154953.32 127.0.0.1:57831->127.0.0.1:4242] 'CMDinfo#\x00\x00\x00\x00'
  [1388154953.32 127.0.0.1:4242->127.0.0.1:57831] 'RESinfo#\x00\x00\x00\x00\x04\x00\x00\x00info'
  [1388154953.32 127.0.0.1:57831->127.0.0.1:4242] 'CMDstats#\x00\x00\x00\x00'
  [1388154953.32 127.0.0.1:4242->127.0.0.1:57831] 'RESstats#\x00\x00\x00\x00\x05\x00\x00\x00stats'
  [1388154953.32 127.0.0.1:57831->127.0.0.1:4242] 'CMDauthentify#\n\x00\x00\x00aStrongPwd'
  [1388154953.32 127.0.0.1:4242->127.0.0.1:57831] 'RESauthentify#\x00\x00\x00\x00\x00\x00\x00\x00'
  [1388154953.32 127.0.0.1:57831->127.0.0.1:4242] 'CMDencrypt#\x06\x00\x00\x00abcdef'
  [1388154953.32 127.0.0.1:4242->127.0.0.1:57831] "RESencrypt#\x00\x00\x00\x00\x06\x00\x00\x00$ !&'$"
  [1388154953.32 127.0.0.1:57831->127.0.0.1:4242] "CMDdecrypt#\x06\x00\x00\x00$ !&'$"
  [1388154953.32 127.0.0.1:4242->127.0.0.1:57831] 'RESdecrypt#\x00\x00\x00\x00\x06\x00\x00\x00abcdef'
  [1388154953.33 127.0.0.1:57831->127.0.0.1:4242] 'CMDbye#\x00\x00\x00\x00'
  [1388154953.33 127.0.0.1:4242->127.0.0.1:57831] 'RESbye#\x00\x00\x00\x00\x00\x00\x00\x00'
  [1388154953.31 127.0.0.1:57831->127.0.0.1:4242] 'CMDidentify#\x04\x00\x00\x00fred'
  [1388154953.31 127.0.0.1:4242->127.0.0.1:57831] 'RESidentify#\x00\x00\x00\x00\x00\x00\x00\x00'
  [1388154953.31 127.0.0.1:57831->127.0.0.1:4242] 'CMDinfo#\x00\x00\x00\x00'
  (...)


Regroup messages in a symbol and do a format partitionment with a delimiter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

According to a quick review of the displayed messages, the character '#' sounds interesting as i appears in the middle of each message. So let's use it as a delimiter::

  symbol = Symbol(messages=messages)

  Format.splitDelimiter(symbol, ASCII("#"))

  print("[+] Symbol structure:")
  print(symbol._str_debug())

  print("[+] Partitionned messages:")
  print(symbol)

We now obtain the following symbol (i.e. our goup of messages) structure::

  [+] Symbol structure:
  Symbol
  |--  Field-0
     |--   Alt
           |--   Data (Raw='RESstats' ((0, 64)))
           |--   Data (Raw='RESauthentify' ((0, 104)))
           |--   Data (Raw='RESidentify' ((0, 88)))
           |--   Data (Raw='CMDstats' ((0, 64)))
           |--   Data (Raw='CMDdecrypt' ((0, 80)))
           |--   Data (Raw='CMDauthentify' ((0, 104)))
           |--   Data (Raw='RESdecrypt' ((0, 80)))
           |--   Data (Raw='RESinfo' ((0, 56)))
           |--   Data (Raw='CMDinfo' ((0, 56)))
           |--   Data (Raw='RESauthentify' ((0, 104)))
           |--   Data (Raw='CMDencrypt' ((0, 80)))
           |--   Data (Raw='CMDauthentify' ((0, 104)))
           |--   Data (Raw='CMDstats' ((0, 64)))
           |--   Data (Raw='RESbye' ((0, 48)))
           |--   Data (Raw='RESdecrypt' ((0, 80)))
           |--   Data (Raw='RESencrypt' ((0, 80)))
           |--   Data (Raw='CMDidentify' ((0, 88)))
           |--   Data (Raw='CMDbye' ((0, 48)))
           |--   Data (Raw='RESinfo' ((0, 56)))
           |--   Data (Raw='RESencrypt' ((0, 80)))
           |--   Data (Raw='RESidentify' ((0, 88)))
           |--   Data (Raw='CMDidentify' ((0, 88)))
           |--   Data (Raw='CMDencrypt' ((0, 80)))
           |--   Data (Raw='RESbye' ((0, 48)))
           |--   Data (Raw='CMDinfo' ((0, 56)))
           |--   Data (Raw='CMDbye' ((0, 48)))
           |--   Data (Raw='CMDdecrypt' ((0, 80)))
           |--   Data (Raw='RESstats' ((0, 64)))
  |--  Field-sep-23
     |--   Data (ASCII=# ((0, 8)))
  |--  Field-2
     |--   Alt
           |--   Data (Raw='\x04\x00\x00\x00fred' ((0, 64)))
           |--   Data (Raw='\x00\x00\x00\x00\x00\x00\x00\x00' ((0, 64)))
           |--   Data (Raw='\x00\x00\x00\x00\x05\x00\x00\x00stats' ((0, 104)))
           |--   Data (Raw='\n\x00\x00\x00aStrongPwd' ((0, 112)))
           |--   Data (Raw='\x00\x00\x00\x00\x00\x00\x00\x00' ((0, 64)))
           |--   Data (Raw='\x00\x00\x00\x00' ((0, 32)))
           |--   Data (Raw='\x00\x00\x00\x00\x00\x00\x00\x00' ((0, 64)))
           |--   Data (Raw='\x00\x00\x00\x00\x00\x00\x00\x00' ((0, 64)))
           |--   Data (Raw='\x00\x00\x00\x00' ((0, 32)))
           |--   Data (Raw='\x06\x00\x00\x00abcdef' ((0, 80)))
           |--   Data (Raw='\x00\x00\x00\x00\x04\x00\x00\x00info' ((0, 96)))
           |--   Data (Raw='\n\x00\x00\x00123456test' ((0, 112)))
           |--   Data (Raw='\x00\x00\x00\x00\x00\x00\x00\x00' ((0, 64)))
           |--   Data (Raw='\x00\x00\x00\x00\n\x00\x00\x00123456test' ((0, 144)))
           |--   Data (Raw='\x07\x00\x00\x00Roberto' ((0, 88)))
           |--   Data (Raw="\x00\x00\x00\x00\x06\x00\x00\x00$ !&'$" ((0, 112)))
           |--   Data (Raw="\x00\x00\x00\x00\n\x00\x00\x00spqvwt6'16" ((0, 144)))
           |--   Data (Raw="\x06\x00\x00\x00$ !&'$" ((0, 80)))
           |--   Data (Raw='\x00\x00\x00\x00\x05\x00\x00\x00stats' ((0, 104)))
           |--   Data (Raw='\x00\x00\x00\x00' ((0, 32)))
           |--   Data (Raw="\n\x00\x00\x00spqvwt6'16" ((0, 112)))
           |--   Data (Raw='\t\x00\x00\x00myPasswd!' ((0, 104)))
           |--   Data (Raw='\x00\x00\x00\x00' ((0, 32)))
           |--   Data (Raw='\x00\x00\x00\x00\x04\x00\x00\x00info' ((0, 96)))
           |--   Data (Raw='\x00\x00\x00\x00\x06\x00\x00\x00abcdef' ((0, 112)))
           |--   Data (Raw='\x00\x00\x00\x00' ((0, 32)))
           |--   Data (Raw='\x00\x00\x00\x00' ((0, 32)))
           |--   Data (Raw='\x00\x00\x00\x00\x00\x00\x00\x00' ((0, 64)))

Regarding the partitioned messages, this now looks like this::

  <pre><code class="bash">
  'CMDidentify'   | '#' | '\x07\x00\x00\x00Roberto'                 
  'RESidentify'   | '#' | '\x00\x00\x00\x00\x00\x00\x00\x00'        
  'CMDinfo'       | '#' | '\x00\x00\x00\x00'                        
  'RESinfo'       | '#' | '\x00\x00\x00\x00\x04\x00\x00\x00info'    
  'CMDstats'      | '#' | '\x00\x00\x00\x00'                        
  'RESstats'      | '#' | '\x00\x00\x00\x00\x05\x00\x00\x00stats'   
  'CMDauthentify' | '#' | '\n\x00\x00\x00aStrongPwd'                
  'RESauthentify' | '#' | '\x00\x00\x00\x00\x00\x00\x00\x00'        
  'CMDencrypt'    | '#' | '\x06\x00\x00\x00abcdef'                  
  'RESencrypt'    | '#' | "\x00\x00\x00\x00\x06\x00\x00\x00$ !&'$"  
  'CMDdecrypt'    | '#' | "\x06\x00\x00\x00$ !&'$"                  
  'RESdecrypt'    | '#' | '\x00\x00\x00\x00\x06\x00\x00\x00abcdef'  
  'CMDbye'        | '#' | '\x00\x00\x00\x00'                        
  'RESbye'        | '#' | '\x00\x00\x00\x00\x00\x00\x00\x00'        
  'CMDidentify'   | '#' | '\x04\x00\x00\x00fred'                    
  (...)    


Cluster according to a key field
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first field seems interesting, as it contains some kind of commands ('CMDencrypt', 'CMDidentify', etc.). Let's thus cluster the symbol according to the first field::

  symbols = Format.clusterByKeyField(symbol, symbol.fields[0])

  print("[+] Number of symbols after clustering: {0}".format(len(symbols)))
  print("[+] Symbol list:")
  for keyFieldName, s in symbols.items():
      print("  * {0}".format(keyFieldName))

The clustering algorithm produces 14 different symbols, where each symbol has a uniq value in the first field.::

  [+] Number of symbols after clustering: 14
  [+] Symbol list:
    * RESdecrypt
    * RESbye
    * RESidentify
    * CMDbye
    * RESencrypt
    * CMDidentify
    * RESstats
    * CMDencrypt
    * RESauthentify
    * CMDdecrypt
    * CMDinfo
    * CMDauthentify
    * RESinfo
    * CMDstats


Apply a format partitionment with a sequence alignment on the third field of each symbol
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As the last field seems to have a dynamic size, let's have a look at what would provide a sequence alignment (i.e. a means to align static and dynamic sub-fields)::

    for symbol in symbols.values():
        Format.splitAligned(symbol.fields[2], doInternalSlick=True)
        print("[+] Partitionned messages:")
        print(symbol)

For the symbol 'CMDencrypt', the sequence alignment of the last field produces the following format, where we can observe a static field of '\x00\x00\x00' surrounded by two variable fields. The last field seems to be the buffer we want to encrypt, as the key field name suggest (i.e. 'CMDencrypt').::

  (...)
  [+] Partitionned messages:
  'CMDencrypt' | '#' | '\n'   | '\x00\x00\x00' | '123456test'
  'CMDencrypt' | '#' | '\x06' | '\x00\x00\x00' | 'abcdef'   
  (...)


Find field relations in each symbol
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's now find any relationships is those messages::

    for symbol in symbols.values():
        rels = RelationFinder.findOnSymbol(symbol)

        print("[+] Relations found: ")
        for rel in rels:
            print("  " + rel["relation_type"] + ", between '" + rel["x_attribute"] + "' of:")
            print("    " + str('-'.join([f.name for f in rel["x_fields"]])))
            p = [v.getValues()[:] for v in rel["x_fields"]]
            print("    " + str(p))
            print("  " + "and '" + rel["y_attribute"] + "' of:")
            print("    " + str('-'.join([f.name for f in rel["y_fields"]])))
            p = [v.getValues()[:] for v in rel["y_fields"]]
            print("    " + str(p))

In the symbol 'CMDencrypt', we have found a relationship between the content of a field (the third one) and the length of another field (the last one, which presumably contains the buffer we want to encrypt).::

  (...)
  [+] Relations found: 
    SizeRelation, between 'value' of:
      Field
      [['\n', '\x06']]
    and 'size' of:
      Field
      [['123456test', 'abcdef']]
  (...)


Find relations and apply them in the symbol structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We then modify the format message to apply the relationship we have just found, by creating a Size field whose value depends on the content of a targeted field. We also specify a factor that basically says that the value of the size field should be one eighth of the size of the buffer field (as every field size is expressed in bits by default)::

    for symbol in symbols.values():
        rels = RelationFinder.findOnSymbol(symbol)

        for rel in rels:

            # Apply first found relationship
            rel = rels[0]
            rel["x_fields"][0].domain = Size(rel["y_fields"], factor=1/8.0)

        print("[+] Symbol structure:")
        print(symbol._str_debug())

The 'CMDencrypt' symbol structure now looks like this::

  (...)
  [+] Symbol structure:
  Symbol_CMDencrypt
  |--  Field-0
     |--   Data (ASCII=CMDencrypt ((0, 80)))
  |--  Field-sep-23
     |--   Data (ASCII=# ((0, 8)))
  |--  Field-2
     |--   Data (Raw=None ((0, None)))
  |--  |--  Field
          |--   Size(['Field']) - Type:Raw=None ((8, 8))
  |--  |--  Field
          |--   Data (Raw='\x00\x00\x00' ((0, 24)))
  |--  |--  Field
          |--   Data (Raw=None ((0, 80)))
  (...)

That is all for the message format inference. Let's now look at the state machine of this toy protocol.

Generate a chained states automaton
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We will generate a basic automaton that illustrates the sequence of commands and responses extracted from a PCAP file. For each message sent, this will create a new transition to a new state, thus the name of *chained states automaton*::

    # Create a session of messages
    session = Session(messages_session1)

    # Abstract this session according to the inferred symbols
    abstractSession = session.abstract(list(symbols.values()))

    # Generate an automata according to the observed sequence of messages/symbols
    automata = Automata.generateChainedStatesAutomata(abstractSession, list(symbols.values()))

    # Print the dot representation of the automata
    dotcode = automata.generateDotCode()
    print(dotcode)

The obtained automaton is finally converted into Dot code in order to render a graphical version of it.::

  digraph G {
  "Start state" [shape=doubleoctagon, style=filled, fillcolor=white, URL="f8d33b83-d6b0-4180-832c-7cce9d6b3fea"];
  "State 1" [shape=ellipse, style=filled, fillcolor=white, URL="a332ed56-e2d8-4c8c-9ec2-99c5f942e9a3"];
  "State 2" [shape=ellipse, style=filled, fillcolor=white, URL="8f45bd4e-fe03-4a26-bf9a-1adec60f597d"];
  "State 3" [shape=ellipse, style=filled, fillcolor=white, URL="01999e79-de00-467d-987a-e9411d57be99"];
  "State 4" [shape=ellipse, style=filled, fillcolor=white, URL="9b20ed29-77e5-43c1-bb8b-cf3a84674941"];
  "State 5" [shape=ellipse, style=filled, fillcolor=white, URL="52ec3815-656b-421b-bb1f-c4f7746be534"];
  "State 6" [shape=ellipse, style=filled, fillcolor=white, URL="1cbbd123-32d5-4cd8-bd01-4fd3bcd8ae38"];
  "State 7" [shape=ellipse, style=filled, fillcolor=white, URL="8a8ab662-db23-4206-ba35-28396ee31115"];
  "State 8" [shape=ellipse, style=filled, fillcolor=white, URL="ee9e0d5d-bb4e-4d2e-8c97-1553afa1cc68"];
  "End state" [shape=ellipse, style=filled, fillcolor=white, URL="3874e4e9-af5d-428e-92b8-e1fda38b6ef9"];
  "Start state" -> "State 1" [fontsize=5, label="OpenChannelTransition", URL="4beecca4-0d48-4ca9-8d83-ffd8766b64c7"];
  "State 1" -> "State 2" [fontsize=5, label="Transition (Symbol_CMDidentify;{Symbol_RESidentify})", URL="c4e5451c-6a53-41f3-9748-7179774eb7de"];
  "State 2" -> "State 3" [fontsize=5, label="Transition (Symbol_CMDinfo;{Symbol_RESinfo})", URL="c4e5451c-6a53-41f3-9748-7179774eb7de"];
  "State 3" -> "State 4" [fontsize=5, label="Transition (Symbol_CMDstats;{Symbol_RESstats})", URL="c4e5451c-6a53-41f3-9748-7179774eb7de"];
  "State 4" -> "State 5" [fontsize=5, label="Transition (Symbol_CMDauthentify;{Symbol_RESauthentify})", URL="c4e5451c-6a53-41f3-9748-7179774eb7de"];
  "State 5" -> "State 6" [fontsize=5, label="Transition (Symbol_CMDencrypt;{Symbol_RESencrypt})", URL="c4e5451c-6a53-41f3-9748-7179774eb7de"];
  "State 6" -> "State 7" [fontsize=5, label="Transition (Symbol_CMDdecrypt;{Symbol_RESdecrypt})", URL="c4e5451c-6a53-41f3-9748-7179774eb7de"];
  "State 7" -> "State 8" [fontsize=5, label="Transition (Symbol_CMDbye;{Symbol_RESbye})", URL="c4e5451c-6a53-41f3-9748-7179774eb7de"];
  "State 8" -> "End state" [fontsize=5, label="CloseChannelTransition", URL="c6ac87b7-5de1-401a-8b75-5d2a73d81264"];
  }


.. figure:: https://dev.netzob.org/attachments/download/172/automata_target_v1_chained.svg
   :align: center
   :target: https://dev.netzob.org/attachments/download/172/automata_target_v1_chained.svg
   :alt: 


Generate a one state automaton
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This time, instead of converting a PCAP into a sequence of states for each message observed, we generate a uniq state that accept any of the observed sent messages to trigger a new transition. In response to each sent message (for example 'CMDencrypt'), we expect a specific response (for example 'REDencrypt')::

    # Create a session of messages
    session = Session(messages_session1)

    # Abstract this session according to the inferred symbols
    abstractSession = session.abstract(list(symbols.values()))

    # Generate an automata according to the observed sequence of messages/symbols
    automata = Automata.generateOneStateAutomata(abstractSession, list(symbols.values()))

    # Print the dot representation of the automata
    dotcode = automata.generateDotCode()
    print(dotcode)

The obtained automaton is finally converted into Dot code in order to render a graphical version of it.::

  digraph G {
  "Start state" [shape=doubleoctagon, style=filled, fillcolor=white, URL="0659071e-1849-4616-a11a-e98edfe86e24"];
  "Main state" [shape=ellipse, style=filled, fillcolor=white, URL="424e0a69-da0b-4030-816a-8368e30a00a9"];
  "End state" [shape=ellipse, style=filled, fillcolor=white, URL="9de3d54b-f0eb-45f8-809a-86a60d22812f"];
  "Start state" -> "Main state" [fontsize=5, label="OpenChannelTransition", URL="3818118b-97db-474f-b9c3-f38c04152a74"];
  "Main state" -> "Main state" [fontsize=5, label="Transition (Symbol_CMDidentify;{Symbol_RESidentify})", URL="f6000e04-10a8-41de-a1a0-29021440684a"];
  "Main state" -> "Main state" [fontsize=5, label="Transition (Symbol_CMDinfo;{Symbol_RESinfo})", URL="f6000e04-10a8-41de-a1a0-29021440684a"];
  "Main state" -> "Main state" [fontsize=5, label="Transition (Symbol_CMDstats;{Symbol_RESstats})", URL="f6000e04-10a8-41de-a1a0-29021440684a"];
  "Main state" -> "Main state" [fontsize=5, label="Transition (Symbol_CMDauthentify;{Symbol_RESauthentify})", URL="f6000e04-10a8-41de-a1a0-29021440684a"];
  "Main state" -> "Main state" [fontsize=5, label="Transition (Symbol_CMDencrypt;{Symbol_RESencrypt})", URL="f6000e04-10a8-41de-a1a0-29021440684a"];
  "Main state" -> "Main state" [fontsize=5, label="Transition (Symbol_CMDdecrypt;{Symbol_RESdecrypt})", URL="f6000e04-10a8-41de-a1a0-29021440684a"];
  "Main state" -> "Main state" [fontsize=5, label="Transition (Symbol_CMDbye;{Symbol_RESbye})", URL="f6000e04-10a8-41de-a1a0-29021440684a"];
  "Main state" -> "End state" [fontsize=5, label="CloseChannelTransition", URL="75a4cc3a-72a4-42a3-af2c-aa3939f899aa"];
  }

.. figure:: https://dev.netzob.org/attachments/download/173/automata_target_v1_onestate.svg
   :align: center
   :target: https://dev.netzob.org/attachments/download/173/automata_target_v1_onestate.svg
   :alt: 


Generate a PTA-based automaton
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Finally, we convert multiple sequences of messages taken form different PCAP files to generate an automaton for which we have merge identical paths. The underlying merging strategy is called a Prefix-Tree Acceptor::

    # Create sessions of messages
    messages_session1 = PCAPImporter.readFile("target_src_v1_session1.pcap").values()
    messages_session3 = PCAPImporter.readFile("target_src_v1_session3.pcap").values()

    session1 = Session(messages_session1)
    session3 = Session(messages_session3)

    # Abstract this session according to the inferred symbols
    abstractSession1 = session1.abstract(list(symbols.values()))
    abstractSession3 = session3.abstract(list(symbols.values()))

    # Generate an automata according to the observed sequence of messages/symbols
    automata = Automata.generatePTAAutomata([abstractSession1, abstractSession3], list(symbols.values()))

    # Print the dot representation of the automata
    dotcode = automata.generateDotCode()
    print(dotcode)

The obtained automaton is finally converted into Dot code in order to render a graphical version of it.::

  digraph G {
  "Start state" [shape=doubleoctagon, style=filled, fillcolor=white, URL="e46d8a67-2a96-479a-9234-c1b38c75b847"];
  "State 0" [shape=ellipse, style=filled, fillcolor=white, URL="0cd8a2c9-4410-45a0-9950-6456546f49dc"];
  "State 1" [shape=ellipse, style=filled, fillcolor=white, URL="bbc10d50-f197-40f6-a674-5f80790ef954"];
  "State 2" [shape=ellipse, style=filled, fillcolor=white, URL="739801b7-9e0d-4fba-a4f5-cf130e6b7fbf"];
  "State 3" [shape=ellipse, style=filled, fillcolor=white, URL="c2075b80-16b9-4bd7-b290-6eb333f94e43"];
  "State 4" [shape=ellipse, style=filled, fillcolor=white, URL="715ede75-d81e-46ea-a7c1-f537e5dba892"];
  "State 9" [shape=ellipse, style=filled, fillcolor=white, URL="ad5873af-c26a-482f-94d9-0cf47c69376b"];
  "State 10" [shape=ellipse, style=filled, fillcolor=white, URL="01859f7d-6b43-45af-8c17-9decb10dea9b"];
  "End state 11" [shape=ellipse, style=filled, fillcolor=white, URL="7f4bd693-a35f-479b-8e86-128dc46c71cf"];
  "State 5" [shape=ellipse, style=filled, fillcolor=white, URL="ee9da65c-b072-4344-bf71-2d67a3b73880"];
  "State 6" [shape=ellipse, style=filled, fillcolor=white, URL="902e76e4-6a9a-45a2-95ba-ae9484f1084f"];
  "State 7" [shape=ellipse, style=filled, fillcolor=white, URL="f7e9b27a-6879-4b4f-bb51-00530f07addf"];
  "End state 8" [shape=ellipse, style=filled, fillcolor=white, URL="fe710eed-287f-4abf-93bf-6878e487d8a9"];
  "Start state" -> "State 0" [fontsize=5, label="OpenChannelTransition", URL="5d6139d0-9b1c-49b2-b19d-91ae8c56f299"];
  "State 0" -> "State 1" [fontsize=5, label="Transition (Symbol_CMDidentify;{Symbol_RESidentify})", URL="a1d2d03d-8c58-4c83-afa1-c40433fbd833"];
  "State 1" -> "State 2" [fontsize=5, label="Transition (Symbol_CMDinfo;{Symbol_RESinfo})", URL="a1d2d03d-8c58-4c83-afa1-c40433fbd833"];
  "State 2" -> "State 3" [fontsize=5, label="Transition (Symbol_CMDstats;{Symbol_RESstats})", URL="a1d2d03d-8c58-4c83-afa1-c40433fbd833"];
  "State 3" -> "State 4" [fontsize=5, label="Transition (Symbol_CMDauthentify;{Symbol_RESauthentify})", URL="a1d2d03d-8c58-4c83-afa1-c40433fbd833"];
  "State 4" -> "State 5" [fontsize=5, label="Transition (Symbol_CMDencrypt;{Symbol_RESencrypt})", URL="a1d2d03d-8c58-4c83-afa1-c40433fbd833"];
  "State 4" -> "State 9" [fontsize=5, label="Transition (Symbol_CMDdecrypt;{Symbol_RESdecrypt})", URL="a1d2d03d-8c58-4c83-afa1-c40433fbd833"];
  "State 9" -> "State 10" [fontsize=5, label="Transition (Symbol_CMDbye;{Symbol_RESbye})", URL="a1d2d03d-8c58-4c83-afa1-c40433fbd833"];
  "State 10" -> "End state 11" [fontsize=5, label="CloseChannelTransition", URL="f7ddbccf-93b6-4496-a153-5b2306d95dac"];
  "State 5" -> "State 6" [fontsize=5, label="Transition (Symbol_CMDdecrypt;{Symbol_RESdecrypt})", URL="a1d2d03d-8c58-4c83-afa1-c40433fbd833"];
  "State 6" -> "State 7" [fontsize=5, label="Transition (Symbol_CMDbye;{Symbol_RESbye})", URL="a1d2d03d-8c58-4c83-afa1-c40433fbd833"];
  "State 7" -> "End state 8" [fontsize=5, label="CloseChannelTransition", URL="f7ddbccf-93b6-4496-a153-5b2306d95dac"];
  }


.. figure:: https://dev.netzob.org/attachments/download/174/automata_target_v1_pta.svg
   :align: center
   :target: https://dev.netzob.org/attachments/download/174/automata_target_v1_pta.svg
   :alt: 


Generate messages according to the inferred model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We now have a pretty good knowledge of the format messsage and grammar of the targeted protocol. Let's thus play with this model, by trying to communicate with a real server implementation.

At first, let's start the server in order to discus with it.::

  $ cd src_v1/
  $ ./server

  Ready to read incoming messages

  (...)

Then, we create a UDP client that will communicate with the server (on 127.0.0.1:4242) by exchanging messages generated from the infered symbols::

    # Create a UDP client instance
    channelOut = UDPClient(remoteIP="127.0.0.1", remotePort=4242)
    abstractionLayerOut = AbstractionLayer(channelOut, list(symbols.values()))
    abstractionLayerOut.openChannel()

    # Visit the automata for n iteration
    state = automata.initialState
    for n in range(8):
        state = state.executeAsInitiator(abstractionLayerOut)

We go through 8 iterations in the automaton.::

  1454: [INFO] AbstractionLayer:openChannel: Going to open the communication channel...
  1454: [INFO] AbstractionLayer:openChannel: Communication channel opened.
  1454: [INFO] State:executeAsInitiator: Next transition: Open.
  1454: [INFO] AbstractionLayer:openChannel: Going to open the communication channel...
  1454: [INFO] AbstractionLayer:openChannel: Communication channel opened.
  1454: [INFO] State:executeAsInitiator: Transition 'Open' leads to state: State 1.
  1455: [INFO] State:executeAsInitiator: Next transition: Transition.
  1455: [INFO] AbstractionLayer:writeSymbol: Going to specialize symbol: 'Symbol_CMDidentify' (id=dbea29b9-7e9f-4c2b-be14-625f675569f3).
  1455: [INFO] AbstractionLayer:writeSymbol: Data generated from symbol 'Symbol_CMDidentify': 'CMDidentify#\x03\x00\x00\x00\xfc{\xdb'.
  1456: [INFO] AbstractionLayer:writeSymbol: Going to write to communication channel...
  1456: [INFO] AbstractionLayer:writeSymbol: Writing to commnunication channel donne..
  1456: [INFO] AbstractionLayer:readSymbol: Going to read from communication channel...
  1456: [INFO] AbstractionLayer:readSymbol: Received data: ''RESidentify#\x00\x00\x00\x00\x00\x00\x00\x00''
  1457: [INFO] AbstractionLayer:readSymbol: Received symbol on communication channel: 'Symbol_RESidentify'
  1457: [INFO] Transition:executeAsInitiator: Possible output symbol: 'Symbol_RESidentify' (id=49c24e1c-3751-412e-9f6a-f006a7de7492).
  1457: [INFO] State:executeAsInitiator: Transition 'Transition' leads to state: State 2.
  1457: [INFO] State:executeAsInitiator: Next transition: Transition.
  1457: [INFO] AbstractionLayer:writeSymbol: Going to specialize symbol: 'Symbol_CMDinfo' (id=5eb47a57-eccf-4d06-8231-0b1ae87f96a7).
  1458: [INFO] AbstractionLayer:writeSymbol: Data generated from symbol 'Symbol_CMDinfo': 'CMDinfo#\x00\x00\x00\x00'.
  1458: [INFO] AbstractionLayer:writeSymbol: Going to write to communication channel...
  1458: [INFO] AbstractionLayer:writeSymbol: Writing to commnunication channel donne..
  1458: [INFO] AbstractionLayer:readSymbol: Going to read from communication channel...
  1458: [INFO] AbstractionLayer:readSymbol: Received data: ''RESinfo#\x00\x00\x00\x00\x04\x00\x00\x00info''
  1462: [INFO] AbstractionLayer:readSymbol: Received symbol on communication channel: 'Symbol_RESinfo'
  1462: [INFO] Transition:executeAsInitiator: Possible output symbol: 'Symbol_RESinfo' (id=b41502e3-21ea-4cb9-9c1e-dc171f715685).
  1462: [INFO] State:executeAsInitiator: Transition 'Transition' leads to state: State 3.
  1462: [INFO] State:executeAsInitiator: Next transition: Transition.
  (...)

Regarding the real server, we can see that received messages are well formated, as the server is able to parse them and send correct responses.::

  $ ./server 

  Ready to read incoming messages
  -> Read: CMDidentify#.
     Command: CMDidentify
     Arg size: 2
     Arg content: ..
  <- Send: 
     Return value: 0
     Size of data buffer: 0
     Data buffer: 
	  ""

  -> Read: CMDinfo#
     Command: CMDinfo
     Arg size: 0
  <- Send: 
     Return value: 0
     Size of data buffer: 4
     Data buffer: 
     DATA: 69 6e 66 6f                                     	"info"

  -> Read: CMDstats#
     Command: CMDstats
     Arg size: 0
  <- Send: 
     Return value: 0
     Size of data buffer: 5
     Data buffer: 
     DATA: 73 74 61 74 73                                  	"stats"

  -> Read: CMDauthentify#.
     Command: CMDauthentify
     Arg size: 6
     Arg content: ......
  <- Send: 
     Return value: 0
     Size of data buffer: 0
     Data buffer: 
  	""

  -> Read: CMDencrypt#.
     Command: CMDencrypt
     Arg size: 2
     Arg content: ..
  <- Send: 
  (...)



Do some fuzzing on a specific symbol
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Finally, we voluntarily twist the format message of the 'CMDencrypt' symbol, in order to try some fuzzing. The format modification corresponds to an extention of the size of the buffer field (i.e. the one which receives the data to encrypt)::

    def send_and_receive_symbol(symbol):
        data = symbol.specialize()
	print("[+] Sending: {0}".format(repr(data)))
	channelOut.write(data)
	data = channelOut.read()
	print("[+] Receiving: {0}".format(repr(data)))

    # Update symbol definition to allow a broader payload size
    symbols["CMDencrypt"].fields[2].fields[2].domain = Raw(nbBytes=(10, 120))

    for i in range(10):
        send_and_receive_symbol(symbols["CMDencrypt"])

We can see that Netzob is only sending CMDencrypt messages with a potentially long last field::

  [+] Sending: 'CMDencrypt#6\x00\x00\x00&\xe0*\xb3\xa8A(\x0b\xd2yA\xb5\xb8\rw\x0fGi\xee\xb3\xd6\xb0<\xfc\xc0\xa7m\xbd\xbc\xde2~\xceE\xe5\xda@\xd4\xed\xed\xf2\xb4\xe7\t\xfbC\xbf\x05\xc6\xce\xfb\x83\xf2\x00'
  (...)

In the server part, we quickly get a segmentation fault, due to a bug in the parsing of the last field.::

  $ gdb ./server
  (gdb) run
  Starting program: /home/fgy/travaux/netzob/git/netzob-resources/experimentations/tutorial_target/src_v1/server 

  Ready to read incoming messages
  (...)
  -> Read: CMDencrypt#6
     Command: CMDencrypt
     Arg size: 54
     Arg content: &?*??A(
  wGi???<???m???2~?E??@????????    ?C??

  Program received signal SIGSEGV, Segmentation fault.
  0x08048bc0 in api_encrypt (in=0x45ce7e32 <Address 0x45ce7e32 out of bounds>, len=3561020133, out=0xb4f2eded <Address 0xb4f2eded out of bounds>) at amo_api.c:80
   80	      tmpData[i] = (in[i] ^ key) % 0xff;

That's all folks for this introduction tutorial. You can get the entire `source code <https://dev.netzob.org/attachments/download/183/inference_target_src_v1.py>`_ of the script used to infer and play with the protocol:

We invite you to read the API documentation or talk with us on IRC (#netzob on Freenode) if you have any question.
