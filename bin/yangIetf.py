#!/usr/bin/env python

# Copyright The IETF Trust 2019, All Rights Reserved
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

# TODO, only check files more recent than a date
__author__ = 'Benoit Claise, Eric Vyncke'
__copyright__ = "Copyright(c) 2015-2019, Cisco Systems, Inc.,  Copyright The IETF Trust 2019, All Rights Reserved"
__email__ = "bclaise@cisco.com, evyncke@cisco.com"

import argparse
import configparser
import datetime
import glob
import json
import os
import shutil
import time

import HTML
import jinja2
import requests
from extract_elem import extract_elem
from extract_emails import extract_email_string
from remove_directory_content import remove_directory_content
from xym import xym

# ----------------------------------------------------------------------
# Cash versions
# ----------------------------------------------------------------------
confd_version = ''
pyang_version = ''
yanglint_version = ''
yumadumppro_version = ''


# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------


def run_pyang(pyang_exec, model, ietf, yangpath, debug_level):
    """
    Run PYANG on the YANG model, with or without the --ietf flag
    :param model: The file name for the model
    :param ietf: a boolean, True for the --ietf pyang flag, False for no --ietf pyang flag
    :param yangpath
    :param debug_level
    :return: the outcome of the PYANG compilation
    """
    os.chdir(yangpath)
    if ietf:
        bash_command = pyang_exec + " --path=\"$MODULES\" --ietf " + model + " 2>&1"
    else:
        bash_command = pyang_exec + " --path=\"$MODULES\" " + model + " 2>&1"
    if debug_level:
        print("DEBUG: " + " in run_pyang: bash_command contains " + bash_command)
    return os.popen(bash_command).read()


def run_pyang_version(pyang_exec, debug_level=0):
    """
    Return the pyang version.
    :param debug_level
    :return: a string composed of the pyang version
    """
    global pyang_version
    if pyang_version == '':
        bash_command = pyang_exec + " -v 2>&1"
        if debug_level:
            print("DEBUG: " + " in run_pyang: bash_command contains " + bash_command)
        pyang_version = os.popen(bash_command).read()
    return pyang_version


def run_confd(confdc_exec, model, yangpath, debug_level):
    """
    Run confdc on the YANG model
    :param model: The file name for the model
    :param yangpath:
    :return: the outcome of the PYANG compilationf
    """
    os.chdir(yangpath)
    bash_command = confdc_exec + " --yangpath " + confdc_yangpath + " -w TAILF_MUST_NEED_DEPENDENCY -c " + model + " 2>&1"
    if debug_level:
        print("DEBUG: " + " in run_confd: bash_command contains " + bash_command)
    return os.popen(bash_command).read()


def run_confd_version(confdc_exec, debug_level=0):
    """
    Return the confd version
    :return: a string composed of the confd version
    """
    global confd_version
    if confd_version == '':
        bash_command = confdc_exec + " --version 2>&1"
        if debug_level:
            print("DEBUG: " + " in run_confd: bash_command contains " + bash_command)
        confd_version = "confd version " + os.popen(bash_command).read()
    return confd_version


def run_yumadumppro(model, yangpath, debug_level):
    """
    Run run_yumadump-pro on the YANG model
    yangdump-pro  --config=/etc/yumapro/yangdump-pro.conf module.yang
    :param model: The file name for the model
    :param yangpath: The directory where the model is
    :param configfilepath: for the --config=/etc/yumapro/yangdump-pro.conf
    :return: the outcome of the PYANG compilation
    """
    os.chdir(yangpath)
    bash_command = "yangdump-pro --quiet-mode --config=/etc/yumapro/yangdump-pro.conf " + model + " 2>&1"
    if debug_level:
        print("DEBUG: " + " in yangdump-pro: bash_command contains " + bash_command)
    result = os.popen(bash_command).read()
    result = result.rstrip()
    result = result.lstrip()
    result = result.replace(model, '')
    if "*** 0 Errors, 0 Warnings" in result:
        result = ""
    return result


def run_yumadumppro_version(debug_level=0):
    """
    Return the yangdump-pro version
    :param debug
    :return: a string composed of the yangdump-pro version
    """
    global yumadumppro_version
    if yumadumppro_version == '':
        bash_command = "yangdump-pro --version 2>&1"
        if debug_level:
            print("DEBUG: " + " in yangdump-pro: bash_command contains " + bash_command)
        yumadumppro_version = os.popen(bash_command).read()
    return yumadumppro_version


def run_yanglint(model, yangpath, debug_level):
    """
    Run yanglint on the YANG model
    :param model: The file name for the model
    :param yangpath: The directory where the model is
    :return: the outcome of the PYANG compilationf
    """
    os.chdir(yangpath)
    bash_command = "yanglint -V -i -p $MODULES " + model + " 2>&1"
    if debug_level:
        print("DEBUG: " + " in run_yanglint: bash_command contains " + bash_command)
    return os.popen(bash_command).read()


def run_yanglint_version(debug_level=0):
    """
    Return the yanglint version
    :param debug
    :return: a string composed of the yanglint version
    """
    global yanglint_version
    if yanglint_version == '':
        bash_command = "yanglint -v 2>&1"
        if debug_level:
            print("DEBUG: " + " in run_yanglint: bash_command contains " + bash_command)
        yanglint_version = os.popen(bash_command).read()
    return yanglint_version


def generate_html_table(l, h, htmlpath, file_name):
    """
    Create a table out of the dict and generate a HTML file
    # status: in progress. Still one issue with <br>

    :param l: The value list to generate the HTML table
    :param h: The header list to generate the HTML table
    :param htmlpath: The directory where the HTML file will be created
    :param file_name: The file name to be created
    :return: None
    """
    generated = ["Generated on " + time.strftime("%d/%m/%Y") + " by the YANG Catalog"]
    htmlcode = HTML.list(generated)
    htmlcode1 = HTML.table(l, header_row=h)
    f = open(htmlpath + file_name, 'w', encoding='utf-8')
    f.write(htmlcode)
    f.write(htmlcode1)
    f.close()
    os.chmod(htmlpath + file_name, 0o664)


def generate_html_list(l, htmlpath, file_name):
    """
    Create a table out of the dict and generate a HTML file
    # status: in progress. Still one issue with <br>

    :param l: The list to generate the HTML table
    :param htmlpath: The directory where the HTML file will be created
    :param file_name: The file name to be created
    :return: None
    """
    generated = ["Generated on " + time.strftime("%d/%m/%Y") + " by the YANG Catalog"]
    htmlcode = HTML.list(generated)
    htmlcode1 = HTML.list(l)
    f = open(htmlpath + file_name, 'w', encoding='utf-8')
    f.write(htmlcode)
    f.write(htmlcode1)
    f.close()
    os.chmod(htmlpath + file_name, 0o664)


def dict_to_list(in_dict):
    """
    Create a list out of a dictionary
    :param in_dict: The input dictionary
    :return: List
    """
    dictlist = []
    for key, value in in_dict.items():
        temp_list = []
        temp_list.append(key)
        for i in range(len(value)):
            temp_list.append(value[i])
        dictlist.append(temp_list)
    return dictlist


def dict_to_list_rfc(in_dict):
    """
    Create a list out of a dictionary
    :param in_dict: The input dictionary
    :return: List
    """
    dictlist = []
    for key, value in in_dict.items():
        dictlist.append((key, str(value)))
    return dictlist


