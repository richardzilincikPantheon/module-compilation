#!/usr/bin/env python
##############################################################################
# Copyright The IETF Trust 2019, All Rights Reserved
# Copyright (c) 2015 Cisco Systems  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
##############################################################################
from __future__ import print_function  # Must be at the beginning of the file

import argparse
import re
import sys

import matplotlib.pyplot as plt
import networkx as nx

from utility.utility import list_files_by_extensions

__author__ = 'Jan Medved, Eric Vyncke'
__copyright__ = 'Copyright(c) 2015, Cisco Systems, Inc.,  Copyright The IETF Trust 2019, All Rights Reserved'
__license__ = 'Eclipse Public License v1.0'
__email__ = 'jmedved@cisco.com, evyncke@cisco.com'

G = nx.DiGraph()

# Regular expressions for parsing yang files; we are only interested in
# the 'module', 'import' and 'revision' statements
MODULE_STATEMENT = re.compile(r'''^[ \t]*(sub)?module +(["'])?([-A-Za-z0-9]*(@[0-9-]*)?)(["'])?.*$''')  # noqa: Q001
IMPORT_STATEMENT = re.compile(
    r'''^[ \t]*import[\s]*([-A-Za-z0-9]*)?[\s]*\{([\s]*prefix[\s]*[\S]*;[\s]*})?.*$''',  # noqa: Q001
)
INCLUDE_STATEMENT = re.compile(r'''^[ \t]*include[\s]*([-A-Za-z0-9]*)?[\s]*\{.*$''')  # noqa: Q001
REVISION_STATEMENT = re.compile(r'''^[ \t]*revision[\s]*(['"])?([-0-9]*)?(['"])?[\s]*\{.*$''')  # noqa: Q001

# Node Attribute Types
# All those attributes do not fare well in network 2.*
TAG_ATTR = 'tag'
IMPORT_ATTR = 'imports'
TYPE_ATTR = 'type'
REV_ATTR = 'revision'

# Tags
RFC_TAG = 'rfc'
DRAFT_TAG = 'draft'
UNKNOWN_TAG = 'unknown'


def warning(s):
    """
    Prints out a warning message to stderr.
    :param s: The warning string to print
    :return: None
    """
    print('WARNING: %s' % s, file=sys.stderr)


def error(s):
    """
    Prints out an error message to stderr.
    :param s: The error string to print
    :return: None
    """
    print('ERROR: %s' % s, file=sys.stderr)


def get_local_yang_files(local_repos: list[str], recurse: bool = False) -> list[str]:
    """
    Gets the list of all yang module files in the specified local repositories
    :param local_repos: List of local repositories, i.e. directories where yang modules may be located
    :return: list of all *.yang files in the local repositories
    """
    yfs = []
    for repo in local_repos:
        yfs.extend(
            list_files_by_extensions(
                repo,
                ('yang',),
                return_full_paths=True,
                recursive=recurse,
                follow_links=True,
            ),
        )
    return yfs


def parse_yang_module(lines):
    """
    Parses a yang module; look for the 'module', 'import'/'include' and
    'revision' statements
    :param lines: Pre-parsed yang files as a list of lines
    :return: module name, module type (module or sub-module), list of
             imports and list of revisions
    """
    module = None
    mod_type = None
    revisions = []
    imports = []

    for line in lines:
        match = MODULE_STATEMENT.match(line)
        if match:
            module = match.groups()[2]
            if match.groups()[0] == 'sub':
                mod_type = 'sub'
            else:
                mod_type = 'mod'
        match = IMPORT_STATEMENT.match(line)
        if match:
            imports.append(match.groups()[0])
        match = INCLUDE_STATEMENT.match(line)
        if match:
            imports.append(match.groups()[0])
        match = REVISION_STATEMENT.match(line)
        if match:
            revisions.append(match.groups()[1])
    return module, mod_type, imports, revisions


