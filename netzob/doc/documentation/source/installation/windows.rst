.. currentmodule:: netzob

.. _installation_windows:

Installation documentation on Windows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This documentation only applies for Netzob 0.3.3.

Installation of dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Steps:

#. Install Python 2.7 (download the installer from
   `python.org <http://www.python.org/ftp/python/2.7.3/python-2.7.3.msi>`_)
#. Install SetupTools (download the installer from
   `pypi.python.org <http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11.win32-py2.7.exe#md5=57e1e64f6b7c7f1d2eddfc9746bbaf20>`_)
#. Install PyGTK (download the installer from
   `gnome.org <http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/pygtk-all-in-one-2.24.2.win32-py2.7.msi>`_)
#. Install WinPCap 4.1.2 (download the installer from
   `winpcap.org <http://www.winpcap.org/install/bin/WinPcap_4_1_2.exe>`_)
#. Install Pcapy 0.10.5 (provided on `Netzob's
   website <http://www.netzob.org/repository/0.3.3/windows-dep/pcapy-0.10.5.win32-py2.7.exe>`_
   ; original source:
   `oss.coresecurity.com <http://oss.coresecurity.com/repo/pcapy-0.10.5.tar.gz>`_)
#. Install following dependencies with SetupTools (be sure to have
   C:\\Python27\\Scripts\\easy\_install.exe in your PATH):

   #. ::

          easy_install numpy

   #. ::

          easy_install impacket

   #. ::

          easy_install -f "http://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-1.1.0/matplotlib-1.1.0.win32-py2.7.exe?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fmatplotlib%2Ffiles%2Fmatplotlib%2Fmatplotlib-1.1.0%2F&ts=1339591175&use_mirror=netcologne" matplotlib

   #. ::

          easy_install bitarray==0.3.5

Installation of Netzob
^^^^^^^^^^^^^^^^^^^^^^

#. Install
   `Netzob <http://www.netzob.org/repository/0.3.3/Netzob-0.3.3.win32-py2.7.exe>`_
   !

**Remark:** If you have disabled Windows UAC, a error can be raised by
Windows when executing Netzob's installer: Failed to start elevated
process (ShellExecute returned 3). So you have to run the installer with
administrator privilege : right-click on the executable and choose "run
as administrator".
