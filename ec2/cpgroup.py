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
Copies a group.  Copes can be made within the same region or from one
region to another.
"""


import os, sys
import time
from optparse import OptionParser
from boto.exception import EC2ResponseError
from boto.ec2.connection import EC2Connection
from boto.ec2.securitygroup import SecurityGroup
from BeautifulSoup import BeautifulStoneSoup
from Instances import StateTimeoutError
from Groups import GroupCopyError, copy_group


def main():
    parser = OptionParser()
    parser.usage = "%prog: [options] <existing group> [new group]"
    parser.add_option("-A", "--aws-access-key-id",
        default=os.environ.get("AWS_ACCESS_KEY_ID", None),
        dest="aws_access_key_id",
        help="AWS access key ID")
    parser.add_option("-S", "--aws-secret-access-key",
        default=os.environ.get("AWS_SECRET_ACCESS_KEY", None),
        dest="aws_secret_access_key",
        help="AWS secret access key")
    parser.add_option("-f", "--from-region",
        default="us-east-1",
        dest="from_region",
        help="The region to copy from")
    parser.add_option("-t", "--to-region",
        default="us-east-1",
        dest="to_region",
        help="The region to copy to")
    parser.add_option("-F", "--force",
        default=False,
        action="store_true",
        dest="force",
        help="If the destination group already exists, overwrite it")
    parser.add_option("-T", "--terminate",
        default=False,
        action="store_true",
        dest="terminate",
        help="Terminate instances using the security group")
    opts, args = parser.parse_args()

    if not (opts.aws_access_key_id and opts.aws_secret_access_key):
        parser.error("provide AWS access key ID and secret access key")

    if len(args) < 1:
        parser.error("insufficient arguments")

    if os.path.isfile(opts.aws_access_key_id):
        aws_access_key_id = open(opts.aws_access_key_id).read().strip()
    else:
        aws_access_key_id = opts.aws_access_key_id

    if os.path.isfile(opts.aws_secret_access_key):
        aws_secret_access_key = open(opts.aws_secret_access_key).read().strip()
    else:
        aws_secret_access_key = opts.aws_secret_access_key

    # The destination group name is optional, if it's not provided we
    # assume that the source and destination group names are identical.
    from_name = args[0]
    try:
        to_name = args[1]
    except IndexError:
        to_name = from_name

    try:
        copy_group(aws_access_key_id, aws_secret_access_key,
            from_name, to_name, opts.from_region, opts.to_region,
            opts.force, opts.terminate)
    except (GroupCopyError, StateTimeoutError), message:
        sys.stderr.write("%s\n" % message)
        sys.exit(1)
    except EC2ResponseError, response:
        soup = BeautifulStoneSoup(response.body)
        reason = soup.response.errors.error.message.contents[0]
        sys.stderr.write("%s\n" % reason)
        sys.exit(1)


if __name__ == "__main__":
    main()
