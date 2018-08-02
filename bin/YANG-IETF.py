#!/usr/bin/python3

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

# TODO, only check files more recent than a date

__author__ = 'Benoit Claise'
__copyright__ = "Copyright(c) 2015-2018, Cisco Systems, Inc."
__email__ = "bclaise@cisco.com"

from xym import xym
from remove_directory_content import remove_directory_content
from extract_emails import extract_email_string
import argparse
import os
import HTML
import json
import time
import re
from operator import itemgetter
from subprocess import Popen, PIPE
import shlex


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


def ietf_draft_name_containing_keyword(drafts, keyword, debug_level):
    """
    Return the list of IETF drafts whose name contains a specific keyword
    # status: troubleshooting done

    :param drafts: list of ietf drafts
    :param keyword: keyword for which to search
    :return: list of drafts containing the keyword
    """
    keyword = keyword.lower()
    drafts_with_keyword = []
    for f in drafts:
        if keyword in f.lower():
            if debug_level > 0:
                print("DEBUG: " + f + " in ietf_draft_name_containing_keyword: contains " + keyword)
            drafts_with_keyword.append(f)
    if debug_level > 0:
        print("DEBUG: " + " in ietf_draft_name_containing_keyword: drafts_with_keyword contains " + \
              str(drafts_with_keyword))
    return drafts_with_keyword


def list_of_ietf_draft_containing_keyword(drafts, keyword, draftpath):
    """
    Returns the IETF drafts that contains a specific keyword
    # status: troubleshooting done

    :param drafts: List of ietf drafts to search for the keyword
    :param keyword: Keyword to search for
    :return: List of ietf drafts containing the keyword
    """
    keyword = keyword.lower()
    list_of_ietf_draft_with_keyword = []
    for f in drafts:
        file_included = False
        for line in open(draftpath + f, 'r'):
            if keyword in line.lower():
                file_included = True
                if debug_level > 0:
                    print("DEBUG: " + f + " in list_of_ietf_draft_containing_keyword: contains " + keyword)
        if file_included:
            list_of_ietf_draft_with_keyword.append(f)
    if debug_level > 0:
        print("DEBUG: " + " in list_of_ietf_draft_containing_keyword: list_of_ietf_draft_with_keyword contains " \
              + str(list_of_ietf_draft_with_keyword))
    return list_of_ietf_draft_with_keyword


def draft_containing_keyword(draft, keyword, draftpath):
    """
    Returns the IETF drafts that contains a specific keyword
    # status: troubleshooting done

    :param draft: One IETF draft to search for the keyword
    :param keyword: Keyword to search for
    :return: Boolean, True if the draft contains the keyword
    """
    for line in open(draftpath + draft, 'r'):
        if keyword in line:
            return True
    return False


def error_extracting_yang_models_from_an_ietf_draft(f, draftpath, binpath):
    """
    Detect drafts that produce an error when extracting a YANG model
    # status: 
    
    :param f: draft file name
    :param draftpath: Path to the draft directory
    :param binpath: Path for scripts
    :return: Boolean, True if it produces an error

    """
    # test first if there is an error extracting the YANG models
    # bash_command = binpath + "rfcstrip -i " + draftpath + " -d " + yangpath + " " + f + " 2>&1"
    bash_command = binpath + "rfcstrip -n -i " + draftpath + " " + f + " 2>&1"
    temp_result = os.popen(bash_command).read()
    if "WARNING" in temp_result and draft_containing_keyword(f, "<CODE BEGINS>", draftpath):
        if debug_level > 0:
            print("DEBUG: " + " in error_extracting_yang_models_from_an_ietf_draft: ERROR in extracting YANG model in " + f)
        return True
    return False


def extract_yang_models_from_ietf_draft(f, draftpath, yangpath, binpath, debug_level):
    """
    extract YANG model from IETF drafts with rfcstrip
    typical command to execute:
        bashCommand = "/home/bclaise/bin/rfcstrip -i /home/bclaise/ietf/my-id-mirror/ -d /home/bclaise/ietf/YANG "
    status: 
       1. what if there are multiple YANG models in the IETF draft
       2. need to return the dictionary key: yang model, value = ietf draft name

    :param f: draft file name
    :param draftpath: Path to the draft directory
    :param yangpath: Path where to put resulting yang files
    :param binpath: Path for scripts
    :return: True if a YANG model is extracted. False otherwise

    """
    os.chdir(yangpath)
    bash_command = binpath + "rfcstrip -i " + draftpath + " " + f
    if debug_level > 0:
        print("DEBUG: " + " in extract_yang_models_from_ietf_draft: bash_command contains " + bash_command)
    temp_result = os.popen(bash_command).read()
    if temp_result == "":
        return False
    else:
        return True


