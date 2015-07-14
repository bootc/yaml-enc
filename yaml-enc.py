#!/usr/bin/python3

# This file is part of yaml-enc.
# Copyright (C) 2015  Chris Boot <bootc@bootc.net>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import argparse
import os
import sys
import yaml

DEFAULT_DIR = '/etc/puppet/yaml-enc'
NODES_SUBDIR = 'nodes'


def read_yaml(base_dir, path):
    """
    Read a YAML file, handling any processing directives.

    Currently only handles a ``:include`` directive, which is used to include
    other YAML files into the current data dictionary.
    """
    # Construct the path to the YAML file
    path_yaml = os.path.join(base_dir, path + '.yaml')

    # Read the YAML data
    with open(path_yaml, 'r') as fd:
        data = yaml.safe_load(fd)

    # Handle any :include directives
    if ':include' in data:
        includes = data[':include']
        del data[':include']

        # The :include value could be a string or a list; if it's a string,
        # convert it to a list for ease
        if isinstance(includes, str):
            includes = [includes]

        # Merge in all included data
        for inc in includes:
            merge(data, read_yaml(base_dir, inc))

    return data


def merge(main, inc):
    """
    Merge ENC data from ``inc`` into ``main``.

    This does a context-sensitive merge for data that may be returned to Puppet
    from an ENC. Generally, when including a YAML file, the values in the
    including file override the values from the included file.

    The following keys are merged:

    ``classes``:
      Any classes present in ``inc`` but *not* already present in ``main`` are
      merged into ``main``. This method handles class arguments, but argument
      lists are *not* merged.

    ``parameters``:
      Any parameters present in ``inc`` but *not* already present in ``main``
      are merged into ``main``. Parameter values are *not* merged.

    ``environment``:
      If ``main`` does not specify an environment but ``inc`` does, the
      environment value is merged.
    """
    # Handle merging classes
    if 'classes' in inc:
        if 'classes' not in main:
            main['classes'] = inc['classes']
        else:
            left = main['classes']
            right = inc['classes']

            # If both are a list, the result should still be a list
            if isinstance(left, list) and isinstance(right, list):
                seen = set(left)
                seen_add = seen.add
                # Add unique items from right to left
                left.extend(x for x in right if not (x in seen or seen_add(x)))
            else:
                # One or the other may be a list, so convert them to dict
                if isinstance(left, list):
                    left = dict.fromkeys(left, None)
                elif isinstance(right, list):
                    right = dict.fromkeys(right, None)

                # Add classes from right to left only if they don't already
                # exist in left
                left.update({k: right[k] for k in right if k not in left})

    # Handle merging parameters
    if 'parameters' in inc:
        if 'parameters' not in main:
            main['parameters'] = inc['parameters']
        else:
            left = main['parameters']
            right = inc['parameters']

            # Add parameters from right to left only if they don't already
            # exist in left
            left.update({k: right[k] for k in right if k not in left})

    # Handle merging environment
    if 'environment' in inc and 'environment' not in main:
        main['environment'] = inc['environment']


def classify_node(base_dir, fqdn):
    return read_yaml(base_dir, os.path.join(NODES_SUBDIR, fqdn))


def classify_all_nodes(base_dir):
    nodes_dir = os.path.join(base_dir, NODES_SUBDIR)
    nodes = []

    for (_, _, filenames) in os.walk(nodes_dir):
        for fqdn in (x[:-5] for x in filenames if x.endswith('.yaml')):
            data = classify_node(base_dir, fqdn)
            data['name'] = fqdn
            nodes.append(data)

        # Break out of the walk; we only want to walk the nodes_dir
        break

    return nodes


def main():
    parser = argparse.ArgumentParser(
        description='YAML-based Puppet External Node Classifier (ENC)')
    parser.add_argument('node', nargs='?',
                        help='FQDN of the node to classify')
    parser.add_argument('--base', '-b', default=DEFAULT_DIR,
                        help='base directory for node YAML files')
    args = parser.parse_args()

    # Check that the base directory exists and is a directory
    if not os.path.isdir(args.base):
        print("E: {base} does not exist or is not a directory"
              .format(base=args.base), file=sys.stderr)
        sys.exit(1)

    # Check that the nodes directory exists and is a directory
    nodes_dir = os.path.join(args.base, NODES_SUBDIR)
    if not os.path.isdir(nodes_dir):
        print("E: {nodes} does not exist or is not a directory"
              .format(nodes=nodes_dir), file=sys.stderr)
        sys.exit(1)

    try:
        if args.node is not None:
            data = classify_node(args.base, args.node)
        else:
            data = classify_all_nodes(args.base)
    except OSError as e:
        print("E: {e.filename}: {e.strerror}".format(e=e), file=sys.stderr)
        sys.exit(1)

    yaml.safe_dump(data, sys.stdout, explicit_start=True)

if __name__ == "__main__":
    main()
