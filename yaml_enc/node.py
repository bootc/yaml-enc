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

import os
import yaml
import yaml_enc

from collections import ChainMap, OrderedDict


class Node(object):
    def __init__(self, fqdn=None, classes={}, parameters={}, environment=None):
        super(Node, self).__init__()
        self.fqdn = fqdn
        self.classes = classes
        self.parameters = parameters
        self.environment = environment

    @classmethod
    def from_yaml(cls, base_dir, fqdn, Loader=yaml.SafeLoader):
        node = cls._from_yaml_include(
            base_dir, os.path.join(yaml_enc.NODES_SUBDIR, fqdn), Loader)
        node.fqdn = fqdn
        return node

    @classmethod
    def all_nodes(cls, base_dir, Loader=yaml.SafeLoader):  # generator
        nodes_dir = os.path.join(base_dir, yaml_enc.NODES_SUBDIR)

        for (_, _, filenames) in os.walk(nodes_dir):
            for fqdn in (x[:-5] for x in filenames if x.endswith('.yaml')):
                yield Node.from_yaml(base_dir, fqdn, Loader=Loader)

            # Break out of the walk; we only want to walk the nodes_dir
            break

    @classmethod
    def _from_yaml_include(cls, base_dir, include, Loader):
        # Construct the path to the YAML file
        path_yaml = os.path.join(base_dir, include + '.yaml')

        # Read the YAML data
        with open(path_yaml, 'r') as fd:
            loader = Loader(fd)
            try:
                data = loader.get_single_data()
            finally:
                loader.dispose()

        node = cls()

        # Handle empty node definitions gracefully
        if data is None:
            return node

        # We can only cope with dicts in the YAML
        if not isinstance(data, dict):
            raise ValueError("{path}: YAML document must have a mapping at "
                             "its top level".format(path=path_yaml))

        # Add the included classes
        classes = data.get('classes', {})
        if isinstance(classes, list):
            classes = dict.fromkeys(classes)
        node.classes = classes

        # Add the included parameters
        node.parameters = data.get('parameters', {})

        # Set the environment
        node.environment = data.get('environment')

        # Handle any :include directives
        try:
            includes = data[':include']
        except KeyError:
            pass
        else:
            # The :include value could be a string or a list
            if isinstance(includes, str):
                includes = [includes]

            nodes = [node]
            nodes.extend(cls._from_yaml_include(base_dir, inc, Loader)
                         for inc in includes)

            node.classes = ChainMap(*[x.classes for x in nodes])
            node.parameters = ChainMap(*[x.parameters for x in nodes])
            node.environment = next((x.environment for x in nodes if
                                     x.environment is not None), None)

        return node

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
