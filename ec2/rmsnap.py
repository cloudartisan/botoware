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
Deletes snapshots supplied as command-line parameters.
"""


import os
import sys
from optparse import OptionParser
from boto.exception import EC2ResponseError
from boto.ec2.connection import EC2Connection
from BeautifulSoup import BeautifulStoneSoup


def main():
    parser = OptionParser()
    parser.usage = "%prog: [options] <snapshot ID> [snapshot ID ...]"
    parser.add_option("-A", "--aws-access-key-id",
        default=os.environ.get("AWS_ACCESS_KEY_ID", None),
        dest="aws_access_key_id",
        help="AWS access key ID")
    parser.add_option("-S", "--aws-secret-access-key",
        default=os.environ.get("AWS_SECRET_ACCESS_KEY", None),
        dest="aws_secret_access_key",
        help="AWS secret access key")
    parser.add_option("--region",
        default=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
        dest="region",
        help="Web service region to use")
    parser.add_option("-v", "--verbose",
        default=False,
        action="store_true",
        dest="verbose",
        help="Verbose results")
    opts, args = parser.parse_args()

    if not (opts.aws_access_key_id and opts.aws_secret_access_key):
        parser.error("provide AWS access key ID and secret access key")

    if len(args) == 0:
        parser.error("provide a snapshot ID")

    if os.path.isfile(opts.aws_access_key_id):
        aws_access_key_id = open(opts.aws_access_key_id).read().strip()
    else:
        aws_access_key_id = opts.aws_access_key_id

    if os.path.isfile(opts.aws_secret_access_key):
        aws_secret_access_key = open(opts.aws_secret_access_key).read().strip()
    else:
        aws_secret_access_key = opts.aws_secret_access_key

    try:
        if opts.verbose:
            print "Connecting to EC2"
        connection = EC2Connection(aws_access_key_id, aws_secret_access_key,
            opts.region)
        if opts.verbose:
            print "Connected to EC2"
    except EC2ResponseError, response:
        soup = BeautifulStoneSoup(response.body)
        reason = soup.response.errors.error.message.contents[0]
        sys.stderr.write("%s\n" % reason)
        sys.exit(1)

    for snapshot in args:
        try:
            if opts.verbose:
                print "Deleting snapshot %s" % snapshot
            connection.delete_snapshot(snapshot)
            if opts.verbose:
                print "Deleted snapshot %s" % snapshot
        except EC2ResponseError, response:
            soup = BeautifulStoneSoup(response.body)
            reason = soup.response.errors.error.message.contents[0]
            sys.stderr.write("%s\n" % reason)


if __name__ == "__main__":
    main()
