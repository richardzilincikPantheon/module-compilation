#!/bin/bash

# Copyright The IETF Trust 2021, All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

MAX_PROCESSES=4

wait_for_processes () {
   while [ $(jobs -r | wc -l) -ge $MAX_PROCESSES ]
   do
      sleep 1s
   done
}

source configure.sh
export LOG=$LOGS/YANGgenericstats.log
date +"%c: Starting" >$LOG

# Need to set some ENV variables for subsequent calls in .PY to confd...
source $CONFD_DIR/confdrc >>$LOG 2>&1

# BBF, we need to flatten the directory structure
mkdir -p $TMP/bbf >>$LOG 2>&1
rm -f $TMP/bbf/* >>$LOG 2>&1
find $NONIETFDIR/yangmodels/yang/standard/bbf -name "*.yang" -exec cp {} $TMP/bbf/ \; >>$LOG 2>&1

mkdir -p $MODULES >>$LOG 2>&1

curl -s -H "Accept: application/json" $MY_URI/api/search/modules -o "$TMP/all_modules_data.json" >>$LOG 2>&1

date +"%c: forking all sub-processes" >>$LOG

yang_generic () {
   python $BIN/yangGeneric.py "$@" >>$LOG 2>&1 &
   wait_for_processes
}

# BBF
yang_generic --metadata "BBF Complete Report: YANG Data Models compilation from https://github.com/BroadbandForum/yang/tree/master" --lint --prefix BBF --rootdir "$TMP/bbf/"

# Standard MEF
yang_generic --metadata "MEF: Standard YANG Data Models compilation from https://github.com/MEF-GIT/YANG-public/tree/master/src/model/standard/" --lint --prefix MEFStandard --rootdir "$NONIETFDIR/mef/YANG-public/src/model/standard/"

# Experimental MEF
yang_generic --metadata "MEF: Draft YANG Data Models compilation from https://github.com/MEF-GIT/YANG-public/tree/master/src/model/draft/" --lint --prefix MEFExperimental --rootdir "$NONIETFDIR/mef/YANG-public/src/model/draft/"

# Standard IEEE published
yang_generic --metadata "IEEE: YANG Data Models compilation from https://github.com/YangModels/yang/tree/master/standard/ieee/published: The 'standard/ieee/published' branch is intended for published standards modules (with approved PARs)." --lint --prefix IEEEStandard --rootdir "$NONIETFDIR/yangmodels/yang/standard/ieee/published/"

# Standard IEEE drafts
yang_generic --metadata "IEEE: YANG Data Models compilation from https://github.com/YangModels/yang/tree/master/standard/ieee/draft: The 'standard/ieee/draft' branch is intended for draft modules with an approved Project Authorization Request (PAR)." --lint --prefix IEEEStandardDraft --rootdir "$NONIETFDIR/yangmodels/yang/standard/ieee/draft/"

# Experimental IEEE
yang_generic --metadata "IEEE: Draft YANG Data Models compilation from https://github.com/YangModels/yang/tree/master/experimental/ieee: The 'experimental/ieee' branch is intended for IEEE work that does not yet have a Project Authorization Request (PAR)." --lint --prefix IEEEExperimental --rootdir "$NONIETFDIR/yangmodels/yang/experimental/ieee/"

# Standard IANA
yang_generic --metadata "IANA: Standard YANG Data Models compilation from https://github.com/YangModels/yang/tree/master/standard/iana: The 'standard/iana' branch is intended for IANA-maintained YANG models." --lint --prefix IANAStandard --rootdir "$NONIETFDIR/yangmodels/yang/standard/iana/"

# Openconfig
yang_generic --metadata "Openconfig: YANG Data Models compilation from https://github.com/openconfig/public" --lint --prefix Openconfig --rootdir "$NONIETFDIR/openconfig/public/release/models/"

# ONF Open Transport
yang_generic --metadata "ONF Open Transport: YANG Data Models compilation from https://github.com/OpenNetworkingFoundation/Snowmass-ONFOpenTransport" --lint --prefix ONFOpenTransport --rootdir "$NONIETFDIR/onf/Snowmass-ONFOpenTransport"

# sysrepo internal
yang_generic --metadata "Sysrepo: internal YANG Data Models compilation from https://github.com/sysrepo/yang/tree/master/internal" --lint --prefix SysrepoInternal --rootdir "$NONIETFDIR/sysrepo/yang/internal/"

# sysrepo applications
yang_generic --metadata "Sysrepo: applications YANG Data Models compilation from https://github.com/sysrepo/yang/tree/master/applications" --lint --prefix SysrepoApplication --rootdir "$NONIETFDIR/sysrepo/yang/applications/"


# ETSI
for path in $(ls -d $NONIETFDIR/yangmodels/yang/standard/etsi/*); do
   version=${path##*/etsi/NFV-SOL006-}
   version_number=${version##*v}
   version_alnum=$(echo $version_number | tr -cd '[:alnum:]')
   yang_generic --metadata "ETSI Complete Report: YANG Data Models compilation from https://github.com/etsi-forge/nfv-sol006/tree/$version" --lint --prefix ETSI$version_alnum --rootdir "$NONIETFDIR/yangmodels/yang/standard/etsi/NFV-SOL006-$version/src/yang"
done

wait

if [ "$IS_PROD" = "True" ]; then
   # OpenROADM public
   #
   # OpenROADM directory structure need to be flattened
   # Each branch representing the version is copied to a separate folder
   # This allows to run the yangGeneric.py script on multiple folders in parallel
   cur_dir=$(pwd)
   cd $NONIETFDIR/openroadm/OpenROADM_MSA_Public
   branches=$(git branch --remotes)
   for branch in $branches; do
      version=${branch##*/}
      first_char=${version:0:1}
      if [[ $first_char =~ ^[[:digit:]] ]]; then
         git checkout $version >>$LOG 2>&1
         mkdir -p $TMP/openroadm-public/$version >>$LOG 2>&1
         rm -f $TMP/openroadm-public/$version/* >>$LOG 2>&1
         find $NONIETFDIR/openroadm/OpenROADM_MSA_Public -name "*.yang" -exec cp {} $TMP/openroadm-public/$version/ \; >>$LOG 2>&1
      fi
   done

   date +"%c: forking all sub-processes for OpenROADM versions" >>$LOG
   for path in $(ls -d $TMP/openroadm-public/*/); do
      version=$(basename $path)
      yang_generic --metadata "OpenRoadm $version: YANG Data Models compilation from https://github.com/OpenROADM/OpenROADM_MSA_Public/tree/$version/model" --lint --prefix OpenROADM$version --rootdir "$TMP/openroadm-public/$version/"
   done
   cd $cur_dir

   cisco () {
      # syntax: cisco meta os
      local meta=$1
      local os_upper=$2
      local os_lower=${os_upper,,}
      date +"%c: processing all Cisco $os_upper modules " >>$LOG
      for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/cisco/$os_lower/*/); do
         git=${path##*/cisco/$os_lower/}
         slash_removed=${git%/}
         prefix=${slash_removed#*/}
         prefix2=$(echo $prefix | tr -cd '[:alnum:]')
         yang_generic --allinclusive --metadata "Cisco $meta $prefix from https://github.com/YangModels/yang/tree/main/vendor/cisco/$os_lower/$git" --lint --prefix Cisco$os_upper$prefix2 --rootdir "$path"
      done
   }
   cisco "NX OS" "NX"
   cisco "IOS XE" "XE"
   cisco "IOS XR" "XR"
   cisco "NCS" "SVO"

   date +"%c: processing non Cisco modules " >>$LOG

   # Juniper
   date +"%c: processing Juniper modules " >>$LOG

   # Juniper/14.2 does not contain subdirectories
   path=$NONIETFDIR/yangmodels/yang/vendor/juniper/14.2/
   git=${path##*/juniper/}
   slash_removed=${git%/}
   prefix=${slash_removed#*/}
   prefix2=$(echo $prefix | tr -cd '[:alnum:]')
   yang_generic --allinclusive --metadata "JUNIPER $prefix from https://github.com/Juniper/yang/tree/master/$git" --lint --prefix Juniper$prefix2 --rootdir "$path"

   # Juniper/15* does not exist
   for i in {16..21}; do
      for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/juniper/$i*/*/); do
         git=${path##*/juniper/}
         slash_removed=${git%/}
         prefix=${slash_removed#*/}
         prefix2=$(echo $prefix | tr -cd '[:alnum:]')
         yang_generic --allinclusive --metadata "JUNIPER $prefix from https://github.com/Juniper/yang/tree/master/$git" --lint --prefix Juniper$prefix2 --rootdir "$path"
      done
   done

   # Huawei
   date +"%c: processing Huawei modules " >>$LOG
   for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/huawei/network-router/*/*/); do
      git=${path##*/network-router/}
      slash_removed=${git%/}
      version=${slash_removed%/*}
      platform=${slash_removed#*/}
      prefix=$(echo $slash_removed | tr -cd '[:alnum:]')
      yang_generic --allinclusive --metadata "HUAWEI ROUTER $version $platform https://github.com/Huawei/yang/tree/master/network-router/$git" --lint --prefix NETWORKROUTER$prefix --rootdir "$path"
   done

   # Ciena
   date +"%c: processing Ciena modules " >>$LOG
   yang_generic --allinclusive --metadata "Ciena https://github.com/YangModels/yang/tree/master/vendor/ciena" --lint --prefix CIENA --rootdir "$NONIETFDIR/yangmodels/yang/vendor/ciena"

   # Fujitsu
   date +"%c: processing Fujitsu modules " >>$LOG
   for path in $(find $NONIETFDIR/yangmodels/yang/vendor/fujitsu/FSS2-API-Yang -name "yang"); do
      git=${path##*/fujitsu/}
      yang_removed=${git%/*}
      prefix=${yang_removed#*/}
      prefix=$(echo $prefix | tr -cd '[:alnum:]')
      yang_generic --allinclusive --metadata "Fujitsu https://github.com/FujitsuNetworkCommunications/FSS2-Yang/tree/master/$git" --lint --prefix Fujitsu$prefix --rootdir "$path"
   done

   # Nokia
   date +"%c: processing Nokia modules " >>$LOG
   for path in $(ls -d $NONIETFDIR/yangmodels/yang/vendor/nokia/*/*/); do
      git=${path##*/7x50_YangModels/}
      slash_removed=${git%/}
      prefix=${slash_removed#*/}
      prefix=$(echo $prefix | tr -cd '[:alnum:]' | sed 's/latestsros//g')
      yang_generic --allinclusive --metadata "Nokia $git https://github.com/nokia/7x50_YangModels/tree/master/$git" --lint --prefix Nokia$prefix --rootdir "$path"
   done
else
   date +"%c: This is not PROD environment - skipping vendor modules parsing" >>$LOG
fi

wait

date +"%c: all sub-process have ended" >>$LOG

# Clean up of the .fxs files created by confdc
date +"%c: cleaning up the now useless .fxs files" >>$LOG
find $NONIETFDIR/ -name *.fxs ! -name fujitsu-optical-channel-interfaces.fxs -print | xargs -r rm >>$LOG 2>&1

# Remove temp directory structure created for parsing OpenROADM and BBF yang modules
rm -rf $TMP/bbf/ >>$LOG 2>&1
rm -rf $TMP/openroadm-public/ >>$LOG 2>&1

date +"%c: reloading cache" >>$LOG
read -ra CRED <<<$(sed 's/\"//g' <<<"$CREDENTIALS")
curl -s -X POST -u "${CRED[0]}":"${CRED[1]}" $MY_URI/api/load-cache >>$LOG 2>&1

date +"%c: End of the script!" >>$LOG
