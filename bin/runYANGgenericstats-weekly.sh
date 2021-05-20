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

wait_for_processes()
{
  PIDS=("$@")
  max_processes=3

  if [ $running -eq $max_processes ]
  then
  for PID in ${PIDS[@]}
    do
      wait $PID || exit 1
    done
    running=0
  fi
}

source configure.sh
export LOG=$LOGS/YANGgenericstats-weekly.log
date +"%c: Starting" > $LOG

# Need to set some ENV variables for subsequent calls in .PY to confd...
source $CONFD_DIR/confdrc >> $LOG 2>&1

mkdir -p $MODULES >> $LOG 2>&1

curl -s -H "Accept: application/json" $MY_URI/api/search/modules -o "$TMP/all_modules_data.json" >> $LOG 2>&1

# Generate the weekly reports

# Cisco NX
date +"%c: processing all Cisco NX modules " >> $LOG
declare -a PIDSNX
running=0
for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/cisco/nx/*/)
do
   meta="NX OS"
   os="NX"
   for path2 in $(ls -d $path)
   do
      ((running=running+1))
      git=${path2##*/cisco/nx/}
      yang_removed=${git%/*}
      prefix=${yang_removed#*/}
      prefix2=$(echo $prefix | tr -cd '[:alnum:]')
      (python yangGeneric.py --allinclusive True --metadata "Cisco $meta $prefix from https://github.com/YangModels/yang/tree/master/vendor/cisco/nx/$git" --lint True --prefix Cisco$os$prefix2 --rootdir "$path2" >> $LOG 2>&1) &
      PIDSNX+=("$!")
      wait_for_processes "${PIDSNX[@]}"
   done
done
# Wait for all child-processes until move to next OS
for PID in ${PIDSNX[@]}
do
   wait $PID || exit 1
done

# Cisco XE
date +"%c: processing all Cisco XE modules " >> $LOG
declare -a PIDSXE
running=0
for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/cisco/xe/*/)
do
   meta="IOS XE"
   os="XE"
   for path2 in $(ls -d $path)
   do
      ((running=running+1))
      git=${path2##*/cisco/xe/}
      yang_removed=${git%/*}
      prefix=${yang_removed#*/}
      prefix2=$(echo $prefix | tr -cd '[:alnum:]')
      (python yangGeneric.py --allinclusive True --metadata "Cisco $meta $prefix from https://github.com/YangModels/yang/tree/master/vendor/cisco/xe/$git" --lint True --prefix Cisco$os$prefix2 --rootdir "$path2" >> $LOG 2>&1) &
      PIDSXE+=("$!")
      wait_for_processes "${PIDSXE[@]}"
   done
done
# Wait for all child-processes until move to next OS
for PID in ${PIDSXE[@]}
do
   wait $PID || exit 1
done

# Cisco XR
date +"%c: processing all Cisco XR modules " >> $LOG
declare -a PIDSXR
running=0
for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/cisco/xr/*/)
do
   meta="IOS XR"
   os="XR"
   for path2 in $(ls -d $path)
   do
      ((running=running+1))
      git=${path2##*/cisco/xr/}
      yang_removed=${git%/*}
      prefix=${yang_removed#*/}
      prefix2=$(echo $prefix | tr -cd '[:alnum:]')
      (python yangGeneric.py --allinclusive True --metadata "Cisco $meta $prefix from https://github.com/YangModels/yang/tree/master/vendor/cisco/xr/$git" --lint True --prefix Cisco$os$prefix2 --rootdir "$path2" >> $LOG 2>&1) &
      PIDSXR+=("$!")
      wait_for_processes "${PIDSXR[@]}"
   done
done
# Wait for all child-processes until move to next OS
for PID in ${PIDSXR[@]}
do
   wait $PID || exit 1
done

# Cisco SVO
date +"%c: processing all Cisco SVO modules " >> $LOG
declare -a PIDSSVO
running=0
for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/cisco/svo/*/)
do
   meta="NCS"
   os="SVO"
   for path2 in $(ls -d $path)
   do
      ((running=running+1))
      git=${path2##*/cisco/svo/}
      yang_removed=${git%/*}
      prefix=${yang_removed#*/}
      prefix2=$(echo $prefix | tr -cd '[:alnum:]')
      (python yangGeneric.py --allinclusive True --metadata "Cisco $meta $prefix from https://github.com/YangModels/yang/tree/master/vendor/cisco/svo/$git" --lint True --prefix Cisco$os$prefix2 --rootdir "$path2" >> $LOG 2>&1) &
      PIDSSVO+=("$!")
      wait_for_processes "${PIDSSVO[@]}"
   done
done
# Wait for all child-processes until move to next vendor
for PID in ${PIDSSVO[@]}
do
   wait $PID || exit 1
done

date +"%c: processing non Cisco modules " >> $LOG

