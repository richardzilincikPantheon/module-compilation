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
LOG=$LOGS/YANGgenericstats.log
echo "Starting" > $LOG
date >> $LOG

# Test the Internet connectivity. Exit if no connectivity
source testI.sh

# Need to set some ENV variables for subsequent calls in .PY to confd...
source $CONFD_DIR/confdrc

# Generate the daily reports

# BBF, we need to flatten the directory structure
# TODO modify the YANG-generic.py file to handle a directory tree ?
mkdir -p $TMP/bbf
rm -f $TMP/bbf/*
find $NONIETFDIR/yangmodels/yang/standard/bbf -name "*.yang" -exec ln -s {} $TMP/bbf/ \;

declare -a PIDS
($BIN/YANG-generic.py --metadata "BBF Complete Report: YANG Data Models compilation from https://github.com/YangModels/yang/tree/master/standard/bbf@7abc8b9" --lint True --prefix BBF --rootdir "$TMP/bbf/" >> $LOG 2>&1) &
PIDS+=("$!")

# Standard MEF
($BIN/YANG-generic.py --metadata "MEF: Standard YANG Data Models compilation from https://github.com/MEF-GIT/YANG-public/tree/master/src/model/standard/" --lint True --prefix MEFStandard --rootdir "$NONIETFDIR/mef/YANG-public/src/model/standard/" >> $LOG 2>&1) &
PIDS+=("$!")

# Experimental MEF
($BIN/YANG-generic.py --metadata "MEF: Draft YANG Data Models compilation from https://github.com/MEF-GIT/YANG-public/tree/master/src/model/draft/" --lint True --prefix MEFExperimental --rootdir "$NONIETFDIR/mef/YANG-public/src/model/draft/" >> $LOG 2>&1) &
PIDS+=("$!")

# Standard IEEE
($BIN/YANG-generic.py --metadata "IEEE: YANG Data Models compilation from https://github.com/YangModels/yang/tree/master/standard/ieee :  The "standard/ieee" branch is intended for approved PARs, for drafts as well as published standards. " --lint True --prefix IEEEStandard --rootdir "$NONIETFDIR/yangmodels/yang/standard/ieee/" >> $LOG 2>&1) &
PIDS+=("$!")

# Experimental IEEE
($BIN/YANG-generic.py --metadata "IEEE: Draft YANG Data Models compilation from https://github.com/YangModels/yang/tree/master/experimental/ieee :  The "experimental/ieee" branch is intended for IEEE work that does not yet have a Project Authorization Request (PAR). " --lint True --prefix IEEEExperimental --rootdir "$NONIETFDIR/yangmodels/yang/experimental/ieee/" >> $LOG 2>&1) &
PIDS+=("$!")

# Openconfig
($BIN/YANG-generic.py --metadata "Openconfig: YANG Data Models compilation from https://github.com/openconfig/public" --lint True --prefix Openconfig --rootdir "$NONIETFDIR/openconfig/public/release/models/" >> $LOG 2>&1) &
PIDS+=("$!")

# ONF Open Transport
($BIN/YANG-generic.py --metadata "ONF Open Transport: YANG Data Models compilation from https://github.com/OpenNetworkingFoundation/Snowmass-ONFOpenTransport" --lint True --prefix ONFOpenTransport --rootdir "$NONIETFDIR/onf/Snowmass-ONFOpenTransport" >> $LOG 2>&1) &
PIDS+=("$!")

# sysrepo internal
($BIN/YANG-generic.py --metadata "Sysrepo: internal YANG Data Models compilation from https://github.com/sysrepo/yang/tree/master/internal" --lint True --prefix SysrepoInternal --rootdir "$NONIETFDIR/sysrepo/yang/internal/" >> $LOG 2>&1) &
PIDS+=("$!")

# sysrepo applications
($BIN/YANG-generic.py --metadata "Sysrepo: applications YANG Data Models compilation from https://github.com/sysrepo/yang/tree/master/applications" --lint True --prefix SysrepoApplication --rootdir "$NONIETFDIR/sysrepo/yang/applications/" >> $LOG 2>&1) &
PIDS+=("$!")

# openroadm public
# openROADM, we need to flatten the directory structure
# TODO modify the YANG-generic.py file to handle a directory tree ?
mkdir -p $TMP/openroadm-public
rm -f $TMP/openroadm-public/*
find $NONIETFDIR/openroadm/OpenROADM_MSA_Public -name "*.yang" -exec ln -s {} $TMP/openroadm-public/ \;

($BIN/YANG-generic.py --metadata "OpenRoadm 2.0.1: YANG Data Models compilation from https://github.com/OpenROADM/OpenROADM_MSA_Public/tree/master/model" --lint True --prefix OpenROADM20 --rootdir "$TMP/openroadm-public/" >> $LOG 2>&1) &
PIDS+=("$!")

# Wait for all child-processes
for PID in $PIDS
do
	wait $PID || exit 1
done

rm -f $TMP/bbf/*.fxs
rm -f $TMP/openroadm-public/*.fxs

# Removed openROADM private handling

#clean up of the .fxs files created by confdc
find $NONIETFDIR/ -name *.fxs -print | xargs rm

