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


import datetime
import matplotlib as mpl
mpl.use('Agg') # To prevent using a X-Windows server
import matplotlib.pyplot as plt
from pylab import *
from matplotlib.dates import MONDAY
from matplotlib.dates import date2num,datestr2num,num2date,num2epoch,strpdate2num # mio - converting date to days since epoch
#from matplotlib.finance import quotes_historical_yahoo_ochl
import matplotlib.finance
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
from random import randint
import json
import os

def historical_yangmodule_compiled_readJSON(jsonfile):
    yangmodule_history_json_file = jsonfile
    with open(yangmodule_history_json_file, 'r') as f:
        yangmodule_history = json.load(f)
    print(" Found " + str(len(yangmodule_history)) + " entrie(s) from " + jsonfile) 

    return yangmodule_history

# fonts
fontr = {'family' : 'serif',
        'color'  : 'red',
        'weight' : 'normal',
        'size'   : 16,
        }

fontb = {'family' : 'serif',
        'color'  : 'blue',
        'weight' : 'normal',
        'size'   : 16,
        }
        
fontg = {'family' : 'serif',
        'color'  : 'green',
        'weight' : 'normal',
        'size'   : 16,
        }
               
# every monday
mondays = WeekdayLocator(MONDAY)
daysFmt = DateFormatter("%d %b '%y")

# every month
months = MonthLocator(range(1, 13), bymonthday=1, interval=1)
monthsFmt = DateFormatter("%b '%y")

# Get some directory values where to store files
web_directory = os.environ['WEB_PRIVATE']

# generate stats for Cisco
yangmoduleCisco_history = historical_yangmodule_compiled_readJSON(web_directory + "/stats/IETFCiscoAuthorsYANGPageCompilationStats.json")
if len(yangmoduleCisco_history) == 0:
    print ('Found no data in IETFCiscoAuthorsYANGPageCompilation.json')
    raise SystemExit
yangmoduledates = []
yangmodulesuccess = []
yangmodulewarning = []
yangmoduletotal = []
for key in sorted(yangmoduleCisco_history):
    # the next line: doesn't take an entry with (0,0,0) for (success,failed,warning)
    if yangmoduleCisco_history[key]['success'] != 0 and yangmoduleCisco_history[key]['warning'] != 0 and yangmoduleCisco_history[key]['total'] != 0:
        yangmoduledates.append(float(key))      # Matplot requires a float for dates
        yangmodulesuccess.append(yangmoduleCisco_history[key]['success'])
        yangmodulewarning.append(yangmoduleCisco_history[key]['warning'])
        yangmoduletotal.append(yangmoduleCisco_history[key]['total'])
fig, ax = plt.subplots()
ax.plot(yangmoduledates, yangmodulesuccess, 'g-', yangmoduledates, yangmoduletotal, 'b-', yangmoduledates, yangmodulewarning, 'r-')
plt.text(735727, 80, r'TOTAL', fontdict=fontb)
plt.text(735727, 25, r'PASSED', fontdict=fontg)
plt.text(735732,  5, r'WARNING', fontdict=fontr)
#ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(daysFmt)
ax.xaxis.set_minor_locator(mondays)
plt.ylabel('# YANG Modules')
ax.set_title('Cisco Authored YANG Modules and Submodules: Compilation Results')
ax.autoscale_view()
ax.grid(True)
fig.autofmt_xdate()
ax.xaxis_date()
savefig(web_directory + '/figures/IETFCiscoAuthorsYANGPageCompilation.png', bbox_inches='tight')

# generate stats for the IETF
yangmodule_history = historical_yangmodule_compiled_readJSON(web_directory + "/stats/IETFYANGPageCompilationStats.json")
if len(yangmodule_history) == 0:
    print ('Found no data in IETFYANGPageCompilationStats.json')
    raise SystemExit
yangmoduledates = []
yangmodulesuccess = []
yangmodulewarning = []
yangmoduletotal = []
for key in sorted(yangmodule_history):
    yangmoduledates.append(float(key))
    yangmodulesuccess.append(yangmodule_history[key]['success'])
    yangmodulewarning.append(yangmodule_history[key]['warning'])
    yangmoduletotal.append(yangmodule_history[key]['total'])     
fig, ax = plt.subplots()
ax.plot(yangmoduledates, yangmodulesuccess, 'g-', yangmoduledates, yangmoduletotal, 'b-', yangmoduledates, yangmodulewarning, 'r-')
plt.text(735697, 95, r'TOTAL', fontdict=fontb)
plt.text(735697, 40, r'PASSED', fontdict=fontg)
plt.text(735712,  5, r'WARNING', fontdict=fontr)
#ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(daysFmt)
ax.xaxis.set_minor_locator(mondays)
plt.ylabel('# YANG Modules')
ax.set_title('IETF YANG Modules and Submodules: Compilation Results')
ax.autoscale_view()
ax.grid(True)
fig.autofmt_xdate()
ax.xaxis_date()
savefig(web_directory + '/figures/IETFYANGPageCompilation.png', bbox_inches='tight')

# generate stats for the IETF RFCs
yangRFC_history = historical_yangmodule_compiled_readJSON(web_directory + "/stats/IETFYANGOutOfRFCStats.json")
if len(yangRFC_history) == 0:
    print ('Found no data in "IETFYANGOutOfRFC.json')
    raise SystemExit
yangmoduledates = []
yangmoduletotal = []
for key in sorted(yangRFC_history):
    yangmoduledates.append(key)
    yangmoduletotal.append(yangRFC_history[key]['total']) 
fig, ax = plt.subplots()
ax.plot(yangmoduledates, yangmoduletotal)
ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(monthsFmt)
plt.ylabel('# RFC YANG Modules')
ax.set_title('IETF YANG Modules and Submodules from RFCs')
ax.autoscale_view()
#plt.ylim(0, 80)
#plt.xlim(int(yangmoduledates[1].encode("utf-8").split(".")[0])+100, int(yangmoduledates[-1].encode("utf-8").split(".")[0])+50)
#int(yangmoduledates[1].encode("utf-8").split(".")[0])
ax.grid(True)
fig.autofmt_xdate()
ax.xaxis_date()
savefig(web_directory + '/figures/IETFYANGOutOfRFC.png', bbox_inches='tight')
