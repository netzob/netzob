.. currentmodule:: netzob

.. _tutorial_peach:

Auto generation of Peach pit files/fuzzers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Principle
^^^^^^^^^

`Peach <http://peachfuzzer.com>`_ is an open-source framework of
fuzzing. It provides API to create smart fuzzers adapted to the tester's
needs through XML configuration files called `*Peach pit
files* <http://peachfuzzer.com/PeachPit>`_.
Making such files needs knowledge of the format message and state
machine of the targeted protocol as well as the actor Peach has to fuzz.

Fortunately, Netzob provides means for reverse engineering of undocumented and
proprietary protocols from provided traces in a semi-automatic way.
Netzob provides an exporter plugin for Peach that can transform
the inferred data model and state machine of a targeted protocol into a
Peach pit file automatically.

This tutorial shows how to take advantage of the Peach exporter plugin
provided in Netzob to automatically construct Peach pit configuration
files.

Prerequisite
^^^^^^^^^^^^

You need Netzob in version 0.4.1 or above.

This tutorial assumes that the user have previously followed the
`Getting started with
Netzob <http://www.netzob.org/resources/tutorial_get_started>`_ tutorial
and have a complete Netzob project (or at least some format messages).
The protocol implementation contains several vulnerabilities that should
be detected during fuzzing.

Moreover it assumes that the user has Peach 2.3.8 installed.

Export
^^^^^^

To export the project go in ``File`` > ``Export the project`` >
``Peach pit file``. The window below should appears :

.. figure:: https://dev.netzob.org/attachments/download/134
   :align: center
   :alt: 

The window is composed of three panels. The left one lists all fuzzer
available. They differ on the state representation. There are three
kinds of fuzzer available:

-  "Randomized state order fuzzer": one state is created for each
   symbols of Netzob and at each step, the fuzzer changes of state for a
   randomly chosen one.
-  "Randomized transitions stateful fuzzer": one state is created for
   each symbols of Netzob and the transitions between these states are
   based on those Netzob allows, weight by their probability.
-  "One-state fuzzer": one state is created corresponding to the chosen
   symbol.

When the fuzzer is on a particular state, it sends fuzzed data that
corresponds to the associated symbol to the target. Choose one of them.

The right panel shows the fuzzer. It gives the user a small idea of what
he is doing and what changes between two configurations.

The bottom panel has two options:

-  The first options ``Fuzzing based on`` tells on which Netzob data
   model the fuzzing is based:

   -  "Variable": use the Netzob variables to make Peach data models. It
      makes more fuzzy but less smart fuzzer.
   -  "Regex": use the Netzob Regex (which are displayed on the top of
      the symbol visualization), it is the simplest solution.

-  The second options ``Mutate static fields`` tells if the static
   fields in the Netzob data model are fuzzed or not.

The ``Export`` button exports the fuzzer into a user defined file.

Use this fuzzer into Peach\ `¶ <#Use-this-fuzzer-into-Peach>`_

Export this fuzzer directly through the ``Export`` button to a file
named "test.xml" into the directory of Peach. It should create a
PeachzobAddons.py file, which is essential for Peach to leverage Netzob
capabilities as "fixup".

The "test.xml" file should look like this. Look closely to the few XML
comments.

