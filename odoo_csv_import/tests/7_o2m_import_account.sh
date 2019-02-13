#!/usr/bin/env bash
$1 ../odoo_import_thread.py --file=origin/test3a.csv --model='account.invoice' --size=50 --worker=1 --conf=conf/connection.conf --o2m --sep=

../odoo_import_thread.py --file=origin/account.invoice10.csv --model='account.invoice' --size=50 --worker=1 --conf=conf/connection.conf --o2m --sep=','

../odoo_import_thread.py --file=origin/stock.pickingb-ordera.csv --model='stock.picking' --size=50 --worker=1 --conf=conf/connection.conf --o2m --sep=','