def list_yang_models_from_ietf_draft(f, draftpath):
    """
    return the list of YANG models in an IETF draft

    :param f: draft file name
    :param draftpath: Path to the draft directory
    :return: list of YANG models within the draft

    """
    first_line_set = False
    first_line = ""
    list_of_yang_modules = []
    if debug_level > 0:
        print("DEBUG: " + " in list_yang_models_from_ietf_draft: extracting YANG models from " + f)
    for line in open(draftpath + f, 'r'):
        if first_line_set:
            combined_line = first_line + line
            if ".yang" in combined_line:
                combined_line = combined_line.strip("\r")
                combined_line = combined_line.strip("\n")
                combined_line = combined_line.replace("<CODE BEGINS>", "")
                combined_line = combined_line.replace("file ", "")
                combined_line = combined_line.replace("\"", "")
                combined_line = combined_line.replace("\n", "")
                combined_line = combined_line.replace("\t", "")
                combined_line = combined_line.replace("\r", "")
                combined_line = combined_line.replace("{", "")
                temp_var = combined_line.split("module")
                combined_line = temp_var[0]
                combined_line = combined_line.lstrip()
                yang_module = combined_line.rstrip()
                list_of_yang_modules.append(yang_module)
            first_line_set = False
            first_line_set = False
            first_line = ""
        if "<CODE BEGINS>" in line:
            if not first_line_set:
                first_line = line
                first_line_set = True
    if debug_level > 0:
        print("DEBUG: " + " in list_yang_models_from_ietf_draft: the list of YANG Models is ")
        print("DEBUG: " + list_of_yang_modules)
    return list_of_yang_modules

def run_pyang(model, ietf, yangpath, debug_level):
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
        bash_command = "$PYANG --path=\"$MODULES\" --ietf " + model + " 2>&1"
    else:
        bash_command = "$PYANG --path=\"$MODULES\" " + model + " 2>&1"        
    if debug_level:
        print("DEBUG: " + " in run_pyang: bash_command contains " + bash_command)
    return os.popen(bash_command).read()
    
def run_pyang_version(debug_level=0):
    """
    Return the pyang version.
    :param debug_level
    :return: a string composed of the pyang version
    """
    bash_command = "$PYANG -v 2>&1"
    if debug_level:
        print("DEBUG: " + " in run_pyang: bash_command contains " + bash_command)
    return os.popen(bash_command).read()

def run_confd(model, yangpath, debug_level):
    """
    Run confdc on the YANG model
    :param model: The file name for the model
    :param yangpath: 
    :return: the outcome of the PYANG compilationf
    """
    os.chdir(yangpath)
    bash_command = "confdc --yangpath $MODULES --yangpath $NONIETFDIR/yangmodels/yang/standard/ieee/draft/ --yangpath $NONIETFDIR/yangmodels/yang/standard/ieee/802.3/draft/ --yangpath $NONIETFDIR/yangmodels/yang/standard/ieee/802.1/draft/ -w TAILF_MUST_NEED_DEPENDENCY -c " + model + " 2>&1"
    if debug_level:
        print("DEBUG: " + " in run_confd: bash_command contains " + bash_command)
    return os.popen(bash_command).read()
    
def run_confd_version(debug_level=0):
    """
    Return the confd version
    :return: a string composed of the confd version
    """
    bash_command = "confdc --version 2>&1"
    if debug_level:
        print("DEBUG: " + " in run_confd: bash_command contains " + bash_command)
    return "confd version " + os.popen(bash_command).read()
    
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
#    bash_command = "yangdump-pro --warn-off=1022 --warn-off=1023 --config=/etc/yumapro/yangdump-pro.conf " + model + " 2>&1"
    bash_command = "yangdump-pro --quiet-mode --config=/etc/yumapro/yangdump-pro.conf " + model + " 2>&1"
    if debug_level:
        print("DEBUG: " + " in yangdump-pro: bash_command contains " + bash_command)
    result = os.popen(bash_command).read()
    result = result.rstrip()
    result = result.lstrip()
    result = re.sub(r'/home/bclaise/.+yang','',result)
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
    bash_command = "yanglint -v 2>&1"
    if debug_level:
        print("DEBUG: " + " in run_yanglint: bash_command contains " + bash_command)
    return os.popen(bash_command).read()
    
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
    generated = ["Generated on " + time.strftime("%d/%m/%Y") + " by Beno&icirc;t Claise"]
    htmlcode = HTML.list(generated)
    htmlcode1 = HTML.table(l, header_row=h)
    f = open(htmlpath + file_name, 'w')
    f.write(htmlcode)
    f.write(htmlcode1)
    f.close()

