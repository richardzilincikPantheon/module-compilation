#!/bin/bash -e

# Copyright The IETF Trust 2019, All Rights Reserved
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
export LOG=$LOGS/YANGgenericstats-weekly.log
date +"%c: Starting" > $LOG

# Need to set some ENV variables for subsequent calls in .PY to confd...
source $CONFD_DIR/confdrc >> $LOG 2>&1

mkdir -p $MODULES >> $LOG 2>&1

# Generate the weekly reports

#TODO dynamic discovery of those models

declare -a PIDS

# IOS-XR 5.3.0
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 5.3.0 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/530/" --lint True --prefix CiscoXR530 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/530/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 5.3.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 5.3.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/531/" --lint True --prefix CiscoXR531 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/531/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 5.3.2
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 5.3.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/532/" --lint True --prefix CiscoXR532 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/532/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 5.3.3
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 5.3.3 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/533/" --lint True --prefix CiscoXR533 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/533/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 5.3.4
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 5.3.4 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/534/" --lint True --prefix CiscoXR534 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/534/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.0.0
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.0.0 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/600/" --lint True --prefix CiscoXR600 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/600/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.0.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.0.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/601/" --lint True --prefix CiscoXR601 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/601/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.0.2
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.0.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/602/" --lint True --prefix CiscoXR602 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/602/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.1.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.1.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/611/" --lint True --prefix CiscoXR611 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/611/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.1.2
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.1.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/612/" --lint True --prefix CiscoXR612 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/612/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.1.3
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.1.3 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/613/" --lint True --prefix CiscoXR613 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/613/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.2.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.2.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/621/" --lint True --prefix CiscoXR621 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/621/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.2.2
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.2.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/622/" --lint True --prefix CiscoXR622 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/622/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.3.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.3.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/631/" --lint True --prefix CiscoXR631 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/631/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.3.2
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.3.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/632/" --lint True --prefix CiscoXR632 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/632/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.4.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.4.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/641/" --lint True --prefix CiscoXR641 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/641/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.4.2
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.4.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/642/" --lint True --prefix CiscoXR642 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/642/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.5.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.5.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/651/" --lint True --prefix CiscoXR651 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/651/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.5.2
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.5.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/652/" --lint True --prefix CiscoXR652 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/652/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.5.3
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.5.3 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/653/" --lint True --prefix CiscoXR653 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/653/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.6.2
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.6.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/662/" --lint True --prefix CiscoXR662 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/662/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 6.6.3
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.6.3 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/663/" --lint True --prefix CiscoXR663 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/663/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XR 7.0.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 7.0.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/701/" --lint True --prefix CiscoXR701 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/701/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.3.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.3.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/1631" --lint True --prefix CiscoXE1631 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/1631/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.3.2
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.3.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/1632" --lint True --prefix CiscoXE1632 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/1632/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.4.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.4.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/1641" --lint True --prefix CiscoXE1641 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/1641/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.5.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.5.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/1651" --lint True --prefix CiscoXE1651 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/1651/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.6.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.6.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/1661" --lint True --prefix CiscoXE1661 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/1661/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.6.2
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.6.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/1662" --lint True --prefix CiscoXE1662 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/1662/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.7.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.7.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/1671" --lint True --prefix CiscoXE1671 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/1671/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.8.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.8.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/1681" --lint True --prefix CiscoXE1681 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/1681/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.9.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.9.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/1691" --lint True --prefix CiscoXE1691 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/1691/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 17.1.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 17.1.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/1711" --lint True --prefix CiscoXE1711 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/1711/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.9.3
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.9.3 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/1693" --lint True --prefix CiscoXE1693 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/1693/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.10.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.10.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/16101" --lint True --prefix CiscoXE16101 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/16101/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.11.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.11.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/16111" --lint True --prefix CiscoXE16111 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/16111/" >> $LOG 2>&1) &
PIDS+=("$!")

