### Dependencies ###

* tcpdump
* python
* python-ptrace
* python-nfqueue
* strace
* lsof
* iptables

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
