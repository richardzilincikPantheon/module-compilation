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
LOG=$LOGS/YANGgenericstats-weekly.log
echo "Starting" > $LOG
date >> $LOG

# Need to set some ENV variables for subsequent calls in .PY to confd...
source $CONFD_DIR/confdrc

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


# NX-OS 7.0-3-I5-1 ) &
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

# Wait for all child-processes
for PID in $PIDS
do
	wait $PID || exit 1
done

# Yumaworks
YANG-generic.py --allinclusive True --metadata "YUMAWORKS: YANG Data Models compilation from https://github.com/YangModels/yang/tree/master/vendor/yumaworks" --lint True --prefix YUMAWORKS --rootdir "$NONIETFDIR/yangmodels/yang/vendor/yumaworks/" >> $LOG 2>&1

# Juniper 18.1
YANG-generic.py --allinclusive True --metadata "JUNIPER 18.1R1 from https://github.com/YangModels/yang/tree/master/vendor/juniper/18.1/" --lint True --prefix Juniper181R1 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/juniper/18.1/18.1R1/" >> $LOG 2>&1

# Juniper 18.2
YANG-generic.py --allinclusive True --metadata "JUNIPER 18.2R1 from https://github.com/YangModels/yang/tree/master/vendor/juniper/18.2/" --lint True --prefix Juniper182R1 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/juniper/18.2/18.2R1/" >> $LOG 2>&1

# Huawei
YANG-generic.py --allinclusive True --metadata "HUAWEI ROUTER 8.9.10 https://github.com/Huawei/yang/tree/master/network-router/8.9.10" --lint True --prefix NETWORKROUTER8910 --rootdir "/home/bclaise/yanggithub/huawei/yang/network-router/8.9.10" >> $LOG 2>&1

# Ciena
YANG-generic.py --allinclusive True --metadata "Ciena https://github.com/YangModels/yang/tree/master/vendor/ciena" --lint True --prefix CIENA --rootdir "$NONIETFDIR/yangmodels/yang/vendor/ciena" >> $LOG 2>&1

#clean up of the .fxs files created by confdc
find $NONIETFDIR/yangmodels -name *.fxs -print | xargs rm

echo "End of the script!" >> $LOG 
date >> $LOG
