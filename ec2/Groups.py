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


from boto.ec2 import get_region
from boto.ec2.connection import EC2Connection
from boto.exception import EC2ResponseError
from Instances import wait_for_state_by_instances


class GroupError(Exception): pass
class GroupMoveError(GroupError): pass
class GroupCopyError(GroupError): pass


def copy_group(aws_access_key, aws_secret_key, src_group_name, dst_group_name,
        src_region_name="us-east-1", dst_region_name="us-east-1",
        force=False, terminate=False):
    if (src_group_name == dst_group_name) and (src_region_name == dst_region_name):
        raise GroupCopyError, "source and destination are identical"
    # Get the source and destination regions
    src_region = get_region(src_region_name,
        aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    dst_region = get_region(dst_region_name,
        aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    # Get the source and destination connections
    src_conn = EC2Connection(aws_access_key, aws_secret_key, region=src_region)
    dst_conn = EC2Connection(aws_access_key, aws_secret_key, region=dst_region)
    # Find the source group, otherwise give up
    try:
        src_group = src_conn.get_all_security_groups([src_group_name])[0]
        src_instances = src_group.instances()
    except IndexError:
        raise GroupCopyError, "unable to find source group"
    # Find the destination group, if it exists
    try:
        dst_group = dst_conn.get_all_security_groups([dst_group_name])[0]
        dst_instances = dst_group.instances()
    except (IndexError, EC2ResponseError):
        dst_group = None
        dst_instances = []
    # If the destination group exists but we have not been asked to force,
    # give up now before we do any damage
    if dst_group and not force:
        raise GroupCopyError, "destination already exists"
    # If asked to terminate, find any instances using the destination
    # group and terminate them
    if terminate:
        for instance in dst_instances:
            instance.stop()
        wait_for_state_by_instances(dst_instances, "terminated")
    # If the destination group exists and we have been asked to force,
    # delete it
    if dst_group and force:
        dst_group.delete()
    # Copy the group and return the newly-created group
    new_group = src_group.copy_to_region(dst_region, dst_group_name)
    return new_group


def move_group(aws_access_key, aws_secret_key, src_group_name, dst_group_name,
        src_region_name="us-east-1", dst_region_name="us-east-1",
        force=False, terminate=False):
    if (src_group_name == dst_group_name) and (src_region_name == dst_region_name):
        raise GroupMoveError, "source and destination are identical"
    # Get the source and destination regions
    src_region = get_region(src_region_name,
        aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    dst_region = get_region(dst_region_name,
        aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    # Get the source and destination connections
    src_conn = EC2Connection(aws_access_key, aws_secret_key, region=src_region)
    dst_conn = EC2Connection(aws_access_key, aws_secret_key, region=dst_region)
    # Find the source group, otherwise give up
    try:
        src_group = src_conn.get_all_security_groups([src_group_name])[0]
        src_instances = src_group.instances()
    except IndexError:
        raise GroupMoveError, "unable to find source group"
    # Find the destination group, if it exists
    try:
        dst_group = dst_conn.get_all_security_groups([dst_group_name])[0]
        dst_instances = dst_group.instances()
    except (IndexError, EC2ResponseError):
        dst_group = None
        dst_instances = []
    # If the destination group exists but we have not been asked to force,
    # give up now before we do any damage
    if dst_group and not force:
        raise GroupMoveError, "destination already exists"
    # If asked to terminate, find any instances using the source group
    # and/or destination group and terminate them
    if terminate:
        for instance in src_instances + dst_instances:
            instance.stop()
        wait_for_state_by_instances(src_instances + dst_instances, "terminated")
    # If the destination group exists and we have been asked to force,
    # delete it
    if dst_group and force:
        dst_group.delete()
    # Copy the group, delete the original group, return the newly-created
    # group
    new_group = src_group.copy_to_region(dst_region, dst_group_name)
    src_group.delete()
    return new_group
