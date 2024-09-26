#!/usr/bin/env python3

import os
import argparse
import json
import stat

def getFileInfo(path):
    stats = os.lstat(path)
    dirname = os.path.dirname(path)

    return {
        "name" : os.path.basename(path),
        "asize" : stats.st_size,
        "dsize" : stats.st_blocks * 512,
        "ino" : stats.st_ino,
        "mtime" : int(stats.st_mtime),
        "type" : "dir" if os.path.isdir(path) else "file",
        "dirs" : f"<root>/{dirname}" if dirname else "<root>",
    }

parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

print(json.dumps(getFileInfo(args.filename)))
