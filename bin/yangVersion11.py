#!/usr/bin/env python

# Copyright The IETF Trust 2019, All Rights Reserved
# Copyright 2015-2018, Cisco Systems
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os

from create_config import create_config
from remove_directory_content import remove_directory_content

__author__ = 'Benoit Claise'
__copyright__ = "Copyright(c) 2015, Cisco Systems, Inc.,  Copyright The IETF Trust 2019, All Rights Reserved"
__license__ = "Apache v2.0"
__email__ = "bclaise@cisco.com"


def YANGversion11(src_path, dest_path, debug):
    """
    YANG 1.1 Processing Tool.
    This is the main (external) API entry for the module.
    The functions copies all YANG 1.1 modules to a yangpath
    :param src_path: The optional directory where to find the source YANG data models
    :param dest_path: The path to store the version 1.1 YANG data models
    :param debug: Determines how much debug output is printed to the console
    """ 

    if debug > 0:
        print("No test condition")
    
    remove_directory_content(dest_path, debug)
    yang_model_list = [f for f in os.listdir(src_path) if os.path.isfile(os.path.join(src_path, f))]
    yang_model_list_v11 = []
    
    for yang_model in yang_model_list:      
        bash_command = "grep yang-version " + src_path  + yang_model + " | grep 1.1"
        if debug > 0:
            print("bash command: " + bash_command)
        temp_result = os.popen(bash_command).read()
        if "1.1" in temp_result:
            if debug > 0:
                print("DEBUG: " + yang_model + " is version 1.1 ")
            yang_model_list_v11.append(yang_model)
            # copy function below could be improved with python command, as opposed to a bash
            bash_command = "cp  " + src_path + "/" + yang_model + " " + dest_path + "/" + yang_model
            temp_result = os.popen(bash_command).read()
    if debug > 0:
        print("DEBUG: YANG Model list with YANG version 1.1: " )
        if yang_model_list_v11:
            print(yang_model_list_v11)
        else:
            print("  No YANG modules version 1.1")

 
# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


if __name__ == '__main__':
    config = create_config()
    ietf_directory = config.get('Directory-Section', 'ietf-directory')

    src_path = os.path.join(ietf_directory, 'YANG')

    parser = argparse.ArgumentParser(description='YANG 1.1 Processing Tool. Copy all YANG 1.1 modules to destpath')
    parser.add_argument('--destpath',
                        help='Path to store the version 1.1 YANG data models. '
                             'Default is "{}/YANG-v11/"'.format(ietf_directory),
                        type=str,
                        default='{}/YANG-v11/'.format(ietf_directory))
    parser.add_argument('--debug',
                        help='Debug level - default is 0',
                        type=int,
                        default=0)

    args = parser.parse_args()
        
    YANGversion11(src_path, args.destpath,args.debug)
