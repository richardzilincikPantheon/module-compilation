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
        self.resource_path = os.path.join(os.environ['SDO_ANALYSIS'], 'tests/resources/yangGeneric')
        yg.debug_level = 0
        yg.draft_path = '/foo/bar'
        yg.web_url = 'https://foo.bar'

    def test_list_of_yang_modules_in_subdir(self):
        result = yg.list_of_yang_modules_in_subdir(os.path.join(self.resource_path, 'dir'), 0)
        self.assertEqual(
            sorted(result),
            [
                os.path.join(os.environ['SDO_ANALYSIS'], 'tests/resources/yangGeneric/dir/bar.yang'),
                os.path.join(os.environ['SDO_ANALYSIS'], 'tests/resources/yangGeneric/dir/foo.yang'),
                os.path.join(os.environ['SDO_ANALYSIS'], 'tests/resources/yangGeneric/dir/subdir/subfoo.yang'),
                os.path.join(os.environ['SDO_ANALYSIS'], 'tests/resources/yangGeneric/dir/subdir/subsubdir/subsubfoo.yang')
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

    def test_metadata_generator(self):
        compilation_results = {
            'pyang_lint': 'foo',
            'pyang': 'bar'
        }
        mg = yg.MetadataGenerator(compilation_results, 'FAILED', '/foo/bar.yang')

        result = mg.get_file_compilation()
        self.assertEqual(result, ['FAILED', 'foo', 'bar'])

        result = mg.get_confd_metadata()
        self.assertEqual(result, {'compilation-status': 'FAILED'})

    @mock.patch('yangGeneric.document_dict', {'bar.yang': 'rfc42.txt'})
    def test_rfc_metadata_generator(self):
        compilation_results = {
            'pyang_lint': 'foo',
            'pyang': 'bar',
            'confdrc': 'boo',
            'yumadump': 'far',
            'yanglint': 'foobar',
        }
        mg = yg.RfcMetadataGenerator(compilation_results, 'FAILED', '/foo/bar.yang')

        result = mg.get_file_compilation()
        self.assertEqual(result, ['FAILED', 'foo', 'bar', 'boo', 'far', 'foobar'])

        result = mg.get_confd_metadata()
        self.assertEqual(result, {
            'compilation-status': 'FAILED',
            'reference': 'https://datatracker.ietf.org/doc/html/rfc42',
            'document-name': 'rfc42.txt',
            'author-email': None
        })

    @mock.patch('yangGeneric.extract_email_string')
    def test_draft_metadata_generator(self, mock_extract_email_string):
        yg.document_dict = {'bar.yang': 'draft-foo-bar-42.txt'}
        compilation_results = {
            'pyang_lint': 'foo',
            'pyang': 'bar',
            'confdrc': 'boo',
            'yumadump': 'far',
            'yanglint': 'foobar',
        }

        def extract_email_string(draft_path: str, email_domain: str, debug_level: int):
            if email_domain == '@cisco.com':
                return 'foo@cisco.com'
            elif email_domain == '@tail-f.com':
                return 'foo@tail-f.com'
            else:
                raise Exception
        
        mock_extract_email_string.side_effect = extract_email_string
        document_name = 'draft-foo-bar-42.txt'
        version_number = 'draft-foo-bar-42'.split('-')[-1]
        mailto = '{}@ietf.org'.format('draft-foo-bar-42')
        draft_name = 'draft-foo-bar'
        datatracker_url = 'https://datatracker.ietf.org/doc/{}/{}'.format(draft_name, version_number)
        draft_url_anchor = '<a href="{}">{}</a>'.format(datatracker_url, document_name)
        email_anchor = '<a href="mailto:{}">Email Authors</a>'.format(mailto)
        cisco_email_anchor = '<a href="mailto:foo@cisco.com,foo@tail-f.com">Email Cisco Authors Only</a>'
        yang_model_anchor = '<a href="https://foo.bar/YANG-modules/bar.yang">Download the YANG model</a>'
        mg = yg.DraftMetadataGenerator(compilation_results, 'FAILED', '/foo/bar.yang')

        expected = [draft_url_anchor, email_anchor, cisco_email_anchor, yang_model_anchor, 'FAILED']
        expected += [result for result in compilation_results.values()]
        result = mg.get_file_compilation()
        self.assertEqual(result, expected)

        result = mg.get_confd_metadata()
        self.assertEqual(result, {
            'compilation-status': 'FAILED',
            'reference': datatracker_url,
            'document-name': document_name,
            'author-email': mailto
        })

    @mock.patch('yangGeneric.extract_email_string')
    def test_example_metadata_generator(self, mock_extract_email_string):
        yg.document_dict = {'bar.yang': 'draft-foo-bar-42.txt'}
        compilation_results = {
            'pyang_lint': 'foo',
            'pyang': 'bar',
            'confdrc': 'boo',
            'yumadump': 'far',
            'yanglint': 'foobar',
        }

        def extract_email_string(draft_path: str, email_domain: str, debug_level: int):
            if email_domain == '@cisco.com':
                return 'foo@cisco.com'
            elif email_domain == '@tail-f.com':
                return 'foo@tail-f.com'
            else:
                raise Exception
        
        mock_extract_email_string.side_effect = extract_email_string
        document_name = 'draft-foo-bar-42.txt'
        version_number = 'draft-foo-bar-42'.split('-')[-1]
        mailto = '{}@ietf.org'.format('draft-foo-bar-42')
        draft_name = 'draft-foo-bar'
        datatracker_url = 'https://datatracker.ietf.org/doc/{}/{}'.format(draft_name, version_number)
        draft_url_anchor = '<a href="{}">{}</a>'.format(datatracker_url, document_name)
        email_anchor = '<a href="mailto:{}">Email Authors</a>'.format(mailto)
        mg = yg.ExampleMetadataGenerator(compilation_results, 'FAILED', '/foo/bar.yang')

        expected = [draft_url_anchor, email_anchor, 'FAILED']
        expected += [result for result in compilation_results.values()]
        result = mg.get_file_compilation()
        self.assertEqual(result, expected)

        result = mg.get_confd_metadata()
        self.assertEqual(result, {})