# IOS-XE 16.11.1
(YANG-generic.py --allinclusive True --metadata "Cisco IOS XE 16.12.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/16121" --lint True --prefix CiscoXE16121 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xe/16121/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-F1-1
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-F1-1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-F1.1" --lint True --prefix CiscoNX703F11 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-F1-1/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-F2-1
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-F2-1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-F2.1" --lint True --prefix CiscoNX703F21 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-F2-1/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-F2-2
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-F2-2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-F2.2" --lint True --prefix CiscoNX703F22 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-F2-2/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-F3-1
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-F3-1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-F3.1" --lint True --prefix CiscoNX703F31 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-F3-1/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-I5-1
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-I5-1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-I5-1" --lint True --prefix CiscoNX703I51 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-I5-1/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-I5-2
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-I5-2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-I5-2" --lint True --prefix CiscoNX703I52 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-I5-2/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-I6-1
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-I6-1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-I6-1" --lint True --prefix CiscoNX703I61 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-I6-1/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-I6-2
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-I6-2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-I6-2" --lint True --prefix CiscoNX703I62 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-I6-2/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-I7-1
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-I7-1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-I7-1" --lint True --prefix CiscoNX703I71 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-I7-1/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-I7-2
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-I7-2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-I7-2" --lint True --prefix CiscoNX703I72 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-I7-2/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-I7-3
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-I7-3 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-I7-3" --lint True --prefix CiscoNX703I73 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-I7-3/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-I7-4
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-I7-4 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-I7-4" --lint True --prefix CiscoNX703I74 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-I7-4/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-I7-5
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-I7-5 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-I7-5" --lint True --prefix CiscoNX703I75 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-I7-5/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-I7-5 a
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-I7-5a from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-I7-5a" --lint True --prefix CiscoNX703I75a --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-I7-5a/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-I7-6
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-I7-6 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-I7-6" --lint True --prefix CiscoNX703I76 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-I7-6/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 7.0-3-I7-7
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS F.0-3-I7-7 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/7.0-3-I7-7" --lint True --prefix CiscoNX703I77 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/7.0-3-I7-7/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 9.2-1
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS 9.2-1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/9.2-1" --lint True --prefix CiscoNX921 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/9.2-1/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 9.2-2
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS 9.2-2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/9.2-2" --lint True --prefix CiscoNX922 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/9.2-2/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 9.2-3
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS 9.2-3 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/9.2-3" --lint True --prefix CiscoNX923 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/9.2-3/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 9.2-4
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS 9.2-4 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/9.2-4" --lint True --prefix CiscoNX924 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/9.2-4/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 9.3-1
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS 9.3-1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/9.3-1" --lint True --prefix CiscoNX931 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/9.3-1/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 9.3-2
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS 9.3-2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/9.3-2" --lint True --prefix CiscoNX932 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/9.3-2/" >> $LOG 2>&1) &
PIDS+=("$!")

