#!/usr/bin/env python

from twisted.internet import reactor
from twisted.internet import task
from twisted.names.client import Resolver

from functools import *
from itertools import *

import sys
import time

r = Resolver('127.0.0.1')

success_count = 0
fail_count = 0
start_ts = 0
stop_ts = 0

def dns_callback(data):
    global success_count

    success_count += 1
    if success_count % 1000 == 0:
        print 'success: %d' % (success_count,)

def dns_errback(data):
    global fail_count

    fail_count += 1
    if fail_count % 1000 == 0:
        print 'error: %d' % (fail_count,)

    pass

def do_query(addr):
    r.lookupAddress(addr).addCallbacks(dns_callback, dns_errback)


def die():
    global success_count
    global fail_count
    
    stop_ts = time.time()
    reactor.stop()

    delta = stop_ts - start_ts
    
    print 'success: %d queries in %f seconds = %f queries/second' % (success_count, delta, success_count/delta)
    print delta
    print 'fail: %d queries in %f seconds = %f queries/second' % (fail_count, delta, fail_count/delta)

ADDRS = ['google.com', 'reddit.com', 'yahoo.com', 'rackspace.com']

for a in islice(cycle(ADDRS), 0, 100):
     task.LoopingCall(partial(do_query, a)).start(0)

reactor.callLater(10, die)

start_ts = time.time()
reactor.run()
