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

#declare -a PIDS

for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/cisco/*/)
do
   subdircount=`find $path -maxdepth 1 -type d | wc -l`
   if [ $subdircount -eq 1 ]
   then
      echo "path to $path*/ does not exists"
      continue
   fi
   if [[ $path == *"/nx/"* ]]
   then
      meta="NX OS"
      os="NX"
   elif [[ $path == *"/xe/"* ]]
   then
      meta="IOS XE"
      os="XE"
   else
      meta="IOS XR"
      os="XR"
   fi
   for path2 in $(ls -d $path*/)
   do
      git=${path2##*/cisco/}
      yang_removed=${git%/*}
      prefix=${yang_removed#*/}
      prefix2=$(echo $prefix | tr -cd '[:alnum:]')
      python yangGeneric.py --allinclusive True --metadata "Cisco $meta $prefix from https://github.com/YangModels/yang/tree/master/vendor/cisco/$git" --lint True --prefix Cisco$os$prefix2 --rootdir "$path2" >> $LOG 2>&1
   done
done

date +"%c: waiting for all forked shell to terminate " >> $LOG
# Wait for all child-processes
#for PID in $PIDS
#do
#	wait $PID || exit 1
#done

date +"%c: processing non Cisco modules " >> $LOG

for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/juniper/*/)
do
   subdircount=`find $path -maxdepth 1 -type d | wc -l`
   if [ $subdircount -eq 1 ]
   then
      echo "path to $path*/ does not exists"
      continue
   fi
   for path2 in $(ls -d $path*/)
   do
      git=${path2##*/juniper/}
      yang_removed=${git%/*}
      prefix=${yang_removed#*/}
      prefix2=$(echo $prefix | tr -cd '[:alnum:]')
      python yangGeneric.py --allinclusive True --metadata "JUNIPER $prefix from https://github.com/YangModels/yang/tree/master/vendor/juniper/$git" --lint True --prefix Juniper$prefix2 --rootdir "$path2" >> $LOG 2>&1
   done
done

for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/huawei/network-router/*/)
do
   git=${path##*/network-router/}
   git=${git::-1}
   yang_removed=${git%/*}
   prefix=${yang_removed#*/}
   prefix=$(echo $prefix | tr -cd '[:alnum:]')
   python yangGeneric.py --allinclusive True --metadata "HUAWEI ROUTER $git https://github.com/Huawei/yang/tree/master/network-router/$git" --lint True --prefix NETWORKROUTER$prefix --rootdir "$path" >> $LOG 2>&1
done


# Ciena
python yangGeneric.py --allinclusive True --metadata "Ciena https://github.com/YangModels/yang/tree/master/vendor/ciena" --lint True --prefix CIENA --rootdir "$NONIETFDIR/yangmodels/yang/vendor/ciena" >> $LOG 2>&1 #&
#PIDS+=("$!")

for path in $(find $NONIETFDIR/yangmodels/yang/vendor/fujitsu/FSS2-API-Yang -name "yang")
do
   git=${path##*/fujitsu/}
   yang_removed=${git%/*}
   prefix=${yang_removed#*/}
   prefix=$(echo $prefix | tr -cd '[:alnum:]')
   python yangGeneric.py --allinclusive True --metadata "Fujitsu https://github.com/YangModels/yang/tree/master/vendor/fujitsu/$git" --lint True --prefix Fujitsu$prefix --rootdir "$path" >> $LOG 2>&1
done

for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/nokia/*/)
do
   subdircount=`find $path -maxdepth 1 -type d | wc -l`
   if [ $subdircount -eq 1 ]
   then
      echo "path to $path*/ does not exists"
      continue
   fi
   for path2 in $(ls -d $path*/)
   do
      git=${path2##*/7x50_YangModels/}
      yang_removed=${git%/*}
      prefix=${yang_removed#*/}
      prefix=$(echo $prefix | tr -cd '[:alnum:]'| sed 's/latestsros//g')
      python yangGeneric.py --allinclusive True --metadata "Nokia $git https://github.com/YangModels/yang/tree/master/vendor/nokia/$git" --lint True --prefix Nokia$prefix --rootdir "$path2" >> $LOG 2>&1
   done
done


date +"%c: waiting for all forked shell to terminate " >> $LOG
# Wait for all child-processes
#for PID in $PIDS
#do
#	wait $PID || exit 1
#done

date +"%c: Cleaning up the remaining .fxs " >> $LOG
#clean up of the .fxs files created by confdc
find $NONIETFDIR/yangmodels -name *.fxs -print | xargs rm >> $LOG 2>&1

date +"%c: reloading cache" >> $LOG
read -ra CRED <<< "$CREDENTIALS"
curl -X POST -u ${CRED[0]}:${CRED[1]} $MY_URI/api/load-cache >> $LOG 2>&1

date +"%c: End of the script!" >> $LOG
