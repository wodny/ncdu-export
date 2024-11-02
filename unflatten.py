#!/usr/bin/env python3

# Convert flattened JSON back to ncdu-compatible JSON.
#
# Copyright (C) 2018-2024 Marcin Szewczyk, marcin.szewczyk[at]wodny.org
#
# Contributors:
#   Atemu (https://github.com/Atemu)
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

import argparse
import json
import sys
import time
from itertools import takewhile
from operator import eq

PROGNAME = "ncdu-export-unflatten"
__version__ = "0.2.0"

argp = argparse.ArgumentParser()
argp.add_argument("file", type=argparse.FileType("r"), help="flat export filename")
argp.add_argument("--ascii", action="store_true", help="dump JSON strings in ASCII (not UTF-8)")
options = argp.parse_args()

options.dumps = json.dumps if options.ascii else lambda v: json.dumps(v, ensure_ascii=False)

prev_dirs = []

print(
    """[1,0,{{"progname":"{0}","progver":"{1}","timestamp":{2}}}""".format(
        PROGNAME,
        __version__,
        int(time.time())
    ),
    end=""
)

def compare_dirs(dirs, prev_dirs):
    common_len = len(list(takewhile(lambda x: eq(*x), zip(dirs, prev_dirs))))
    closed = len(prev_dirs) - common_len
    opened = len(dirs) - common_len
    return closed, opened

def adjust_depth(dirs, prev_dirs):
    closed, opened = compare_dirs(dirs, prev_dirs)
    if closed:
        print("]"*closed, end="")
    if opened:
        for opened_dir in dirs[-opened:]:
            print(""",\n[{{"name":{},"asize":0,"dsize":0,"ino":0,"mtime":0}}""".format(
                options.dumps(opened_dir)
            ), end="")

for line in options.file:
    obj = json.loads(line)
    dirs = obj["dirs"]
    if not isinstance(dirs, list):
        dirs = dirs.lstrip("/")
        dirs = dirs.split("/") if dirs else []
    etype = obj["type"]
    del obj["dirs"]
    del obj["type"]
    adjust_depth(dirs, prev_dirs)
    if etype == "dir":
        print(",\n[{}".format(options.dumps(obj)), end="")
        dirs.append(obj["name"])
    else:
        print(",\n{}".format(options.dumps(obj)), end="")
    prev_dirs = dirs

dirs = []
adjust_depth(dirs, prev_dirs)
print("]")
