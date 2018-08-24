#!/usr/bin/env python

__author__ = 'Benoit Claise'
__copyright__ = "Copyright(c) 2015-2018, Cisco Systems, Inc."
__license__ = "Apache V2.0"
__email__ = "bclaise@cisco.com"


import argparse
import configparser
import os
import HTML
import json
import time
import datetime
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import date2num,datestr2num,num2date,num2epoch,strpdate2num
from extract_emails import extract_email_string


# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------

def list_of_files_in_dir(srcdir, extension, debug_level):
    """
    Returns the list of file in a directory   
    :param srcdir: directory to search for files
    :param extension: file extension to search for
    :param debug_level: If > 0 print(some debug statements to the console
    :return: list of files
    """
    files = [f for f in os.listdir(srcdir) if os.path.isfile(os.path.join(srcdir, f))]
    yang_files = []
    for f in files:
        if f.endswith(extension):
            yang_files.append(f)
            if debug_level > 0:
                print("DEBUG: " + f + " in list_of_files_in_dir: ends with " + extension)
        else:
            if debug_level > 0:
                print("DEBUG: " + f + " in list_of_files_in_dir: doesn't ends with " + extension)
    return yang_files
 
 
def list_of_files_in_dir_created_after_date(files, srcdir, d, debug_level):
    """
    only select the files created wihin the number of days selected   
    :param files: list of files
    :param srcdir: directory to search for files
    :param d: number of days
    :param debug_level: If > 0 print(some debug statements to the console
    :return: list of files
    """
    new_files = []
    dt = datetime.datetime.utcnow()               # datetime now (all in UTC)
    if debug_level > 0:
        print(dt)
    delta = datetime.timedelta(d)                 # x days interval
    dtdays = dt - delta                           # datetime x days earlier than now
    if debug_level > 0:
        print(dtdays)
    for f in files:
        if debug_level > 0:
            print(srcdir + "/" + f)
        t = os.path.getmtime(srcdir + "/" + f)    # time of last modification in seconds
        dt = datetime.datetime.utcfromtimestamp(t)    # datetime representation 
        if dt > dtdays:
            if debug_level > 0:
                print("Keep")
            new_files.append(f)
        else:
            if debug_level > 0:
                print("Dont keep")
    return new_files    
    
def file_name_containing_keyword(drafts, keyword, debug_level):
    """
    Return the list of file whose name contains a specific keyword

    :param drafts: list of ietf drafts
    :param keyword: keyword for which to search
    :return: list of drafts containing the keyword
    """
    keyword = keyword.lower()
    drafts_with_keyword = []
    for f in drafts:
        if keyword in f.lower():
            if debug_level > 0:
                print("DEBUG: " + f + " in file_name_containing_keyword: contains " + keyword)
            drafts_with_keyword.append(f)
    if debug_level > 0:
        print("DEBUG: " + " in file_name_containing_keyword: drafts_with_keyword contains " + \
              str(drafts_with_keyword))
    drafts_with_keyword.sort()
    return drafts_with_keyword
    
def list_of_ietf_draft_containing_keyword(drafts, keyword, draftpath, debug_level):
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
    with open(path + file_name, 'w') as outfile:
        json.dump(in_dict, outfile, indent = 4, ensure_ascii = True)
    
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
    
# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


if __name__ == "__main__":
    bin_directory = os.environ['BIN']
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config.read('/etc/yangcatalog/yangcatalog.conf')
    web_private = config.get('Web-Section', 'private_directory')
    backup_directory = config.get('Directory-Section', 'backup')
    ietf_directory = config.get('Directory-Section', 'ietf_directory')

    parser = argparse.ArgumentParser(description='YANG Stats Extractor')
    parser.add_argument("--htmlpath", default= backup_directory + '/',
                        help="The path to get the HTML file (optional). Default is '" + backup_directory + "/'")
    parser.add_argument("--days", default="-1",
                        help="The numbers of days to get back in history. Default is all")
    parser.add_argument("--draftpathstrict", default= ietf_directory + "/draft-with-YANG-strict/",
                        help="The path to get the ietf drafts containing YANG model(s), with xym strict flag = True. Default is '" + ietf_directory + "/draft-with-YANG-strict/'")
    parser.add_argument("--draftpathnostrict", default= ietf_directory + "/draft-with-YANG-no-strict/",
                        help="The path to get the ietf drafts containing YANG model(s), with xym strict flag = False. Default is '" + ietf_directory + "/draft-with-YANG-no-strict/'")
    parser.add_argument("--draftpathdiff", default= ietf_directory + "/draft-with-YANG-diff/",
                        help="The path to put the ietf drafts containing YANG model(s), diff from flag = True and False. Default is '" + ietf_directory + "/draft-with-YANG-diff/'")
    parser.add_argument("--statspath", default= web_private + "/stats/",
                        help="The optional directory where to put the stats files . Default is '" + web_private + "/stats/'")
    parser.add_argument("--binpath", default= bin_directory, help="Optional directory where to find the "
                                                                        "script executables. Default is '" + bin_directory + "'")
 
    parser.add_argument("--debug", type=int, default=0, help="Debug level; the default is 0")

    args = parser.parse_args()
    debug_level = args.debug
    
