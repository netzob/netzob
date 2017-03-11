from debian:latest
run yes y | apt-get update && yes y | apt-get upgrade
run yes y | apt-get install python python-dev 
run yes y | apt-get install python-pip python-setuptools 
run yes y | apt-get install python-babel python-sphinx
run yes y | apt-get install python-numpy python-pcapy 
run yes y | apt-get install gcc make
run yes y | apt-get install git
run yes y | apt-get install ipython
workdir root
run git clone https://dev.netzob.org/git/netzob -b next
workdir netzob
run python setup.py build
run python setup.py develop
run python setup.py install
workdir /root
run mkdir -p /root/.ipython/profile_default/startup/
run echo "from netzob.all import *" > /root/.ipython/profile_default/startup/00_netzob.py
cmd /usr/bin/ipython
