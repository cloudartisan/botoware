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


import time


class TimeoutError(Exception): pass


def waitForStateWithTimeout(instances, desiredState, timeout=300, nap=10):
    """
    Waits a limited period of time for a list of instances to reach a
    desired state.  Raises TimeoutError if the timeout occurs.
    """
    start = time.time()
    end = start + timeout
    waiting = instances[:]
    while waiting and time.time() < end:
        checking = waiting[:]
        ready = []
        for instance in checking:
            instance.update()
            if instance.state == desiredState:
                waiting.remove(instance)
            else:
                print "[%d] %s not ready" % (time.time() - start, instance)
        time.sleep(nap)
    if len(waiting) != 0:
        raise TimeoutError("%s still running" % waiting)
