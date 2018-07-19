SDO_ANALYSIS
============

Parameters
----------

All configuration of all the Python and shell scripts are defined into configure.sh (which refers to several files in ../conf).

Pre-requisites
--------------
It is strongly advised to use virtualenv to ensure a clean Python3 environment
virtualenv -p /usr/bin/python3  --system-site-packages

### Other packages
install libyang (apt-get)

install confd from https://developer.cisco.com/site/confD/downloads/

https://www.yumaworks.com/dld/ yangpro-sdk

Python package https://www.decalage.info/files/HTML.py-0.04.zip

install xym with line 593 modified as with open(os.path.join(srcdir, source_id), encoding='latin-1', errors='ignore') as sf:

Python package matplotlib