def generate_html_list(l, htmlpath, file_name):
    """
    Create a table out of the dict and generate a HTML file
    # status: in progress. Still one issue with <br>
    
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
        dictlist.append((key,str(value)))
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
        print("DEBUG: " + in_dict)
    inv_dict = {}
    for k, v in in_dict.items():
        for l in in_dict[k]:
            inv_dict[l] = k
    if debug_level > 0:
        print("DEBUG: in invert_yang_modules_dict: print dictionary before inversion")
        print("DEBUG: " + inv_dict)
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
#        if in_dict[k][2] == compilation_condition: 
         if in_dict[k][3] == compilation_condition: 

            t+=1
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
    f = open(path + file_name, 'w')
    f.write(json.dumps(in_dict))
    f.close()


def read_dictionary_file_in_json(path, file_name):
    """
    Read a file, in json, with my directory data
    For testing purposes.
    # status: THERE IS A BUG, a couple of u' added
    # , u'ietf-opt-if-g698-2.yang': [u'draft-name TBD', u'email address TBD', u'another TBD', u'/home/bclaise/ietf/YANG/ietf-opt-if-g698-2.yang:196: error: premature end of file\n']}

    :param path: The directory where the json file with be created
    :param file_name: The file name to be created
    :return: dictionary
    """
    json_data = open(path + file_name)
    return json.load(json_data)
    
def move_old_examples_YANG_modules_from_RFC(path, path2, debug_level):
    """
    Move some YANG modules, which are documented at http://www.claise.be/IETFYANGOutOfRFCNonStrictToBeCorrected.html: 
    ietf-foo@2010-01-18.yang, hw.yang, hardware-entities.yang, udmcore.yang, and ct-ipfix-psamp-example.yang
    Those YANG modules, from old RFCs, don't follow the example- conventions
    :param path: the path where to remove the YANG modules
    :return: none
    """ 
    for y in ["ietf-foo@2010-01-18.yang", "hw.yang", "hardware-entities.yang", "udmcore.yang", "ct-ipfix-psamp-example@2011-03-15.yang", "example-ospf-topology.yang"]:
        bash_command = "mv " + path + y + " " + path2 + y
        temp_result = os.popen(bash_command).read()
        if debug_level > 0:
            print("DEBUG: " + " move_old_examples_YANG_modules_from_RFC: error " + temp_result)   


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
    elif  "warning" in result_pyang:
        compilation_pyang = "PASSED WITH WARNINGS"
    elif result_pyang == "":
        compilation_pyang = "PASSED"
    else:
        compilation_pyang = "NOT SURE"
        
    # logic for pyang compilation result:
    if "error" in result_no_ietf_flag:
        compilation_pyang_no_ietf = "FAILED" 
    elif  "warning" in result_no_ietf_flag:
        compilation_pyang_no_ietf = "PASSED WITH WARNINGS"
    elif result_no_ietf_flag == "":
        compilation_pyang_no_ietf = "PASSED"
    else:
        compilation_pyang_no_ietf = "NOT SURE"
         
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
    # Next three lines could be removed when mount-point is supported by yanglint
    # result_yanglint = result_yanglint.rstrip()
    # if result_yanglint.endswith("extension statement found, ignoring."):
    #     compilation_yanglint = "PASSED"
        
    # determine the combined compilation status, based on the different compilers
    compilation_list = [compilation_pyang, compilation_pyang_no_ietf, compilation_confd, compilation_yuma, compilation_yanglint]
    if "FAILED" in compilation_list:
        compilation = "FAILED"
    elif "PASSED WITH WARNINGS" in compilation_list:
        compilation = "PASSED WITH WARNINGS"
    elif compilation_list == ["PASSED", "PASSED", "PASSED", "PASSED", "PASSED"]:    
        compilation = "PASSED"
    else:
        compilation = "NOT SURE"

    # Next three lines to be removed after troubleshooting
    #compilation_list = [compilation_pyang, compilation_pyang_no_ietf, compilation_confd, compilation_yuma, compilation_yanglint, compilation]
    #print yang_file + " " + str(compilation_list) + " "+ result_pyang + " " + result_no_ietf_flag + " "+ result_confd + " "+ result_yuma + " "+ result_yanglint
    #return compilation_list
    
    return compilation


def module_or_submodule(input_file):
    if input_file:
        file_input = open(input_file, "r")
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
        print ('File ' + input_file + ' not yang file or not well formated')
        return 'wrong file'
    else:
        return None


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    home = os.path.expanduser('~')
    ietf_directory = os.environ['IETFDIR']
    web_private = os.environ['WEB_PRIVATE']
    web_url = os.environ['WEB_URL']
    parser = argparse.ArgumentParser(description='Yang RFC/Draft Processor')
    parser.add_argument("--draftpath", default= ietf_directory + "/my-id-mirror/",
                        help="The optional directory where to find the source drafts. "
                             "Default is " + ietf_directory + "'/my-id-mirror/'")
    parser.add_argument("--rfcpath", default= ietf_directory + "/rfc/",
                        help="The optional directory where to find the source RFCs. Default is '" + ietf_directory + "/rfc/'")
    parser.add_argument("--binpath", default=home + "/bin/", help="Optional directory where to find the "
                                                                        "script executables. Default is '" + home + "/bin/'")
    parser.add_argument("--htmlpath", default= web_private + '/',
                        help="The path to create the HTML file (optional). Default is '" + web_private + "/'")
    parser.add_argument("--yangpath", default= ietf_directory + "/YANG/", help="The optional directory where to put the "
                                                                               "correctly extracted models. "
                                                                               "Default is " + ietf_directory + "'/YANG/'")
    parser.add_argument("--allyangpath", default= ietf_directory +"/YANG-all/", help="The optional directory where to store "
                                                                               "all extracted models (including bad ones). "
                                                                               " Default is '" + ietf_directory + "/YANG-all/'")
    parser.add_argument("--allyangexamplepath", default= ietf_directory  + "/YANG-example/", help="The optional directory where to store "
                                                                               "all extracted example models (starting with example- and not with CODE BEGINS/END). "
                                                                               " Default is '" + ietf_directory + "/YANG-example/'")
    parser.add_argument("--yangexampleoldrfcpath", default= ietf_directory  + "/YANG-example-old-rfc/", help="The optional directory where to store "
                                                                               "the hardcoded YANG module example models from old RFCs (not starting with example-). "
                                                                               " Default is '" + ietf_directory + "/YANG-example-old-rfc/'")
    parser.add_argument("--allyangdraftpathstrict", default= ietf_directory  + "/draft-with-YANG-strict/", help="The optional directory where to store "
                                                                               "all drafts containing YANG model(s), with strict xym rule = True. "
                                                                               " Default is '" + ietf_directory + "/draft-with-YANG-strict/'")
    parser.add_argument("--allyangdraftpathnostrict", default= ietf_directory  + "/draft-with-YANG-no-strict/", help="The optional directory where to store "
                                                                               "all drafts containing YANG model(s), with strict xym rule = False. "
                                                                               " Default is '" + ietf_directory + "/draft-with-YANG-no-strict/'")
    parser.add_argument("--allyangdraftpathonlyexample", default= ietf_directory  + "/draft-with-YANG-example/", help="The optional directory where to store "
                                                                               "all drafts containing YANG model(s) with examples," 
                                                                               "with strict xym rule = True, and strictexample True. "
                                                                               " Default is '" + ietf_directory + "/draft-with-YANG-example/'")
    parser.add_argument("--rfcyangpath", default= ietf_directory  + "/YANG-rfc/", help="The optional directory where to store "
                                                                               "the data models extracted from RFCs"
                                                                               "Default is '" + ietf_directory + "/YANG-rfc/'")
    parser.add_argument("--rfcextractionyangpath", default= ietf_directory  + "/YANG-rfc-extraction/", help="The optional directory where to store "
                                                                               "the typedef, grouping, identity from data models extracted from RFCs"
                                                                               "Default is '" + ietf_directory  + "/YANG-rfc/'")
    parser.add_argument("--draftextractionyangpath", default= ietf_directory  + "/YANG-extraction/", help="The optional directory where to store "
                                                                               "the typedef, grouping, identity from data models correctely extracted from drafts"
                                                                               "Default is '" + home + "/ietf/YANG-rfc/'")
    parser.add_argument("--strict", type=bool, default=False, help='Optional flag that determines syntax enforcement; '
                                                                   "'If set to 'True' <CODE BEGINS> / <CODE ENDS> are "
                                                                   "required; default is 'False'")                                                                                 
    parser.add_argument("--debug", type=int, default=0, help="Debug level; the default is 0")

    args = parser.parse_args()
    debug_level = args.debug
    # note: args.strict is not used

    
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
    ietf_drafts = [f for f in os.listdir(args.draftpath) if os.path.isfile(os.path.join(args.draftpath, f))]
    ietf_rfcs = [f for f in os.listdir(args.rfcpath) if os.path.isfile(os.path.join(args.rfcpath, f))]
        
    # Extracting YANG Modules from IETF drafts
    draft_yang_dict = {}
    draft_yang_all_dict = {}
    draft_yang_example_dict = {}
    rfc_yang_dict = {}
    
    for rfc_file in ietf_rfcs:
        # Extract the correctly formatted YANG Models in args.rfcyangpath
        yang_models_in_rfc = xym.xym(rfc_file, args.rfcpath, args.rfcyangpath, strict=True, strict_examples=False, debug_level=args.debug, add_line_refs=False, force_revision_pyang=False, force_revision_regexp=True)
        if yang_models_in_rfc:
            if debug_level > 0:
                print("DEBUG: in main: extracted YANG models from RFC:")
                print("DEBUG: " + str(yang_models_in_rfc))
                print
            # typedef, grouping, and identity extraction from RFCs
            for y in yang_models_in_rfc:
                if not y.startswith("example-"):
                    print("Extraction for " + y)
                    bash_command = "extractor.py --srcdir " + args.rfcyangpath + " --dstdir " + args.rfcextractionyangpath + " --type typedef " + y
                    temp_result = os.popen(bash_command).read()
                    if debug_level > 0:
                        print("DEBUG: " + " extracting the typdefs containing a RFC YANG model:  error " + temp_result)
                    
                    bash_command = "extractor.py --srcdir " + args.rfcyangpath + " --dstdir " + args.rfcextractionyangpath + " --type grouping " + y
                    temp_result = os.popen(bash_command).read()
                    if debug_level > 0:
                        print("DEBUG: " + " extracting the grouping containing a RFC YANG model:  error " + temp_result)
                    
                    bash_command = "extractor.py --srcdir " + args.rfcyangpath + " --dstdir " + args.rfcextractionyangpath + " --type identity " + y
                    temp_result = os.popen(bash_command).read()
                    if debug_level > 0:
                        print("DEBUG: " + " extracting the grouping containing a RFC YANG model:  error " + temp_result)
                    #if not y.startswith("iana-"):
					    # this is where I add the check
            rfc_yang_dict[rfc_file] = yang_models_in_rfc
    
    for draft_file in ietf_drafts:
        # Extract the correctly formatted YANG Models in args.yangpath
        yang_models_in_draft = xym.xym(draft_file, args.draftpath, args.yangpath, strict=True, strict_examples=False, debug_level=args.debug, add_line_refs=False, force_revision_pyang=False, force_revision_regexp=True)
       
        if yang_models_in_draft:
            if debug_level > 0:
                print("DEBUG: in main: extracted YANG models from draft:")
                print("DEBUG: " + yang_models_in_draft)
                print

#            yang_models_in_draft_with_revision = []
            for y in yang_models_in_draft: 
                # typedef, grouping, and identity extraction from drafts            
                if not y.startswith("example-"):
                    print("extraction for " + y)
                    bash_command = "extractor.py --srcdir " + args.yangpath + " --dstdir " + args.draftextractionyangpath + " --type typedef " + y
                    temp_result = os.popen(bash_command).read()
                    if debug_level > 0:
                        print("DEBUG: " + " extracting the typdefs containing a draft YANG model:  error " + temp_result)
                    
                    bash_command = "extractor.py --srcdir " + args.yangpath + " --dstdir " + args.draftextractionyangpath + " --type grouping " + y
                    temp_result = os.popen(bash_command).read()
                    if debug_level > 0:
                        print("DEBUG: " + " extracting the grouping containing a draft YANG model:  error " + temp_result)
                    
                    bash_command = "extractor.py --srcdir " + args.yangpath + " --dstdir " + args.draftextractionyangpath + " --type identity " + y
                    temp_result = os.popen(bash_command).read()
                    if debug_level > 0:
                       print("DEBUG: " + " extracting the grouping containing a draft YANG model:  error " + temp_result)        
                       
            draft_yang_dict[draft_file] = yang_models_in_draft   
            
            # copy the draft in a specific directory for strict = True
            bash_command = "cp " + args.draftpath + draft_file + " " + args.allyangdraftpathstrict
            temp_result = os.popen(bash_command).read()
            if debug_level > 0 and temp_result:
                print("DEBUG: " + " copy the IETF draft containing a YANG model:  error " + temp_result)

    # Extract the correctly formatted example YANG Models in args.allyangexamplepath
        yang_models_in_draft = xym.xym(draft_file, args.draftpath, args.allyangexamplepath, strict=True, strict_examples=True, debug_level=args.debug)
        if yang_models_in_draft:
            if debug_level > 0:
                print("DEBUG: in main: extracted YANG models from draft:")
                print("DEBUG: " + yang_models_in_draft)
                print  
            draft_yang_example_dict[draft_file] = yang_models_in_draft
            
            # copy the draft in a specific directory for strict = True
            bash_command = "cp " + args.draftpath + draft_file + " " + args.allyangdraftpathonlyexample
            temp_result = os.popen(bash_command).read()
            if debug_level > 0:
                print("DEBUG: " + " copy the IETF draft containing a YANG model:  error " + temp_result)
                
        # Extract  all YANG Models, included the wrongly formatted ones, in args.allyangpath
        yang_models_in_draft = xym.xym(draft_file, args.draftpath, args.allyangpath, strict=False, strict_examples=False, debug_level=args.debug)
        if yang_models_in_draft:
            if debug_level > 0:
                print("DEBUG: in main: extracted YANG models from draft:")
                print("DEBUG: " + yang_models_in_draft)
                print
            draft_yang_all_dict[draft_file] = yang_models_in_draft          

            # copy the draft in a specific directory for strict = False
            bash_command = "cp " + args.draftpath + draft_file + " " + args.allyangdraftpathnostrict
            temp_result = os.popen(bash_command).read()
            if debug_level > 0:
                print("DEBUG: " + " copy the IETF draft containing a YANG model:  error " + temp_result)
            
    # invert the key, value in the dictionary. Should be key: yang model, value: draft-file
    yang_draft_dict = invert_yang_modules_dict(draft_yang_dict, debug_level)
    yang_example_draft_dict = invert_yang_modules_dict(draft_yang_example_dict, debug_level)
    yang_draft_all_dict = invert_yang_modules_dict(draft_yang_all_dict, debug_level)   
    yang_rfc_dict = invert_yang_modules_dict(rfc_yang_dict, debug_level)
    # Remove the YANG modules (the key in the inverted rfc_dict dictionary dictionary)
    # which are documented at http://www.claise.be/IETFYANGOutOfRFCNonStrictToBeCorrected.html: 
	# and the example-ospf-topology.yang, which is bug in xym
    # ietf-foo@2010-01-18.yang, hw.yang, hardware-entities.yang, udmcore.yang, and ct-ipfix-psamp-example.yang
    yang_rfc_dict = {k:v for k,v in yang_rfc_dict.items() if k != 'ietf-foo@2010-01-18.yang' and k != 'hw.yang' and k != 'hardware-entities.yang' and k != 'udmcore.yang' and k != 'ct-ipfix-psamp-example@2011-03-15.yang' and k != 'example-ospf-topology.yang' }
    # Move the YANG modules, which are documented at http://www.claise.be/IETFYANGOutOfRFCNonStrictToBeCorrected.html: 
    # ietf-foo@2010-01-18.yang, hw.yang, hardware-entities.yang, udmcore.yang, and ct-ipfix-psamp-example.yang
	# and the example-ospf-topology.yang, which is bug in xym
    # Those YANG modules, from old RFCs, don't follow the example- conventions
    move_old_examples_YANG_modules_from_RFC(args.rfcyangpath, args.yangexampleoldrfcpath, debug_level)
    
    # YANG modules from drafts: PYANG validation, dictionary generation, dictionary inversion, and page generation
    dictionary = {}
    dictionary_no_submodules = {}
    for yang_file in yang_draft_dict:
        draft_name, email, compilation = "", "", ""
        result_pyang, result_no_ietf_flag, result_confd, result_yuma, result_yanglint = "", "", "", "", "" 
        # print("PYANG compilation of " + yang_file)
        ietf_flag = True
        result_pyang = run_pyang(yang_file, ietf_flag, args.yangpath, debug_level)
        ietf_flag = False
        result_no_ietf_flag = run_pyang(yang_file, ietf_flag, args.yangpath, debug_level)
        result_confd = run_confd(yang_file, args.yangpath, debug_level)
        result_yuma = run_yumadumppro(yang_file, args.yangpath, debug_level)
        result_yanglint = run_yanglint(yang_file, args.yangpath, debug_level)      
        draft_name = yang_draft_dict[yang_file]
        url = draft_name.split(".")[0]
        url = url.rstrip('-0123456789')
        mailto = url + "@ietf.org"
        url = "http://datatracker.ietf.org/doc/" + url
        draft_url = '<a href="' + url + '">' + draft_name + '</a>'
        email = '<a href="mailto:' + mailto + '">Email Authors</a>'
        url2 = web_url + "/YANG-modules/" + yang_file
        yang_url = '<a href="' + url2 + '">Download the YANG model</a>'
        
        compilation = combined_compilation(yang_file, result_pyang, result_no_ietf_flag, result_confd, result_yuma, result_yanglint)  
        
        dictionary[yang_file] = (draft_url, email, yang_url, compilation, result_pyang, result_no_ietf_flag, result_confd, result_yuma, result_yanglint)
        if module_or_submodule(args.yangpath + yang_file) == 'module':
            dictionary_no_submodules[yang_file] = (draft_url, email, yang_url, compilation, result_pyang, result_no_ietf_flag, result_confd, result_yuma, result_yanglint)

        
    # Dictionary serialization
    write_dictionary_file_in_json(dictionary, args.htmlpath, "IETFYANGDraft.json")
    # YANG modules from drafts: : make a list out of the dictionary
    my_list = []
    my_list = sorted(dict_to_list(dictionary_no_submodules))
    # YANG modules from drafts: replace CR by the BR HTML tag
    my_new_list = []
    my_new_list = list_br_html_addition(my_list)
    # YANG modules from drafts: HTML page generation for yang models
    print
    print("HTML page generation")
    header=['YANG Model', 'Draft Name', 'Email', 'Download the YANG model', 'Compilation', 'Compilation Result (pyang --ietf). ' + run_pyang_version(0), 'Compilation Result (pyang). Note: also generates errors for imported files. ' + run_pyang_version(0), 'Compilation Results (confdc) Note: also generates errors for imported files. ' + run_confd_version(0), 'Compilation Results (yangdump-pro). Note: also generates errors for imported files. ' + run_yumadumppro_version(0), 'Compilation Results (yanglint -V -i). Note: also generates errors for imported files. ' + run_yanglint_version(0)]
    generate_html_table(my_new_list, header, args.htmlpath, "IETFYANGDraftPageCompilation.html")
    
    # Example- YANG modules from drafts: PYANG validation, dictionary generation, dictionary inversion, and page generation
    dictionary_example = {}
    dictionary_no_submodules_example = {}
    for yang_file in yang_example_draft_dict:
        draft_name, email, compilation = "", "", ""
        result_pyang, result_no_ietf_flag = "", ""
        ietf_flag = True
        result_pyang = run_pyang(yang_file, ietf_flag, args.allyangexamplepath, debug_level)
        ietf_flag = False
        result_no_ietf_flag = run_pyang(yang_file, ietf_flag, args.allyangexamplepath, debug_level)
        draft_name = yang_example_draft_dict[yang_file]
        url = draft_name.split(".")[0]
        url = url.rstrip('-0123456789')
        mailto = url + "@ietf.org"
        url = "http://datatracker.ietf.org/doc/" + url
        draft_url = '<a href="' + url + '">' + draft_name + '</a>'
        email = '<a href="mailto:' + mailto + '">Email Authors</a>'
        if "error" in result_pyang:
            compilation = "FAILED" 
        elif  "warning" in result_pyang:
            compilation = "PASSED WITH WARNINGS"
        elif result_pyang == "":
            compilation = "PASSED"
        else:
            compilation = "NOT SURE"
        dictionary_example[yang_file] = (draft_url, email, compilation, result_pyang, result_no_ietf_flag)
        if module_or_submodule(args.allyangexamplepath + yang_file) == 'module':
            dictionary_no_submodules_example[yang_file] = (draft_url, email, compilation, result_pyang, result_no_ietf_flag)

    # Dictionary serialization
    write_dictionary_file_in_json(dictionary_example, args.htmlpath, "IETFYANGDraftExample.json")
    # dictionary2 = {}
    # dictionary2 = read_dictionary_file_in_json(args.htmlpath, "IETFYANG.json")
    # YANG modules from drafts: : make a list out of the dictionary
    my_list = []
    my_list = sorted(dict_to_list(dictionary_no_submodules_example))
    # YANG modules from drafts: replace CR by the BR HTML tag
    my_new_list = []
    my_new_list = list_br_html_addition(my_list)
    # YANG modules from drafts: HTML page generation for yang models
    print
    print("HTML page generation for Example YANG Models")
    header=['YANG Model', 'Draft Name', 'Email', 'Compilation', 'Compilation Result (pyang --ietf)', 'Compilation Result (pyang). Note: also generates errors for imported files.']
    generate_html_table(my_new_list, header, args.htmlpath, "IETFYANGDraftExamplePageCompilation.html")
    
    
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
        # Uncomment next three lines if I want to remove the submodule from the RFC report in http://www.claise.be/IETFYANGOutOfRFC.png
        #dictionary_no_submodules2[yang_file] = rfc_url
        #if module_or_submodule(args.rfcyangpath + yang_file) == 'module':
            #dictionary_no_submodules2[yang_file] = rfc_url

    # Dictionary serialization
    write_dictionary_file_in_json(dictionary2, args.htmlpath, "IETFYANGRFC.json")

# (Un)comment next two lines if I want to remove the submodule from the RFC report in http://www.claise.be/IETFYANGOutOfRFC.png
    my_yang_in_rfc = sorted(dict_to_list_rfc(dictionary2))
#    my_yang_in_rfc = sorted(dict_to_list_rfc(dictionary_no_submodules2), key = itemgetter(1))
    
    # stats number generation
    number_of_modules_YANG_models_from_ietf_drafts = len(yang_draft_dict.keys())
    number_of_modules_YANG_models_from_ietf_drafts_passed_compilation_without_warnings = number_of_yang_modules_that_passed_compilation(dictionary, "PASSED")
    number_of_modules_YANG_models_from_ietf_drafts_passed_compilation_wit_warnings = number_of_yang_modules_that_passed_compilation(dictionary, "PASSED WITH WARNINGS")
    number_of_all_modules = len([f for f in os.listdir(args.allyangpath) if os.path.isfile(os.path.join(args.allyangpath, f))])
    number_of_example_modules_YANG_models_from_ietf_drafts = len(yang_example_draft_dict.keys())    
    
    # YANG modules from RFCs: HTML page generation for yang models
    header=['YANG Model (and Submodel)', 'RFC']
    generate_html_table(my_yang_in_rfc, header, args.htmlpath, "IETFYANGRFC.html")
    # HTML page generation for statistics
#    line1 = ""
    line2 = "<H3>IETF YANG MODELS</H3>"
    line5 = "Number of correctly extracted YANG models from IETF drafts: " + str(number_of_modules_YANG_models_from_ietf_drafts)
    line6 = "Number of YANG models in IETF drafts that passed compilation without warnings: " + str(number_of_modules_YANG_models_from_ietf_drafts_passed_compilation_without_warnings) + "/" + str(number_of_modules_YANG_models_from_ietf_drafts)
    line7 = "Number of YANG models in IETF drafts that passed compilation with warnings: " + str(number_of_modules_YANG_models_from_ietf_drafts_passed_compilation_wit_warnings) + "/" + str(number_of_modules_YANG_models_from_ietf_drafts)
    line8 = "Number of all YANG models in IETF drafts (example, badly formatted, etc. ): " + str(number_of_all_modules)
    line9 = "Number of correctly extracted example YANG models from IETF drafts: " + str(number_of_example_modules_YANG_models_from_ietf_drafts)
    my_list2 = [line2, line5, line6, line7, line8, line9]

    generate_html_list(my_list2, args.htmlpath, "IETFYANGPageMain.html")

    # Stats generation for the standard output 
    print("--------------------------")
    print("Number of correctly extracted YANG models from IETF drafts: " + str(number_of_modules_YANG_models_from_ietf_drafts))
    print("Number of YANG models in IETF drafts that passed compilation without warnings: " + str(number_of_modules_YANG_models_from_ietf_drafts_passed_compilation_without_warnings) + "/" + str(number_of_modules_YANG_models_from_ietf_drafts))
    print("Number of YANG models in IETF drafts that passed compilation with warnings: " + str(number_of_modules_YANG_models_from_ietf_drafts_passed_compilation_wit_warnings) + "/" + str(number_of_modules_YANG_models_from_ietf_drafts))
    print("Number of all YANG models in IETF drafts (example, badly formatted, etc. ): " + str(number_of_all_modules))
    print("Number of correctly extracted example YANG models from IETF drafts: " + str(number_of_example_modules_YANG_models_from_ietf_drafts))

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
            result_pyang = run_pyang(yang_file, ietf_flag, args.allyangpath, debug_level)
            ietf_flag = False
            result_no_ietf_flag = run_pyang(yang_file, ietf_flag, args.allyangpath, debug_level)
            result_confd = run_confd(yang_file, args.yangpath, debug_level)
            result_yuma = run_yumadumppro(yang_file, args.yangpath, debug_level)
            result_yanglint = run_yanglint(yang_file, args.yangpath, debug_level)      
            draft_name = yang_draft_dict[yang_file]
            url = draft_name.split(".")[0]
            url = url.rstrip('-0123456789')
            mailto = url + "@ietf.org"
            url = "http://datatracker.ietf.org/doc/" + url
            draft_url = '<a href="' + url + '">' + draft_name + '</a>'
            email = '<a href="mailto:' + mailto + '">Email All Authors</a>'
            cisco_email = '<a href="mailto:' + cisco_email + '">Email Cisco Authors Only</a>'                   
            url2 = web_url + "/YANG-modules/" + yang_file
            yang_url = '<a href="' + url2 + '">Download the YANG model</a>'
            
            compilation = combined_compilation(yang_file, result_pyang, result_no_ietf_flag, result_confd, result_yuma, result_yanglint)  

            dictionary[yang_file] = (draft_url, email, cisco_email, yang_url, compilation, result_pyang, result_no_ietf_flag, result_confd, result_yuma, result_yanglint)
            if module_or_submodule(args.yangpath + yang_file) == 'module':
                dictionary_no_submodules[yang_file] = (draft_url, email, cisco_email, yang_url, compilation, result_pyang, result_no_ietf_flag, result_confd, result_yuma, result_yanglint)
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
            
    # make a list out of the dictionary
    my_list = []
    my_list = sorted(dict_to_list(dictionary_no_submodules))
# I believe I can remove the next line    
#    my_yang_in_rfc = sorted(dict_to_list_rfc(yang_rfc_dict))   
    # replace CR by the BR HTML tag
    my_new_list = []
    my_new_list = list_br_html_addition(my_list)
    # HTML page generation for yang models
    print
    print("Cisco HTML page generation")
    header=['YANG Model', 'Draft Name', 'All Authors Email', 'Only Cisco Email','Download the YANG model','Compilation', 'Compilation Results (pyang --ietf)', 'Compilation Results (pyang). Note: also generates errors for imported files.', 'Compilation Results (confdc) Note: also generates errors for imported files', 'Compilation Results (yumadump-pro). Note: also generates errors for imported files.', 'Compilation Results (yanglint -V -i). Note: also generates errors for imported files.']
    generate_html_table(my_new_list, header, args.htmlpath, "IETFYANGCiscoAuthorsPageCompilation.html")
    print(output_email_string_unique)

