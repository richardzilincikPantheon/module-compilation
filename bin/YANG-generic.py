#!/usr/bin/env python
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
import configparser
import os
import HTML
import time
import json
import re
from subprocess import Popen, PIPE
import shlex


__author__ = 'Benoit Claise'
__copyright__ = "Copyright(c) 2015-2018, Cisco Systems, Inc."
__license__ = "Apache 2.0"
__email__ = "bclaise@cisco.com"


# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------


def list_of_yang_modules_in_dir(srcdir, debug_level):
    """
    Returns the list of YANG Modules (.yang) in a directory   
    :param srcdir: directory to search for yang files
    :param debug_level: If > 0 print some debug statements to the console
    :return: list of YANG files
    """
    files = [f for f in os.listdir(srcdir) if os.path.isfile(os.path.join(srcdir, f))]
    yang_files = []
    for f in files:
        if f.endswith(".yang"):
            yang_files.append(f)
            if debug_level > 0:
                print("DEBUG: " + f + " in list_of_yang_modules_in_dir: is a YANG model")
        else:
            if debug_level > 0:
                print("DEBUG: " + f + " in list_of_yang_modules_in_dir: is not a YANG model")
    return yang_files


def list_of_yang_modules_in_subdir(srcdir, debug_level):
    """
    Returns the list of YANG Modules (.yang) in all sub-directories   
    :param srcdir: root directory to search for yang files
    :param debug_level: If > 0 print some debug statements to the console
    :return: list of YANG files
    """
    ll = []
    for root, dirs, files in os.walk(srcdir):
        for f in files:
            if f.endswith(".yang"):
                if debug_level > 0:
                    print(os.path.join(root, f))
                ll.append(os.path.join(root, f))
    return ll


def run_pyang(p, model, pyang_param, allinclu, take_pyang_param_into_account=True, debug_level=True):
    """
    Run PYANG on the YANG model, with or without the --lint flag
    :p: the path where to look for the models  
    :param model: The file name for the model
    :param pyang_param: a boolean, True for the --lint pyang flag, False for no --lint pyang flag
    :allinclu: if True, the YANG module path is p. If false, the default one
    :param take_pyang_param_into_account: a boolean, 
        True: take pyang_param into account, i.e. --lint or --ietf
        False: generate pyang without arguments
    :param debug_level: If > 0 print some debug statements to the console
    :return: the outcome of the PYANG compilation
    """
# PYANG search path is indicated by the -p parameter which can occur multiple times
#    The following directories are always added to the search path:
#        1. current directory
#        2. $YANG_MODPATH
#        3. $HOME/yang/modules
#        4. $YANG_INSTALL/yang/modules OR if $YANG_INSTALL is unset <the default installation directory>/yang/modules (on Unix systems: /usr/share/yang/modules)


    directory = os.path.dirname(model)
    filename = model.split("/")[-1]
    os.chdir(directory)
    if pyang_param and take_pyang_param_into_account and allinclu:
        bash_command = " --lint -p " + p + " " + filename + " 2>&1"
    elif pyang_param and take_pyang_param_into_account and not allinclu:
        bash_command = " --lint -p "  + modules_directory + " " + filename + " 2>&1"
    elif not pyang_param and take_pyang_param_into_account and allinclu:
        bash_command = " --ietf -p " + p + " " + filename + " 2>&1"
    elif not pyang_param and take_pyang_param_into_account and not allinclu:
        bash_command = " --ietf -p "  + modules_directory + " " + filename + " 2>&1"
    elif allinclu:
        bash_command = " -p " + p + " " + filename + " 2>&1"
    else:
        bash_command = " -p " + modules_directory + " " + filename + " 2>&1"
    bash_command = pyang_exec + bash_command
    if debug_level:
        print("DEBUG: " + " in run_pyang: bash_command contains " + bash_command)
    return os.popen(bash_command).read()