def get_yang_modules(yfiles, tag):
    """
    Creates a list of yang modules from the specified yang files and stores
    them as nodes in a Networkx directed graph. This function also stores
    node attributes (list of imports, tag, revision, ...) for each module
    in the NetworkX data structures. The function uses the global variable
    G (directed network graph of yang model dependencies)
    :param yfiles: List of files containing yang modules
    :param tag: Tag - RFC or draft for now
    :return: None; resulting nodes are stored in G.
    """
    for yf in yfiles:
        try:
            with open(yf, encoding='latin-1', errors='ignore') as yfd:
                name, mod_type, imports, revisions = parse_yang_module(yfd.readlines())
                if len(revisions) > 0:
                    rev = max(revisions)
                else:
                    error("No revision specified for module '%s', file '%s'" % (name, yf))
                    rev = None
                # IF we already have a module with a lower revision, replace it now
                try:
                    en = G.nodes[name]
                    en_rev = en['revision']
                    if en_rev:
                        if rev:
                            if rev > en_rev:
                                warning("Replacing revision for module '%s' ('%s' -> '%s')" % (name, en_rev, rev))
                                G.nodes[name]['revision'] = rev
                                G.nodes[name]['imports'] = imports
                    else:
                        if rev:
                            warning("Replacing revision for module '%s' ('%s' -> '%s')" % (name, en_rev, rev))
                            G.nodes[name]['revision'] = rev
                            G.nodes[name]['imports'] = imports
                except KeyError:
                    G.add_node(name, type=mod_type, tag=tag, imports=imports, revision=rev)
        except IOError as ioe:
            print(ioe)


def prune_graph_nodes(graph, tag):
    """
    Filers graph nodes to only nodes that are tagged with the specified tag
    :param graph: Original graph to prune
    :param tag: Tag for nodes of interest
    :return: List of nodes tagged with the specified tag
    """
    node_list = []
    for node_name in graph.nodes():
        try:
            if graph.nodes[node_name]['tag'] == tag:
                #            if graph.nodes[node_name]['attr_dict'][TAG_ATTR] == tag:
                node_list.append(node_name)
        except KeyError:
            pass
    return node_list


def get_module_dependencies():
    """
    Creates the dependencies  between modules (i.e. the edges) in the NetworkX
    directed graph created by 'get_yang_modules()'
    This function uses the global variable G (directed network graph of yang
    modules)
    :return: None
    """
    # TODO should probably avoid calling this function in all functions...
    attr_dict = nx.get_node_attributes(G, 'imports')
    for node_name in G.nodes():
        for imp in attr_dict[node_name]:
            if imp in G:
                G.add_edge(node_name, imp)
            else:
                error("Module '%s': imports unknown module '%s'" % (node_name, imp))


def get_unknown_modules():
    unknown_nodes = []
    # Next line is added
    attr_dict = nx.get_node_attributes(G, 'imports')
    for node_name in G.nodes():
        for imp in attr_dict[node_name]:
            if imp not in G:
                unknown_nodes.append(imp)
                warning("Module '%s': imports module '%s' that was not scanned" % (node_name, imp))
    for un in unknown_nodes:
        G.add_node(un, type='module', tag=UNKNOWN_TAG, imports=[], revision=None)


def print_impacting_modules(single_node=None):
    """
    For each module, print a list of modules that the module is depending on,
    i.e. modules whose change can potentially impact the module. The function
    shows all levels of dependency, not just the immediately imported
    modules.
    :return:
    """
    print('\n===Impacting Modules===')
    for node_name in G.nodes():
        if single_node and (node_name != single_node):
            continue
        descendants = nx.descendants(G, node_name)
        print(augment_format_string(node_name, '\n%s:') % node_name)
        for d in descendants:
            print(augment_format_string(d, '    %s') % d)


def augment_format_string(node_name, fmts):
    """
    Depending on the tag for the specified node, this function will add
    a marker to the specified format string. Tags can currently be 'rfc'
    or 'draft', the marker is '*' (asterisk)
    :param node_name: Node name to query
    :param fmts: format string to augment
    :return: Augmented format string
    """
    module_tag = G.nodes[node_name]['tag']
    #    module_tag = G.nodes[node_name]['attr_dict'][TAG_ATTR]
    if module_tag == RFC_TAG:
        return fmts + ' *'
    if module_tag == UNKNOWN_TAG:
        return fmts + ' (?)'
    return fmts


def print_impacted_modules(single_node=None):
    """
     For each module, print a list of modules that depend on the module, i.e.
     modules that would be impacted by a change in this module. The function
     shows all levels of dependency, not just the immediately impacted
     modules.
    :return:
    """
    print('\n===Impacted Modules===')
    for node_name in G.nodes():
        if single_node and (node_name != single_node):
            continue
        ancestors = nx.ancestors(G, node_name)
        if len(ancestors) > 0:
            print(augment_format_string(node_name, '\n%s:') % node_name)
            for a in ancestors:
                print(augment_format_string(a, '    %s') % a)


def get_subgraph_for_node(node_name):
    """
    Prints the dependency graph for only the specified node_name (a full dependency
    graph can be difficult to read).
    :param node_name: Node for which to print the sub-graph
    :return:
    """
    ancestors = nx.ancestors(G, node_name)
    ancestors.add(node_name)
    return nx.subgraph(G, ancestors)


