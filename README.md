# CoinSearchr-site
CoinSearchr Flask site to serve the CoinSearchr search tool at https://coinsearchr.com/.

CoinSearchr is a website which allows for easy searching/lookup of many cryptocurrencies. It is natively compatible with OpenSearch-compatible browsers like Firefox and Vivaldi.

## Guides
* https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3
* https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04
* AWStats Setup: https://luxagraf.net/src/awstats-nginx-ubuntu-debian

## Common Tasks
### Run a Dev Server
1. `source venv/bin/activate`
2. `export FLASK_APP=coinsearchr` (optional)
3. `export FLASK_ENV=development` (enables auto-reload and others)
4. Run the dev server like `python3 wsgi.py`, and access it through the nginx HTTPS port forwarder on https://coinsearchr.com:5001/

### Management
* Do management actions with `python3 manage.py -h` (like `python3 manage.py -a init_db` and `python3 manage.py -a run_tasks`)

## Server Notes
* Server must be in Etc/UTC time

