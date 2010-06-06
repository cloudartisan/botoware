#!/usr/bin/env python

"""
Copyright (c) 2010 David Taylor
http://www.cloudartisan.com

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


from optparse import OptionParser
from boto.ec2.connection import EC2Connection


def stopall(connection):
    instances = []
    reservations = connection.get_all_instances()
    for reservation in reservations:
        instances.extend([instance.id for instance in reservation.instances])
    connection.stop_instances(instances)


def main():
    parser = OptionParser()
    parser.add_option("-A", "--aws-access-key-id",
        dest="awsAccessKeyID", help="AWS access key ID")
    parser.add_option("-S", "--aws-secret-access-key",
        dest="awsSecretAccessKey", help="AWS secret access key")
    opts, args = parser.parse_args()

    if not opts.awsAccessKeyID:
        parser.error("AWS access key ID required")
    if not opts.awsSecretAccessKey:
        parser.error("AWS secret access key required")

    connection = EC2Connection(opts.awsAccessKeyID, opts.awsSecretAccessKey)
    stopall(connection)


if __name__ == "__main__":
    main()
