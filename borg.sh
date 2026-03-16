#!/bin/sh

# Runs `borg create` with the required flags and pipe stderr to borg2flat
exec borg create --dry-run --list "$@" 2>&1 | $(dirname "$0")/borg2flat.py /dev/stdin
