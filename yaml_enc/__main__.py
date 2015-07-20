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
import yaml_enc

from .node import Node


def main():
    parser = argparse.ArgumentParser(
        description='YAML-based Puppet External Node Classifier (ENC)')
    parser.add_argument('FQDN', nargs='?',
                        help='hostname of the node to classify')
    parser.add_argument('--base', '-b', default=yaml_enc.DEFAULT_DIR,
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
