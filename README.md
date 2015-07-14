yaml-enc: a simple YAML-based Puppet ENC
========================================

This is a very simple tool to act as a Puppet External Node Classifier (ENC).
It was written to replace the last of the functionality of Puppet Dashboard
that was not covered by tools such as PuppetBoard or Puppet Explorer.

Features
--------

- Lightweight and fast. This tool is a single script that doesn't try to do
  anything particularly clever. It just looks up node information in a
  directory full of YAML files.

- Node definitions are just files, so they can be kept in Git or some other
  version control system, perhaps alongside the rest of your Puppet manifests
  and Hiera data.

- Well, it does do one clever thing: it can "include" other YAML files into the
  node definition. You can keep all your common elements in a small number of
  YAML files and include them in your node definitions where you need them.

- It's written for Python 3.x. So far this has only really been tested on
  Python 3.4 on Debian Jessie. The only required external module is PyYAML /
  python3-yaml. I'm much more of a Python person than a ruby person.

Why not Puppet Dashboard?
-------------------------

PuppetLabs have abandoned Puppet Dashboard and handed it over to the community,
where it is in fact thriving. It works well, but is a monolithic tool that
tries to be both an ENC and a tool for observing node status including looking
at facts and reports.

PuppetLabs have released PuppetDB as a tool to handle storing facts, reports
and catalogues (for use with exported resources) but Puppet Dashboard makes no
use of it directly. You probably end up with having reports stored in two
places, especially if you're already using/evaluating PuppetBoard or Puppet
Explorer.

This tool takes care of the ENC side of Puppet Dashboard. Calling this script
is much more efficient than making an HTTP request into a web application and
querying a database.

Examples
--------

TODO

License
-------

Copyright (C) 2015  Chris Boot <bootc@bootc.net>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
