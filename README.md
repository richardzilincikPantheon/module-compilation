SDO ANALYSIS
============

This part of YangCatalog.org server fetches all YANG modules from different repositories and also scan all IETF RFC and drafts for YANG modules.

Once all those modules are retrieved they are validated by several tools.

Most of the code is in the `bin/` directory and uses bash and Python3 scripts.

Some configuration files are in the `conf/` directory including `paths.sh` which defines all paths used by the scripts. This script merely reads the global configuration file `/etc/yangcatalog/yangcatalog.conf` and creates the required environement variables required by the shell scripts.

The file `/etc/yangcatalog/IETF-draft-list-with-no-YANG-problem.txt` contains a list of IETF drafts having a `xym`extraction error but containing no actual YANG modules. Those I-D are removed from the local I-D reporsitory.


*Some pre-requisistes are defined int he README.md in bin directory*

Directory structure
-------------------

After running all those scripts, the following directories are populated:

- Directory-Section:modules_directory ($MODULES in shell):
- Directory-Section:non_ietf_directory ($NONIETFDIR in shell):
- Directory-Section:ietf_directory ($IETFDIR in shell):
  - YANG/ correctly extracted models from IETF drafts
  - YANG-all/ all extracted models (including bad ones) from IETF drafts
  - YANG-example/ all extracted example models (starting with example- and not with CODE BEGINS/END)
  - YANG-example-old-rfc/ the hardcoded YANG module example models from old RFCs (not starting with example-)
  - draft-with-YANG-strict/ all drafts containing YANG model(s), with strict xym rule = True
  - draft-with-YANG-no-strict/ all drafts containing YANG model(s), with strict xym rule = False
  - draft-with-YANG-example/ all drafts containing YANG model(s) with examples
  - YANG-rfc/ correctly extracted models from RFCs
  - YANG-rfc-extraction/ the typedef, grouping, identity from data models extracted from RFCs
  - YANG-extraction/ the typedef, grouping, identity from data models correctely extracted from drafts
  - my-id-mirror/ a mirror of all IETF draft (rsycnh from IETF)
  - rfc/ a mirror of all IETF RFC (rsycnh from IETF)
- ($WEB in shell):
  - YANG-modules/ all YANG modules extracted fro IETF documents (a copy of $IETFDIR/YANG)
- Web-Section:private_directory ($WEBPRIVATE in shell):
  - <SDO>.json the list of all YANG modules of the SDO including compilation statistics
  - <SDO>YANGPageCompilation.html table of all YANG models of the SDO including compilation statistics
  - <SDO>YANGPageMain.html summary of compilation results for all YANG modules of this SDO
  - figures/*.png a couple of graphics including dependency graphs for some modules (ietf-interfaces, ..), for all YANG modules known (heavy graph), and history statistics
  - stats/*.json statistics about YANG modules extracted from IETF drafts and RFC 
- Directory-Section --key backup ($BACKUPDIR in shell): an history directory contaiing all files from <SDO> with a date suffix (used to generated the history graphcis)