def list_br_html_addition(l):
    """
    # Replace the /n by the <br> HTML tag throughout the list
    # status: in progress.

    :param l: The list
    :return: List
    """
    for sublist in l:
        for i in range(len(sublist)):
            if type(sublist[i]) == type(''):
                sublist[i] = sublist[i].replace("\n", "<br>")
    return l


def invert_yang_modules_dict(in_dict, debug_level):
    """
    Invert the dictionary of key:draft name, value:list of YANG models
    Into a dictionary of key:YANG model, value:draft name

    :param in_dict: input dictionary
    :return: inverted output dictionary
    """
    if debug_level > 0:
        print("DEBUG: in invert_yang_modules_dict: print dictionary before inversion")
        print("DEBUG: " + str(in_dict))
    inv_dict = {}
    for k, v in in_dict.items():
        for l in in_dict[k]:
            inv_dict[l] = k
    if debug_level > 0:
        print("DEBUG: in invert_yang_modules_dict: print dictionary before inversion")
        print("DEBUG: " + str(inv_dict))
    return inv_dict


def number_of_yang_modules_that_passed_compilation(in_dict, compilation_condition):
    """
    return the number of drafts that passed the pyang compilation
    :in_dict : the "PASSED" or "FAILED" is in the 3rd position of the list,
               in the dictionary key:yang-model, list of values
    : compilation_condition: a string
                             currently 3 choices: PASSED, PASSED WITH WARNINGS, FAILED
    :return: the number of "PASSED" YANG models
    """
    t = 0
    for k, v in in_dict.items():
        if in_dict[k][3] == compilation_condition:
            t += 1
    return t


def write_dictionary_file_in_json(in_dict, path, file_name):
    """
    Create a file, in json, with my directory data
    For testing purposes.
    # status: in progress.

    :param in_dict: The dictionary
    :param path: The directory where the json file with be created
    :param file_name: The file name to be created
    :return: None
    """
    with open(path + file_name, 'w', encoding='utf-8') as fw:
        fw.write(json.dumps(in_dict, indent=2, sort_keys=True, separators=(',', ': ')))
    os.chmod(path + file_name, 0o664)


def move_old_examples_YANG_modules_from_RFC(path, path2, debug_level):
    """
    Move some YANG modules, which are documented at http://www.claise.be/IETFYANGOutOfRFCNonStrictToBeCorrected.html:
    ietf-foo@2010-01-18.yang, hw.yang, hardware-entities.yang, udmcore.yang, and ct-ipfix-psamp-example.yang
    Those YANG modules, from old RFCs, don't follow the example- conventions
    :param path: the path from where we move the YANG modules
    :param path2: the path to where we move the YANG modules
    :param debug_level: debugging level
    :return: none
    """
    with open('{}/resources/old-rfcs.json'.format(os.path.dirname(os.path.realpath(__file__))), 'r') as f:
        modules = json.load(f)
    for y in modules:
        if not os.path.isfile(path + y):
            continue
        bash_command = "mv " + path + y + " " + path2 + y
        temp_result = os.popen(bash_command).read()
        if debug_level > 0:
            print("DEBUG: " + " move_old_examples_YANG_modules_from_RFC: error " + temp_result)


def remove_invalid_files(dir, yang_dict):
    """
    Remove YANG modules in directory having invalid filenames. The root cause is XYM extracting YANG modules with non valid filename...
    :param dir: the directory to analyze for invalid filenames.
    :return none
    """
    for full_fname in glob.glob(dir + '/' + '*.yang'):
        fname = os.path.basename(full_fname)
        if ' ' in fname:
            os.remove(full_fname)
            if yang_dict.get(fname):
                yang_dict.pop(fname)
            print("Invalid YANG module removed: " + full_fname)
        if '@YYYY-MM-DD' in fname:
            os.remove(full_fname)
            if yang_dict.get(fname):
                yang_dict.pop(fname)
            print("Invalid YANG module removed: " + full_fname)
        if fname.startswith('.yang'):
            os.remove(full_fname)
            if yang_dict.get(fname):
                yang_dict.pop(fname)
            print("Invalid YANG module removed: " + full_fname)
        if fname.startswith('@'):
            os.remove(full_fname)
            if yang_dict.get(fname):
                yang_dict.pop(fname)
            print("Invalid YANG module removed: " + full_fname)


def combined_compilation(yang_file, result_pyang, result_no_ietf_flag, result_confd, result_yuma, result_yanglint):
    """
    Determine the combined compilation results
    :result_pyang: compilation results from pyang --ietf
    :result_no_ietf_flag: compilation results from pyang
    :result_confd: compilation from confd
    :result_yuma: compilation from yuma
    :result_yanglint: compilation from yanglint
    :return: the combined compilatiion result
    """
    if "error" in result_pyang:
        compilation_pyang = "FAILED"
    elif "warning" in result_pyang:
        compilation_pyang = "PASSED WITH WARNINGS"
    elif result_pyang == "":
        compilation_pyang = "PASSED"
    else:
        compilation_pyang = "UNKNOWN"

    # logic for pyang compilation result:
    if "error" in result_no_ietf_flag:
        compilation_pyang_no_ietf = "FAILED"
    elif "warning" in result_no_ietf_flag:
        compilation_pyang_no_ietf = "PASSED WITH WARNINGS"
    elif result_no_ietf_flag == "":
        compilation_pyang_no_ietf = "PASSED"
    else:
        compilation_pyang_no_ietf = "UNKNOWN"

    # logic for confdc compilation result:
    #    if "error" in result_confd and yang_file in result_confd:
    if "error" in result_confd:
        compilation_confd = "FAILED"
    #   The following doesn't work. For example, ietf-diffserv@2016-06-15.yang, now PASSED (TBC):
    #     Error: 'ietf-diffserv@2016-06-15.yang' import of module 'ietf-qos-policy' failed
    #     ietf-diffserv@2016-06-15.yang:11.3: error(250): definition not found
    #   This issue is that an import module that fails => report the main module as FAILED
    #   Another issue with ietf-bgp-common-structure.yang
    # If the error is on the module itself, then, that's an error
    elif "warning" in result_confd:
        compilation_confd = "PASSED WITH WARNINGS"
    elif result_confd == "":
        compilation_confd = "PASSED"
    else:
        compilation_confd = "UNKNOWN"
    # "cannot compile submodules; compile the module instead" error  message
    # => still print the message, but doesn't report it as FAILED
    if "error: cannot compile submodules; compile the module instead" in result_confd:
        compilation_confd = "PASSED"

    # logic for yumaworks compilation result:
    # remove the draft name from result_yuma
    if result_yuma == "":
        compilation_yuma = "PASSED"
    elif "0 Errors, 0 Warnings" in result_yuma:
        compilation_yuma = "PASSED"
    elif "Error" in result_yuma and yang_file in result_yuma and "0 Errors" not in result_yuma:
        # This is an approximation: if Error in an imported module, and warning on this current module
        # then it will report the module as FAILED
        # Solution: look at line by line comparision of Error and yang_file
        compilation_yuma = "FAILED"
    elif "Warning" in result_yuma and yang_file in result_yuma:
        compilation_yuma = "PASSED WITH WARNINGS"
    elif "Warning" in result_yuma and yang_file not in result_yuma:
        compilation_yuma = "PASSED"
    else:
        compilation_yuma = "UNKNOWN"

    # logic for yanglint compilation result:
    if "err :" in result_yanglint:
        compilation_yanglint = "FAILED"
    elif "warn:" in result_yanglint:
        compilation_yanglint = "PASSED WITH WARNINGS"
    elif result_yanglint == "":
        compilation_yanglint = "PASSED"
    else:
        compilation_yanglint = "UNKNOWN"
    # "err : Unable to parse submodule, parse the main module instead." error  message
    # => still print the message, but doesn't report it as FAILED
    if "err : Unable to parse submodule, parse the main module instead." in result_yanglint:
        compilation_yanglint = "PASSED"
    # Next three lines could be removed when mount-point is supported by yanglint
    # result_yanglint = result_yanglint.rstrip()
    # if result_yanglint.endswith("extension statement found, ignoring."):
    #     compilation_yanglint = "PASSED"

    # determine the combined compilation status, based on the different compilers
    compilation_list = [compilation_pyang, compilation_pyang_no_ietf, compilation_confd, compilation_yuma,
                        compilation_yanglint]
    if "FAILED" in compilation_list:
        compilation = "FAILED"
    elif "PASSED WITH WARNINGS" in compilation_list:
        compilation = "PASSED WITH WARNINGS"
    elif compilation_list == ["PASSED", "PASSED", "PASSED", "PASSED", "PASSED"]:
        compilation = "PASSED"
    else:
        compilation = "UNKNOWN"

    return compilation