# Juniper
date +"%c: processing Juniper modules " >> $LOG
declare -a PIDJUNIPER
running=0
for i in {14..20}
do
   # Juniper/14.2 does not contain subdirectories
   if [ $i -eq 14 ]
   then
         path=$(ls -d $NONIETFDIR/yangmodels/yang/vendor/juniper/$i*/)
         git=${path##*/juniper/}
         yang_removed=${git%/*}
         prefix=${yang_removed#*/}
         prefix2=$(echo $prefix | tr -cd '[:alnum:]')
         python yangGeneric.py --allinclusive True --metadata "JUNIPER $prefix from https://github.com/Juniper/yang/tree/master/$git" --lint True --prefix Juniper$prefix2 --rootdir "$path" >> $LOG 2>&1
   # Juniper/15* does not exist
   elif [ $i -eq 15 ]
   then
      continue
   else
      for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/juniper/$i*/)
      do
         for path2 in $(ls -d $path*/)
         do
            ((running=running+1))
            git=${path2##*/juniper/}
            yang_removed=${git%/*}
            prefix=${yang_removed#*/}
            prefix2=$(echo $prefix | tr -cd '[:alnum:]')
            (python yangGeneric.py --allinclusive True --metadata "JUNIPER $prefix from https://github.com/Juniper/yang/tree/master/$git" --lint True --prefix Juniper$prefix2 --rootdir "$path2" >> $LOG 2>&1) &
            PIDJUNIPER+=("$!")
            wait_for_processes "${PIDJUNIPER[@]}"
         done
      done
      for PID in ${PIDJUNIPER[@]}
      do
         wait $PID || exit 1
      done
      unset PIDJUNIPER
   fi
done

# Huawei
date +"%c: processing Huawei modules " >> $LOG
declare -a PIDSHUAWEI
running=0
for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/huawei/network-router/8.20.0/*/)
do
   ((running=running+1))
   git=${path##*/network-router/8.20.0/}
   git=${git::-1}
   yang_removed=${git%/*}
   prefix=${yang_removed#*/}
   (python yangGeneric.py --allinclusive True --metadata "HUAWEI ROUTER $git https://github.com/Huawei/yang/tree/master/network-router/8.20.0/$git" --lint True --prefix NETWORKROUTER$prefix --rootdir "$path" >> $LOG 2>&1) &
   PIDSHUAWEI+=("$!")
   wait_for_processes "${PIDSHUAWEI[@]}"
done
# Wait for all child-processes
for PID in ${PIDSHUAWEI[@]}
do
   wait $PID || exit 1
done

# Ciena
date +"%c: processing Ciena modules " >> $LOG
python yangGeneric.py --allinclusive True --metadata "Ciena https://github.com/YangModels/yang/tree/master/vendor/ciena" --lint True --prefix CIENA --rootdir "$NONIETFDIR/yangmodels/yang/vendor/ciena" >> $LOG 2>&1

# Fujitsu
date +"%c: processing Fujitsu modules " >> $LOG
declare -a PIDSFUJITSU
running=0
for path in $(find $NONIETFDIR/yangmodels/yang/vendor/fujitsu/FSS2-API-Yang -name "yang")
do
   ((running=running+1))
   git=${path##*/fujitsu/}
   yang_removed=${git%/*}
   prefix=${yang_removed#*/}
   prefix=$(echo $prefix | tr -cd '[:alnum:]')
   (python yangGeneric.py --allinclusive True --metadata "Fujitsu https://github.com/FujitsuNetworkCommunications/FSS2-Yang/tree/master/$git" --lint True --prefix Fujitsu$prefix --rootdir "$path" >> $LOG 2>&1) &
   PIDSFUJITSU+=("$!")
   wait_for_processes "${PIDSFUJITSU[@]}"
done
# Wait for all child-processes
for PID in ${PIDSFUJITSU[@]}
do
	wait $PID || exit 1
done

# Nokia
date +"%c: processing Nokia modules " >> $LOG
declare -a PIDSNOKIA
running=0
for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/nokia/*/)
do
   for path2 in $(ls -d $path*/)
   do
      ((running=running+1))
      git=${path2##*/7x50_YangModels/}
      yang_removed=${git%/*}
      prefix=${yang_removed#*/}
      prefix=$(echo $prefix | tr -cd '[:alnum:]'| sed 's/latestsros//g')
      (python yangGeneric.py --allinclusive True --metadata "Nokia $git https://github.com/nokia/7x50_YangModels/tree/master/$git" --lint True --prefix Nokia$prefix --rootdir "$path2" >> $LOG 2>&1) &
      PIDSNOKIA+=("$!")
      wait_for_processes "${PIDSNOKIA[@]}"
   done
done
# Wait for all child-processes
for PID in ${PIDSNOKIA[@]}
do
	wait $PID || exit 1
done

date +"%c: Cleaning up the remaining .fxs " >> $LOG
# clean up of the .fxs files created by confdc
find $NONIETFDIR/yangmodels -name *.fxs ! -name fujitsu-optical-channel-interfaces.fxs -print  | xargs -r rm >> $LOG 2>&1

date +"%c: reloading cache" >> $LOG
read -ra CRED <<< "$CREDENTIALS"
curl -s -X POST -u "${CRED[0]}":"${CRED[1]}" $MY_URI/api/load-cache >> $LOG 2>&1

date +"%c: End of the script!" >> $LOG