def print_dependents(graph, preamble_list, imports):
    """
    Print the immediate dependencies (imports/includes), and for each
    immediate dependency print its dependencies
    :param graph: Dictionary containing the subgraph of dependencies that
                  we are about to print
    :param preamble_list: Preamble list, list of string to print out before each
               dependency (Provides the offset for higher order dependencies)
    :param imports: List of immediate imports/includes
    :return:
    """
    # Create the preamble string for the current level
    preamble = ''
    for preamble_string in preamble_list:
        preamble += preamble_string
    # Print a newline for the current level
    print(preamble + '  |')
    for i in range(len(imports)):
        print(augment_format_string(imports[i], preamble + '  +--> %s') % imports[i])
        # Determine if a dependency has dependencies on its own; if yes,
        # print them out before moving onto the next dependency
        try:
            imp_imports = graph[imports[i]]
            if i < (len(imports) - 1):
                preamble_list.append('  |   ')
            else:
                preamble_list.append('      ')
            print_dependents(graph, preamble_list, imp_imports)
            preamble_list.pop(-1)
            # Only print a newline if we're NOT the last processed module
            if i < (len(imports) - 1):
                print(preamble + '  |')
        except KeyError:
            pass


def print_dependency_tree():
    """
    For each module, print the dependency tree for imported modules
    :return: None
    """
    print('\n=== Module Dependency Trees ===')
    for node_name in G.nodes():
        if G.nodes[node_name]['tag'] != UNKNOWN_TAG:
            #        if G.nodes[node_name]['attr_dict'][TAG_ATTR] != UNKNOWN_TAG:
            dg = nx.dfs_successors(G, node_name)
            plist = []
            print(augment_format_string(node_name, '\n%s:') % node_name)
            if len(dg):
                imports = dg[node_name]
                print_dependents(dg, plist, imports)


def prune_standalone_nodes():
    """
    Remove from the module dependency graph all modules that do not have any
    dependencies (i.e they neither import/include any modules nor are they
    imported/included by any modules)
    :return: the connected module dependency graph
    """
    ng = nx.DiGraph(G)
    for node_name in G.nodes():
        ancestors = nx.ancestors(G, node_name)
        descendants = nx.descendants(G, node_name)
        if len(ancestors) == 0 and len(descendants) == 0:
            ng.remove_node(node_name)
    return ng


def get_dependent_modules():
    print('\n===Dependent Modules===')
    for node_name in G.nodes():
        dependents = tuple(nx.bfs_predecessors(G, node_name))
        if len(dependents):
            print(dependents)


def init(rfc_repos, draft_repos, recurse=False):
    """
    Initialize the dependency graph
    :param rfc_repos: List of local repositories for yang modules defined in
                      IETF RFCs
    :param draft_repos: List of local repositories for yang modules defined in
                        IETF drafts
    :return: None
    """
    rfc_yang_files = get_local_yang_files(rfc_repos, recurse)
    print("\n*** Scanning %d RFC yang module files for 'import' and 'revision' statements..." % len(rfc_yang_files))
    get_yang_modules(rfc_yang_files, RFC_TAG)
    num_rfc_modules = len(G.nodes())
    print('\n*** Found %d RFC yang modules.' % num_rfc_modules)

    draft_yang_files = get_local_yang_files(draft_repos, recurse)
    print("\n*** Scanning %d draft yang module files for 'import' and 'revision' statements..." % len(draft_yang_files))
    get_yang_modules(draft_yang_files, DRAFT_TAG)
    num_draft_modules = len(G.nodes()) - num_rfc_modules
    print('\n*** Found %d draft yang modules.' % num_draft_modules)

    print('\n*** Analyzing imports...')
    get_unknown_modules()
    num_unknown_modules = len(G.nodes()) - (num_rfc_modules + num_draft_modules)
    print('\n*** Found %d imported/included yang modules that were scanned.' % num_unknown_modules)

    print('\n*** Creating module dependencies...')
    get_module_dependencies()
    print('\nInitialization finished.\n')


