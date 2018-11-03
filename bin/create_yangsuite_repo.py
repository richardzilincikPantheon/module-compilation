#!/usr/bin/python3
# env must be:
# MEDIA_ROOT=/var/yang/yangsuite
# DJANGO_SETTINGS_MODULE=yangsuite.settings.develop

from ysfilemanager import YSYangRepository, YSMutableYangSet
from yangsuite.paths import set_base_path
import re
import os

def delete_yangset(ysname):
    try:
        YSMutableYangSet.delete('yangcat', ysname)
    except Exception as e:
        print("YangSet {} not deleted: {}".format(ysname, e))

def create_repo(directory, reponame):
    try:
        YSYangRepository.delete('yangcat', reponame)
    except Exception as e:
        print("Repository {} not deleted: {}".format(reponame, e))

    # Re-create the YangSet
    repo = YSYangRepository.create('yangcat', reponame)
    repo.add_yang_files(directory, remove=False, include_subdirs=True)
    repo.write()
    print("Repository {} created.".format(reponame))

def create_yangset(pattern, reponame, ysname):
    try:
        ys = YSMutableYangSet.load('yangcat', ysname)
    except:
        print("Cannot load the YangSet: {}, instantiating it".format(ysname))
        # owner, setname, modules, repository=None, reponame=None
        ys = YSMutableYangSet('yangcat', ysname, [], reponame=reponame)

    print("YangSet {} created, adding files....".format(ysname))
    module_dict = dict()
    regex = re.compile(pattern)
    repo = YSYangRepository('yangcat', reponame)
    for module in repo.get_modules_and_revisions():
            (module_name, revision, path) = module
            if regex.match(module_name):
                if module_name in module_dict:
                        if module_dict[module_name] < revision:
                            print("Changing revision date of {} from {} to {}".format(module_name, module_dict[module_name], revision))
                            module_dict[module_name] = revision
                else:
                        module_dict[module_name] = revision
                        print("Adding {}@{}".format(module_name, revision))

    for module, revision in module_dict.items():
            print("Inserting module {}@{}...".format(module,revision))
            try:
                ys.modules += [[module, revision]]
            except Exception as e:
                print("Error while loading {}@{}:".format(module, revision, e))
    print()
    print("All modules are added, now saving")
    ys.write()

# Some initialization code
set_base_path(os.environ['MEDIA_ROOT'])

# First need to delete previous yangsets
delete_yangset('RFC and drafts')
delete_yangset('IETF examples')
delete_yangset('Set of all known modules')
delete_yangset('BBF') 
delete_yangset('IEEE')
delete_yangset('MEF')

# Now (re) create the repository
create_repo('/var/yang/ietf/YANG-all', 'IETF')
create_repo('/var/yang/all_modules', 'Repo of all known modules')
create_repo('/var/yang/nonietf/yangmodels/yang/standard/bbf', 'BBF')
create_repo('/var/yang/nonietf/yangmodels/yang/standard/ieee', 'IEEE')
create_repo('/var/yang/nonietf/yangmodels/yang/standard/mef', 'MEF')

# and finally the yangset
create_yangset('ietf.*', 'IETF', 'RFC and drafts')
create_yangset('example.*', 'IETF', 'IETF examples')
create_yangset('.*', 'Repo of all known modules', 'Set of all known modules')
create_yangset('bbf-.*', 'BBF', 'BBF')
create_yangset('ieee.*', 'IEEE', 'IEEE')  # Names are ieee802-*
create_yangset('mef-.*', 'MEF', 'MEF')
