#!/usr/bin/env python

import os
import re
import sys

# This script implements this old sed|grep|awk pipeline...
#
#	$(SED) 's/^ *//;s/ *, */,/' | \
#	$(GREP) '^[^#]' | \
#	awk ' \
#		/CUT_OUT_BEGIN/ { no_write=1; next; }; \
#		/CUT_OUT_END/ { no_write=0; next; }; \
#		{ if (!no_write) print; next; }; \
#	' - > $@.tmp && \

comma_blanks = re.compile(r' *, *')

no_write = False

if len(sys.argv) != 3:
    sys.exit("Usage: makegperf.py <cpp_in> <out_gperf>")

with open(sys.argv[1], 'r') as in_fp:
    with open(sys.argv[2], 'w') as out_fp:
        for line in in_fp.readlines():
            line = line.strip()

            if len(line) == 0 or line[0] == '#':
                continue

            if line == "CUT_OUT_BEGIN":
                no_write = True
                continue
            elif line == "CUT_OUT_END":
                no_write = False
                continue

            if no_write:
                continue

            line = re.sub(comma_blanks, ",", line, count=1)

            out_fp.write(line + os.linesep);