category_list = ["FAILED", "PASSED WITH WARNINGS", "PASSED", "Email All Authors"]
all_files = list_of_files_in_dir(args.htmlpath, "html", debug_level)
#print(files

# only select the files created wihin the number of days selected
if int(args.days) > 0:
    files = list_of_files_in_dir_created_after_date(all_files, args.htmlpath, int(args.days), debug_level)
else:
    files = all_files

prefix = "IETFCiscoAuthorsYANGPageCompilation" 
selected_files = file_name_containing_keyword(files, prefix, debug_level)

IETFYANGCiscoAuthorsPageCompilation = {}
IETFYANGPageCompilation = {}
    
for prefix in ["IETFCiscoAuthorsYANGPageCompilation_", "IETFDraftYANGPageCompilation_", "IEEEYANGPageCompilation_", "LithiumODLPageCompilation_"]:
    print('')
    print("Looking at the files starting with: " + prefix)
    print("FILENAME: NUMBER OF DAYS SINCE EPOCH, TOTAL YANG MODULES, PASSED, PASSEDWITHWARNINGS, FAILED")
    for f in file_name_containing_keyword(files, prefix, debug_level):   
        bash_command = "grep" + " " + category_list[0] + " " + args.htmlpath + f + " | wc -l " +" 2>&1"
        failed_result = os.popen(bash_command).read()
        failed_result = failed_result.rstrip("\r\n")
    
        bash_command = "grep" + " " + "\"PASSED WITH WARNINGS\"" + " " + args.htmlpath + f + " | wc -l " +" 2>&1"
        passed_with_warning_result = os.popen(bash_command).read()
        passed_with_warning_result = passed_with_warning_result.rstrip("\r\n")
   
        bash_command = "grep" + " " + category_list[2] + " " + args.htmlpath + f + " | grep -v WARNINGS | wc -l " +" 2>&1"
        passed_result = os.popen(bash_command).read()
        passed_result = passed_result.rstrip("\r\n")

#        bash_command = "grep" + " " + "\"Email All Authors\"" + " " + args.htmlpath + f + " | wc -l " +" 2>&1"
        bash_command = "grep" + " " + ".txt" + " " + args.htmlpath + f + " | wc -l " +" 2>&1"
        total_result = os.popen(bash_command).read()
        total_result = total_result.rstrip("\r\n")
        if prefix == "LithiumODLPageCompilation_":
            total_result = str(int(failed_result) + int(passed_with_warning_result) + int(passed_result))
    
        f = f.split(".")[0]
        year = f.split("_")[1]
        month = f.split("_")[2]
        day = f.split("_")[3] 
        extracted_date = datetime.date(int(year), int(month), int(day))
        matplot_date = date2num(extracted_date)
#        print(f + ": " + str(matplot_date)  + " " + total_result + " " + passed_result + " " + passed_with_warning_result + " " + failed_result)
        if prefix == "IETFCiscoAuthorsYANGPageCompilation_":
            IETFYANGCiscoAuthorsPageCompilation[matplot_date] = {"total":total_result, "warning":passed_with_warning_result, "success":passed_result}
        elif prefix == "IETFDraftYANGPageCompilation_":
            IETFYANGPageCompilation[matplot_date] = {"total":total_result, "warning":passed_with_warning_result, "success":passed_result}

# write IETFYANGCiscoAuthorsPageCompilation to a json file
if int(args.days) == -1:
    write_dictionary_file_in_json(IETFYANGCiscoAuthorsPageCompilation, args.statspath, "IETFCiscoAuthorsYANGPageCompilationStats.json")
    write_dictionary_file_in_json(IETFYANGPageCompilation, args.statspath, "IETFYANGPageCompilationStats.json")

#Print the number of RFCs per date, and store the info into a json file            
IETFYANGOutOfRFC = {}
prefix = "IETFYANGOutOfRFC_"
print('')
print("Looking at the files starting with :" + prefix)
print("FILENAME: NUMBER OF DAYS SINCE EPOCH, NUMBER OF YANG MODELS IN RFCS")
for f in file_name_containing_keyword(files, prefix, debug_level):   
    bash_command = "grep .yang "+ args.htmlpath + f + " | wc -l " +" 2>&1"
    rfc_result = os.popen(bash_command).read()
    rfc_result = rfc_result.rstrip("\r\n")
    f = f.split(".")[0]
    year = f.split("_")[1]
    month = f.split("_")[2]
    day = f.split("_")[3]  
    extracted_date = datetime.date(int(year), int(month), int(day))   
