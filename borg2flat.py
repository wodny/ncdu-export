#!/usr/bin/env python3

import os
import argparse
import json
import stat

def getFileInfo(path, root):
    stats = os.lstat(path)
    dirname = os.path.dirname(path)

    return {
        "name" : os.path.basename(path),
        "asize" : stats.st_size,
        "dsize" : stats.st_blocks * 512,
        "ino" : stats.st_ino,
        "mtime" : int(stats.st_mtime),
        "type" : "dir" if os.path.isdir(path) else "file",
        "dirs" : f"{root}/{dirname}" if dirname else root,
    }

p = argparse.ArgumentParser()
p.add_argument("--root", default="<root>", help="root directory name")
p.add_argument("filename", help="find export filename")
args = p.parse_args()

args.root = args.root.rstrip("/")

print(json.dumps(getFileInfo(args.filename, args.root)))