def module_or_submodule(input_file):
    if input_file:
        file_input = open(input_file, "r", encoding='utf-8')
        all_lines = file_input.readlines()
        file_input.close()
        commented_out = False
        for each_line in all_lines:
            module_position = each_line.find('module')
            submodule_position = each_line.find('submodule')
            cpos = each_line.find('//')
            if commented_out:
                mcpos = each_line.find('*/')
            else:
                mcpos = each_line.find('/*')
            if mcpos != -1 and cpos > mcpos:
                if commented_out:
                    commented_out = False
                else:
                    commented_out = True
            if submodule_position >= 0 and (submodule_position < cpos or cpos == -1) and not commented_out:
                return 'submodule'
            if module_position >= 0 and (module_position < cpos or cpos == -1) and not commented_out:
                return 'module'
        print('File ' + input_file + ' not yang file or not well formated')
        return 'wrong file'
    else:
        return None


def check_yangcatalog_data(confdc_exec, pyang_exec, yang_path, resutl_html_dir, yang_file, datatracker_url, document_name, email, compilation,
                           result_pyang_flag, result_pyang_no_flag,
                           result_confd, result_yuma, result_yanglint, all_modules, ietf=None):
    def __resolve_maturity_level():
        if ietf == 'ietf-rfc':
            return 'ratified'
        elif ietf in ['ietf-draft', 'ietf-example']:
            maturity_level = document_name.split('-')[1]
            if 'ietf' in maturity_level:
                return 'adopted'
            else:
                return 'initial'
        else:
            return 'not-applicable'

    def __resolve_working_group():
        IETF_RFC_MAP = {
            "iana-crypt-hash@2014-08-06.yang": "NETMOD",
            "iana-if-type@2014-05-08.yang": "NETMOD",
            "ietf-complex-types@2011-03-15.yang": "N/A",
            "ietf-inet-types@2010-09-24.yang": "NETMOD",
            "ietf-inet-types@2013-07-15.yang": "NETMOD",
            "ietf-interfaces@2014-05-08.yang": "NETMOD",
            "ietf-ip@2014-06-16.yang": "NETMOD",
            "ietf-ipfix-psamp@2012-09-05.yang": "IPFIX",
            "ietf-ipv4-unicast-routing@2016-11-04.yang": "NETMOD",
            "ietf-ipv6-router-advertisements@2016-11-04.yang": "NETMOD",
            "ietf-ipv6-unicast-routing@2016-11-04.yang": "NETMOD",
            "ietf-key-chain@2017-06-15.yang": "RTGWG",
            "ietf-l3vpn-svc@2017-01-27.yang": "L3SM",
            "ietf-lmap-common@2017-08-08.yang": "LMAP",
            "ietf-lmap-control@2017-08-08.yang": "LMAP",
            "ietf-lmap-report@2017-08-08.yang": "LMAP",
            "ietf-netconf-acm@2012-02-22.yang": "NETCONF",
            "ietf-netconf-monitoring@2010-10-04.yang": "NETCONF",
            "ietf-netconf-notifications@2012-02-06.yang": "NETCONF",
            "ietf-netconf-partial-lock@2009-10-19.yang": "NETCONF",
            "ietf-netconf-time@2016-01-26.yang": "N/A",
            "ietf-netconf-with-defaults@2011-06-01.yang": "NETCONF",
            "ietf-netconf@2011-06-01.yang": "NETCONF",
            "ietf-restconf-monitoring@2017-01-26.yang": "NETCONF",
            "ietf-restconf@2017-01-26.yang": "NETCONF",
            "ietf-routing@2016-11-04.yang": "NETMOD",
            "ietf-snmp-common@2014-12-10.yang": "NETMOD",
            "ietf-snmp-community@2014-12-10.yang": "NETMOD",
            "ietf-snmp-engine@2014-12-10.yang": "NETMOD",
            "ietf-snmp-notification@2014-12-10.yang": "NETMOD",
            "ietf-snmp-proxy@2014-12-10.yang": "NETMOD",
            "ietf-snmp-ssh@2014-12-10.yang": "NETMOD",
            "ietf-snmp-target@2014-12-10.yang": "NETMOD",
            "ietf-snmp-tls@2014-12-10.yang": "NETMOD",
            "ietf-snmp-tsm@2014-12-10.yang": "NETMOD",
            "ietf-snmp-usm@2014-12-10.yang": "NETMOD",
            "ietf-snmp-vacm@2014-12-10.yang": "NETMOD",
            "ietf-snmp@2014-12-10.yang": "NETMOD",
            "ietf-system@2014-08-06.yang": "NETMOD",
            "ietf-template@2010-05-18.yang": "NETMOD",
            "ietf-x509-cert-to-name@2014-12-10.yang": "NETMOD",
            "ietf-yang-library@2016-06-21.yang": "NETCONF",
            "ietf-yang-metadata@2016-08-05.yang": "NETMOD",
            "ietf-yang-patch@2017-02-22.yang": "NETCONF",
            "ietf-yang-smiv2@2012-06-22.yang": "NETMOD",
            "ietf-yang-types@2010-09-24.yang": "NETMOD",
            "ietf-yang-types@2013-07-15.yang": "NETMOD"
        }
        if ietf == 'ietf-rfc':
            return IETF_RFC_MAP.get('{}.yang'.format(name_revision))
        else:
            return document_name.split('-')[2]

    updated_modules = []
    pyang_module = '{}/{}'.format(yang_path, yang_file)
    found = False
    for root, dirs, files in os.walk(yang_path):
        if found:
            break
        for ff in files:
            if ff == yang_file:
                pyang_module = '{}/{}'.format(root, ff)
                found = True
            if found:
                break
    if not found:
        print("Error file " + yang_file + " not found in dir or subdir of " + yang_path)
    name_revision = \
        os.popen('$PYANG -f' + 'name --name-print-revision --path="$MODULES" ' + pyang_module + ' 2> /dev/null').read().rstrip().split(
            ' ')[0]
    if '@' not in name_revision:
        name_revision += '@1970-01-01'
    if name_revision in all_modules:
        module_data = all_modules[name_revision].copy()
        update = False
        if module_data.get('document-name') != document_name and document_name is not None and document_name != '':
            update = True
            module_data['document-name'] = document_name

        if module_data.get('reference') != datatracker_url and datatracker_url is not None and datatracker_url != '':
            update = True
            module_data['reference'] = datatracker_url

        if module_data.get('author-email') != email and email is not None and email != '':
            update = True
            module_data['author-email'] = email

        if compilation is not None and compilation != '' and module_data.get(
            'compilation-status') != compilation.lower().replace(' ', '-'):
            update = True
            module_data['compilation-status'] = compilation.lower().replace(' ', '-')

        if compilation is not None:

            def render(tpl_path, context):
                """Render jinja html template
                    Arguments:
                        :param tpl_path: (str) path to a file
                        :param context: (dict) dictionary containing data to render jinja
                            template file
                        :return: string containing rendered html file
                """

                path, filename = os.path.split(tpl_path)
                return jinja2.Environment(
                    loader=jinja2.FileSystemLoader(path or './')
                ).get_template(filename).render(context)

            name = module_data['name']
            rev = module_data['revision']
            org = module_data['organization']
            file_url = '{}@{}_{}.html'.format(name, rev, org)
            result = {'name': name,
                      'revision': rev,
                      'pyang_lint': result_pyang_flag,
                      'pyang': result_pyang_no_flag,
                      'confdrc': result_confd, 'yumadump': result_yuma,
                      'yanglint': result_yanglint}

            ths = list()
            option = '--lint'
            if ietf is not None:
                option = '--ietf'
            ths.append('Compilation Result (pyang {}). {}'.format(option, run_pyang_version(pyang_exec)))
            ths.append('Compilation Result (pyang). Note: also generates errors for imported files. {}'.format(
                run_pyang_version(pyang_exec)))
            ths.append('Compilation Results (confdc) Note: also generates errors for imported files. {}'.format(
                run_confd_version(confdc_exec)))
            ths.append('Compilation Results (yangdump-pro). Note: also generates errors for imported files. {}'.format(
                run_yumadumppro_version()))
            ths.append(
                'Compilation Results (yanglint -V -i). Note: also generates errors for imported files. {}'.format(
                    run_yanglint_version()))

            context = {'result': result,
                       'ths': ths}
            template = os.path.dirname(os.path.realpath(__file__)) + '/resources/compilationStatusTemplate.html'
            rendered_html = render(template, context)
            if os.path.isfile('{}/{}'.format(resutl_html_dir, file_url)):
                with open('{}/{}'.format(resutl_html_dir, file_url), 'r', encoding='utf-8') as f:
                    existing_output = f.read()
                if existing_output != rendered_html:
                    with open('{}/{}'.format(resutl_html_dir, file_url), 'w', encoding='utf-8') as f:
                        f.write(rendered_html)
                    os.chmod('{}/{}'.format(resutl_html_dir, file_url), 0o664)
            if compilation == 'PASSED':
                comp_result = ''
            else:
                comp_result = 'https://yangcatalog.org/results/{}'.format(file_url)
            if module_data['compilation-result'] != comp_result:
                update = True
                module_data['compilation-result'] = comp_result

        if ietf is not None and module_data['organization'] == 'ietf':
            wg = __resolve_working_group()
            if (module_data.get('ietf') is None or module_data['ietf']['ietf-wg'] != wg) and wg is not None:
                update = True
                module_data['ietf'] = {}
                module_data['ietf']['ietf-wg'] = wg

        mat_level = __resolve_maturity_level()
        if module_data.get('maturity-level') != mat_level:
            if mat_level == 'not-applicable':
                if module_data.get('maturity-level') is None or module_data.get('maturity-level') == '':
                    update = True
                    module_data['maturity-level'] = mat_level
            else:
                update = True
                module_data['maturity-level'] = mat_level

        if update:
            updated_modules.append(module_data)
            print('DEBUG: updated_modules: {}'.format(name_revision))

    else:
        print('WARN: {} not in confd yet'.format(name_revision))
    return updated_modules