# NX-OS 9.3-3
(YANG-generic.py --allinclusive True --metadata "Cisco NX OS 9.3-3 from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/9.3-3" --lint True --prefix CiscoNX933 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/nx/9.3-3/" >> $LOG 2>&1) &
PIDS+=("$!")

date +"%c: waiting for all forked shell to terminate " >> $LOG 
# Wait for all child-processes
for PID in $PIDS
do
	wait $PID || exit 1
done

date +"%c: processing non Cisco modules " >> $LOG 

# Juniper 17.2
YANG-generic.py --allinclusive True --metadata "JUNIPER 17.2R1 from https://github.com/YangModels/yang/tree/master/vendor/juniper/17.2/" --lint True --prefix Juniper172R1 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/juniper/17.2/17.2R1/" >> $LOG 2>&1 &
PIDS+=("$!")

# Juniper 17.3
YANG-generic.py --allinclusive True --metadata "JUNIPER 17.3R1 from https://github.com/YangModels/yang/tree/master/vendor/juniper/17.3/" --lint True --prefix Juniper173R1 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/juniper/17.3/17.3R1/" >> $LOG 2>&1 &
PIDS+=("$!")

# Juniper 17.4
YANG-generic.py --allinclusive True --metadata "JUNIPER 17.4R1 from https://github.com/YangModels/yang/tree/master/vendor/juniper/17.4/" --lint True --prefix Juniper174R1 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/juniper/17.4/17.4R1/" >> $LOG 2>&1 &
PIDS+=("$!")

# Juniper 18.1
YANG-generic.py --allinclusive True --metadata "JUNIPER 18.1R1 from https://github.com/YangModels/yang/tree/master/vendor/juniper/18.1/" --lint True --prefix Juniper181R1 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/juniper/18.1/18.1R1/" >> $LOG 2>&1 &
PIDS+=("$!")

# Juniper 18.2
YANG-generic.py --allinclusive True --metadata "JUNIPER 18.2R1 from https://github.com/YangModels/yang/tree/master/vendor/juniper/18.2/" --lint True --prefix Juniper182R1 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/juniper/18.2/18.2R1/" >> $LOG 2>&1 &
PIDS+=("$!")

# Huawei
YANG-generic.py --allinclusive True --metadata "HUAWEI ROUTER 8.9.10 https://github.com/Huawei/yang/tree/master/network-router/8.9.10" --lint True --prefix NETWORKROUTER8910 --rootdir "$NONIETFDIR/nonietf/yangmodels/yang/vendor/huawei/yang/network-router/8.9.10" >> $LOG 2>&1 &
PIDS+=("$!")

# Ciena
YANG-generic.py --allinclusive True --metadata "Ciena https://github.com/YangModels/yang/tree/master/vendor/ciena" --lint True --prefix CIENA --rootdir "$NONIETFDIR/yangmodels/yang/vendor/ciena" >> $LOG 2>&1 &
PIDS+=("$!")

# Fujitsu T100 2.4.2
YANG-generic.py --allinclusive True --metadata "Fujitsu https://github.com/YangModels/yang/tree/master/vendor/fujitsu/FSS2-API-Yang/T100/2.4.2/yang" --lint True --prefix FujitsuT100242 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/fujitsu/FSS2-API-Yang/T100/2.4.2/yang" >> $LOG 2>&1 &
PIDS+=("$!")

# Fujitsu T100 2.4
YANG-generic.py --allinclusive True --metadata "Fujitsu https://github.com/YangModels/yang/tree/master/vendor/fujitsu/FSS2-API-Yang/T100/2.4/yang" --lint True --prefix FujitsuT10024 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/fujitsu/FSS2-API-Yang/T100/2.4/yang" >> $LOG 2>&1 &
PIDS+=("$!")

# Fujitsu T400 1.1.2
YANG-generic.py --allinclusive True --metadata "Fujitsu https://github.com/YangModels/yang/tree/master/vendor/fujitsu/FSS2-API-Yang/T400/1.1.2/yang" --lint True --prefix FujitsuT400112 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/fujitsu/FSS2-API-Yang/T400/1.1.2/yang" >> $LOG 2>&1 &
PIDS+=("$!")

# Fujitsu T400 1.2
YANG-generic.py --allinclusive True --metadata "Fujitsu https://github.com/YangModels/yang/tree/master/vendor/fujitsu/FSS2-API-Yang/T400/1.2/yang" --lint True --prefix FujitsuT40012 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/fujitsu/FSS2-API-Yang/T400/1.2/yang" >> $LOG 2>&1 &
PIDS+=("$!")

# Fujitsu T600-OC 1.1
YANG-generic.py --allinclusive True --metadata "Fujitsu https://github.com/YangModels/yang/tree/master/vendor/fujitsu/FSS2-API-Yang/T600-OC/1.1/yang" --lint True --prefix FujitsuT600OC11 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/fujitsu/FSS2-API-Yang/T600-OC/1.1/yang" >> $LOG 2>&1 &
PIDS+=("$!")

# Fujitsu T600-OC 1.2
YANG-generic.py --allinclusive True --metadata "Fujitsu https://github.com/YangModels/yang/tree/master/vendor/fujitsu/FSS2-API-Yang/T600-OC/1.2/yang" --lint True --prefix FujitsuT600OC12 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/fujitsu/FSS2-API-Yang/T600-OC/1.2/yang" >> $LOG 2>&1 &
PIDS+=("$!")

# Fujitsu T600-OC 1.1
YANG-generic.py --allinclusive True --metadata "Fujitsu https://github.com/YangModels/yang/tree/master/vendor/fujitsu/FSS2-API-Yang/T600/1.1/yang" --lint True --prefix FujitsuT60011 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/fujitsu/FSS2-API-Yang/T600/1.1/yang" >> $LOG 2>&1 &
PIDS+=("$!")

# Fujitsu T600-OC 1.2
YANG-generic.py --allinclusive True --metadata "Fujitsu https://github.com/YangModels/yang/tree/master/vendor/fujitsu/FSS2-API-Yang/T600/1.2/yang" --lint True --prefix FujitsuT60012 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/fujitsu/FSS2-API-Yang/T600/1.2/yang" >> $LOG 2>&1 &
PIDS+=("$!")

date +"%c: waiting for all forked shell to terminate " >> $LOG
# Wait for all child-processes
for PID in $PIDS
do
	wait $PID || exit 1
done

date +"%c: Cleaning up the remaining .fxs " >> $LOG 
#clean up of the .fxs files created by confdc
find $NONIETFDIR/yangmodels -name *.fxs -print | xargs rm >> $LOG 2>&1

date +"%c: End of the script!" >> $LOG 
