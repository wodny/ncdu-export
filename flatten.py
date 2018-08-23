#!/usr/bin/env python3

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

try:
    import ijson.backends.yajl2_cffi as ijson
except ImportError:
    import ijson

import sys
import argparse
import json
from enum import IntEnum

class ParserState(IntEnum):
    # - arrays are directory listings
    # - array's first entry contains meta-data of the directory itself
    # - maps are file meta-data sets
    START       = 0
    HEADER      = 1 # started parsing header
    ARRAY_START = 2 # non-header array start
    FIRST_MAP   = 3 # first map in array started
    SUBSEQ_MAP  = 4 # any other map in array started

state = ParserState.START
dirs = []
key = None
obj = {}

argp = argparse.ArgumentParser()
argp.add_argument("file", type=argparse.FileType("rb"), help="ncdu export filename")
argp.add_argument("--dirs", choices=["array", "string"], default="array", help="directory name format output to flat file")
argp.add_argument("--verbose", action="store_true", help="enable verbose mode (inc. ijson variant)")
options = argp.parse_args()

if options.verbose:
    sys.stderr.write("ijson module variant: {}\n".format(ijson.__name__))

parser = ijson.parse(options.file)
for prefix, event, value in parser:
    if event == "start_array":
        if state != ParserState.START:
            # started non-header array (directory listing)
            state = ParserState.ARRAY_START
        else:
            # started header, omit this map
            state = ParserState.HEADER
    elif event == "end_array":
        # array means a (sub)directory so it was at least a second entry
        # (first entry is the directory's meta-data)
        state = ParserState.SUBSEQ_MAP
        if dirs:
            dirs.pop()
    elif state == ParserState.ARRAY_START and event == "start_map":
        # directory's meta-data
        state = ParserState.FIRST_MAP
        obj = {}
    elif state in [ParserState.FIRST_MAP, ParserState.SUBSEQ_MAP] and event == "start_map":
        # directory entry's meta-data
        state = ParserState.SUBSEQ_MAP
        obj = {}
    elif event == "map_key":
        # fill in the meta-data map
        key = value
    elif event in ["number", "string"]:
        # no other types expected
        obj[key] = value
    elif event == "end_map":
        # meta-data object complete
        if state == ParserState.FIRST_MAP:
            obj["type"] = "dir"
        elif state == ParserState.SUBSEQ_MAP:
            obj["type"] = "file"

        if state != ParserState.HEADER:
            # output meta-data (omit header)
            obj["dirs"] = dirs if options.dirs == "array" else "/".join(dirs)
            print(json.dumps(obj))

        if state == ParserState.FIRST_MAP:
            # entered a directory, expand path for its entries
            dirs.append(obj["name"])
