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

from .node import Node  # noqa

DEFAULT_DIRS = [
    '/etc/puppetlabs/code/yaml-enc',
    '/etc/puppetlabs/puppet/yaml-enc',
    '/etc/puppet/yaml-enc',
]
NODES_SUBDIR = 'nodes'

# Import this last so the circular dependency doesn't cause us trouble
from .__main__ import main  # noqa
