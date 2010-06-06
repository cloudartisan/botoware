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
Moves a group from one region to another.
"""


import os, sys
import time
from optparse import OptionParser
from boto.exception import EC2ResponseError
from boto.ec2.connection import EC2Connection
from boto.ec2.securitygroup import SecurityGroup
from BeautifulSoup import BeautifulStoneSoup
from utils import TimeoutError, waitForStateWithTimeout


class GroupRenameError(Exception): pass


def moveGroup(connection, group, newRegion, terminate=False):
    instances = group.instances()
    if len(instances) > 0 and terminate == False:
        raise GroupRenameError("Security group in use, not terminating")
    if instances:
        connection.terminate_instances([instance.id for instance in instances])
        waitForStateWithTimeout(instances, "terminated")
    group.copy_to_region(newRegion, group.name)
    group.delete()


def main():
    parser = OptionParser()
    parser.usage = "%prog: [options] <group name> <from region> <to region>"
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
    parser.add_option("-f", "--force",
        default=False,
        action="store_true",
        dest="force",
        help="If the destination group already exists, overwrite it")
    parser.add_option("-t", "--terminate",
        default=False,
        action="store_true",
        dest="terminate",
        help="Terminate instances using the security group")
    opts, args = parser.parse_args(sys.argv[1:])

    if not (opts.awsAccessKeyID or opts.awsSecretAccessKey):
        parser.error("provide AWS access key ID and secret access key")

    if len(args) != 3:
        parser.error("insufficient arguments")

    groupName = args[0]
    fromRegion = args[1]
    toRegion = args[2]
    if fromRegion == toRegion:
        sys.stderr.write("From and to regions must be different\n")
        sys.exit(1)

    awsAccessKeyID = opts.awsAccessKeyID
    awsSecretAccessKey = opts.awsSecretAccessKey
    region = opts.region

    try:
        connection = EC2Connection(awsAccessKeyID, awsSecretAccessKey,
            region=fromRegion)
        srcGroup = connection.get_all_security_groups([groupName])[0]
    except IndexError:
        sys.stderr.write("No such group %s, wrong region?\n" % origName)
        sys.exit(1)
    except EC2ResponseError:
        soup = BeautifulStoneSoup(response.body)
        reason = soup.response.errors.error.message.contents[0]
        sys.stderr.write("%s\n" % reason)
        sys.exit(1)

    # If force, get rid of any destination that might be in the way
    if opts.force:
        try:
            connection = EC2Connection(awsAccessKeyID, awsSecretAccessKey,
                region=toRegion)
            destGroup = connection.get_all_security_groups([groupName])[0]
            destGroup.delete()
        except (IndexError, EC2ResponseError):
            pass

    try:
        moveGroup(connection, srcGroup, toRegion, opts.terminate)
    except (GroupRenameError, TimeoutError), message:
        sys.stderr.write("%s\n" % message)
        sys.exit(1)
    except EC2ResponseError, response:
        soup = BeautifulStoneSoup(response.body)
        reason = soup.response.errors.error.message.contents[0]
        sys.stderr.write("%s\n" % reason)
        sys.exit(1)


if __name__ == "__main__":
    main()
