Netzob : inferring communication protocols

### Presentation ###

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

### Installation ###

Netzob currently supports Linux platforms.

Dependencies :

* tcpdump
* python
* python-ptrace
* nfqueue-bindings-python
* python-hachoir
* python-matplotlib
* python-dpkt
* python-pcapy
* strace
* lsof
* iptables
* python-bitarray
* python-pyasn1

or, on Debian-like operating systems :

$ sudo apt-get install tcpdump python python-ptrace nfqueue-bindings-python python-hachoir-subfile python-matplotlib python-dpkt strace lsof iptables python-pcapy python-bitarray python-pyasn1

And then, 

$ python setup.py build

### Usage ###

Just run the following command to launch the graphical interface

$ ./netzob

### Documentation ###

Dependency for documentation building :

* python-sphinx

## Requirements for Network and PCAP input ##

Dependencies : tcpdump
Configuration : 

$ sudo setcap cap_net_raw=ep /usr/bin/python2.6
$ sudo setcap cap_net_raw=ep /usr/sbin/tcpdump

## Requirements for IPC input on Ubuntu ##

sudo bash -c "echo 0 > /proc/sys/kernel/yama/ptrace_scope"

### Generates documentation ###

The folder "doc/documentation" contains the documentation of Netzob in sphynx format (.rst).
Therefore, if you want to have updated HTMLs in the "/doc/documentation/build/" directory
based on the sources of the documentation which is located in "/doc/documentation/source/" you'll
have to execute the following command :

sphinx-build -b html doc/documentation/source/ doc/documentation/build/
