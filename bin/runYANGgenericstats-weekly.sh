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

# Test the Internet connectivity. Exit if no connectivity
source testI.sh

# Need to set some ENV variables for subsequent calls in .PY to confd...
source $CONFD_DIR/confdrc

# Generate the weekly reports

# IOS-XR 5.3.0
YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 5.3.0 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/530/" --lint True --prefix CiscoXR530 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/530/" >> $LOG 2>&1

# IOS-XR 5.3.1
YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 5.3.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/531/" --lint True --prefix CiscoXR531 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/531/" >> $LOG 2>&1

# IOS-XR 5.3.2
YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 5.3.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/532/" --lint True --prefix CiscoXR532 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/532/" >> $LOG 2>&1

# IOS-XR 5.3.3
YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 5.3.3 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/533/" --lint True --prefix CiscoXR533 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/533/" >> $LOG 2>&1

# IOS-XR 5.3.4
YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 5.3.4 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/534/" --lint True --prefix CiscoXR534 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/534/" >> $LOG 2>&1

# IOS-XR 6.0.0
YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.0.0 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/600/" --lint True --prefix CiscoXR600 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/600/" >> $LOG 2>&1

# IOS-XR 6.0.1
YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.0.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/601/" --lint True --prefix CiscoXR601 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/601/" >> $LOG 2>&1

# IOS-XR 6.0.2
YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.0.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/602/" --lint True --prefix CiscoXR602 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/602/" >> $LOG 2>&1

# IOS-XR 6.1.1
YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.1.1 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/611/" --lint True --prefix CiscoXR611 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/611/" >> $LOG 2>&1

# IOS-XR 6.1.2
YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.1.2 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/612/" --lint True --prefix CiscoXR612 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/612/" >> $LOG 2>&1

# IOS-XR 6.1.3
YANG-generic.py --allinclusive True --metadata "Cisco IOS XR 6.1.3 from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/613/" --lint True --prefix CiscoXR613 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/cisco/xr/613/" >> $LOG 2>&1

# Juniper 18.1
YANG-generic.py --allinclusive True --metadata "JUNIPER 18.1R1 from https://github.com/YangModels/yang/tree/master/vendor/juniper/18.1/" --lint True --prefix Juniper181R1 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/juniper/18.1/18.1R1/" >> $LOG 2>&1

# Juniper 18.2
YANG-generic.py --allinclusive True --metadata "JUNIPER 18.2R1 from https://github.com/YangModels/yang/tree/master/vendor/juniper/18.2/" --lint True --prefix Juniper182R1 --rootdir "$NONIETFDIR/yangmodels/yang/vendor/juniper/18.2/18.2R1/" >> $LOG 2>&1

# Huawei
#YANG-generic.py --allinclusive True --metadata "HUAWEI ROUTER 8.9.10 https://github.com/Huawei/yang/tree/master/network-router/8.9.10" --lint True --prefix NETWORKROUTER8910 --rootdir "/home/bclaise/yanggithub/huawei/yang/network-router/8.9.10" >> $LOG 2>&1

# Ciena
YANG-generic.py --allinclusive True --metadata "Ciena https://github.com/YangModels/yang/tree/master/vendor/ciena" --lint True --prefix CIENA --rootdir "$NONIETFDIR/yangmodels/yang/vendor/ciena" >> $LOG 2>&1


#clean up of the .fxs files created by confdc
find /home/bclaise/yanggithub/ -name *.fxs -print | xargs rm

echo "End of the script!" >> $LOG 
date >> $LOG
