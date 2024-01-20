#!/usr/bin/env python
import json
from argparse import ArgumentParser
from urllib.request import urlopen
import logging
import glob
import os


parser = ArgumentParser()
parser.add_argument("-u", "--url", dest="url", required=True,
                    help="url to fetch data", metavar="path")
parser.add_argument("-v", "--verbose",
                    action="store_true", dest="verbose", default=False,
                    help="print status messages to stdout")

args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.ERROR)

logging.info('starting cleanup')
for f in glob.glob("./nginx/conf.d/*.conf"):
    os.remove(f)
logging.info('cleanup done')


logging.info(f'fetching url: {args.url}')

json_data = urlopen(args.url).read()
logging.info(f'json_data: {json_data}')

for item in json.loads(urlopen(args.url).read()):
    logging.info(f'started processing {item["domain"]}')
    with open(f"./nginx/conf.d/{item['domain']}.conf", "w") as f:
        f.write(f"""
server {{
    listen 80;
    server_name {item['domain']};
    location / {{
        proxy_pass {item['cf']};
    }}
    access_log /var/log/nginx/access-{item['domain']}.log;
    error_log /var/log/nginx/error-{item['domain']}.log;
}}
""")
    logging.info(f'finished processing {item["domain"]}')
logging.info('done')