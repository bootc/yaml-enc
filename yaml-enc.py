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

from collections import ChainMap, OrderedDict


DEFAULT_DIR = '/etc/puppet/yaml-enc'
NODES_SUBDIR = 'nodes'


class Node(object):
    def __init__(self, base_dir, fqdn, classes={}, parameters={},
                 environment=None):
        super(Node, self).__init__()
        self.base_dir = base_dir
        self.fqdn = fqdn
        self.classes = ChainMap(classes)
        self.parameters = ChainMap(parameters)
        self.environment = environment

    @classmethod
    def from_yaml(cls, base_dir, fqdn, Loader=yaml.SafeLoader):
        node = cls(base_dir, fqdn)
        node.merge_yaml(os.path.join(NODES_SUBDIR, fqdn), Loader=Loader)
        return node

    @classmethod
    def all_nodes(cls, base_dir, Loader=yaml.SafeLoader):  # generator
        nodes_dir = os.path.join(base_dir, NODES_SUBDIR)

        for (_, _, filenames) in os.walk(nodes_dir):
            for fqdn in (x[:-5] for x in filenames if x.endswith('.yaml')):
                yield Node.from_yaml(base_dir, fqdn, Loader=Loader)

            # Break out of the walk; we only want to walk the nodes_dir
            break

    def merge_yaml(self, path, Loader=yaml.SafeLoader):
        # Construct the path to the YAML file
        path_yaml = os.path.join(self.base_dir, path + '.yaml')

        # Read the YAML data
        with open(path_yaml, 'r') as fd:
            loader = Loader(fd)
            try:
                data = loader.get_single_data()
            finally:
                loader.dispose()

        # Handle empty node definitions gracefully
        if data is None:
            return

        # We can only cope with dicts in the YAML
        if not isinstance(data, dict):
            print("E: {path}: YAML document must have a mapping at its top "
                  "level".format(path=path_yaml), file=sys.stderr)
            sys.exit(1)

        # Add the included classes
        try:
            classes = data['classes']
        except KeyError:
            pass
        else:
            if isinstance(classes, list):
                classes = dict.fromkeys(classes)
            self.classes.maps.append(classes)

        # Add the included parameters
        try:
            self.parameters.maps.append(data['parameters'])
        except KeyError:
            pass

        # Set the environment
        try:
            if self.environment is None:
                self.environment = data['environment']
        except KeyError:
            pass

        # Handle any :include directives
        try:
            includes = data[':include']
        except KeyError:
            pass
        else:
            # The :include value could be a string or a list
            if isinstance(includes, str):
                self.merge_yaml(includes)
            else:
                for inc in includes:
                    self.merge_yaml(inc)

    def _flatten(self):
        flattened = OrderedDict(name=self.fqdn)

        if not any(self.classes.values()):
            # If none of our classes have any arguments, use a list instead
            flattened['classes'] = list(self.classes.keys())
        else:
            # Flatten our list of classes
            flattened['classes'] = dict(self.classes)

        # Flatten our list of parameters
        flattened['parameters'] = dict(self.parameters)

        if self.environment is not None:
            flattened['environment'] = self.environment

        return flattened

    @classmethod
    def add_yaml_representer(cls, dumper=yaml.SafeDumper):
        def _node_yaml_representer(dumper, node):
            return dumper.represent_mapping(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                node._flatten().items())
        dumper.add_representer(cls, _node_yaml_representer)


# Teach PyYAML how to represent Node objects
Node.add_yaml_representer()


def main():
    parser = argparse.ArgumentParser(
        description='YAML-based Puppet External Node Classifier (ENC)')
    parser.add_argument('FQDN', nargs='?',
                        help='hostname of the node to classify')
    parser.add_argument('--base', '-b', default=DEFAULT_DIR,
                        help='base directory for node YAML files')
    args = parser.parse_args()

    # Check that the base directory exists and is a directory
    if not os.path.isdir(args.base):
        print("E: {} does not exist or is not a directory".format(args.base),
              file=sys.stderr)
        sys.exit(1)

    try:
        if args.FQDN is not None:
            data = Node.from_yaml(args.base, args.FQDN)
        else:
            data = list(Node.all_nodes(args.base))
    except OSError as e:
        print("E: {e.filename}: {e.strerror}".format(e=e), file=sys.stderr)
        sys.exit(1)
    else:
        yaml.safe_dump(data, sys.stdout, explicit_start=True)

if __name__ == "__main__":
    main()