def run_pyang_version(debug_level=0):
    """
    Return the pyang version.
    :param debug_level
    :return: a string composed of the pyang version
    """
    bash_command = pyang_exec + " -v 2>&1"
    if debug_level:
        print("DEBUG: " + " in run_pyang: bash_command contains " + bash_command)
    return os.popen(bash_command).read()

def run_confd(p, model, allinclu, debug_level):
    """
    Run confdc on the YANG model
    :p: the path where to look for the models  
    :param model: The file name for the model
    :allinclu: if True, the YANG module path is p. If false, the default one
    :param debug_level: If > 0 print some debug statements to the console
    :return: the outcome of the PYANG compilation
    """
    # Note: confd doesn't include YANG module recursively and doesn't follow symbolic links
    # Every single time there is a new directory with YANG modules, I need to add it to the bash_command
    directory = os.path.dirname(model)
    filename = model.split("/")[-1]
    os.chdir(directory)
    if allinclu:
        bash_command = confdc_exec + " --yangpath " + p + " -w TAILF_MUST_NEED_DEPENDENCY -c " + model + " 2>&1"
    else:
        bash_command = confdc_exec + " --yangpath " + modules_directory + " --yangpath " + ietf_directory + "/YANG/ --yangpath " + non_ietf_directory + "/mef/YANG-public/src/model/draft/common/ --yangpath " + non_ietf_directory + "/mef/YANG-public/src/model/dependent/ --yangpath " + non_ietf_directory + "/mef/YANG-public/src/model/standard/ --yangpath " + non_ietf_directory + "/mef/YANG-public/src/model/draft/ --yangpath " + non_ietf_directory + "/yangmodels/yang/standard/ieee/draft/ --yangpath " + non_ietf_directory + "/yangmodels/yang/standard/ieee/draft/802.3 --yangpath " + non_ietf_directory +"/yangmodels/yang/standard/ieee/draft/802.1 --yangpath " + non_ietf_directory + "/bbf/install/yang/common --yangpath " + non_ietf_directory + "/bbf/install/yang/interface --yangpath " + non_ietf_directory + "/bbf/install/yang/networking -w TAILF_MUST_NEED_DEPENDENCY -c " + model + " 2>&1"
        if debug_level:
            print("DEBUG: " + " in run_confd: bash_command contains " + bash_command)
    return os.popen(bash_command).read()

def run_confd_version(debug_level=0):
    """
    Return the confd version
    :return: a string composed of the confd version
    """
    bash_command = confdc_exec + " --version 2>&1"
    if debug_level:
        print("DEBUG: " + " in run_confd: bash_command contains " + bash_command)
    return "confd version " + os.popen(bash_command).read()

def run_yumadumppro(p, model, allinclu, debug_level):
    """
    Run run_yumadump-pro on the YANG model
    yangdump-pro  --config=/etc/yumapro/yangdump-pro.conf module.yang
    :p: the path where to look for the models  
    :param model: The file name for the model, including the full path
    :allinclu: if True, the YANG module path is p. If false, the default one
    :return: the outcome of the PYANG compilation
    """
    directory = os.path.dirname(model)
    filename = model.split("/")[-1]
    os.chdir(directory)
    if allinclu:
        bash_command = "yangdump-pro --quiet-mode --config=/etc/yumapro/yangdump-pro-allinclusive.conf " + model + " 2>&1"
    else:
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
    bash_command = "yangdump-pro --version 2>&1"
    if debug_level:
        print("DEBUG: " + " in yangdump-pro: bash_command contains " + bash_command)
    return os.popen(bash_command).read()

def run_yanglint(p, model, allinclu, debug_level):
    """
    Run yanglint on the YANG model
    :p: the path where to look for the models
    :param model: The file name for the model , including the full path
    :allinclu: if True, the YANG module path is p. If false, the default one
    :return: the outcome of the PYANG compilationf
    """
    directory = os.path.dirname(model)
