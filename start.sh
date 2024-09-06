#!/bin/bash

WP='/opt/G19s'
cd $WP

source .env/bin/activate
if [ "$?" -ne 0 ]; then
    echo "Error"
    exit 1
fi

/opt/G19s/.env/bin/python main.py
if [ "$?" -ne 0 ]; then
    echo "Error"
    exit 2
fi