# Nginx Virtualhost Generator & Certbot

## requirements

- python3.6+
- nginx

# usage

```bash
./run.py

usage: run.py [-h] -u path -e email [--production] [-v]
run.py: error: the following arguments are required: -u/--url, -e/--email
```

```bash
./run.py -u https://268f-103-240-162-120.ngrok-free.app/sample_domains.json --verbose -e pratikb@york.ie
```