#    filename = model.split("/")[-1]
    os.chdir(directory)
    if allinclu:
        bash_command = "yanglint -V -i -p " + p + " " + model + " 2>&1"
    else:
        bash_command = "yanglint -V -i -p " + modules_directory + "/ " + model + " 2>&1"
    if debug_level:
        print("DEBUG: " + " in run_yanglint: bash_command contains " + bash_command)
    return os.popen(bash_command).read()

def run_yanglint_version(debug_level=0):
    """
    Return the yanglint version
    :param debug
    :return: a string composed of the yanglint version
    """
    bash_command = "yanglint -v 2>&1"
    if debug_level:
        print("DEBUG: " + " in run_yanglint: bash_command contains " + bash_command)
    return os.popen(bash_command).read()

def generate_html_table(l, h, htmlpath, file_name, txt=""):
    """
    Create a table out of the dict and generate a HTML file
    :param l: The value list to generate the HTML table
    :param h: The header list to generate the HTML table
    :param htmlpath: The directory where the HTML file will be created
    :param file_name: The file name to be created
    :param txt: Extra metadata text to inserted in the generated ligne
                typically: SDO, github source, etc...
    :return: None
    """
    generated = ["Generated on " + time.strftime("%d/%m/%Y") + " by Beno&icirc;t Claise: " + txt]
    htmlcode = HTML.list(generated)
    htmlcode1 = HTML.table(l, header_row=h)
    f = open(htmlpath + file_name, 'w')
    f.write(htmlcode)
    f.write(htmlcode1)
    f.close()


def generate_html_list(l, htmlpath, file_name):
    """
    Create a table out of the dict and generate a HTML file
    :param l: The list to generate the HTML table
    :param htmlpath: The directory where the HTML file will be created
    :param file_name: The file name to be created
    :return: None
    """
    generated = ["Generated on " + time.strftime("%d/%m/%Y") + " by Beno&icirc;t Claise"]
    htmlcode = HTML.list(generated)
    htmlcode1 = HTML.list(l)
    f = open(htmlpath + file_name, 'w')
    f.write(htmlcode)
    f.write(htmlcode1)
    f.close()


def dict_to_list(in_dict):
    """
    Create a list out of a dictionary  
    :param in_dict: The input dictionary
    :return: List
    """
    dictlist = []
    for key, value in in_dict.items():
        temp_list = [key]
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
    :param l: The list 
    :return: List
    """
    for sublist in l:
        for i in range(len(sublist)):
            if isinstance(sublist[i], str):
#            if type(sublist[i]) == type(''):
                sublist[i] = sublist[i].replace("\n", "<br>")
    return l


def number_of_yang_modules_that_passed_compilation(in_dict, pos, compilation_condition):
    """
    return the number of drafts that passed the pyang compilation 
    :param in_dict:
    :param in_dict : dictionary
               in the dictionary key:yang-model, list of values
    :param pos : the position in the list where the compilation_condidtion is
        the "PASSED" or "FAILED" is in the 2nd position of the list if the document location is included
        the "PASSED" or "FAILED" is in the 1rd position of the list if the document location is not included
    :param compilation_condition: a string
                             currently 3 choices: PASSED, PASSED WITH WARNINGS, FAILED
    :return: the number of "PASSED" YANG models
    """
    t = 0
    for k, v in in_dict.items():
        if in_dict[k][pos - 1] == compilation_condition:
            t += 1
    return t

def combined_compilation(yang_file, result_pyang, result_confd, result_yuma, result_yanglint):
    """
    Determine the combined compilation results
    :result_pyang: compilation results from pyang --ietf
