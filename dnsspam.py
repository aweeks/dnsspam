#!/usr/bin/env python

import argparse
from dns.resolver import Resolver
import simplejson as json
import time
import logging
from multiprocessing import Pool
from functools import *
from itertools import *
import signal
import sys

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

LOG.addHandler(ch)

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def do_query(args, query):
    resolver = Resolver(filename=args.resolv)

    LOG.debug('using nameservers %s', resolver.nameservers)
    
    count = query.get('count', 1)
    delay = query.get('delay', 0)
    qname = query['qname']
    rdtype = query['rdtype']

    error_count = 0
    for n in range(0, count):
        if n % 100 == 0:
            LOG.debug('query: %s %s #%d', qname, rdtype, n)
        try:
            resolver.query(qname, rdtype)
        except Exception:
            error_count += 1
        time.sleep(delay/1000.0)

    return count, error_count

def do_parallel_queries(args, pool, queries):
    try:
        start = time.time()
        counts = pool.map_async(partial(do_query, args), queries).get(100000000)
        duration = time.time() - start
        
        success = sum([l[0] for l in counts])
        error = sum([l[1] for l in counts])
        LOG.debug('success: %d queries in %f seconds = %f queries/second', success, duration, success/duration)
        LOG.debug('error: %d queries in %f seconds = %f queries/second', error, duration, error/duration)
    except KeyboardInterrupt:
        pool.terminate()
        sys.exit(1)

POOL = Pool(20, init_worker)

def main():
    parser = argparse.ArgumentParser(description='Generate lots of DNS queries')
    parser.add_argument('--resolv', type=str, help='resolv.conf')
    parser.add_argument('--queries', type=str, help='query config')

    args = parser.parse_args()
    
    with open(args.queries, 'r') as f:
        queries = json.loads(f.read())

    for qs in queries:
        do_parallel_queries(args, POOL, qs)

if __name__ == '__main__':
    main()
    time.sleep(1.0)
