#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2018 SUSE LLC
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; version 2.1.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Zoltán Balogh <zbalogh@suse.com>
# Summary: Simple tool to list changelogs of packages in the available
# repositories.

from __future__ import print_function
import os
import argparse
import sys
import datetime
import re
import subprocess
from argparse import ArgumentParser
import requests
import rpm
import xml.etree.ElementTree as ET


def log_text(text):
    print(text)


def parse_args():
    p = ArgumentParser(prog='changelog.py',
                       description='Shows the changelog' +
                       'of one ore more packages.',
                       formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('-d', '--debug',
                   default=False, action='store_true', dest='debug',
                   help='debug mode')
    p.add_argument('-v', '--verbose',
                   default=False, action='store_true', dest='verbose',
                   help='verbose mode')
    p.add_argument('-e', '--expression',
                   default=False, action='store_true', dest='expression',
                   help='Enable regular expression in package name')
    p.add_argument("-p", "--package", dest="package", default=None,
                   help="Package name \
                              or regular expression to match packages.")
    p.add_argument("-r", "--repositories",
                   dest="repos", default="repo-oss",
                   help="Comma separated list of repositores \
                              to search for changelogs.")
    p.add_argument("-a", "--all",
                   dest="all", default=False,
                   action='store_true',
                   help="Lists changelogs for all packages")
    if len(sys.argv[1:]) == 0:
        p.print_help()
        p.exit()
    return p


parser = parse_args()
args = parser.parse_args(sys.argv[1:])
if args.debug:
    log_text('\nargs: ' + str(sys.argv))

repository_list = args.repos.split(",")

list_of_xml_files = []

# Find the cache file of the repositories
for root, dirs, files in os.walk("/var/cache/zypp/raw/"):
    for file in files:
        if file.endswith("primary.xml.gz"):
            for repository in repository_list:
                if repository in root:
                    list_of_xml_files.append(os.path.join(root, file))

ts = rpm.TransactionSet("", (rpm._RPMVSF_NOSIGNATURES or
                        rpm.RPMVSF_NOHDRCHK or
                        rpm._RPMVSF_NODIGESTS or
                        rpm.RPMVSF_NEEDPAYLOAD))

# Get the available respostories from the xml outout of zypper
# and find the URLs of the repositories
zypp_process = subprocess.Popen(["zypper",
                                 "-x",
                                 "lr"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
stdout_value, stderr_value = zypp_process.communicate()
repo_tree = ET.ElementTree(ET.fromstring(stdout_value))
repo_root = repo_tree.getroot()

for files in list_of_xml_files:
    for repo in repo_root.iter('repo'):
        if repo.get('alias') in files:
            mirror_url = repo.find('url').text

    zcat_process = subprocess.Popen(["zcat",
                                     "%s" % files],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    stdout_value, stderr_value = zcat_process.communicate()

    tree = ET.ElementTree(ET.fromstring(stdout_value))
    root = tree.getroot()
    xml_ns = root.tag.split('}')[0].strip('{')

    # Loop thru the packages listed in the repository cache files
    for package in root.findall('doc:package', namespaces={'doc': xml_ns}):
        if not args.all:
            if args.expression:
                pattern = re.compile(args.package)
                if not pattern.match("%s" % package[0].text):
                    continue
            else:
                if args.package != package[0].text:
                    continue

        # Find the segment/offset of the header part of the rpm package
        for field in package[11].findall('rpm:header-range',
                                         namespaces={'rpm':
                                                     'http://linux.duke.edu' +
                                                     '/metadata/rpm'}):
            start = field.get('start')
            end = field.get('end')
            url = '%s%s' % (mirror_url, package[10].get('href'))
            log_text(url)
            try:
                # Fetch the rpm header as it contains the changelogs
                rpm_header = requests.get(url,
                                          headers={'Range':
                                                   'bytes=0-%s' % (end)})
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)
                continue
            # Dump the header to a temporary file as the ts.hdrFromFdno
            # needs a real file to process
            with open('temp_header.rpm', 'w+b') as f:
                f.write(rpm_header.content)
                f.flush()
            fd = os.open('temp_header.rpm', os.O_RDONLY)
            # Parse the changelog, time and contributor's name
            h = ts.hdrFromFdno(fd)
            changelog_name = h[rpm.RPMTAG_CHANGELOGNAME]
            changelog_time = h[rpm.RPMTAG_CHANGELOGTIME]
            changelog_text = h[rpm.RPMTAG_CHANGELOGTEXT]
            for (name, time, text) in zip(changelog_name,
                                          changelog_time,
                                          changelog_text):
                datetime_time = datetime.datetime.fromtimestamp(time)
                if args.verbose:
                    print("* %s - %s\n%s" % (datetime_time, name, text))
                else:
                    print("* %s - %s" % (datetime_time, name))
