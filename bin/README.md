SDO_ANALYSIS
============

Directory structure
-------------------
The configure.sh file contains all variables used by shell & Python scripts

Pre-requisites
--------------
virtualenv -p /usr/bin/python3  --system-site-packages
install libyang (apt-get)
install confd from https://developer.cisco.com/site/confD/downloads/
https://www.yumaworks.com/dld/ yangpro-sdk
Python package https://www.decalage.info/files/HTML.py-0.04.zip
install xym with line 593 modified as with open(os.path.join(srcdir, source_id), encoding='latin-1', errors='ignore') as sf:
