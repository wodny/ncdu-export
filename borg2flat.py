#!/usr/bin/env python3

import os
import argparse
import json
import stat
import sys

def getFileInfo(path, root, is_excluded = False):
    stats = os.lstat(path)
    dirname = os.path.dirname(path)

    return {
        "name" : os.path.basename(path),
        "asize" : stats.st_size,
        "dsize" : stats.st_blocks * 512,
        "ino" : stats.st_ino,
        "mtime" : int(stats.st_mtime),
        "type" : "dir" if os.path.isdir(path) and not is_excluded else "file",
        "dirs" : f"{root}/{dirname}" if dirname else root,
    } | ({
        "excluded" : "pattern",
    } if is_excluded else { })

p = argparse.ArgumentParser()
p.add_argument("--root", default="<root>", help="root directory name")
p.add_argument("file", type=argparse.FileType("r"), help="borg export filename")
args = p.parse_args()

args.root = args.root.rstrip("/")

for line in args.file:
    # FIXME For now we map errors to exclusions because flatten does not
    # support adding "read_error": true
    exclusion_letters = [ "x", "E" ]
    inclusion_letters = [ "-" ]
    # Borg prints errors to the same output as the dry-run output i.e.
    # inaccessible: dir_open: [Errno 13] Permission denied: 'inaccessible'
    # The best determinator for this is that they typically don't have a space
    # as the second character and don't start with a -
    # FIXME ask upstream for a better solution
    if line[1] != " " or line[0] not in exclusion_letters + inclusion_letters:
        print(f"ERROR: Not a legal borg dry-run line: \"{line.rstrip('\n')}\"", file=sys.stderr)
        continue

    filename = line[2:].rstrip("\n")
    excluded = line[0] in exclusion_letters
    print(json.dumps(getFileInfo(filename, args.root, excluded)))
