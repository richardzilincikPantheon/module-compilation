SDO ANALYSIS
============

This part of YangCatalog.org server fetches all YANG modules from different repositories and also scan all IETF RFC and drafts for YANG modules.

Once all those modules are retrieved they are validated by several tools.

Most of the code is in the bin/ directory and uses bash and Python3 scripts.

Some configuration files are in the conf/ directory including paths.sh which defines all paths used by the scripts.
