#!/usr/bin/env python
import json
from argparse import ArgumentParser
from urllib.request import urlopen
import logging
import glob
from os import symlink, remove
from os.path import exists
from certbot.main import main as certbot_main
from shutil import copy

parser = ArgumentParser()
parser.add_argument("-u", "--url", dest="url", required=True,
                    help="url to fetch data", metavar="path")
parser.add_argument('-e', '--email', dest='email', required=True,
                    help="email address to register with letsencrypt", metavar="email")
parser.add_argument('--production', dest='production', action='store_true',
                    help="use production letsencrypt server", default=False)
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
    remove(f)

logging.info('cleanup done')

logging.info(f'fetching url: {args.url}')

json_data = urlopen(args.url).read()
logging.info(f'json_data: {json_data}')

domains = []

for item in json.loads(urlopen(args.url).read()):
    logging.info(f'started processing {item["domain"]}')
    domains.append(item['domain'])

    with open(f"./nginx/conf.d/{item['domain']}.conf", "w") as f:
        f.write(f"""
server {{
    listen 80;
    server_name {item['domain']} www.{item['domain']};
    location / {{
        proxy_pass {item['cf']};
    }}
    access_log /var/log/nginx/access-{item['domain']}.log;
    error_log /var/log/nginx/error-{item['domain']}.log;
}}
""")

    logging.info(f'finished processing {item["domain"]}')
logging.info('done')

certbot_args = [
    '--nginx',
    '--agree-tos',
    '-m', args.email,
    '--redirect',
    '--non-interactive',
    '--expand',
    '--force-renewal',
    '--work-dir', '/tmp/work',
    '--config-dir', '/tmp/config',
    '--logs-dir', '/tmp/logs',
    '--domains', ','.join(domains)
]

for file in glob.glob("./nginx/conf.d/*.conf"):
    copy(file, "/etc/nginx/sites-available/")
    soft_dest = f"/etc/nginx/sites-enabled/{file.split('/')[-1]}"

    if exists(soft_dest):
        remove(soft_dest)

    symlink(f"/etc/nginx/sites-available/{file.split('/')[-1]}", soft_dest)

if not args.production:
    certbot_args.extend(['--staging',
                         '--dry-run',
                         '--test-cert',
                         'certonly'])

certbot_main(certbot_args)
