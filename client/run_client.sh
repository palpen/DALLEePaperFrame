#!/usr/bin/bash
# The IP adress should be the IP address of the server, not the IP address of the app (which is 0.0.0.0)
python3 client.py --server-address $1 --config-file $2