#    print(f + " : " + str(date2num(extracted_date)) +" " + rfc_result)
    IETFYANGOutOfRFC[str(date2num(extracted_date))] = {"total":rfc_result}
# write IETFYANGOutOfRFC to a json file
if int(args.days) == -1:
    write_dictionary_file_in_json(IETFYANGOutOfRFC, args.statspath, "IETFYANGOutOfRFCStats.json")
    
 # pie chart
 # IETF: total number of 
 # ODL: total number in Lithium
 # 
for prefix in ["IEEEYANGPageCompilation_", "IETFCiscoAuthorsYANGPageCompilation_", "IETFYANGPageCompilation_", "LithiumODLPageCompilation_"]:
    print('')
    print("Looking at the files starting with: " + prefix + " for the newest file")
    # next line returns the newest file
    matching_files = file_name_containing_keyword(all_files, prefix, debug_level)
    if debug_level > 0:
        if len(matching_files):
            print(matching_files[-1])
        else:
            print("No matching files")
    if len(matching_files):
        bash_command = "grep" + " " + ".txt" + " " + args.htmlpath + matching_files[-1]  + " | wc -l " +" 2>&1"
        total_result = os.popen(bash_command).read()
        total_result = total_result.rstrip("\r\n")
        if prefix == "LithiumODLPageCompilation_":
            total_result = str(int(failed_result) + int(passed_with_warning_result) + int(passed_result))
            # because failed_result, passed_with_warning_result, and passed_result are unchanged from the loop before
            # this is an ugly hack
        print("  " + str(total_result))
    else:
        print("  0")
    
# determine the number of company authored drafts
# two methods
# first, based on extract_email_string: it searches for the email keyword and then the company email address
# second, doing a simple grep through all the lines for the drafts containing YANG models

#cisco_numbers = 0
#brocade_numbers = 0
#juniper_numbers = 0
#huawei_numbers = 0
#total_number_drafts = 0
 
#files = [f for f in os.listdir(args.draftpathstrict) if os.path.isfile(os.path.join(args.draftpathstrict, f))]
 
#for draft_file in files:
#    total_number_drafts += 1
#    if extract_email_string(args.draftpathstrict + draft_file, "@cisco.com", debug_level):
#        cisco_numbers += 1
#    if extract_email_string(args.draftpathstrict + draft_file, "@brocade.com", debug_level):
#        brocade_numbers += 1
#    if extract_email_string(args.draftpathstrict + draft_file, "@huawei.com", debug_level):
#        huawei_numbers += 1
#    if extract_email_string(args.draftpathstrict + draft_file, "@juniper.net", debug_level):
#        juniper_numbers += 1
        
#print("get YANG drafts authored per company: method 1"
#print("Cisco authored drafts with YANG Model(s): " + str(cisco_numbers)
#print("Huawei authored drafts with YANG Model(s): " + str(huawei_numbers)
#print("Juniper authored drafts with YANG Model(s): " + str(juniper_numbers) 
#print("Brocade authored drafts with YANG Model(s): " + str(brocade_numbers)
           
# method 2

total_number_drafts = 0 
files = [f for f in os.listdir(args.draftpathstrict) if os.path.isfile(os.path.join(args.draftpathstrict, f))]
files_no_strict = [f for f in os.listdir(args.draftpathnostrict) if os.path.isfile(os.path.join(args.draftpathnostrict, f))]
total_number_drafts = len(files) 
total_number_drafts_no_strict = len(files_no_strict) 