::

    <?xml version="1.0" encoding="utf-8"?>
    <Peach xmlns="http://phed.org/2008/Peach" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://phed.org/2008/Peach /peach/peach.xsd">
      <Include ns="default" src="file:defaults.xml"/>
      <Import import="PeachzobAddons"/>

      <DataModel name="dataModel 1">
        <Blob name="Field 0_0" valueType="hex" value="6170695f"/>
        <Blob name="Field 1_0" valueType="hex">
          <Fixup class="PeachzobAddons.Or">
            <Param name="values" value="Blob,696e666f; Blob,7374617473"/>
          </Fixup>

        </Blob>
        <Blob name="Field 2_0" valueType="hex" value="2300000000000000000000000000000000000000000000"/>
        <Blob name="Field 3_0" valueType="hex" value="00"/>
      </DataModel>
      <DataModel name="dataModel 2">
        <Blob name="Field 0_0" valueType="hex" value="6170695f62796523000000000000000000000000000000000000000000000000"/>

      </DataModel>
      <DataModel name="dataModel 3">
        <Blob name="Field 0_0" valueType="hex" value="6170695f6964656e746966792366726564000000000000000000000000000000"/>
      </DataModel>
      <DataModel name="dataModel 4">
        <Blob name="Field 0_0" valueType="hex" value="6170695f61757468656e74696679236d79506173737764210000000000000000"/>

      </DataModel>
      <DataModel name="dataModel 5">
        <Blob name="Field 0_0" valueType="hex" value="6170695f656e6372797074233132333435367465737400000000000000000000"/>
      </DataModel>
      <DataModel name="dataModel 6">
        <Blob name="Field 0_0" valueType="hex" value="6170695f64656372797074237370717677743627313600000000000000000000"/>

      </DataModel>
      <DataModel name="dataModel 7">
        <Blob name="Default-1_0" valueType="hex" value="00000000"/>
        <Blob name="Default-2-1_0" valueType="hex" value="23"/>
        <Blob name="Default-2-2-1-1_0" valueType="hex">
          <Fixup class="PeachzobAddons.Or">

            <Param name="values" value="Blob,00000000000000; Blob,00000004000000; Blob,00000005000000; Blob,0000000a000000; Blob,64000000000000; Blob,8b04080a000000"/>
          </Fixup>
        </Blob>
        <Blob name="Default-2-2-1-2_0" valueType="hex">
          <Fixup class="PeachzobAddons.Or">
            <Param name="values" value="Blob,00000000000000000000; Blob,31323334353674657374; Blob,696e666f000000000000; Blob,73707176777436273136; Blob,73746174730000000000"/>

          </Fixup>
        </Blob>
        <Blob name="Default-2-2-2_0" valueType="hex" value="00000000000000000000"/>
      </DataModel>
      <DataModel name="dataModel 9">
        <Blob name="Field 0">

          <Fixup class="PeachzobAddons.RandomField">
            <Param name="minlen" value="0"/>
            <Param name="maxlen" value="1024"/>
            <Param name="type" value="Blob"/>
          </Fixup>
        </Blob>

      </DataModel>
      <StateModel initialState="state 0" name="stateModel">
        <State name="state 0">
          <Action ref="state 1" type="changeState" when="random.randint(1,8)==1"/>
          <Action ref="state 2" type="changeState" when="random.randint(1,7)==1"/>
          <Action ref="state 3" type="changeState" when="random.randint(1,6)==1"/>

          <Action ref="state 4" type="changeState" when="random.randint(1,5)==1"/>
          <Action ref="state 5" type="changeState" when="random.randint(1,4)==1"/>
          <Action ref="state 6" type="changeState" when="random.randint(1,3)==1"/>
          <Action ref="state 7" type="changeState" when="random.randint(1,2)==1"/>
          <Action ref="state 9" type="changeState"/>
        </State>

        <State name="state 1">
          <Action type="output">
            <DataModel ref="dataModel 1"/>
            <Data name="data"/>
          </Action>
        </State>

        <State name="state 2">
          <Action type="output">
            <DataModel ref="dataModel 2"/>
            <Data name="data"/>
          </Action>
        </State>

        <State name="state 3">
          <Action type="output">
            <DataModel ref="dataModel 3"/>
            <Data name="data"/>
          </Action>
        </State>

        <State name="state 4">
          <Action type="output">
            <DataModel ref="dataModel 4"/>
            <Data name="data"/>
          </Action>
        </State>

        <State name="state 5">
          <Action type="output">
            <DataModel ref="dataModel 5"/>
            <Data name="data"/>
          </Action>
        </State>

        <State name="state 6">
          <Action type="output">
            <DataModel ref="dataModel 6"/>
            <Data name="data"/>
          </Action>
        </State>

        <State name="state 7">
          <Action type="output">
            <DataModel ref="dataModel 7"/>
            <Data name="data"/>
          </Action>
        </State>

        <State name="state 9">
          <Action type="output">
            <DataModel ref="dataModel 9"/>
            <Data name="data"/>
          </Action>
        </State>

      </StateModel>
      <Agent name="DefaultAgent">
        <!--Todo: Configure the Agents.-->
      </Agent>
      <Test name="DefaultTest">
        <!--Todo: Enable Agent <Agent ref="TheAgent"/> -->

        <StateModel ref="stateModel"/>
        <Publisher class="udp.Udp">
          <Param name="host" value="127.0.0.1"/>
          <Param name="port" value="4242"/>
        </Publisher>
        <Publisher class="udp.Udp">

          <Param name="host" value="127.0.0.1"/>
          <Param name="port" value="10000"/>
        </Publisher>
        <!--The Netzob project has several simulator actors, so this file have several publishers. Choose one of them and remove the others.-->
      </Test>
      <Run name="DefaultRun">

        <!--Todo: Configure the run.-->
        <Logger class="logger.Filesystem">
          <Param name="path" value="logs"/>
        </Logger>
        <Test ref="DefaultTest"/>
      </Run>

    </Peach>