def push_to_confd(updated_modules, config):
    print('creating patch request to confd with updated data')
    json_modules_data = json.dumps({'modules': {'module': updated_modules}})
    confd_protocol = config.get('General-Section', 'protocol-confd')
    confd_port = config.get('Web-Section', 'confd-port')
    confd_host = config.get('Web-Section', 'confd-ip')
    credentials = config.get('Secrets-Section', 'confd-credentials').strip('"').split()
    confd_prefix = '{}://{}:{}'.format(confd_protocol, confd_host, confd_port)
    if '{"module": []}' not in json_modules_data:
        url = confd_prefix + '/restconf/data/yang-catalog:catalog/modules/'
        response = requests.patch(url, data=json_modules_data,
                                  auth=(credentials[0],
                                        credentials[1]),
                                  headers={
                                      'Accept': 'application/yang-data+json',
                                      'Content-type': 'application/yang-data+json'})
        if response.status_code < 200 or response.status_code > 299:
            print('Request with body {} on path {} failed with {}'.
                  format(json_modules_data, url,
                         response.text))
    return []


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    home = os.path.expanduser('~')
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config.read('/etc/yangcatalog/yangcatalog.conf')
    web_url = config.get('Web-Section', 'my-uri')
    web_private = config.get('Web-Section', 'private-directory')

    ietf_directory = config.get('Directory-Section', 'ietf-directory')
    pyang_exec = config.get('Tool-Section', 'pyang-exec')
    confdc_exec = config.get('Tool-Section', 'confdc-exec')
    confdc_yangpath = config.get('Tool-Section', 'confdc-yangpath')

    api_ip = config.get('Web-Section', 'ip')
    protocol = config.get('General-Section', 'protocol-api')
    resutl_html_dir = config.get('Web-Section', 'result-html-dir')

    parser = argparse.ArgumentParser(description='Yang RFC/Draft Processor')
    parser.add_argument("--draftpath", default=ietf_directory + "/my-id-mirror/",
                        help="The optional directory where to find the source drafts. "
                             "Default is '" + ietf_directory + "/my-id-mirror/' but could also be '" + ietf_directory + "/my-id-archive-mirror/' to get expired drafts as well")
    parser.add_argument("--rfcpath", default=ietf_directory + "/rfc/",
                        help="The optional directory where to find the source RFCs. Default is '" + ietf_directory + "/rfc/'")
    parser.add_argument("--binpath", default=home + "/bin/", help="Optional directory where to find the "
                                                                  "script executables. Default is '" + home + "/bin/'")
    parser.add_argument("--htmlpath", default=web_private + '/',
                        help="The path to create the HTML file (optional). Default is '" + web_private + "/'")
    parser.add_argument("--yangpath", default=ietf_directory + "/YANG/", help="The optional directory where to put the "
                                                                              "correctly extracted models. "
                                                                              "Default is " + ietf_directory + "'/YANG/'")
    parser.add_argument("--allyangpath", default=ietf_directory + "/YANG-all/",
                        help="The optional directory where to store "
                             "all extracted models (including bad ones). "
                             " Default is '" + ietf_directory + "/YANG-all/'")
    parser.add_argument("--allyangexamplepath", default=ietf_directory + "/YANG-example/",
                        help="The optional directory where to store "
                             "all extracted example models (starting with example- and not with CODE BEGINS/END). "
                             " Default is '" + ietf_directory + "/YANG-example/'")
    parser.add_argument("--yangexampleoldrfcpath", default=ietf_directory + "/YANG-example-old-rfc/",
                        help="The optional directory where to store "
                             "the hardcoded YANG module example models from old RFCs (not starting with example-). "
                             " Default is '" + ietf_directory + "/YANG-example-old-rfc/'")
    parser.add_argument("--allyangdraftpathstrict", default=ietf_directory + "/draft-with-YANG-strict/",
                        help="The optional directory where to store "
                             "all drafts containing YANG model(s), with strict xym rule = True. "
                             " Default is '" + ietf_directory + "/draft-with-YANG-strict/'")
    parser.add_argument("--allyangdraftpathnostrict", default=ietf_directory + "/draft-with-YANG-no-strict/",
                        help="The optional directory where to store "
                             "all drafts containing YANG model(s), with strict xym rule = False. "
                             " Default is '" + ietf_directory + "/draft-with-YANG-no-strict/'")
    parser.add_argument("--allyangdraftpathonlyexample", default=ietf_directory + "/draft-with-YANG-example/",
                        help="The optional directory where to store "
                             "all drafts containing YANG model(s) with examples,"
                             "with strict xym rule = True, and strictexample True. "
                             " Default is '" + ietf_directory + "/draft-with-YANG-example/'")
    parser.add_argument("--rfcyangpath", default=ietf_directory + "/YANG-rfc/",
                        help="The optional directory where to store "
                             "the data models extracted from RFCs"
                             "Default is '" + ietf_directory + "/YANG-rfc/'")
    parser.add_argument("--rfcextractionyangpath", default=ietf_directory + "/YANG-rfc-extraction/",
                        help="The optional directory where to store "
                             "the typedef, grouping, identity from data models extracted from RFCs"
                             "Default is '" + ietf_directory + "/YANG-rfc/'")
    parser.add_argument("--draftextractionyangpath", default=ietf_directory + "/YANG-extraction/",
                        help="The optional directory where to store "
                             "the typedef, grouping, identity from data models correctely extracted from drafts"
                             "Default is '" + home + "/ietf/YANG-extraction/'")
    parser.add_argument("--strict", type=bool, default=False, help='Optional flag that determines syntax enforcement; '
                                                                   "'If set to 'True' <CODE BEGINS> / <CODE ENDS> are "
                                                                   "required; default is 'False'")
    parser.add_argument("--debug", type=int, default=0, help="Debug level; the default is 0")

    args = parser.parse_args()
    debug_level = args.debug
    all_yang_catalog_metadta = {}
    prefix = '{}://{}'.format(protocol, api_ip)
    modules = requests.get('{}/api/search/modules'.format(prefix)).json()
    for mod in modules['module']:
        all_yang_catalog_metadta['{}@{}'.format(mod['name'], mod['revision'])] = mod

    # note: args.strict is not used
    print(str(datetime.datetime.now().time()) + ': Starting', flush=True)

    # empty the yangpath, allyangpath, and rfcyangpath directory content
    remove_directory_content(args.yangpath, debug_level)
    remove_directory_content(args.allyangpath, debug_level)
    remove_directory_content(args.rfcyangpath, debug_level)
    remove_directory_content(args.allyangexamplepath, debug_level)
    remove_directory_content(args.yangexampleoldrfcpath, debug_level)
    remove_directory_content(args.allyangdraftpathstrict, debug_level)
    remove_directory_content(args.allyangdraftpathnostrict, debug_level)
    remove_directory_content(args.allyangdraftpathonlyexample, debug_level)
    remove_directory_content(args.rfcextractionyangpath, debug_level)
    remove_directory_content(args.draftextractionyangpath, debug_level)

    # must run the rsync-clean-up.py script
    ietf_drafts = []
    for fname in os.listdir(args.draftpath):
        ffname = os.path.join(args.draftpath, fname)
        if os.path.isfile(ffname):
            with open(ffname, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if '<CODE BEGINS>' in line:
                        ietf_drafts.append(fname)
                        break
    ietf_drafts.sort()
    ietf_rfcs = [f for f in os.listdir(args.rfcpath) if os.path.isfile(os.path.join(args.rfcpath, f))]
    ietf_rfcs.sort()

    print(str(datetime.datetime.now().time()) + ': file list generated', flush=True)
    # Extracting YANG Modules from IETF drafts
    draft_yang_dict = {}
    draft_yang_all_dict = {}
    draft_yang_example_dict = {}
    rfc_yang_dict = {}

    for rfc_file in ietf_rfcs:
        # Extract the correctly formatted YANG Models in args.rfcyangpath
        yang_models_in_rfc = xym.xym(rfc_file, args.rfcpath, args.rfcyangpath, strict=True, strict_examples=False,
                                     debug_level=args.debug, add_line_refs=False, force_revision_pyang=False,
                                     force_revision_regexp=True)
        if yang_models_in_rfc:
            # Basic sanity checks
            if any(' ' in filename for filename in yang_models_in_rfc):
                print(
                    "File " + rfc_file + " has invalid module name" + '[%s]' % ', '.join(map(str, yang_models_in_rfc)))
                ietf_rfcs.remove(rfc_file)
                continue
            if any('YYYY-MM-DD' in filename for filename in yang_models_in_rfc):
                print(
                    "File " + rfc_file + " has invalid module name" + '[%s]' % ', '.join(map(str, yang_models_in_rfc)))
                ietf_rfcs.remove(rfc_file)
                continue
            if any('.yang' == filename for filename in yang_models_in_rfc):
                print(
                    "File " + rfc_file + " has invalid module name" + '[%s]' % ', '.join(map(str, yang_models_in_rfc)))
                ietf_rfcs.remove(rfc_file)
                continue
            if debug_level > 0:
                print("DEBUG: in main: extracted YANG models from RFC:")
                print("DEBUG: " + str(yang_models_in_rfc))
            # typedef, grouping, and identity extraction from RFCs
            for y in yang_models_in_rfc:
                if not y.startswith("example-"):
                    print("Identifier definition extraction for " + y)
                    extract_elem(os.path.join(args.rfcyangpath + '/', y), args.rfcextractionyangpath, 'typedef')
                    extract_elem(os.path.join(args.rfcyangpath + '/', y), args.rfcextractionyangpath, 'grouping')
                    extract_elem(os.path.join(args.rfcyangpath + '/', y), args.rfcextractionyangpath, 'identity')
                    # if not y.startswith("iana-"):
                    # this is where I add the check
            rfc_yang_dict[rfc_file] = yang_models_in_rfc
    yang_rfc_dict = invert_yang_modules_dict(rfc_yang_dict, debug_level)
    remove_invalid_files(args.rfcyangpath, yang_rfc_dict)
    print(str(datetime.datetime.now().time()) + ': all RFC processed', flush=True)

    for draft_file in ietf_drafts:
        # Extract the correctly formatted YANG Models into args.yangpath
        yang_models_in_draft = xym.xym(draft_file, args.draftpath, args.yangpath, strict=True, strict_examples=False,
                                       debug_level=args.debug, add_line_refs=False, force_revision_pyang=False,
                                       force_revision_regexp=True)

        if yang_models_in_draft:
            # Basic sanity check
            if any(' ' in filename for filename in yang_models_in_draft):
                print("File " + draft_file + " has invalid module name")
                ietf_drafts.remove(draft_file)
                continue
            if any('YYYY-MM-DD' in filename for filename in yang_models_in_draft):
                print("File " + draft_file + " has invalid module name")
                ietf_drafts.remove(draft_file)
                continue
            if any('.yang' == filename for filename in yang_models_in_draft):
                print("File " + draft_file + " has invalid module name")
                ietf_drafts.remove(draft_file)
                continue
            if debug_level > 0:
                print("DEBUG: in main: extracted YANG models from draft:")
                print("DEBUG: " + str(yang_models_in_draft))

            for y in yang_models_in_draft:
                # typedef, grouping, and identity extraction from drafts
                if not y.startswith("example-"):
                    print("Identifier definition extraction for " + y)
                    extract_elem(os.path.join(args.yangpath + '/', y), args.draftextractionyangpath, 'typedef')
                    extract_elem(os.path.join(args.yangpath + '/', y), args.draftextractionyangpath, 'grouping')
                    extract_elem(os.path.join(args.yangpath + '/', y), args.draftextractionyangpath, 'identity')

            draft_yang_dict[draft_file] = yang_models_in_draft

            # copy the draft in a specific directory for strict = True
            shutil.copy2(args.draftpath + draft_file, args.allyangdraftpathstrict)

        # Extract the correctly formatted example YANG Models in args.allyangexamplepath
        yang_models_in_draft = xym.xym(draft_file, args.draftpath, args.allyangexamplepath, strict=True,
                                       strict_examples=True, debug_level=args.debug, add_line_refs=False,
                                       force_revision_pyang=False,
                                       force_revision_regexp=True)
        if yang_models_in_draft:
            # Basic sanity checks
            if any(' ' in filename for filename in yang_models_in_draft):
                print("File has invalid module name")
                continue
            if any('YYYY-MM-DD' in filename for filename in yang_models_in_draft):
                print("File has invalid module name")
                continue
            if any('.yang' == filename for filename in yang_models_in_draft):
                print("File has invalid module name")
                continue
            if debug_level > 0:
                print("DEBUG: in main: extracted YANG models from draft:")
                print("DEBUG: " + str(yang_models_in_draft))

            draft_yang_example_dict[draft_file] = yang_models_in_draft

            # copy the draft in a specific directory for strict = True
            shutil.copy2(args.draftpath + draft_file, args.allyangdraftpathonlyexample)

        # Extract  all YANG Models, included the wrongly formatted ones, in args.allyangpath
        yang_models_in_draft = xym.xym(draft_file, args.draftpath, args.allyangpath, strict=False,
                                       strict_examples=False, debug_level=args.debug, add_line_refs=False,
                                       force_revision_pyang=False,
                                       force_revision_regexp=True)
        if yang_models_in_draft:
            # Basic sanity checks
            if any(' ' in filename for filename in yang_models_in_draft):
                print("File has invalid module name")
                continue
            if any('YYYY-MM-DD' in filename for filename in yang_models_in_draft):
                continue
            if any('.yang' == filename for filename in yang_models_in_draft):
                continue
            if debug_level > 0:
                print("DEBUG: in main: extracted YANG models from draft:")
                print("DEBUG: " + str(yang_models_in_draft))
                print
            draft_yang_all_dict[draft_file] = yang_models_in_draft

            # copy the draft in a specific directory for strict = False
            shutil.copy2(args.draftpath + draft_file, args.allyangdraftpathnostrict)

    # invert the key, value in the dictionary. Should be key: yang model, value: draft-file
    yang_draft_dict = invert_yang_modules_dict(draft_yang_dict, debug_level)
    remove_invalid_files(args.yangpath, yang_draft_dict)
    yang_example_draft_dict = invert_yang_modules_dict(draft_yang_example_dict, debug_level)
    remove_invalid_files(args.allyangexamplepath, yang_example_draft_dict)
    yang_draft_all_dict = invert_yang_modules_dict(draft_yang_all_dict, debug_level)
    remove_invalid_files(args.allyangpath, yang_draft_all_dict)
    print(str(datetime.datetime.now().time()) + ': all IETF drafts processed', flush=True)
    print(str(datetime.datetime.now().time()) + ': Python dict inverted', flush=True)
    # Remove the YANG modules (the key in the inverted rfc_dict dictionary dictionary)
    # which are documented at http://www.claise.be/IETFYANGOutOfRFCNonStrictToBeCorrected.html:
    # and the example-ospf-topology.yang, which is bug in xym
    # ietf-foo@2010-01-18.yang, hw.yang, hardware-entities.yang, udmcore.yang, and ct-ipfix-psamp-example.yang
    yang_rfc_dict = {k: v for k, v in yang_rfc_dict.items() if
                     k != 'ietf-foo@2010-01-18.yang' and k != 'hw.yang' and k != 'hardware-entities.yang' and k != 'udmcore.yang' and k != 'ct-ipfix-psamp-example@2011-03-15.yang' and k != 'example-ospf-topology.yang'}
    # Move the YANG modules, which are documented at http://www.claise.be/IETFYANGOutOfRFCNonStrictToBeCorrected.html:
    # ietf-foo@2010-01-18.yang, hw.yang, hardware-entities.yang, udmcore.yang, and ct-ipfix-psamp-example.yang
    # and the example-ospf-topology.yang, which is bug in xym
    # Those YANG modules, from old RFCs, don't follow the example- conventions
    move_old_examples_YANG_modules_from_RFC(args.rfcyangpath, args.yangexampleoldrfcpath, debug_level)
    print(str(datetime.datetime.now().time()) + ': YANG modules moved', flush=True)

    # YANG modules from drafts: PYANG validation, dictionary generation, dictionary inversion, and page generation
    dictionary = {}
    dictionary_no_submodules = {}
    updated_modules = []
    for yang_file in yang_draft_dict:
        draft_name, email, compilation = "", "", ""
        result_pyang, result_no_ietf_flag, result_confd, result_yuma, result_yanglint = "", "", "", "", ""
        ietf_flag = True
        result_pyang = run_pyang(pyang_exec, yang_file, ietf_flag, args.yangpath, debug_level)
        ietf_flag = False
        result_no_ietf_flag = run_pyang(pyang_exec, yang_file, ietf_flag, args.yangpath, debug_level)
        result_confd = run_confd(confdc_exec, yang_file, args.yangpath, debug_level)
        result_yuma = run_yumadumppro(yang_file, args.yangpath, debug_level)
        result_yanglint = run_yanglint(yang_file, args.yangpath, debug_level)
        draft_name = yang_draft_dict[yang_file]
        url = draft_name.split(".")[0]
        rev_num = url.split("-")[-1]
        url = url.rstrip('-0123456789')
        mailto = url + "@ietf.org"
        url = "https://datatracker.ietf.org/doc/" + url + '/' + rev_num
        draft_url = '<a href="' + url + '">' + draft_name + '</a>'
        email = '<a href="mailto:' + mailto + '">Email Authors</a>'
        url2 = web_url + "/YANG-modules/" + yang_file
        yang_url = '<a href="' + url2 + '">Download the YANG model</a>'

        compilation = combined_compilation(yang_file, result_pyang, result_no_ietf_flag, result_confd, result_yuma,
                                           result_yanglint)
        updated_modules.extend(
            check_yangcatalog_data(confdc_exec, pyang_exec, args.yangpath, resutl_html_dir, yang_file, url, draft_name, mailto, compilation,
                                   result_pyang,
                                   result_no_ietf_flag, result_confd, result_yuma, result_yanglint,
                                   all_yang_catalog_metadta, 'ietf-draft'))
        if len(updated_modules) > 100:
            updated_modules = push_to_confd(updated_modules, config)
        dictionary[yang_file] = (
            draft_url, email, yang_url, compilation, result_pyang, result_no_ietf_flag, result_confd, result_yuma,
            result_yanglint)
        if module_or_submodule(args.yangpath + yang_file) == 'module':
            dictionary_no_submodules[yang_file] = (
                draft_url, email, yang_url, compilation, result_pyang, result_no_ietf_flag, result_confd, result_yuma,
                result_yanglint)
    print(str(datetime.datetime.now().time()) + ': IETF drafts validated/compiled', flush=True)

    # Dictionary serialization
    write_dictionary_file_in_json(dictionary, args.htmlpath, "IETFDraft.json")
    print(str(datetime.datetime.now().time()) + ': IETFDraft.json generated', flush=True)
    # YANG modules from drafts: : make a list out of the dictionary
    my_list = []
    my_list = sorted(dict_to_list(dictionary_no_submodules))
    # YANG modules from drafts: replace CR by the BR HTML tag
    my_new_list = []
    my_new_list = list_br_html_addition(my_list)
    # YANG modules from drafts: HTML page generation for yang models
    print(str(datetime.datetime.now().time()) + ": HTML page generation", flush=True)
    header = ['YANG Model', 'Draft Name', 'Email', 'Download the YANG model', 'Compilation',
              'Compilation Result (pyang --ietf). ' + run_pyang_version(pyang_exec, 0),
              'Compilation Result (pyang). Note: also generates errors for imported files. ' + run_pyang_version(pyang_exec, 0),
              'Compilation Results (confdc) Note: also generates errors for imported files. ' + run_confd_version(confdc_exec, 0),
              'Compilation Results (yangdump-pro). Note: also generates errors for imported files. ' + run_yumadumppro_version(
                  0),
              'Compilation Results (yanglint -V -i). Note: also generates errors for imported files. ' + run_yanglint_version(
                  0)]
    generate_html_table(my_new_list, header, args.htmlpath, "IETFDraftYANGPageCompilation.html")

    # Example- YANG modules from drafts: PYANG validation, dictionary generation, dictionary inversion, and page generation
    dictionary_example = {}
    dictionary_no_submodules_example = {}
    for yang_file in yang_example_draft_dict:
        draft_name, email, compilation = "", "", ""
        result_pyang, result_no_ietf_flag = "", ""
        ietf_flag = True
        result_pyang = run_pyang(pyang_exec, yang_file, ietf_flag, args.allyangexamplepath, debug_level)
        ietf_flag = False
        result_no_ietf_flag = run_pyang(pyang_exec, yang_file, ietf_flag, args.allyangexamplepath, debug_level)
        draft_name = yang_example_draft_dict[yang_file]
        url = draft_name.split(".")[0]
        rev_num = url.split("-")[-1]
        url = url.rstrip('-0123456789')
        mailto = url + "@ietf.org"
        url = "https://datatracker.ietf.org/doc/" + url + '/' + rev_num
        draft_url = '<a href="' + url + '">' + draft_name + '</a>'
        email = '<a href="mailto:' + mailto + '">Email Authors</a>'
        if "error" in result_pyang:
            compilation = "FAILED"
        elif "warning" in result_pyang:
            compilation = "PASSED WITH WARNINGS"
        elif result_pyang == "":
            compilation = "PASSED"
        else:
            compilation = "UNKNOWN"
        updated_modules.extend(
            check_yangcatalog_data(confdc_exec, pyang_exec, args.yangpath, resutl_html_dir, yang_file, url, draft_name, mailto, compilation,
                                   result_pyang,
                                   result_no_ietf_flag, '', '', '',
                                   all_yang_catalog_metadta, 'ietf-example'))
        if len(updated_modules) > 100:
            updated_modules = push_to_confd(updated_modules, config)
        dictionary_example[yang_file] = (draft_url, email, compilation, result_pyang, result_no_ietf_flag)
        if module_or_submodule(args.allyangexamplepath + yang_file) == 'module':
            dictionary_no_submodules_example[yang_file] = (
                draft_url, email, compilation, result_pyang, result_no_ietf_flag)
    print(str(datetime.datetime.now().time()) + ': example YANG modules in IETF drafts validated/compiled', flush=True)

    # Dictionary serialization
    write_dictionary_file_in_json(dictionary_example, args.htmlpath, "IETFDraftExample.json")
    print(str(datetime.datetime.now().time()) + ': IETFDraftExample.json generated', flush=True)
    # dictionary2 = {}
    # dictionary2 = read_dictionary_file_in_json(args.htmlpath, "IETFYANG.json")
    # YANG modules from drafts: : make a list out of the dictionary
    my_list = []
    my_list = sorted(dict_to_list(dictionary_no_submodules_example))
    # YANG modules from drafts: replace CR by the BR HTML tag
    my_new_list = []
    my_new_list = list_br_html_addition(my_list)
    # YANG modules from drafts: HTML page generation for yang models
    print(str(datetime.datetime.now().time()) + ": HTML page generation for Example YANG Models", flush=True)
    header = ['YANG Model', 'Draft Name', 'Email', 'Compilation', 'Compilation Result (pyang --ietf)',
              'Compilation Result (pyang). Note: also generates errors for imported files.']
    generate_html_table(my_new_list, header, args.htmlpath, "IETFDraftExampleYANGPageCompilation.html")

    # YANG modules from RFCs: dictionary2 generation, dictionary2 inversion, and page generation
    # With dictionary2 generation: formatting for the IETFYANGOutOfRFC.html page
    dictionary2 = {}
    dictionary_no_submodules2 = {}
    for yang_file in yang_rfc_dict:
        rfc_name = yang_rfc_dict[yang_file]
        rfc_name = rfc_name.split(".")[0]
        url = "https://tools.ietf.org/html/" + rfc_name
        rfc_url = '<a href="' + url + '">' + rfc_name + '</a>'
        dictionary2[yang_file] = rfc_url
        updated_modules.extend(
            check_yangcatalog_data(confdc_exec, pyang_exec, args.yangpath, resutl_html_dir, yang_file, url, rfc_name, None, None,
                                   None, None, None, None, None, all_yang_catalog_metadta, 'ietf-rfc'))
        if len(updated_modules) > 100:
            updated_modules = push_to_confd(updated_modules, config)
        # Uncomment next three lines if I want to remove the submodule from the RFC report in http://www.claise.be/IETFYANGOutOfRFC.png
        # dictionary_no_submodules2[yang_file] = rfc_url
        # if module_or_submodule(args.rfcyangpath + yang_file) == 'module':
        # dictionary_no_submodules2[yang_file] = rfc_url

    # Dictionary serialization
    write_dictionary_file_in_json(dictionary2, args.htmlpath, "IETFYANGRFC.json")
    print(str(datetime.datetime.now().time()) + ': IETFYANGRFC.json generated', flush=True)

    # (Un)comment next two lines if I want to remove the submodule from the RFC report in http://www.claise.be/IETFYANGOutOfRFC.png
    my_yang_in_rfc = sorted(dict_to_list_rfc(dictionary2))
    #    my_yang_in_rfc = sorted(dict_to_list_rfc(dictionary_no_submodules2), key = itemgetter(1))

    # stats number generation
    number_of_modules_YANG_models_from_ietf_drafts = len(yang_draft_dict.keys())
    number_of_modules_YANG_models_from_ietf_drafts_passed_compilation_without_warnings = number_of_yang_modules_that_passed_compilation(
        dictionary, "PASSED")
    number_of_modules_YANG_models_from_ietf_drafts_passed_compilation_wit_warnings = number_of_yang_modules_that_passed_compilation(
        dictionary, "PASSED WITH WARNINGS")
    number_of_all_modules = len(
        [f for f in os.listdir(args.allyangpath) if os.path.isfile(os.path.join(args.allyangpath, f))])
    number_of_example_modules_YANG_models_from_ietf_drafts = len(yang_example_draft_dict.keys())

    # YANG modules from RFCs: HTML page generation for yang models
    header = ['YANG Model (and Submodel)', 'RFC']
    generate_html_table(my_yang_in_rfc, header, args.htmlpath, "IETFYANGRFC.html")
    # HTML page generation for statistics
    #    line1 = ""
    line2 = "<H3>IETF YANG MODELS</H3>"
    line5 = "Number of correctly extracted YANG models from IETF drafts: " + str(
        number_of_modules_YANG_models_from_ietf_drafts)
    line6 = "Number of YANG models in IETF drafts that passed compilation without warnings: " + str(
        number_of_modules_YANG_models_from_ietf_drafts_passed_compilation_without_warnings) + "/" + str(
        number_of_modules_YANG_models_from_ietf_drafts)
    line7 = "Number of YANG models in IETF drafts that passed compilation with warnings: " + str(
        number_of_modules_YANG_models_from_ietf_drafts_passed_compilation_wit_warnings) + "/" + str(
        number_of_modules_YANG_models_from_ietf_drafts)
    line8 = "Number of all YANG models in IETF drafts (example, badly formatted, etc. ): " + str(number_of_all_modules)
    line9 = "Number of correctly extracted example YANG models from IETF drafts: " + str(
        number_of_example_modules_YANG_models_from_ietf_drafts)
    my_list2 = [line2, line5, line6, line7, line8, line9]

    generate_html_list(my_list2, args.htmlpath, "IETFYANGPageMain.html")
    print(str(datetime.datetime.now().time()) + ': IETFYANGPageMain.html generated', flush=True)

    # Stats generation for the standard output
    print("--------------------------")
    print("Number of correctly extracted YANG models from IETF drafts: " + str(
        number_of_modules_YANG_models_from_ietf_drafts))
    print("Number of YANG models in IETF drafts that passed compilation without warnings: " + str(
        number_of_modules_YANG_models_from_ietf_drafts_passed_compilation_without_warnings) + "/" + str(
        number_of_modules_YANG_models_from_ietf_drafts))
    print("Number of YANG models in IETF drafts that passed compilation with warnings: " + str(
        number_of_modules_YANG_models_from_ietf_drafts_passed_compilation_wit_warnings) + "/" + str(
        number_of_modules_YANG_models_from_ietf_drafts))
    print("Number of all YANG models in IETF drafts (example, badly formatted, etc. ): " + str(number_of_all_modules))
    print("Number of correctly extracted example YANG models from IETF drafts: " + str(
        number_of_example_modules_YANG_models_from_ietf_drafts), flush=True)

    # YANG modules from drafts, for CiscoAuthors: HTML page generation for yang models
    output_email = ""
    dictionary = {}
    dictionary_no_submodules = {}
    for yang_file in yang_draft_dict:
        cisco_email = extract_email_string(args.draftpath + yang_draft_dict[yang_file], "@cisco.com", debug_level)
        tailf_email = extract_email_string(args.draftpath + yang_draft_dict[yang_file], "@tail-f.com", debug_level)
        if tailf_email:
            if cisco_email:
                cisco_email = cisco_email + "," + tailf_email
            else:
                cisco_email = tailf_email
        if cisco_email:
            output_email = output_email + cisco_email + ", "
            draft_name, email, compilation = "", "", "",
            result_pyang, result_no_ietf_flag, result_confd, result_yuma, result_yanglint = "", "", "", "", ""
            # print("PYANG compilation of " + yang_file)
            ietf_flag = True
            result_pyang = run_pyang(pyang_exec, yang_file, ietf_flag, args.allyangpath, debug_level)
            ietf_flag = False
            result_no_ietf_flag = run_pyang(pyang_exec, yang_file, ietf_flag, args.allyangpath, debug_level)
            result_confd = run_confd(confdc_exec, yang_file, args.yangpath, debug_level)
            result_yuma = run_yumadumppro(yang_file, args.yangpath, debug_level)
            result_yanglint = run_yanglint(yang_file, args.yangpath, debug_level)
            draft_name = yang_draft_dict[yang_file]
            url = draft_name.split(".")[0]
            rev_num = url.split("-")[-1]
            url = url.rstrip('-0123456789')
            mailto = url + "@ietf.org"
            url = "https://datatracker.ietf.org/doc/" + url + '/' + rev_num
            draft_url = '<a href="' + url + '">' + draft_name + '</a>'
            email = '<a href="mailto:' + mailto + '">Email All Authors</a>'
            cisco_email = '<a href="mailto:' + cisco_email + '">Email Cisco Authors Only</a>'
            url2 = web_url + "/YANG-modules/" + yang_file
            yang_url = '<a href="' + url2 + '">Download the YANG model</a>'

            compilation = combined_compilation(yang_file, result_pyang, result_no_ietf_flag, result_confd, result_yuma,
                                               result_yanglint)
            updated_modules.extend(
                check_yangcatalog_data(confdc_exec, pyang_exec, args.yangpath, resutl_html_dir, yang_file, url, draft_name, mailto, compilation,
                                       result_pyang,
                                       result_no_ietf_flag, result_confd, result_yuma, result_yanglint,
                                       all_yang_catalog_metadta, 'ietf-draft'))
            if len(updated_modules) > 100:
                updated_modules = push_to_confd(updated_modules, config)
            dictionary[yang_file] = (
                draft_url, email, cisco_email, yang_url, compilation, result_pyang, result_no_ietf_flag, result_confd,
                result_yuma, result_yanglint)
            if module_or_submodule(args.yangpath + yang_file) == 'module':
                dictionary_no_submodules[yang_file] = (
                    draft_url, email, cisco_email, yang_url, compilation, result_pyang, result_no_ietf_flag,
                    result_confd,
                    result_yuma, result_yanglint)
    output_email = output_email.rstrip(", ")
    # output_email is a string, comma separated, of cisco email address
    # want to, via a list, remove the duplicate, then re-generate a string
    output_email_list = [i.strip() for i in output_email.split(',')]
    output_email_list_unique = []
    for i in output_email_list:
        if i not in output_email_list_unique:
            output_email_list_unique.append(i)
    output_email_string_unique = ""
    for i in output_email_list_unique:
        output_email_string_unique = output_email_string_unique + ", " + i

    updated_modules = push_to_confd(updated_modules, config)

    # make a list out of the dictionary
    my_list = []
    my_list = sorted(dict_to_list(dictionary_no_submodules))
    # replace CR by the BR HTML tag
    my_new_list = []
    my_new_list = list_br_html_addition(my_list)
    # HTML page generation for yang models
    print(str(datetime.datetime.now().time()) + ": Cisco HTML page generation", flush=True)
    header = ['YANG Model', 'Draft Name', 'All Authors Email', 'Only Cisco Email', 'Download the YANG model',
              'Compilation', 'Compilation Results (pyang --ietf)',
              'Compilation Results (pyang). Note: also generates errors for imported files.',
              'Compilation Results (confdc) Note: also generates errors for imported files',
              'Compilation Results (yumadump-pro). Note: also generates errors for imported files.',
              'Compilation Results (yanglint -V -i). Note: also generates errors for imported files.']
    generate_html_table(my_new_list, header, args.htmlpath, "IETFCiscoAuthorsYANGPageCompilation.html")
    print(output_email_string_unique)
    print(str(datetime.datetime.now().time()) + ': IETFCiscoAuthorsYANGPageCompilation.html generated', flush=True)
    print(str(datetime.datetime.now().time()) + ': end of job', flush=True)