#    :result_no_ietf_flag: compilation results from pyang
    :result_confd: compilation from confd 
    :result_yuma: compilation from yuma 
    :result_yanglint: compilation from yanglint 
    :return: the combined compilatiion result
    """
    if "error" in result_pyang:
        compilation_pyang = "FAILED"
    elif  "warning" in result_pyang:
        compilation_pyang = "PASSED WITH WARNINGS"
    elif result_pyang == "":
        compilation_pyang = "PASSED"
    else:
        compilation_pyang = "NOT SURE"

    # logic for confdc compilation result:
    if "error" in result_confd:
        compilation_confd = "FAILED"
    #   The following doesn't work. For example, ietf-diffserv@2016-06-15.yang, now PASSED (TBC):
    #     Error: 'ietf-diffserv@2016-06-15.yang' import of module 'ietf-qos-policy' failed
    #     ietf-diffserv@2016-06-15.yang:11.3: error(250): definition not found
    #   This issue is that an import module that fails => report the main module as FAILED
    #   Another issue with ietf-bgp-common-structure.yang
    # Martin should fix confdc. See "cannot compile submodules; compile the module instead" email
    # If the error is on the module itself, then, that's an error
    elif  "warning" in result_confd:
        compilation_confd = "PASSED WITH WARNINGS"
    elif result_confd == "":
        compilation_confd = "PASSED"
    else:
        compilation_confd = "NOT SURE"
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
    elif "Error" in result_yuma and yang_file in result_yuma and  "0 Errors" not in result_yuma:
    # This is an approximation: if Error in an imported module, and warning on this current module
    # then it will report the module as FAILED
    # Solution: look at line by line comparision of Error and yang_file
        compilation_yuma = "FAILED"
    elif  "Warning" in result_yuma and yang_file in result_yuma:
        compilation_yuma = "PASSED WITH WARNINGS"
    elif  "Warning" in result_yuma and yang_file not in result_yuma:
        compilation_yuma = "PASSED"
    else:
        compilation_yuma = "NOT SURE"

    # logic for yanglint compilation result:
    if  "err :" in result_yanglint:
        compilation_yanglint = "FAILED"
    elif  "warn:" in result_yanglint:
        compilation_yanglint = "PASSED WITH WARNINGS"
    elif result_yanglint == "":
        compilation_yanglint = "PASSED"
    else:
        compilation_yanglint = "NOT SURE"
    # "err : Unable to parse submodule, parse the main module instead." error  message
    # => still print the message, but doesn't report it as FAILED  
    if "err : Unable to parse submodule, parse the main module instead." in result_yanglint:
        compilation_yanglint = "PASSED"

    # determine the combined compilation status, based on the different compilers
    compilation_list = [compilation_pyang, compilation_confd, compilation_yuma, compilation_yanglint]
    if "FAILED" in compilation_list:
        compilation = "FAILED"
    elif "PASSED WITH WARNINGS" in compilation_list:
        compilation = "PASSED WITH WARNINGS"
    elif compilation_list == ["PASSED", "PASSED", "PASSED", "PASSED"]:
        compilation = "PASSED"
    else:
        compilation = "NOT SURE"

    # Next two lines to be removed after troubleshooting
    #compilation_list = [compilation_pyang, compilation_confd, compilation_yuma, compilation_yanglint, compilation]
    #print(yang_file + ": " + str(compilation_list) + "/"+ result_pyang + "/" + result_confd + "/"+ result_yuma + "/"+ result_yanglint + "/\n----")

    return compilation


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
    f = open(path + file_name, 'w')
    f.write(json.dumps(in_dict))
    f.close()


def read_dictionary_file_in_json(path, file_name):
    """
    Read a file, in json, with my directory data
    For testing purposes.

    :param path: The directory where the json file with be created
    :param file_name: The file name to be created
    :return: dictionary
    """
    json_data = open(path + file_name)
    return json.load(json_data)


def get_mod_rev(module):
    mname = ''
    mrev = ''
    #bt = ''

    with open(module, 'r', encoding='latin-1', errors='ignore') as ym:
        for line in ym:
            if mname != '' and mrev != '':# and bt != '':
                return mname + '@' + mrev# + ' (belongs-to {})'.format(bt)

            if mname == '':
                m = re.search(r'^\s*(sub)?module\s+([\w\-\d]+)', line)
                if m:
                    mname = m.group(2)
                    continue

            if mrev == '':
                m = re.search(r'^\s*revision\s+"?([\d\-]+)"?', line)
                if m:
                    mrev = m.group(1)
                    continue

            #if bt == '':
            #    m = re.search(r'^\s*belongs-to\s+([\w\-\d]+)', line)
            #    if m:
            #        bt = m.group(1)
            #        continue

    #if bt != '':
    #    return mname + '@' + mrev + ' (belongs-to {})'.format(bt)
    if mrev == '':
        return mname
    else: 
        return mname + '@' + mrev

def module_or_submodule(input_file):
    if input_file:
        file_input = open(input_file, "r", encoding='latin-1', errors='ignore')
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
    

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    home = os.path.expanduser('~')
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config.read('/etc/yangcatalog/yangcatalog.conf')
    web_private = config.get('Web-Section', 'private_directory') + '/'
    non_ietf_directory = config.get('Directory-Section', 'non_ietf_directory') 
    ietf_directory = config.get('Directory-Section', 'ietf_directory') 
    modules_directory = config.get('Directory-Section', 'modules_directory') 
    pyang_exec = config.get('Tool-Section', 'pyang_exec') 
    confdc_exec = config.get('Tool-Section', 'confdc_exec') 
    parser = argparse.ArgumentParser(description='YANG Dcoument Processor: generate tables with compilation errors/warnings')
    parser.add_argument("--rootdir", default=".",
                        help="The root directory where to find the source YANG models. "
                             "Default is '.'")
    parser.add_argument("--binpath", default=home + "/bin/",
                        help="Optional directory where to find the "
                             "script executables. Default is '" + home + "/bin/'")
    parser.add_argument("--htmlpath", default=web_private,
                        help="The path to create the HTML file (optional). Default is '" + web_private + "'")
    parser.add_argument("--metadata", default="",
                        help="Metadata text (such as SDOs, github location, etc.) "
                             "to be displayed on the generated HTML page"
                             "Default is NULL")
    parser.add_argument("--lint", type=bool, default=False,
                        help="Optional flag that determines pyang syntax enforcement; "
                             "If set to 'True', pyang --lint is run"
                             "Otherwise, pyang --ietf is run"
                             "Default is False")
    parser.add_argument("--allinclusive", type=bool, default=False,
                        help="Optional flag that determines whether the rootdir directory contains all imported YANG modules; "
                             "If set to 'True', the YANG validators only look in the rootdir directory. "
                             "Otherwise, the YANG validators look in " + modules_directory + ". "
                             "Default is False")
    parser.add_argument("--prefix", default="", help="Prefix for generating HTML file name"
                                                     "Example: MEF, IEEEStandards, IEEEExperimental"
                                                     "Default is NULL")
    parser.add_argument("--debug", type=int, default=0, help="Debug level; the default is 0")
    args = parser.parse_args()

    yang_list = list_of_yang_modules_in_subdir(args.rootdir, args.debug)
    if args.debug > 0:
        print("yang_list content: ")
        print(yang_list)

    # YANG modules from drafts: PYANG validation, dictionary generation, dictionary inversion, and page generation
    dictionary = {}
    dictionary_no_submodules = {}
    for yang_file in yang_list:
        compilation = ""
        # print "PYANG compilation of " + yang_file
        result_pyang = run_pyang(args.rootdir, yang_file, args.lint, args.allinclusive, True, args.debug)
        result_no_pyang_param = run_pyang(args.rootdir, yang_file, args.lint, args.allinclusive, False, args.debug)
        result_confd = run_confd(args.rootdir, yang_file, args.allinclusive, args.debug)
        result_yuma = run_yumadumppro(args.rootdir, yang_file, args.allinclusive, args.debug)
        # if want to populate the document location from github, must uncomment the following 3 lines
        # the difficulty: find back the exact githbut location, while everything is already copied in my local
        # directories: maybe Carl's catalog service will help
        #        draft_name = yang_file
        #        draft_name = "https://github.com/MEF-GIT/YANG/tree/master/src/model/draft/" + yang_file
        #        draft_name_url = '<a href="' + draft_name + '">' + yang_file + '</a>'   
        #
        # determine the status, based on the different compilers
        # remove the draft name from result_yuma
        result_yanglint = run_yanglint(args.rootdir, yang_file, args.allinclusive, args.debug)

        # if want to populate the document location from github, must uncomment the following line
        #        dictionary[yang_file] = (draft_name_url, compilation, result, result_no_pyang_param)
        yang_file_without_path = yang_file.split("/")[-1]
        compilation = combined_compilation(yang_file_without_path, result_pyang, result_confd, result_yuma, result_yanglint)

        # Add the @revision to the yang_file if not present
        if "@" in yang_file and ".yang" in yang_file:
            out = get_mod_rev(yang_file)
            if out.rstrip():
                new_yang_file_without_path_with_revision = out.rstrip() + ".yang"
                if new_yang_file_without_path_with_revision.split('@')[0] != yang_file_without_path.split('@')[0]:
                    print('Name of the yang file ' + yang_file_without_path + ' is wrong changing to correct one')
                    yang_file_without_path = new_yang_file_without_path_with_revision
                if new_yang_file_without_path_with_revision.split('@')[1].split('.')[0] != yang_file_without_path.split('@')[1].split('.'):
                    print('revision of the yang file ' + yang_file_without_path + ' is wrong changing to correct one')
                    yang_file_without_path = new_yang_file_without_path_with_revision

                dictionary[yang_file_without_path] = (compilation, result_pyang, result_no_pyang_param, result_confd, result_yuma, result_yanglint)
                if module_or_submodule(yang_file) == 'module':
                    dictionary_no_submodules[yang_file_without_path] = (
                    compilation, result_pyang, result_no_pyang_param, result_confd, result_yuma, result_yanglint)
            else:
                print("Unable to get name@revision out of " + yang_file + ' no output')
        else:
            # execute "/usr/local/bin/pyang/pyang -f name-revision <YANG-module-name>", 
            # which returns out = <YANG-module-name>@<revision>
            #command_string = "/usr/local/bin/pyang -f name-revision " + yang_file + " 2> /dev/null"
            #proc = Popen(shlex.split(command_string), stdout=PIPE, stderr=PIPE)
            #out, err = proc.communicate()
            #if err:
            #    print("ERROR extracting revision from file with: pyang -f name-revision " + yang_file)
            #    print("  Error: " + err)
            #    print()
            out = get_mod_rev(yang_file)
            if out.rstrip():
                new_yang_file_without_path_with_revision = out.rstrip() + ".yang"
                if args.debug > 0:
                    print("DEBUG: Adding the revision to YANG module because xym can't get revision (missing from the YANG module): " + yang_file)
                    #print("DEBUG:  command_string: " + command_string)
                    print("DEBUG:  out: " + new_yang_file_without_path_with_revision)
                    #print("DEBUG:  err: " + err)
                dictionary[new_yang_file_without_path_with_revision] = (compilation, result_pyang, result_no_pyang_param, result_confd, result_yuma, result_yanglint)
                if module_or_submodule(yang_file) == 'module':
                    dictionary_no_submodules[new_yang_file_without_path_with_revision] = (
                        compilation, result_pyang, result_no_pyang_param, result_confd, result_yuma, result_yanglint)
            else:
                print("Unable to get name@revision out of " + yang_file + ' no output')
                #print("ERROR: pyang -f name name-revision ... doesn't work for " + yang_file + " no output")

#        dictionary[yang_file_without_path] = (compilation, result_pyang, result_no_pyang_param, result_confd, result_yuma, result_yanglint)

    # Dictionary serialization
#    write_dictionary_file_in_json(dictionary, args.htmlpath, args.prefix + ".json")
#    json_filename = args.prefix + ".json"
    write_dictionary_file_in_json(dictionary, args.htmlpath, args.prefix + ".json")

    # YANG modules from drafts: : make a list out of the dictionary
    my_list = []
    my_list = sorted(dict_to_list(dictionary_no_submodules))

    # YANG modules from drafts: replace CR by the BR HTML tag
    my_new_list = []
    my_new_list = list_br_html_addition(my_list)

    # YANG modules from drafts: HTML page generation for yang models
    print()
    print(args.prefix + "YANGPageCompilation.html HTML page generation in directory " + args.htmlpath)
    print(args.prefix + "YANGPageMain.html HTML page generation in directory " + args.htmlpath)
    # if want to populate the document location from github, must uncomment the following line
    # if want to populate the document location from github, must change all occurences from
    # number_of_yang_modules_that_passed_compilation(dictionary, 1, ...
    # to number_of_yang_modules_that_passed_compilation(dictionary, 2, ...
    if args.lint:
        compilation_result_text = "Compilation Result (pyang --lint). "
    else:
        compilation_result_text = "Compilation Result (pyang --ietf). "
    # if want to populate the document location from github, must uncomment the following line
    # header=['YANG Model', 'Document Location', 'Compilation', 'Compilation Result (pyang --lint)',
    # 'Compilation Result (pyang)']
#    header = ['YANG Model', 'Compilation', compilation_result_text, 'Compilation Result (pyang)', 'Compilation Results (confdc) Note: alo generate errors for errors found in imported files', 'Compilation Results (yangdump-pro). Note: alo generate errors for errors found in imported files.', 'Compilation Results (yanglint -V -i). Note: also generates errors for imported files.']
    header = ['YANG Model', 'Compilation', compilation_result_text + run_pyang_version(0), 'Compilation Result (pyang). Note: also generates errors for imported files. ' + run_pyang_version(0), 'Compilation Results (confdc) Note: also generates errors for imported files. ' + run_confd_version(0), 'Compilation Results (yangdump-pro). Note: also generates errors for imported files. ' + run_yumadumppro_version(0), 'Compilation Results (yanglint -V -i). Note: also generates errors for imported files. ' + run_yanglint_version(0)]

    generate_html_table(my_new_list, header, args.htmlpath, args.prefix + "YANGPageCompilation.html", args.metadata)

    # HTML page generation for statistics
    passed_without_warnings = number_of_yang_modules_that_passed_compilation(dictionary, 1, "PASSED")
    passed_with_warnings = number_of_yang_modules_that_passed_compilation(dictionary, 1, "PASSED WITH WARNINGS")
    total_number = len(yang_list)
    failed = total_number - passed_without_warnings - passed_with_warnings

    line2 = args.prefix + " YANG MODELS"
    line6 = "Number of YANG data models from " + args.prefix + " that passed compilation: " + str(passed_without_warnings) + "/" + str(total_number)
    line7 = "Number of YANG data models from " + args.prefix + " that passed compilation with warnings: " + str(passed_with_warnings) + "/" + str(total_number)
    line8 = "Number of YANG data models from " + args.prefix + " that failed compilation: " + str(failed) + "/" + str(total_number)
    my_list2 = [line2, line6, line7, line8]
    generate_html_list(my_list2, args.htmlpath, args.prefix + "YANGPageMain.html")

    print("--------------------------")
    print("Number of YANG data models from " + args.prefix + ": " + str(len(yang_list)))
    print("Number of YANG data models from " + args.prefix + " that passed compilation: " + str(passed_without_warnings) + "/" + str(total_number))
    print("Number of YANG data models from " + args.prefix + " that passed compilation with warnings: " + str(passed_with_warnings) + "/" + str(total_number))
    print("Number of YANG data models from " + args.prefix + " that failed compilation: " + str(failed) + "/" + str(total_number))
