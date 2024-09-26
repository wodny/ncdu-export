#!/usr/bin/env python3

import os
import argparse
import json
import stat

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
p.add_argument("file", type=argparse.FileType("r"), help="find export filename")
args = p.parse_args()

args.root = args.root.rstrip("/")

for line in args.file:
    filename = line.rstrip("\n")
    print(json.dumps(getFileInfo(filename, args.root)))
