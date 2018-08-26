#!/usr/bin/env python3

# Convert find output to flat JSON compatible with other tools.
#
# Copyright (C) 2018 Marcin Szewczyk, marcin.szewczyk[at]wodny.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import argparse
import json

p = argparse.ArgumentParser()
p.add_argument("--root", default="<root>", help="root directory name")
p.add_argument("file", type=argparse.FileType("r"), help="find export filename")
options = p.parse_args()

options.root = options.root.rstrip("/")

for line in options.file:
    asize, dsize, ino, mtime, etype = line.rstrip().split(":")
    filename = options.file.readline()
    while filename[-2:] != "\0\n":
        filename += options.file.readline()
    dirname, _, filename = filename[:-2].rpartition("/")
    print("""{{"name":{},"asize":{},"dsize":{},"ino":{},"mtime":{},"type":"{}","dirs":{}}}""".format(
        json.dumps(filename),
        asize, int(dsize) * 1024, ino, mtime, "dir" if etype == "d" else "file",
        json.dumps(dirname and "{}/{}".format(options.root, dirname) or options.root)
    ))
