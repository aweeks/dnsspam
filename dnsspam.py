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
    
    count = query.get('count', 1)
    delay = query.get('delay', 0)
    qname = query['qname']
    rdtype = query['rdtype']

    for n in range(0, count):
        if n % 100 == 0:
            LOG.debug('query: %s %s #%d', qname, rdtype, n)
        resolver.query(qname, rdtype).rrset.items
        time.sleep(delay/1000.0)

def do_parallel_queries(args, pool, queries):
    try:
        pool.map_async(partial(do_query, args), queries).get(100000000)
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
