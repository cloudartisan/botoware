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


import sys
from optparse import OptionParser
from boto.exception import BotoClientError
from boto.ec2.connection import EC2Connection
from boto.ec2.securitygroup import SecurityGroup


class GroupRenameError(BotoClientError): pass


def renameGroup(connection, orig, new, region=None, terminate=False):
    origGroup = SecurityGroup(connection, name=orig)
    instances = origGroup.instances()
    if len(instances) > 0:
        if terminate == False:
            raise GroupRenameError("Security group in use, not terminating")
        # FIXME need to write a busy wait with timeout
        raise NotImplementedError("renameGroup:terminate + busy wait + timeout")
        connection.terminate_instances(instances)
    newGroup = connection.create_security_group(new, origGroup.description)
    newGroup.rules = origGroup.rules


def main():
    parser = OptionParser()
    parser.usage = "%prog: [options] <original name> <new name>"
    parser.add_option("-A", "--aws-access-key-id",
        dest="awsAccessKeyID", help="AWS access key ID")
    parser.add_option("-S", "--aws-secret-access-key",
        dest="awsSecretAccessKey", help="AWS secret access key")
    parser.add_option("--region", default=None,
        dest="region", help="Web service region to use")
    parser.add_option("-t", "--terminate", action="store_true", default=False,
        dest="terminate", help="Terminate instances using the security group")
    opts, args = parser.parse_args(sys.argv[1:])

    if not (opts.awsAccessKeyID or opts.awsSecretAccessKey):
        parser.error("provide AWS access key ID and secret access key")

    if not (len(args) == 2):
        parser.error("supply original and new group names")

    orig = args[0]
    new = args[1]

    try:
        connection = EC2Connection(opts.awsAccessKeyID, opts.awsSecretAccessKey)
        renameGroup(connection, orig, new, opts.region, opts.terminate)
    except GroupRenameError, message:
        sys.stderr.write("%s\n" % message)
        sys.exit(1)


if __name__ == "__main__":
    main()
