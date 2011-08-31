### Dependencies ###

* tcpdump
* python
* python-ptrace
* python-nfqueue
* python-hachoir
* python-matplotlib
* strace
* lsof
* iptables
* python-matplotlib

for documentation purposes :
* python-sphinx

### Installation ###

$ cd lib/libNeedleman/
$ gcc -fPIC -O3 -fopenmp -shared -I/usr/include/python2.6 -lpython2.6 -o libNeedleman.so NeedlemanWunsch.c

## Requirements for Network and PCAP input ##

Dependencies : tcpdump
Configuration : 

$ sudo setcap cap_net_raw=ep /usr/bin/python2.6
$ sudo setcap cap_net_raw=ep /usr/sbin/tcpdump

## Requirements for IPC input on Ubuntu ##

sudo bash -c "echo 0 > /proc/sys/kernel/yama/ptrace_scope"

### Running Netzob ###

$ ./run_netzob

### Generates documentation ###

The folder "doc/documentation" contains the documentation of Netzob in sphynx format (.rst).
Therefore, if you want to have updated HTMLs in the "/doc/documentation/build/" directory
based on the sources of the documentation which is located in "/doc/documentation/source/" you'll
have to execute the following command :

sphinx-build -b html doc/documentation/source/ doc/documentation/build/
