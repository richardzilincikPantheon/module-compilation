#!/usr/bin/python
import datetime
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from pylab import *
from matplotlib.dates import MONDAY
from matplotlib.dates import date2num,datestr2num,num2date,num2epoch,strpdate2num # mio - converting date to days since epoch
#from matplotlib.finance import quotes_historical_yahoo_ochl
import matplotlib.finance
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
from random import randint
import json
# from benoitGenerateYangHistory import historical_yangmodule_compiled_readJSON

YANGHISTORY_JSON_FILE_NAME = 'yangcompile_history.json'

# returns dictionary with values indexed by datefprint
# date {'total': 0, 'success': 0, 'warning':0}

def historical_yangmodule_compiled(basedate):
    basedate = basedate
    yangmodulesuccessLast = 0
    yangmodule_history = {}

    for i in range(1,400):
        date = basedate + i
        yangmodule_history[date] = {'total': 0, 'success':0, 'warning':0}
        yangmodule_history[date]['success'] = randint(0,1) + yangmodulesuccessLast
        yangmodulesuccessLast = yangmodule_history[date]['success']

    return yangmodule_history
    
    
def historical_yangmodule_compiled_generate(basedate):
    yangmodule_history = historical_yangmodule_compiled(basedate)
    # print json.dumps(yangmodule_history)
    with open(YANGHISTORY_JSON_FILE_NAME, 'w') as f:
        f.write(json.dumps(yangmodule_history))
 
    return YANGHISTORY_JSON_FILE_NAME

    
def historical_yangmodule_compiled_readJSON(jsonfile):
    yangmodule_history_json_file = jsonfile
    with open(yangmodule_history_json_file, 'r') as f:
        yangmodule_history = json.load(f)
    # print yangmodule_history

    return yangmodule_history

date1 = datetime.date(2013, 1, 1)
date2 = datetime.date(2015, 6, 1)
# print date2num(date1)

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
#daysFmt = SimpleDateFormatter(""yyyy-MM-dd")

# every month
months = MonthLocator(range(1, 13), bymonthday=1, interval=1)
monthsFmt = DateFormatter("%b '%y")

# TODO transfer dictionary to 2x Array
basedate = date2num(date1)

# generate stats for Cisco
yangmoduleCisco_history = historical_yangmodule_compiled_readJSON("/media/sf_ubuntu-share/www/stats/IETFYANGPageCompilationCiscoAuthorsStats.json")
# print json.dumps(yangmoduleCisco_history)
# print yangmoduleCisco_history
if len(yangmoduleCisco_history) == 0:
    print ('Found no data in IETFYANGPageCompilationCiscoAuthors.json')
    raise SystemExit
yangmoduledates = []
yangmodulesuccess = []
yangmodulewarning = []
yangmoduletotal = []
for key in sorted(yangmoduleCisco_history):
    # the next line: doesn't take an entry with (0,0,0) for (success,failed,warning)
    if yangmoduleCisco_history[key]['success'] != 0 and yangmoduleCisco_history[key]['warning'] != 0 and yangmoduleCisco_history[key]['total'] != 0:
        yangmoduledates.append(key)
        yangmodulesuccess.append(yangmoduleCisco_history[key]['success'])
        # Next line: want to create the warning curves as warning + success, for a visual effect
        # yangmodulewarning.append(int(yangmoduleCisco_history[key]['warning']) + int(yangmoduleCisco_history[key]['success']))
        yangmodulewarning.append(yangmoduleCisco_history[key]['warning'])
        yangmoduletotal.append(yangmoduleCisco_history[key]['total'])
# if we become interested in using actual date rather then numerical form
# print type(str(num2date(list(yangmoduleCisco_history)[0])))
# print str(num2date(list(yangmoduleCisco_history)[0]))
# print list(yangmoduleCisco_history)[0]
fig, ax = plt.subplots()
ax.plot(yangmoduledates, yangmodulesuccess, 'g-', yangmoduledates, yangmoduletotal, 'b-', yangmoduledates, yangmodulewarning, 'r-')
plt.text(735727, 80, r'TOTAL', fontdict=fontb)
plt.text(735727, 25, r'PASSED', fontdict=fontg)
plt.text(735732, 05, r'WARNING', fontdict=fontr)
#ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(daysFmt)
ax.xaxis.set_minor_locator(mondays)
plt.ylabel('# YANG Modules')
ax.set_title('Cisco Authored YANG Modules and Submodules: Compilation Results')
ax.autoscale_view()
#print ax
ax.grid(True)
fig.autofmt_xdate()
savefig('/media/sf_ubuntu-share/www/figures/IETFYANGPageCompilationCiscoAuthors.png', bbox_inches='tight')
# plt.show()

# generate stats for the IETF
yangmodule_history = historical_yangmodule_compiled_readJSON("/media/sf_ubuntu-share/www/stats/IETFYANGPageCompilationStats.json")
if len(yangmodule_history) == 0:
    print ('Found no data in IETFYANGPageCompilation.json')
    raise SystemExit
yangmoduledates = []
yangmodulesuccess = []
yangmodulewarning = []
yangmoduletotal = []
for key in sorted(yangmodule_history):
    yangmoduledates.append(key)
    yangmodulesuccess.append(yangmodule_history[key]['success'])
    yangmodulewarning.append(yangmodule_history[key]['warning'])
    yangmoduletotal.append(yangmodule_history[key]['total'])     
fig, ax = plt.subplots()
ax.plot(yangmoduledates, yangmodulesuccess, 'g-', yangmoduledates, yangmoduletotal, 'b-', yangmoduledates, yangmodulewarning, 'r-')
plt.text(735697, 95, r'TOTAL', fontdict=fontb)
plt.text(735697, 40, r'PASSED', fontdict=fontg)
plt.text(735712, 05, r'WARNING', fontdict=fontr)
#ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(daysFmt)
ax.xaxis.set_minor_locator(mondays)
plt.ylabel('# YANG Modules')
ax.set_title('IETF YANG Modules and Submodules: Compilation Results')
ax.autoscale_view()
#print ax
ax.grid(True)
fig.autofmt_xdate()
savefig('/media/sf_ubuntu-share/www/figures/IETFYANGPageCompilation.png', bbox_inches='tight')

# generate stats for the IETF RFCs
yangRFC_history = historical_yangmodule_compiled_readJSON("/media/sf_ubuntu-share/www/stats/IETFYANGOutOfRFCStats.json")
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
#ax.xaxis.set_minor_locator(mondays)
plt.ylabel('# RFC YANG Modules')
ax.set_title('IETF YANG Modules and Submodules from RFCs')
ax.autoscale_view()
plt.ylim(0, 80)
plt.xlim(int(yangmoduledates[1].encode("utf-8").split(".")[0])+100, int(yangmoduledates[-1].encode("utf-8").split(".")[0])+50)
int(yangmoduledates[1].encode("utf-8").split(".")[0])

#print ax
ax.grid(True)
fig.autofmt_xdate()
savefig('/media/sf_ubuntu-share/www/figures/IETFYANGOutOfRFC.png', bbox_inches='tight')

# plt.show()





