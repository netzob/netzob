from debian:latest
run yes y | apt-get update && yes y | apt-get upgrade
run yes y | apt-get install python python-dev python-impacket
run yes y | apt-get install libxml2-dev libxslt-dev
run yes y | apt-get install python-setuptools python-gi
run yes y | apt-get install gir1.2-gtk-3.0 gir1.2-glib-2.0 gir1.2-gdkpixbuf-2.0 gir1.2-pango-1.0
run yes y | apt-get install libgtk-3-0 graphviz
run yes y | apt-get install python-babel python-sphinx
run yes y | apt-get install python-numpy
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
