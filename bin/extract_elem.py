#!/usr/bin/env python

# Copyright (c) 2015-2018 Cisco and/or its affiliates.

# This software is licensed to you under the terms of the Apache License, Version 2.0 (the "License").
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
# The code, technical concepts, and all information contained herein, are the property of Cisco Technology, Inc.
# and/or its affiliated entities, under various laws including copyright, international treaties, patent,
# and/or contract. Any use of the material herein must be in accordance with the terms of the License.
# All rights not expressly granted by the License are reserved.
# Unless required by applicable law or agreed to separately in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

__author__ = 'Eric Vyncke'
__copyright__ = "Copyright(c) 2019, Cisco Systems, Inc."
__email__ = "evyncke@cisco.com"

import re

def extract_elem(module_fname, extract_dir, elem_type):
    # Let's parse the module, we will create files when seeing the keywords such as 'identity-networking-instance-type.txt'
    open_bracket_count = 0
    in_comment = False
    found_keyword = False
    file_out = None
    with open(module_fname, 'r', encoding='latin-1', errors='ignore') as ym:
        for line in ym:
            if not found_keyword: # Still looking for keyword
                comment_start = line.find('//')
                if in_comment:
                    in_comment = (line.find('*/') < 0)
                else:
                    in_comment = (line.find('/*') >= 0)
                keyword_start = line.find(elem_type)
                # Check whether the keyword is outside of comments and not too early on the line (it could appear in description...)
                if keyword_start > 0 and keyword_start < 5 and (keyword_start < comment_start or comment_start < 0) and not in_comment:
                    found_keyword = True
            if found_keyword: # Processing the keyword
                if file_out == None:
                    file_out = open(extract_dir + '/' + elem_type + '-' + get_identifier(elem_type, line) + '.txt', 'w')
#                    print("Creating file: " + extract_dir + '/' + elem_type + '-' + get_identifier(elem_type, line) + '.txt')
                file_out.write(line)
                if line.find('{') >= 0:
                    open_bracket_count = open_bracket_count + 1
                if line.find('}') >= 0:
                    open_bracket_count = open_bracket_count - 1
                # Are we out of the outermost brackets?
                if open_bracket_count == 0:
#                    file_out.write("\n")
                    file_out.close()
                    file_out = None
                    found_keyword = False

def get_identifier(elem_type, line):
    match = re.match('\s*' + elem_type + '\s+([-_\w]+)' + '\s*{', line)
    if match:
        return match.group(1)
    else:
        print("*** Did not find '" + elem_type + "' in line: ' " + line + "'.")
        return None

if __name__ == "__main__":
	extract_elem('/var/www/html/YANG-modules/ietf-nat@2018-09-27.yang', '/tmp/extract', 'typedef')
