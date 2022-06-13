# Copyright The IETF Trust 2022, All Rights Reserved
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


__author__ = 'Richard Zilincik'
__copyright__ = 'Copyright The IETF Trust 2022, All Rights Reserved'
__license__ = 'Apache License, Version 2.0'
__email__ = 'richard.zilincik@pantheon.tech'

import unittest
import os
from unittest import mock

import yangGeneric as yg


class TestYangGeneric(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource_path = os.path.join(os.getenv('VIRTUAL_ENV', '/sdo_analysis'), 'tests/resources/yangGeneric')

    def test_list_of_yang_modules_in_subdir(self):
        result = yg.list_of_yang_modules_in_subdir(os.path.join(self.resource_path, 'dir'), 0)
        self.assertEqual(
            sorted(result),
            [
                '/sdo_analysis/tests/resources/yangGeneric/dir/bar.yang',
                '/sdo_analysis/tests/resources/yangGeneric/dir/foo.yang',
                '/sdo_analysis/tests/resources/yangGeneric/dir/subdir/subfoo.yang',
                '/sdo_analysis/tests/resources/yangGeneric/dir/subdir/subsubdir/subsubfoo.yang'
            ]
        )

    def test_pyang_compilation_status(self):
        result = yg.pyang_compilation_status('warning: foo\nerror: bar\nfoobar\n')
        self.assertEqual(result, 'FAILED')

        result = yg.pyang_compilation_status('foo\nwarning: bar\n foobar\n')
        self.assertEqual(result, 'PASSED WITH WARNINGS')

        result = yg.pyang_compilation_status('')
        self.assertEqual(result, 'PASSED')

        result = yg.pyang_compilation_status('foo\nbar\nfoobar\n')
        self.assertEqual(result, 'UNKNOWN')
    
    def test_confd_compilation_status(self):
        result = yg.confd_compilation_status('warning: foo\nerror: bar\nfoobar\n')
        self.assertEqual(result, 'FAILED')

        result = yg.confd_compilation_status('foo\nwarning: bar\n foobar\n')
        self.assertEqual(result, 'PASSED WITH WARNINGS')

        result = yg.confd_compilation_status('')
        self.assertEqual(result, 'PASSED')

        result = yg.confd_compilation_status('foo\nbar\nfoobar\n')
        self.assertEqual(result, 'UNKNOWN')

        # NOTE: is this intended behavior?
        result = yg.confd_compilation_status('error: foo\nerror: cannot compile submodules; compile the module instead\nbar\n')
        self.assertEqual(result, 'PASSED')

    def test_yuma_compilation_status(self):
        result = yg.yuma_compilation_status(
            'foo@bar.yang:2.2: warning(42): foobar\n'
            'foo@bar.yang:1.1: error(42): foobar\n'
            'foo@bar.yang:3.3: error(332): foobar\n'
            '*** 2 Errors, 1 Warnings',
            'foo@bar.yang'
        )
        self.assertEqual(result, 'FAILED')

        result = yg.yuma_compilation_status(
            'foo@bar.yang:3.3: error(332): foobar\n'
            'foo@bar.yang:2.2: warning(42): foobar\n'
            'bar@foo.yang:1.1: error(42): foobar\n'
            '*** 1 Errors, 1 Warnings',
            'foo@bar.yang'
        )
        self.assertEqual(result, 'PASSED WITH WARNINGS')

        result = yg.yuma_compilation_status(
            'foo@bar.yang:3.3: error(332): foobar\n'
            'bar@foo.yang:1.1: error(42): foobar\n'
            'bar@foo.yang:3.3: warning(42): foobar\n'
            'foo@bar.yang:3.3: error(332): foobar\n'
            'far@boo.yang:4.4: error(42): foobar\n'
            '*** 2 Errors, 0 Warnings',
            'foo@bar.yang'
        )
        self.assertEqual(result, 'PASSED')

        result = yg.yuma_compilation_status('', 'foo@bar.yang')
        self.assertEqual(result, 'PASSED')

        result = yg.yuma_compilation_status('foo\nbar\nfoobar\n', 'foo@bar.yang')
        self.assertEqual(result, 'UNKNOWN')

    def test_yanglint_compilation_status(self):
        result = yg.yanglint_compilation_status('warn: foo\nerr : bar\nfoobar\n')
        self.assertEqual(result, 'FAILED')

        result = yg.yanglint_compilation_status(
            'err : Input data contains submodule which cannot be parsed directly without its main module.\n foobar'
        )
        self.assertEqual(result, 'PASSED')

        result = yg.yanglint_compilation_status('foo\nwarn: bar\n foobar\n')
        self.assertEqual(result, 'PASSED WITH WARNINGS')

        result = yg.yanglint_compilation_status('')
        self.assertEqual(result, 'PASSED')

        result = yg.yanglint_compilation_status('foo\nbar\nfoobar\n')
        self.assertEqual(result, 'UNKNOWN')

    def test_combined_compilation_status(self):
        result = yg.combined_compilation_status(['PASSED', 'FAILED', 'PASSED WITH WARNINGS', 'UNKNOWN'])
        self.assertEqual(result, 'FAILED')

        result = yg.combined_compilation_status(['PASSED', 'PASSED', 'PASSED WITH WARNINGS', 'UNKNOWN'])
        self.assertEqual(result, 'PASSED WITH WARNINGS')

        result = yg.combined_compilation_status(['PASSED', 'PASSED', 'PASSED', 'PASSED'])
        self.assertEqual(result, 'PASSED')

        result = yg.combined_compilation_status(['PASSED', 'UNKNOWN', 'PASSED', 'PASSED'])
        self.assertEqual(result, 'UNKNOWN')

    def test_get_mod_rev(self):
        result = yg.get_mod_rev(os.path.join(self.resource_path, 'yang-catalog@2017-09-26.yang'))
        self.assertEqual(result, 'yang-catalog@2017-09-26')

        result = yg.get_mod_rev(os.path.join(self.resource_path, 'yang-catalog@2018-04-03.yang'))
        self.assertEqual(result, 'yang-catalog@2018-04-03')

    @mock.patch('requests.get')
    def test_get_modules(self, mock_get: mock.MagicMock):
        mock_get.return_value = mock.MagicMock(json=lambda: {'requested': 'data'})

        with mock.patch('yangGeneric.open', mock.mock_open(read_data='{"loaded": "data"}')):
            result = yg.get_modules('/var/yang/tmp', 'http://0.0.0.0')
        self.assertEqual(result, {'loaded': 'data'})

        with mock.patch('yangGeneric.open', mock.mock_open(read_data='{}')):
            result = yg.get_modules('/var/yang/tmp', 'http://0.0.0.0')
        self.assertEqual(result, {'requested': 'data'})

        with mock.patch('yangGeneric.open', mock.MagicMock(side_effect=Exception)):
            result = yg.get_modules('/var/yang/tmp', 'http://0.0.0.0')
        self.assertEqual(result, {'requested': 'data'})
