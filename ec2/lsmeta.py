#!/usr/bin/env python
#
# Copyright (c) 2010 David Taylor
# http://www.cloudartisan.com
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""
Pull out the metadata of an instance.
"""


import os
import sys
from pprint import pprint
from optparse import OptionParser
from boto.utils import get_instance_metadata


def main():
    parser = OptionParser()
    parser.usage = "%prog: [options]"
    parser.add_option("--raw",
        default=False,
        action="store_true",
        dest="raw",
        help="Raw output, suitable for eval/JSON")
    opts, args = parser.parse_args()

    instance_metadata = get_instance_metadata()
    if opts.raw:
        print instance_metadata
    else:
        for key, val in instance_metadata.items():
            print "%s: %s" % (key.replace("/", ""), val.replace("\n", ", "))


if __name__ == "__main__":
    main()
