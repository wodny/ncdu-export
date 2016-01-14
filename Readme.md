# Standalone ncdu export feature

[ncdu][1] (NCurses Disk Usage) is a great utility with an ncurses 
interface that allows browsing through directories and check their disk 
usage (like the `du` command). It first walks through a directory and 
then allows browsing the cached result.

Newer versions (≥1.9) of [ncdu][1] have a feature allowing you to make 
a [JSON export file][2] on a remote machine (`-o` option) and then 
browse directories locally (`-f` option).

On some old machines there may be an old version of [ncdu][1] without 
that option or there may be no [ncdu][1] at all and it may be expensive 
to build [ncdu][1] for every one of them. This tool is a workaround - it 
generates an export file compatible with [ncdu][1] and requires only 
Python 2.6 (or newer) on the remote machine.

Currently the output is not identical to [ncdu][1]'s output but should 
work well enough.

[1]: https://dev.yorhel.nl/ncdu
[2]: https://dev.yorhel.nl/ncdu/jsonfmt
