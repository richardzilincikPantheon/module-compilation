#!/bin/bash -e

# Copyright (c) 2018 Cisco and/or its affiliates.
# This software is licensed to you under the terms of the Apache License, Version 2.0 (the "License").
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
# The code, technical concepts, and all information contained herein, are the property of Cisco Technology, Inc.
# and/or its affiliated entities, under various laws including copyright, international treaties, patent,
# and/or contract. Any use of the material herein must be in accordance with the terms of the License.
# All rights not expressly granted by the License are reserved.
# Unless required by applicable law or agreed to separately in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

source configure.sh
LOG=$LOGS/YANGIETFstats.log
date +"%c: Starting" > $LOG

# Need to set some ENV variables for subsequent calls in .PY to confd...
# TODO probably to be moved inside the confd caller
source $CONFD_DIR/confdrc

# rsynch the IETF drafts and RFCs
mkdir -p $IETFDIR/my-id-mirror
rm -f $IETFDIR/my-id-mirror/*.yang

cd $IETFDIR

rsync -avz --include 'draft-*.txt' --exclude '*' --delete rsync.ietf.org::internet-drafts my-id-mirror  >> $LOG 2>&1
rsync -avlz --delete --delete-excluded --exclude=dummy.txt --exclude="std-*.txt" --exclude="bcp-*.txt" --exclude="rfc-retrieval.txt" --exclude="rfc-index*.txt" --exclude="RFCs_for_errata.txt" --exclude="rfc-ref.txt" --exclude="rfcxx00.txt" --exclude="*index*" --include="*.txt"  --exclude="*" ftp.rfc-editor.org::rfcs rfc  >> $LOG 2>&1


#remove the drafts with xym.py error, but that don't contain YANG data modules
YANG-exclude-bad-drafts.py >> $LOG 2>&1

#copy the current content to the -old files 
if [ -f $WEB_PRIVATE/IETFDraftYANGPageCompilation.html ]
then
	cp $WEB_PRIVATE/IETFDraftYANGPageCompilation.html $WEB_PRIVATE/IETFDraftYANGPageCompilation-old.html
fi
if [ -f $WEB_PRIVATE/IETFCiscoAuthorsYANGPageCompilation.html ]
then
	cp $WEB_PRIVATE/IETFCiscoAuthorsYANGPageCompilation.html $WEB_PRIVATE/IETFCiscoAuthorsYANGPageCompilation-old.html
fi

# Some directory and symbolic links may need to be created
# TODO have a script to create those
mkdir -p $IETFDIR/YANG
mkdir -p $IETFDIR/YANG-all
mkdir -p $IETFDIR/YANG-example
mkdir -p $IETFDIR/YANG-extraction
mkdir -p $IETFDIR/YANG-rfc
mkdir -p $IETFDIR/YANG-rfc-extraction
mkdir -p $IETFDIR/YANG-example-old-rfc
mkdir -p $IETFDIR/YANG-v11
mkdir -p $IETFDIR/draft-with-YANG-strict
mkdir -p $IETFDIR/draft-with-YANG-no-strict
mkdir -p $IETFDIR/draft-with-YANG-example
mkdir -p $IETFDIR/draft-with-YANG-diff
mkdir -p $MODULES
rm -f $MODULES/ieee.draft
ln -f -s $NONIETFDIR/yangmodels/yang/standard/ieee/draft/ $MODULES/ieee.draft
rm -f $MODULES/ieee.802.1.draft
ln -f -s $NONIETFDIR/yangmodels/yang/standard/ieee/802.1/draft/ $MODULES/ieee.802.1.draft
rm -f $MODULES/ieee.802.3.draft
ln -f -s $NONIETFDIR/yangmodels/yang/standard/ieee/802.3/draft/ $MODULES/ieee.802.3.draft
rm -f $MODULES/mef
ln -f -s $NONIETFDIR/mef/YANG-public/src/model/standard/ $MODULES/mef
ln -f -s $NONIETFDIR/openconfig/public/release/models/ $MODULES/open-config-main

# Extract all YANG models from RFC/I-D
# TODO only process new I-D/RFC
YANG-IETF.py >> $LOG 2>&1
#clean up of the .fxs files created by confdc
rm -f $IETFDIR/YANG/*.fxs

# move all IETF YANG to the web part
mkdir -p $WEB/YANG-modules
rm -f $WEB/YANG-modules/*
cp --preserve $IETFDIR/YANG/*.yang $WEB/YANG-modules

# Generate the report for RFC-ed YANG modules, and ftp the files.
YANG-generic.py --metadata "RFC-produced YANG models: Oh gosh, not all of them correctly passed pyang version 1.7 with --ietf :-( " --prefix RFCStandard --rootdir "$IETFDIR/YANG-rfc/" >> $LOG 2>&1
date +"%c: All RFC processed" >> $LOG

#Generate the diff files 
# Need to add || true as diff returns 1 in case of different files...
diff $WEB_PRIVATE/IETFDraftYANGPageCompilation.html $WEB_PRIVATE/IETFDraftYANGPageCompilation-old.html > $WEB_PRIVATE/IETFDraftYANGPageCompilation-diff.txt || true
diff $WEB_PRIVATE/IETFCiscoAuthorsYANGPageCompilation.html $WEB_PRIVATE/IETFCiscoAuthorsYANGPageCompilation-old.html > $WEB_PRIVATE/IETFCiscoAuthorsYANGPageCompilation-diff.txt || true
date +"%c: Diff files generated" >> $LOG

# create the tar files
cd $IETFDIR/YANG-rfc
tar cfz $WEB_DOWNLOADABLES/YANG-RFC.tgz *yang
cd $IETFDIR/YANG
tar cfz $WEB_DOWNLOADABLES/YANG.tgz *yang
cd $IETFDIR/YANG-all
tar cfz $WEB_DOWNLOADABLES/All-YANG-drafts.tgz *yang
date +"%c: YANG v1.0 tarball files generated" >> $LOG

# copy the YANG 1.1 data models in $IETF_DIR/YANG-v11
YANGversion11.py >> $LOG 2>&1

cd $IETFDIR/YANG-v11
tar cvfz $WEB_DOWNLOADABLES/YANG-v11.tgz *yang
date +"%c: YANG v1.1 tarball files generated" >> $LOG

date +"%c: End of the script!" >> $LOG