This tutorial will not talk about Peach agents but configuring one of
them could be useful. In the Test block, there is as many publishers as
the Netzob simulator has actors. One publisher is needed, remove the
others. If there is no publishers, create one according to the model
above. On this example, the tester remove the second publisher.

Launch the fuzzing
^^^^^^^^^^^^^^^^^^

You first have to start the targeted server:

::

    ./server

Assuming that the user exports the "test.xml" file into the Peach
directory, you can now start the fuzzer:

::

    python peach.py test.xml

After few seconds, you should trigger a segfault or a stack smashing
detection.

::

    -> Read: api_identify#fred
       Command: api_identify
       Arg: fred
    <- Send: 
       Return value: 0
       Size of data buffer: 13
       Data buffer: 
       DATA: 72 65 73 70 5f 69 64 65 6e 74 69 66 79              "resp_identify" 

    -> Read: api_identify#f

       Command: api_identify
       Arg: f

    *** stack smashing detected ***: ./server terminated
    ======= Backtrace: =========
    /lib/i386-linux-gnu/libc.so.6(__fortify_fail+0x45)[0xcec045]
    /lib/i386-linux-gnu/libc.so.6(+0x103ffa)[0xcebffa]
    ./server[0x8048a3c]
    ./server[0x8048eb4]
    ./server[0x8048985]
    /lib/i386-linux-gnu/libc.so.6(__libc_start_main+0xf3)[0xc014d3]
    ./server[0x8048831]
    ======= Memory map: ========
    00289000-0028a000 r-xp 00000000 00:00 0          [vdso]
    002fb000-00317000 r-xp 00000000 08:03 2605207    /lib/i386-linux-gnu/libgcc_s.so.1
    00317000-00318000 r--p 0001b000 08:03 2605207    /lib/i386-linux-gnu/libgcc_s.so.1
    00318000-00319000 rw-p 0001c000 08:03 2605207    /lib/i386-linux-gnu/libgcc_s.so.1
    00bb4000-00bd4000 r-xp 00000000 08:03 673152     /lib/i386-linux-gnu/ld-2.15.so
    00bd4000-00bd5000 r--p 0001f000 08:03 673152     /lib/i386-linux-gnu/ld-2.15.so
    00bd5000-00bd6000 rw-p 00020000 08:03 673152     /lib/i386-linux-gnu/ld-2.15.so
    00be8000-00d8b000 r-xp 00000000 08:03 672879     /lib/i386-linux-gnu/libc-2.15.so
    00d8b000-00d8c000 ---p 001a3000 08:03 672879     /lib/i386-linux-gnu/libc-2.15.so
    00d8c000-00d8e000 r--p 001a3000 08:03 672879     /lib/i386-linux-gnu/libc-2.15.so
    00d8e000-00d8f000 rw-p 001a5000 08:03 672879     /lib/i386-linux-gnu/libc-2.15.so
    00d8f000-00d92000 rw-p 00000000 00:00 0 
    08048000-0804a000 r-xp 00000000 08:03 6488874    /home/sygus/travaux/netzob/target_protocol/server
    0804a000-0804b000 r--p 00001000 08:03 6488874    /home/sygus/travaux/netzob/target_protocol/server
    0804b000-0804c000 rw-p 00002000 08:03 6488874    /home/sygus/travaux/netzob/target_protocol/server
    09e0d000-09e2e000 rw-p 00000000 00:00 0          [heap]
    b778b000-b778c000 rw-p 00000000 00:00 0 
    b77a8000-b77ac000 rw-p 00000000 00:00 0 
    bf90f000-bf930000 rw-p 00000000 00:00 0          [stack]
    Abandon (core dumped)
