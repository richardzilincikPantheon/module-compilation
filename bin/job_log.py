#!/usr/bin/env python

# Copyright The IETF Trust 2020, All Rights Reserved
# This software is licensed to you under the terms of the Apache License, Version 2.0 (the 'License").
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
# The code, technical concepts, and all information contained herein, are the property of Cisco Technology, Inc.
# and/or its affiliated entities, under various laws including copyright, international treaties, patent,
# and/or contract. Any use of the material herein must be in accordance with the terms of the License.
# All rights not expressly granted by the License are reserved.
# Unless required by applicable law or agreed to separately in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

__author__ = "Slavomir Mazur"
__copyright__ = "Copyright The IETF Trust 2020, All Rights Reserved"
__license__ = "Apache License, Version 2.0"
__email__ = "slavomir.mazur@pantheon.tech"

import sys
import json
import argparse

if sys.version_info >= (3, 4):
    import configparser as ConfigParser
else:
    import ConfigParser

if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config._interpolation = ConfigParser.ExtendedInterpolation()
    config.read('/etc/yangcatalog/yangcatalog.conf')
    temp_dir = config.get('Directory-Section', 'temp')
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', default=0, help='Cronjob start time', required=True)
    parser.add_argument('--end', default=0, help='Cronjob end time', required=True)
    parser.add_argument('--status', default='Fail', help='Result of cronjob run', required=True)
    parser.add_argument('--filename', default='', help='Name of job', required=True)
    args = parser.parse_args()
    result = {}
    result['start'] = int(args.start)
    result['end'] = int(args.end)
    result['status'] = args.status
    if args.status == 'Success':
        result['last_successfull'] = int(args.end)
    try:
        with open('{}/cronjob.json'.format(temp_dir), 'r') as f:
            file_content = json.load(f)
    except:
        file_content = {}

    file_content[args.filename] = result

    with open('{}/cronjob.json'.format(temp_dir), 'w') as f:
        f.write(json.dumps(file_content, indent=4))
