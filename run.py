#!/usr/bin/env python
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-u", "--url", dest="url", required=True,
                    help="url to fetch data", metavar="path")
parser.add_argument("-q", "--quiet",
                    action="store_false", dest="verbose", default=True,
                    help="don't print status messages to stdout")

args = parser.parse_args()

print(args)