def plot_module_dependency_graph(graph):
    # def plot_module_dependency_graph(graph, node):
    """
    Plot a graph of specified yang modules. this function is used to plot
    both the full dependency graph of all yang modules in the DB, or a
    subgraph of dependencies for a specified module
    :param graph: Graph to be plotted
    :return: None
    """
    #    fixed_positions = {node: [0.5, 0.5] }
    #    print(fixed_positions)
    pos = nx.spring_layout(graph, iterations=50, center=[0.5, 0.5], weight=2, k=0.6)
    # EVY  pos = nx.spring_layout(graph, iterations=2000, threshold=1e-5, fixed=fixed_positions, k=k, center=[0.5, 0.5])
    #    pos = nx.spring_layout(graph, iterations=2000, threshold=1e-6)
    print(pos)
    # Draw RFC nodes (yang modules) in red
    nx.draw_networkx_nodes(
        graph,
        pos=pos,
        nodelist=prune_graph_nodes(graph, RFC_TAG),
        node_size=200,
        node_shape='s',
        node_color='red',
        alpha=0.5,
        linewidths=0.25,
        label='RFC',
    )
    # Draw draft nodes (yang modules) in green
    nx.draw_networkx_nodes(
        graph,
        pos=pos,
        nodelist=prune_graph_nodes(graph, DRAFT_TAG),
        node_size=150,
        node_shape='o',
        node_color='green',
        alpha=0.5,
        linewidths=0.25,
        label='Draft',
    )
    # Draw unknown nodes (yang modules) in green
    nx.draw_networkx_nodes(
        graph,
        pos=pos,
        nodelist=prune_graph_nodes(graph, UNKNOWN_TAG),
        node_size=200,
        node_shape='^',
        node_color='orange',
        alpha=1.0,
        linewidths=0.25,
        label='Unknown',
    )
    # Draw edges in light gray (fairly transparent)
    nx.draw_networkx_edges(graph, pos=pos, alpha=0.25, arrows=False)
    # Draw labels on nodes (modules)
    nx.draw_networkx_labels(graph, pos=pos, font_size=14, font_weight='normal', alpha=1.0)


##############################################################################
# symd - Show Yang Module Dependencies.
#
# A program to analyze and show dependencies between yang modules
##############################################################################


if __name__ == '__main__':
    # Set matplotlib into non-interactive mode
    plt.interactive(False)

    parser = argparse.ArgumentParser(description='Show the dependency graph for a set of yang models.')
    parser.add_argument(
        '--draft-repos',
        help='List of local directories where models defined in IETF drafts are located.',
        type=str,
        nargs='+',
        default=['./'],
    )
    parser.add_argument(
        '--rfc-repos',
        help='List of local directories where models defined in IETF RFC are located.',
        type=str,
        nargs='+',
        default=['./'],
    )
    parser.add_argument(
        '-r',
        '--recurse',
        help='Recurse into directories specified to find yang models',
        action='store_true',
        default=False,
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--graph', help='Plot the overall dependency graph.', action='store_true', default=False)
    g.add_argument(
        '--sub-graphs',
        help='Plot the dependency graphs for the specified modules.',
        type=str,
        nargs='+',
        default=[],
    )
    g.add_argument(
        '--impact-analysis',
        help='For each scanned yang module, print the impacting and impacted modules.',
        action='store_true',
        default=False,
    )
    g.add_argument(
        '--single-impact-analysis',
        help='For a single yang module, print the impacting and impacted modules',
        type=str,
    )
    g.add_argument(
        '--dependency-tree',
        help='For each scanned yang module, print its dependency tree to stdout '
        '(i.e. show all the modules that it depends on).',
        action='store_true',
        default=False,
    )
    g.add_argument(
        '--single-dependency-tree',
        help='For a single yang module, print its dependency tree to stdout '
        '(i.e. show all the modules that it depends on).',
        type=str,
    )
    args = parser.parse_args()

    init(args.rfc_repos, args.draft_repos, recurse=args.recurse)

    if args.dependency_tree:
        print_dependency_tree()

    if args.single_dependency_tree:
        print_dependency_tree()

    if args.impact_analysis:
        print_impacting_modules()
        print_impacted_modules()

    if args.single_impact_analysis:
        print_impacting_modules(single_node=args.single_impact_analysis)
        print_impacted_modules(single_node=args.single_impact_analysis)

    plot_num = 1

    if args.graph:
        # Set matplotlib into non-interactive mode
        plt.interactive(False)
        ng = prune_standalone_nodes()
        plt.figure(plot_num, figsize=(40, 40))
        plot_num += 1
        print('Plotting the overall dependency graph...')
        plot_module_dependency_graph(ng)
        plt.savefig('modules.png')
        print('    Done.')

    for node in args.sub_graphs:
        # Set matplotlib into non-interactive mode
        plt.interactive(False)
        plt.figure(plot_num, figsize=(20, 20))
        #        plt.figure(plot_num, figsize=(40, 40))
        plot_num += 1
        print(f'Plotting graph for module \'{node}\'...')
        try:
            # EVY: do we need this extract argument ???
            #            plot_module_dependency_graph(get_subgraph_for_node(node), node)
            plot_module_dependency_graph(get_subgraph_for_node(node))
            plt.savefig('%s.png' % node)
            print('    Done.')
        except nx.NetworkXError as e:
            print('    %s' % e)

    print('\n')
