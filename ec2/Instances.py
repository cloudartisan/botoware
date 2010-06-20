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


import time


class InstanceError(Exception): pass
class StateTimeoutError(InstanceError): pass


def wait_for_state_by_instances(instances, desired_state, timeout=300, nap=10):
    """
    Waits a limited period of time for a list of instances to reach a
    desired state.  Raises StateTimeoutError if the timeout occurs.
    """
    start = time.time()
    end = start + timeout
    waiting = instances[:]
    while waiting and time.time() < end:
        checking = waiting[:]
        for instance in checking:
            instance.update()
            if instance.state == desired_state:
                waiting.remove(instance)
            else:
                print "[%d] %s not ready" % (time.time() - start, instance)
        time.sleep(nap)
    if len(waiting) != 0:
        raise StateTimeoutError("%s still running" % waiting)


def reboot_all(aws_access_key_id, aws_secret_access_key, region):
    """
    Reboots all running instances in a given region.
    """
    connection = EC2Connection(aws_access_key_id, aws_secret_access_key,
        region=region)
    instances = []
    reservations = connection.get_all_instances()
    for reservation in reservations:
        instances.extend([instance.id for instance in reservation.instances])
    connection.reboot_instances(instances)


def stop_all(aws_access_key_id, aws_secret_access_key, region):
    """
    Stops all running instances in a given region.
    """
    connection = EC2Connection(aws_access_key_id, aws_secret_access_key,
        region=region)
    reservations = connection.get_all_instances()
    for reservation in reservations:
        reservation.stop_all()
