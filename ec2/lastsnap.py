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
Determines the latest snapshot.  Supports an optional prefix to restrict the
results.  Useful for determining the latest snapshot in a "lineage" of
snapshots that have the same prefix for the same volume.
"""


import os, sys, bisect
from time import mktime, strptime
from optparse import OptionParser
from boto.exception import EC2ResponseError
from boto.ec2.connection import EC2Connection
from BeautifulSoup import BeautifulStoneSoup


def main():
    parser = OptionParser()
    parser.usage = "%prog: [options]"
    parser.add_option("-A", "--aws-access-key-id",
        default=os.environ.get("AWS_ACCESS_KEY", None),
        dest="awsAccessKeyID",
        help="AWS access key ID")
    parser.add_option("-S", "--aws-secret-access-key",
        default=os.environ.get("AWS_SECRET_KEY", None),
        dest="awsSecretAccessKey",
        help="AWS secret access key")
    parser.add_option("--region",
        default=None,
        dest="region",
        help="Web service region to use")
    parser.add_option("-o", "--owner",
        default="self",
        dest="owner",
        help="Snapshot owner (self/all/<user ID>)")
    parser.add_option("-O", "--oldest",
        default=False,
        action="store_true",
        dest="oldest",
        help="Oldest instead of most recent")
    parser.add_option("-i", "--invert",
        default=False,
        action="store_true",
        dest="invert",
        help="Invert the search result (eg, recent 7 of 10 becomes oldest 3")
    parser.add_option("-n", "--num",
        default=1,
        dest="num",
        help="Number of last snapshots to show")
    parser.add_option("-d", "--description",
        default=None,
        dest="description",
        help="Limit the search based on description")
    parser.add_option("-v", "--verbose",
        default=False,
        action="store_true",
        dest="verbose",
        help="Verbose results")
    opts, args = parser.parse_args()

    if not (opts.awsAccessKeyID or opts.awsSecretAccessKey):
        parser.error("provide AWS access key ID and secret access key")

    if os.path.isfile(opts.awsAccessKeyID):
        awsAccessKeyID = open(opts.awsAccessKeyID).read().strip()
    else:
        awsAccessKeyID = opts.awsAccessKeyID

    if os.path.isfile(opts.awsSecretAccessKey):
        awsSecretAccessKey = open(opts.awsSecretAccessKey).read().strip()
    else:
        awsSecretAccessKey = opts.awsSecretAccessKey

    try:
        num = int(opts.num)
    except TypeError:
        sys.stderr.write("Number argument must be an integer\n")
        sys.exit(1)

    try:
        connection = EC2Connection(awsAccessKeyID, awsSecretAccessKey,
            region=opts.region)
        snapshots = connection.get_all_snapshots(owner=opts.owner)
    except EC2ResponseError, response:
        soup = BeautifulStoneSoup(response.body)
        reason = soup.response.errors.error.message.contents[0]
        sys.stderr.write("%s\n" % reason)
        sys.exit(1)

    # Filter by prefix of each description?
    if opts.description:
        f = lambda s: s.description.startswith(opts.description)
        snapshots = filter(f, snapshots)

    # Sort by start time
    sortedSnaps = []
    for snapshot in snapshots:
        secs = mktime(strptime(snapshot.start_time, "%Y-%m-%dT%H:%M:%S.000Z"))
        bisect.insort(sortedSnaps, (secs, snapshot))

    last = []
    if opts.oldest:
        if opts.invert:
            last = map(lambda s: s[1], sortedSnaps[num:])
        else:
            last = map(lambda s: s[1], sortedSnaps[0:num])
    else:
        if opts.invert:
            last = map(lambda s: s[1], sortedSnaps[0:-num])
        else:
            last = map(lambda s: s[1], sortedSnaps[-num:])

    for l in last:
        if opts.verbose:
            print l.id, l.start_time, l.description
        else:
            print l.id


if __name__ == "__main__":
    main()
