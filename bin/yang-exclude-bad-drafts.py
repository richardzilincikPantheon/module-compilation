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

import argparse
import os

from create_config import create_config

__author__ = 'bclaise@cisco.com'


SOURCE = '/etc/yangcatalog/IETF-draft-list-with-no-YANG-problem.txt'


def list_lines_from_file(path, debug_level):
    """
    Returns a list of all the lines in the file
    :param path: file path path
    :param debug_level: debug level
    :return: a list of all the lines in the file
    """
    list_of_line = []
    with open(path) as f:
        for line in f:
            line = line.replace("\n", "")
            if debug_level > 1:
               print("  line: " + line)
            list_of_line.append(line)
    if debug_level > 1:
        print(" List of lines from the list_lines_from_file function" + str(list_of_line))
    if not list_of_line:
        if debug_level > 1:
            print(" List empty from the list_lines_from_file function")
    return list_of_line


def remove_files(files, directory, debug_level):
    """
    Remove a list of files from a directory
    :param files: list of files to remove
    :param directory: directory
    :param debug_level: debug level
    """
    for file in files:
        bash_command = "rm -f {}".format(os.path.join(directory, file))
        if debug_level > 1:
            print("bash_command: " + bash_command)
        temp_result = os.popen(bash_command).readlines()
        if debug_level > 0:
            print(temp_result)
    return 


def replace_draft_version_by_asterix(ll, debug_level):
    """
    Replace the draft version by an asterix
    :param ll: list of lines
    :param debug_level: debug level
    :return: a list of all the lines in the file, with the draft version replaced by *
    """
    newll = []
    for l in ll:
        head, sep, tail = l.partition('.')
        l = head.rstrip('-0123456789') + "*"
        if debug_level > 0:
            print("replace_draft_version_by_asterix: new file " + l)
        newll.append(l)
    if debug_level > 0:
        print("replace_draft_version_by_asterix: new list " + str(newll))
    return newll


if __name__ == '__main__':
    """
    Testing functions
    """
    config = create_config()
    ietf_directory = config.get('Directory-Section', 'ietf-directory')

    parser = argparse.ArgumentParser(description='Remove drafts well-known as having xym errors, '
                                                 'but that do not contain YANG models')
    parser.add_argument('--dstdir',
                        help='Directory from which to remove the drafts. '
                             'Default is "{}/my-id-mirror/"'.format(ietf_directory),
                        type=str,
                        default='{}/my-id-mirror/'.format(ietf_directory))
    parser.add_argument('--debug',
                        help='Debug level - default is 0',
                        type=int,
                        default=0)
    args = parser.parse_args()

    ll = list_lines_from_file(SOURCE, args.debug)
    llasterix = replace_draft_version_by_asterix(ll, args.debug)
    dir = os.path.dirname(SOURCE)
    remove_files(llasterix, args.dstdir, args.debug)
