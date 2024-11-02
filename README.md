# Standalone ncdu export feature and some other tools

[ncdu][1] (NCurses Disk Usage) is a great utility with an ncurses 
interface that allows browsing through directories and check their disk 
usage (like the `du` command). It first walks through a directory and 
then allows browsing the cached result.

Newer versions (≥1.9) of [ncdu][1] have a feature allowing you to make 
a [JSON export file][2] on a remote machine (`-o` option) and then 
browse directories locally (`-f` option).

On some old machines there may be an old version of [ncdu][1] without 
that option or there may be no [ncdu][1] at all and it may be expensive 
to build [ncdu][1] for every one of them or for some reason you cannot 
get static binaries for a specific platform. The **ncdu-export** tool is 
a workaround - it generates an export file compatible with [ncdu][1] and 
**requires only Python 2.6 or Python 3.2** (or newer) on the remote 
machine.

Below, there is also a script based on the `find` command only (without 
using Python).

Note, however, that there are **static binaries** for x86, x86\_64 and 
ARM available directly from the [ncdu's][1] homepage, so tools from this 
repository may be useful only if you cannot use those static binaries.

Currently the scripts' output is not identical to [ncdu][1]'s output but 
should work well enough.

Example:

    1. Copy the script to the remote host
    $ scp ncdu-export remote-host:

    2A. Pipe meta-data via ssh to a local file:
    $ ssh remote-host ./ncdu-export -p / > files.json

    2B. Collect meta-data on the remote host and then download it:
    $ ssh remote-host
    $ ./ncdu-export -p / > files.json
    ^D
    $ scp remote-host:files.json .

    3. Analyze the data
    $ ncdu -f files.json

## Remarks on usage

### Pointing to the interpreter

If you get the `/usr/bin/env: ‘python’: No such file or directory` 
message you need to call a chosen version of python explicitly in one of 
the following ways:

- `python2 ncdu-export` (if using Python 2),
- `python3 ncdu-export` (if using Python 3),
- fix the first line (hashbang) of the script according to your 
  environment.

### Names encoded using UTF-8 or ASCII

Since version 0.8.0 `ncdu-export` encodes names using UTF-8 by default.
Use the `-a` switch to output ASCII. The default changed because at the 
time of writing this the original `ncdu` ≥ 2.5 based on Zig does not 
accept JSON with names encoded in ASCII. See #6 for details.

## Other tools

Tools described below are prepared for filenames containing unusual characters 
like newlines. They support `-` as the FILE's name so you can use them with 
pipes.

### Flatten/unflatten

Sometimes one can have a need to automatically filter meta-data dumped using 
the [ncdu][1] or `ncdu-export` tools. Those dumps can be quite big, hundreds of 
megabytes. One can process those dumps with [jq][3], but:

- using [jq][3] in non-stream mode can consume a lot of RAM,
- getting directory name from this kind of dump may be quite complicated (I 
  don't like my own example with `walk`),
- I didn't find a way to process ncdu's output in jq's [stream mode][4] and 
  using methods like `fromstream(1|truncate_stream(inputs))`; I suppose it's 
  because contrary to most formats used in jq's usage examples ncdu's format is 
  not flat (it's an array of arrays of maps).

This set of tools can be used to flatten ncdu's output, make it easy to process 
using [jq][3] and then optionally unflatten it back again. These tools depend on 
the [ijson][5] Python library using the [YAJL2][6] library underneath. Those 
libraries work on streams and parse JSON incrementally so it's possible to 
convert huge dumps without consuming all the RAM.

The `yajl2_cffi` backend is chosen automatically (if available). It's faster 
than the pure Python backend. During experiments it reduced the conversion time 
by as much as 40%.

Example of filtering files modified before 2018-01-01:

    $ ./ncdu-export -mp a-directory > files.json
    $ ./flatten.py files.json > files-flat.json
    $ export ts=$(date -d 2018-01-01 +%s)

    Rebrowsing in ncdu:
    $ jq -c 'select(.mtime < (env.ts | tonumber))' < files-flat.json > files-flat-before2018.json
    $ ./unflatten.py files-flat-before2018.json > files-before2018.json
    $ ncdu -f files-before2018.json

    Putting files in an archive and removing them:
    $ jq -j 'select(.mtime < (env.ts | tonumber) and .type == "file") | .dirs + "/" + .name + "\u0000"' < files-flat.json > files-flat-before2018.txt
    $ tar cvzf archive.tgz --null -T files-flat-before2018.txt --remove-files

### Find export

There is also a script that allows you to produce a meta-data dump just using 
the `find` command on a remote host (without using [ncdu][1] nor Python at all) 
and then process it locally to regenerate the ncdu-compatible JSON format. It 
works thanks to find's `printf` action (available in the Linux version, not the 
BusyBox one).

    $ ./find.sh a-directory > find-export.txt
    $ ./find2flat.py find-export.txt > find-flat-export.json
    $ ./unflatten.py find-flat-export.json > find-export.json
    $ ncdu -f find-export.json

or

    $ ./find.sh ~/projects/ | ./find2flat.py - | ./unflatten.py - | ncdu -f -

## Graph of tools


                         .------------.
         .---------------| filesystem |
         |               '------------'
         |                      |
         |                      | ncdu -o / ncdu-export
         |                      v
         |                  .------.         .---------.
         | find.sh          | ncdu | ncdu -f |  ncdu   |
         |                  | JSON |-------->| preview |
         |                  '------'         '---------'
         |                    |  ^
         |         flatten.py |  | unflatten.py
         v                    v  |
    .--------.              .------.
    |  find  | find2flat.py | flat |<---. jq filtering
    | output |------------->| JSON |----'
    '--------'              '------'
                                |
                                | jq
                                v
                          .-----------.        .---------.
                          |    tar    | tar -T |   tar   |
                          | file list |------->| archive |
                          '-----------'        '---------'



[1]: https://dev.yorhel.nl/ncdu
[2]: https://dev.yorhel.nl/ncdu/jsonfmt
[3]: https://stedolan.github.io/jq
[4]: https://stedolan.github.io/jq/manual/#Streaming
[5]: https://pypi.org/project/ijson/
[6]: http://lloyd.github.io/yajl/
