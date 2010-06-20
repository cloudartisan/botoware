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
Stops all servers.
"""


from optparse import OptionParser
from boto.ec2.connection import EC2Connection
from Instances import stop_all


def main():
    parser = OptionParser()
    parser.add_option("-A", "--aws-access-key-id",
        default=os.environ.get("AWS_ACCESS_KEY_ID", None),
        dest="aws_access_key_id", help="AWS access key ID")
    parser.add_option("-S", "--aws-secret-access-key",
        default=os.environ.get("AWS_SECRET_ACCESS_KEY", None),
        dest="aws_secret_access_key", help="AWS secret access key")
    parser.add_option("--region", default=None,
        dest="region", help="Web service region to use")
    opts, args = parser.parse_args()

    if not opts.aws_access_key_id:
        parser.error("AWS access key required")

    if not opts.aws_secret_access_key:
        parser.error("AWS secret key required")

    if os.path.isfile(opts.aws_access_key_id):
        aws_access_key_id = open(opts.aws_access_key_id).read().strip()
    else:
        aws_access_key_id = opts.aws_access_key_id

    if os.path.isfile(opts.aws_secret_access_key):
        aws_secret_access_key = open(opts.aws_secret_access_key).read().strip()
    else:
        aws_secret_access_key = opts.aws_secret_access_key

    stop_all(aws_access_key_id, aws_secret_access_key, region=opts.region)


if __name__ == "__main__":
    main()
