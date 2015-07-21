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
import yaml_enc

from .node import Node


def classify_mode(args):
    try:
        if args.FQDN is not None:
            data = Node.from_yaml(args.base, args.FQDN)
        else:
            data = list(Node.all_nodes(args.base))
    except OSError as e:
        print("E: {e.filename}: {e.strerror}".format(e=e), file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print("E: {e}".format(e=e), file=sys.stderr)
        sys.exit(1)
    else:
        yaml.safe_dump(data, sys.stdout, explicit_start=True)


def import_mode(args):
    # Read node definitions from stdin
    data = yaml.safe_load(stream=sys.stdin)

    if not isinstance(data, list):
        print("E: input YAML document is not a list", file=sys.stderr)
        sys.exit(1)

    for nodeinfo in data:
        if 'name' not in nodeinfo:
            print("E: expected node information to contain a 'name' field",
                  file=sys.stderr)
            sys.exit(1)

        # If we were given an FQDN on the command-line and it doesn't match the
        # name of the node in the YAML, skip it
        if args.FQDN is not None and nodeinfo['name'] != args.FQDN:
            continue

        node = Node(
            classes=nodeinfo.get('classes', {}),
            parameters=nodeinfo.get('parameters', {}),
            environment=nodeinfo.get('environment', None))

        path = os.path.join(args.base, yaml_enc.NODES_SUBDIR,
                            nodeinfo['name'] + '.yaml')

        with open(path, 'w') as fd:
            yaml.safe_dump(node, fd, explicit_start=True,
                           default_flow_style=False)


PROGRAM_MODES = {
    'classify': classify_mode,
    'import': import_mode,
}


def main():
    parser = argparse.ArgumentParser(
        description='YAML-based Puppet External Node Classifier (ENC)')
    parser.add_argument('FQDN', nargs='?',
                        help='hostname of the node to classify')
    parser.add_argument('--base', '-b', default=yaml_enc.DEFAULT_DIR,
                        help='base directory for node YAML files')
    parser.add_argument('--mode', default='classify',
                        choices=PROGRAM_MODES.keys(),
                        help='mode of operation; default: %(default)s')
    args = parser.parse_args()

    # Check that the base directory exists and is a directory
    if not os.path.isdir(args.base):
        print("E: {} does not exist or is not a directory".format(args.base),
              file=sys.stderr)
        sys.exit(1)

    # Run the function for the requested program mode
    PROGRAM_MODES[args.mode](args)

if __name__ == "__main__":
    main()
