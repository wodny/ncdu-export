#!/bin/sh

# Output meta-data and null-delimited names of files in a format 
# compatible with the find2flat tool.

exec find "$@" -mindepth 1 -printf '%s:%k:%i:%Ts:%y\n%P\0\n'