print()
print("Print, per company, the number of IETF drafts containing YANG model(s)")
print("Total numbers of drafts with YANG Model(s): " + str(total_number_drafts)  + " - non strict rules: " + str(total_number_drafts_no_strict))
print('')
print("Yumarkworks: " + str(len(list_of_ietf_draft_containing_keyword(files, "@yumaworks.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@yumaworks.com", args.draftpathnostrict, debug_level))))
print("Tail-f: " + str(len(list_of_ietf_draft_containing_keyword(files, "@tail-f.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@tail-f.com", args.draftpathnostrict, debug_level))))
print
print("Cisco: " + str(len(list_of_ietf_draft_containing_keyword(files, "@cisco.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@cisco.com", args.draftpathnostrict, debug_level))))
print("Huawei: " + str(len(list_of_ietf_draft_containing_keyword(files, "@huawei.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@huawei.com", args.draftpathnostrict, debug_level))))
print("Juniper: " + str(len(list_of_ietf_draft_containing_keyword(files, "@juniper.net", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@juniper.net", args.draftpathnostrict, debug_level))))
print("Ericsson: " + str(len(list_of_ietf_draft_containing_keyword(files, "@ericsson.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@ericsson.com", args.draftpathnostrict, debug_level))))
print("Alcatel-Lucent: " + str(len(list_of_ietf_draft_containing_keyword(files, "@alcatel-lucent.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@alcatel-lucent.com", args.draftpathnostrict, debug_level))))
print("Ciena: " + str(len(list_of_ietf_draft_containing_keyword(files, "@ciena.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@ciena.com", args.draftpathnostrict, debug_level))))
print("Brocade: " + str(len(list_of_ietf_draft_containing_keyword(files, "@brocade.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@brocade.com", args.draftpathnostrict, debug_level))))
print("ZTE: " + str(len(list_of_ietf_draft_containing_keyword(files, "@zte.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@zte.com", args.draftpathnostrict, debug_level))))
print("Fujitsu: " + str(len(list_of_ietf_draft_containing_keyword(files, "@jp.fujitsu.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@jp.fujitsu.com", args.draftpathnostrict, debug_level))))
print("Intel: " + str(len(list_of_ietf_draft_containing_keyword(files, "@intel.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@intel.com", args.draftpathnostrict, debug_level))))
print("Infinera: " + str(len(list_of_ietf_draft_containing_keyword(files, "@infinera.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@infinera.com", args.draftpathnostrict, debug_level))))
print("Metaswitch: " + str(len(list_of_ietf_draft_containing_keyword(files, "@metaswitch.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@metaswitch.com", args.draftpathnostrict, debug_level))))
print('')
print("Google: " + str(len(list_of_ietf_draft_containing_keyword(files, "@google.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@google.com", args.draftpathnostrict, debug_level))))
print("Verizon: " + str(len(list_of_ietf_draft_containing_keyword(files, "@verizon.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@verizon.com", args.draftpathnostrict, debug_level))))
print("AT&T: " + str(len(list_of_ietf_draft_containing_keyword(files, "@att.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@att.com", args.draftpathnostrict, debug_level))))
print("Telefonica: " + str(len(list_of_ietf_draft_containing_keyword(files, "@telefonica.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@telefonica.com", args.draftpathnostrict, debug_level))))
print("Orange: " + str(len(list_of_ietf_draft_containing_keyword(files, "@orange.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@orange.com", args.draftpathnostrict, debug_level))))
print("BT: " + str(len(list_of_ietf_draft_containing_keyword(files, "@bt.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@bt.com", args.draftpathnostrict, debug_level))))
print("Level 3: " + str(len(list_of_ietf_draft_containing_keyword(files, "@level3.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@level3.com", args.draftpathnostrict, debug_level))))
print("Comcast: " + str(len(list_of_ietf_draft_containing_keyword(files, "@cable.comcast.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@cable.comcast.com", args.draftpathnostrict, debug_level))))
print("China Unicom: " + str(len(list_of_ietf_draft_containing_keyword(files, "@chinaunicom.cn", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@chinaunicom.cn", args.draftpathnostrict, debug_level))))
print("China Mobile: " + str(len(list_of_ietf_draft_containing_keyword(files, "@chinamobile.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@chinamobile.com", args.draftpathnostrict, debug_level))))
print("Microsoft: " + str(len(list_of_ietf_draft_containing_keyword(files, "@microsoft.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@microsoft.com", args.draftpathnostrict, debug_level))))
print("DT: " + str(len(list_of_ietf_draft_containing_keyword(files, "@telekom.de", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@telekom.de", args.draftpathnostrict, debug_level))))
print("Softbank: " + str(len(list_of_ietf_draft_containing_keyword(files, "softbank.co.jp", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "softbank.co.jp", args.draftpathnostrict, debug_level))))
print('')
print("Packet Design: " + str(len(list_of_ietf_draft_containing_keyword(files, "@packetdesign.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@packetdesign.com", args.draftpathnostrict, debug_level))))
print("Qosmos: " + str(len(list_of_ietf_draft_containing_keyword(files, "@qosmos.com", args.draftpathstrict, debug_level))) + " - non strict rules: " + str(len(list_of_ietf_draft_containing_keyword(files_no_strict, "@qosmos.com", args.draftpathnostrict, debug_level))))
 
                     
# diff between files and files_no_strict lists
files_diff = []
for f in files_no_strict:
    if f not in files:
        files_diff.append(f)
        # copy f in /home/bclaise/ietf/draft-with-YANG-diff
        bash_command = "cp " + args.draftpathnostrict + f + " " + args.draftpathdiff
        temp_result = os.popen(bash_command).read()
        if debug_level > 0:
            print("DEBUG: " + " copy the IETF draft containing a YANG model in draft-with-YANG-diff:  error " + temp_result)
if debug_level > 0:
    print("DEBUG: " + " print the diff between files and files_no_strict lists, so the files with xym extraction issues: " + str(files_diff))
