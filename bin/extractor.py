#!/usr/bin/env python


import argparse
import os.path
import sys

__author__ = 'Jie Dong, Tianran Zhou'
__copyright__ = "Copyright(c) 2015, Huawei Technologies"
__license__ = "New-style BSD"
__email__ = "jie.dong@huawei.com, zhoutianran@huawei.com"
__version__ = "1.1"
# Addition from 1.0 to 1.1 by miroslav.kovac@pantheon.tech <miroslav.kovac@pantheon.tech>


def get_name(type, head):
    name = head
    name = name.strip()
    name = name.lstrip(type)
    name = name.rstrip(' {')
    name = name.lstrip()
    print(name)
    return name


def extract_type(input_file, dst_path, dst_file, type, mode):
    finput = open(input_file, "r")
    alllines = finput.readlines()
    finput.close()
    foutput = 0

    dst_flag = True
    if dst_file.strip() == 'separate':
        dst_flag = False

    if dst_flag == True:
        output_file = dst_path + dst_file
        if mode == True:
            foutput = open(output_file, 'w')
        else:
            foutput = open(output_file, 'a')

    start_flag = False
    title_flag = False
    nbrac = 0

    comented_out = False
    for eachline in alllines:
        if start_flag == False:
            spos = eachline.find(type, )
            cpos = eachline.find('//')
            if comented_out:
                mcpos = eachline.find('*/')
            else:
                mcpos = eachline.find('/*')
            if mcpos != -1:
                if comented_out:
                    comented_out = False
                else:
                    comented_out = True
            if spos >= 0 and spos < 5 and (spos < cpos or cpos == -1) and not comented_out:
                start_flag = True
                title_flag = True

        if start_flag == True:
            if title_flag == True:
                if dst_flag == False:
                    output_file = dst_path + type + '-' + get_name(type, eachline) + '.txt'
                    foutput = open(output_file, "w")

                title_flag = False

            foutput.writelines(eachline)

            spos = eachline.find('{', )
            if spos >= 0:
                nbrac = nbrac + 1

            spos = eachline.find('}', )
            if spos >= 0:
                nbrac = nbrac - 1

            if nbrac == 0:
                start_flag = False
                foutput.writelines('\n')
                if dst_flag == False:
                    foutput.close

    if dst_flag == True:
        foutput.close


def extract(src_path, src_file, dst_path, dst_file, type, debug):
    input_file = src_path + src_file

    if type == 'all':
        extract_type(input_file, dst_path, dst_file, 'typedef', True)
        extract_type(input_file, dst_path, dst_file, 'grouping', False)
        extract_type(input_file, dst_path, dst_file, 'identity', False)
    else:
        extract_type(input_file, dst_path, dst_file, type, True)


if __name__ == "__main__":
    """
    Command line utility
    """
    parser = argparse.ArgumentParser(description='Extracts the typedef, identity, and grouping from a YANG model')
    parser.add_argument("source", help="The URL or file name of the YANG model to extract info from")
    parser.add_argument("--srcdir", default='./', help="Optional: directory where to find the source text; "
                                                       "default is './'")
    parser.add_argument("--dstdir", default='./', help="Optional: directory where to put the extracted yang info; "
                                                       "default is './'")
    parser.add_argument("--dstfile", default='separate', help="Optional: file to append the extracted information; "
                                                              "default is 'separate file for each component'")
    parser.add_argument("--type", default='all',
                        help="Optional flag that determines what to extract (typedef, identity, or grouping); "
                             "default is 'all'")
    parser.add_argument("--debug", type=int, default=0, help="Optional: debug level")
    args = parser.parse_args()

    extracted_info = extract(args.srcdir, args.source, args.dstdir, args.dstfile, args.type, args.debug)
