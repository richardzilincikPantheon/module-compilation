#!/usr/bin/env python

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


import os, shutil, argparse

__author__ = 'bclaise@cisco.com'

def remove_directory_content(d, debug_level):
    """
    :param d: the directory from which the content should be removed
    :return: none
    """
    if not os.path.isdir(d):
        return
    for the_file in os.listdir(d):
        file_path = os.path.join(d, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                if debug_level > 0:
                    print("DEBUG: removing the file " + file_path)
            elif os.path.isdir(file_path) and not os.path.islink(file_path): 
                shutil.rmtree(file_path)
                if debug_level > 0:
                    print("DEBUG: removing the subdirectory " + file_path)
        except Exception as e:
            print("Exception: " + str(e))


if __name__ == "__main__":
    """
    Testing functions
    """
    parser = argparse.ArgumentParser(description='Remove Directory Content')
    parser.add_argument("dir", help="The directory content to remove")
    parser.add_argument("--debug", type=int, default=0, help="Debug level; default is 0")
    args = parser.parse_args()

    if args.debug > 0:
        print("DEBUG: attempting to remove the " + args.dir + " directory content")
    remove_directory_content(args.dir, args.debug)
