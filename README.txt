[******************************************************************************]
[**********]                                                       [***********]
[**********]       Netzob : inferring communication protocols      [***********]
[**********]                                                       [***********]
[******************************************************************************]


[******************************************************************************]
[***********************]       1. Presentation      [*************************]
[******************************************************************************]

Netzob simplifies the work for security auditors by providing a
complete framework for the reverse engineering of communication
protocols.

It handles different types of protocols : text protocols (like HTTP
and IRC), fixed fields protocols (like IP and TCP) and variable fields
protocols (like ASN.1 based formats).  Netzob is therefore suitable
for reversing network protocols, structured files and system and
process flows (IPC and communication with drivers). Netzob is provided
with modules dedicated to capture data in multiple contexts (network,
file, process and kernel data acquisition).


[******************************************************************************]
[***********************]       2. Installation      [*************************]
[******************************************************************************]

Netzob currently supports Linux x86 and x64 platforms. A Windows
version is expected soon.

Dependencies :

* python
* python-ptrace
* python-matplotlib
* python-pcapy
* python-bitarray
* python-lxml
* python-dev
* libjs-sphinxdoc
* python-sphinx
* python-setuptools
* graphviz

Linux-specific dependencies :

* strace
* lsof

Or, on Debian-like operating systems :

$ sudo apt-get install python python-ptrace python-matplotlib strace lsof \
  python-pcapy python-bitarray python-dev python-lxml libjs-sphinxdoc     \
  python-sphinx python-setuptools graphviz

And then, 

$ python setup.py build


[******************************************************************************]
[***********************]           3. Usage         [*************************]
[******************************************************************************]

Just run the following command to launch the graphical interface

$ ./netzob


[******************************************************************************]
[***********************]       4. Documentation     [*************************]
[******************************************************************************]

Documentation generation :

The folder "doc/documentation" contains the documentation of Netzob in sphynx
format (.rst). Therefore, if you want to have updated HTMLs in the
"/doc/documentation/build/" directory based on the sources of the documentation
which is located in "/doc/documentation/source/" you'll have to execute the
following command :

$ sphinx-build -b html doc/documentation/source/ doc/documentation/build/


[******************************************************************************]
[***********************]       5. Miscellaneous     [*************************]
[******************************************************************************]

** Requirements for Network and PCAP input **

Configuration : 

$ sudo setcap cap_net_raw=ep /usr/bin/python2.XX

** Requirements for IPC input on Ubuntu **

$ sudo bash -c "echo 0 > /proc/sys/kernel/yama/ptrace_scope"


[******************************************************************************]
[***********************]          6. Contact        [*************************]
[******************************************************************************]

* Website : http://www.netzob.org
* Email : contact@netzob.org
* Mailing lists : https://lists.netzob.org/wws/
* Developer's room : https://dev.netzob.org
* IRC : #netzob on Freenode

Authors:
* Georges Bossert
* Frédéric Guihéry

Sponsors:
* Amossys : http://www.amossys.fr
* Supélec : http://www.rennes.supelec.fr/ren/rd/cidre/
