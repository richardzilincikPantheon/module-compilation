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

export YANG=/home/yang
export YANGVAR=`get_config.py --section Directory-Section --key var`
export BIN=$YANG/sdo_analysis/bin
export CONF=$YANG/sdo_analysis/conf
export BACKUPDIR=$YANGVAR/backup
export CONFD_DIR=/opt/confd
export PYANG=/usr/local/bin/pyang

#
# Repositories
#
export NONIETFDIR=$YANGVAR/nonietf
export IETFDIR=$YANGVAR/ietf
export MODULES=$YANGVAR/yang/modules

#
# Working directories
export LOGS=`get_config.py --section Directory-Section --key logs`
export TMP=`get_config.py --section Directory-Section --key temp`

#
# Where the HTML pages lie
#
export WEB_PRIVATE=`get_config.py --section Web-Section --key private_directory`
export WEB=`get_config.py --section Web-Section --key public_directory`
